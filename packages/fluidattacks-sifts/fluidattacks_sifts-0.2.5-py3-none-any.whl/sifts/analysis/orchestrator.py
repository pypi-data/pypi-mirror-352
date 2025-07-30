import logging
from collections.abc import AsyncGenerator
from pathlib import Path

from agents import Agent, ModelSettings
from boto3 import Session
from openai.types.shared import Reasoning
from tree_sitter import Node

from sifts.analysis.code_parser import (
    analyze_method_node,
    iter_project_functions,
    process_file_for_functions,
)
from sifts.analysis.results_processor import convert_analysis_result, process_result
from sifts.analysis.tools.search_by_id import GET_FUNCTION_BY_ID_TOOL
from sifts.analysis.tools.search_by_name import SEARCH_FUNCTION_TOOL
from sifts.analysis.types import TreeExecutionContext, VulnerabilityAssessment
from sifts.common_types.snippets import ItemAnalysisResult, Safe, Vulnerable
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import merge_async_generators
from sifts.core.types import Language
from sifts.io.db.ctags_tinydb import create_tiny_db_from_ctags
from sifts.io.db.dynamodb import create_dynamo_context
from sifts.io.db.opensearch_client import setup_opensearch_client
from sifts.io.db.sqlite import SQLiteVulnDB
from sifts.io.file_system import find_projects
from sifts.llm.config_data import MODEL_PARAMETERS
from sifts.llm.constants import LLM_MODELS
from sifts.llm.router import ResilientRouter

LOGGER = logging.getLogger(__name__)


def get_agent(*, strict: bool = True, enable_navigation: bool = False) -> Agent:
    return Agent(
        name="Hacker",
        instructions=MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["system"]
        if strict
        else MODEL_PARAMETERS["prompts"]["agents"]["vuln_loose"]["system"],
        mcp_servers=[],
        model="o4-mini",
        model_settings=ModelSettings(reasoning=Reasoning(effort="low")),
        tools=(
            [
                SEARCH_FUNCTION_TOOL,
                GET_FUNCTION_BY_ID_TOOL,
            ]
            if enable_navigation
            else []
        ),
        output_type=VulnerabilityAssessment,
    )


async def analyze_project(
    *,
    config: SiftsConfig,
    context: TreeExecutionContext,
    exclude: list[str] | None = None,
) -> AsyncGenerator[Vulnerable | Safe | None, None]:
    agent = get_agent(
        strict=config.analysis.strict_mode,
        enable_navigation=config.analysis.enable_navigation,
    )

    function_iter = (
        iter_functions_from_line_config(context, config)
        if config.analysis.lines_to_check
        else iter_functions_from_project(
            context,
            config,
            exclude,
        )
    )

    function_pairs = []
    async for where, method_node in function_iter:
        function_pairs.append((where, method_node))

    function_coroutines = [
        analyze_method_node(
            method_node=method_node,
            where=where,
            context=context,
            agent=agent,
            config=config,
        )
        for where, method_node in function_pairs
    ]

    async for result in merge_async_generators(function_coroutines, limit=50):
        try:
            if result is not None:
                yield result
        except Exception:
            LOGGER.exception("Error processing function")


async def get_valid_functions(
    file_path: Path,
    lines: list[int],
) -> list[Node]:
    result: list[Node] = []
    async for _, node in process_file_for_functions(file_path):
        if any(x for x in lines if node.start_point[0] <= x <= node.end_point[0]):
            result.append(node)
    return result


async def iter_functions_from_line_config(
    context: TreeExecutionContext,
    config: SiftsConfig,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields functions to analyze based on line configs."""
    for line_config in config.analysis.lines_to_check:
        if not (config.analysis.working_dir / line_config.file).is_relative_to(
            context.working_dir,
        ):
            continue
        functions = await get_valid_functions(
            config.analysis.working_dir / line_config.file,
            line_config.lines,
        )
        for function in functions:
            yield (
                (config.analysis.working_dir / line_config.file).relative_to(
                    config.analysis.working_dir,
                ),
                function,
            )


async def iter_functions_from_project(
    context: TreeExecutionContext,
    config: SiftsConfig,
    exclude: list[str] | None = None,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields all functions in the project."""
    async for file_path, function_node in iter_project_functions(
        context.working_dir,
        config.analysis.exclude_files + (exclude or []),
        include_patterns_param=config.analysis.include_files or None,
        start_working_dir=config.analysis.working_dir,
    ):
        try:
            where = Path(context.working_dir, file_path).relative_to(config.analysis.working_dir)
        except ValueError:
            where = Path(file_path)
        if not (config.analysis.working_dir / where).exists():
            LOGGER.warning("File %s does not exist", where)
            continue
        yield (where, function_node)


LOGGER = logging.getLogger(__name__)


SESSION = Session()
dynamo_startup, dynamo_shutdown, get_resource = create_dynamo_context()


async def scan_projects(config: SiftsConfig) -> list[ItemAnalysisResult]:
    await dynamo_startup()
    router = ResilientRouter(
        model_list=LLM_MODELS,
        routing_strategy="simple-shuffle",
        enable_pre_call_checks=True,
        cache_responses=True,
    )
    if router.cache.redis_cache is not None:
        await router.cache.redis_cache.ping()
    db_client = SQLiteVulnDB(
        str(config.results_db_path),
    )

    projects = find_projects(config.analysis.working_dir)
    open_client = await setup_opensearch_client()

    all_results = []

    async def process_single_project(
        working_dir: Path,
        language: Language,
        exclude: list[str] | None,
    ) -> AsyncGenerator[ItemAnalysisResult, None]:
        """Procesa un solo proyecto y retorna sus vulnerabilidades."""
        if config.analysis.lines_to_check and not any(
            (config.analysis.working_dir / item.file).is_relative_to(working_dir)
            for item in config.analysis.lines_to_check
        ):
            return

        LOGGER.info(
            "Analyzing project %s",
            working_dir.relative_to(Path(config.analysis.working_dir)),
        )
        tiny_db = await create_tiny_db_from_ctags(working_dir, exclude, language)
        context = TreeExecutionContext(
            working_dir=working_dir,
            tiny_db=tiny_db,
            db_client=db_client,
            analysis_dir=Path(config.analysis.working_dir),
            open_client=open_client,
            router=router,
        )

        try:
            # Get results from analyze_project_tree directly as AsyncGenerator
            async for response in analyze_project(
                context=context,
                config=config,
                exclude=exclude,
            ):
                if response is not None:
                    # Convert the result (equivalent to the map operation)
                    converted = convert_analysis_result(
                        response,
                        group_name=config.context.group_name or "",
                    )

                    # Process the result and add to our list
                    processed = await process_result(
                        converted,
                        db_client,
                    )
                    yield processed
        except Exception:
            LOGGER.exception(
                "Error in analysis for project %s",
                working_dir.relative_to(Path(config.analysis.working_dir)),
            )

    # Crear coroutines para cada proyecto
    project_coroutines = [
        process_single_project(working_dir, language, exclude)
        for working_dir, language, exclude in projects
    ]

    # Usar limited_as_completed para procesar proyectos con límite de concurrencia
    async for project_result in merge_async_generators(project_coroutines, limit=3):
        try:
            all_results.append(project_result)
        except Exception:
            LOGGER.exception("Error processing project")

    LOGGER.info("Total vulnerabilities found: %d", len(all_results))
    return await db_client.get_vulnerabilities_vulnerable()
