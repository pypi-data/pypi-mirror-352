import asyncio
import fnmatch
import hashlib
import logging
from collections.abc import AsyncGenerator, Generator
from os import walk
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING

import aiofiles
from agents import Agent, MaxTurnsExceeded, Runner, trace
from fluidattacks_core.serializers.snippet import find_function_name
from fluidattacks_core.serializers.syntax import (
    TREE_SITTER_FUNCTION_DECLARATION_MAP,
    InvalidFileType,
    extract_imports,
    get_language_from_path,
    parse_content_tree_sitter,
    query_nodes_by_language,
)
from opensearchpy import AsyncOpenSearch
from tree_sitter import Node

from sifts.analysis.criteria import filter_candidate_codes, generate_candidate_text
from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.analysis.types import TreeExecutionContext, VulnerabilityAssessment
from sifts.common_types.snippets import (
    Safe,
    Snippet,
    SnippetHit,
    Vulnerable,
    num_tokens_from_string,
)
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import limited_parallel
from sifts.io.db.opensearch_client import (
    SearchParameters,
    search_similar_vulnerabilities_by_field_name_bm25,
    search_similar_vulnerabilities_by_knn_code,
)
from sifts.io.file_system_defaults import TEST_FILES
from sifts.llm.config_data import MODEL_PARAMETERS
from sifts.llm.propose_changes import get_functional_semantics
from sifts.llm.ranking import reciprocal_rank_fusion_with_score
from sifts.llm.router import RouterStrict
from sifts.llm.usage import calculate_cost

if TYPE_CHECKING:
    from openai.types.responses import (
        ResponseInputItemParam,
    )

LOGGER = logging.getLogger(__name__)


async def _create_snippet(  # noqa: PLR0913
    *,
    root_id: str,
    group_name: str | None,
    where: str,
    method_node: Node,
    language: str,
    code: str,
) -> Snippet | None:
    try:
        function_name = None
        identifier_ = find_function_name([method_node], language)
        if identifier_:
            identifier_node, _ = identifier_
            text = identifier_node.text
            function_name = (
                text.decode("utf-8") if (text is not None and isinstance(text, bytes)) else text
            )

        snippet_hash = hashlib.sha3_256(code.encode()).hexdigest()
        return Snippet(
            sk=f"ROOT#{root_id}",
            pk=f"PATH#{where}#SNIPPET#{snippet_hash}",
            commit="",
            hash_type="sha3_256",
            language=language,
            snippet_content=code,
            group_name=group_name,
            root_id=root_id,
            root_nickname=None,
            snippet_hash=snippet_hash,
            where=where,
            start_point=[method_node.start_point.row + 1, method_node.start_point.column + 1],
            end_point=[method_node.end_point.row + 1, method_node.end_point.column + 1],
            name=function_name,
        )
    except ValueError:
        return None


async def _get_semantics_and_embeddings(
    snippet: Snippet,
    router: RouterStrict,
) -> tuple[str | None, str | None]:
    if not snippet.snippet_content:
        return None, None

    abstract_propose, detailed_behavior = await get_functional_semantics(
        code=snippet.snippet_content,
        router=router,
    )
    if not abstract_propose or not detailed_behavior:
        return None, None

    return abstract_propose, detailed_behavior


async def _search_candidates(
    open_client: AsyncOpenSearch,
    snippet: Snippet,
    abstract_propose: str,
    detailed_behavior: str,
    search_parameters: SearchParameters,
) -> list[str]:
    if not snippet.snippet_content:
        return []

    candidates_hits: list[SnippetHit] = reciprocal_rank_fusion_with_score(
        top_n=100,
        hits_lists=await asyncio.gather(
            *[
                search_similar_vulnerabilities_by_knn_code(
                    open_client=open_client,
                    snippet_content=snippet.snippet_content,
                    search_parameters=search_parameters,
                ),
                search_similar_vulnerabilities_by_field_name_bm25(
                    open_client=open_client,
                    field_value=abstract_propose,
                    field_name="abstract_propose",
                    search_parameters=search_parameters,
                ),
                search_similar_vulnerabilities_by_field_name_bm25(
                    open_client=open_client,
                    field_value=detailed_behavior,
                    field_name="detailed_behavior",
                    search_parameters=search_parameters,
                ),
            ],
        ),
    )
    filtered_candidates = filter_candidate_codes(candidates_hits)[:10]
    unique_codes = set()
    result = []
    for candidate in filtered_candidates:
        code = candidate["_source"]["metadata"]["criteria_code"]
        if code not in unique_codes:
            unique_codes.add(code)
            result.append(code)

    return result


async def _process_single_candidate_group(  # noqa: PLR0911, PLR0913
    candidates_group: list[str],
    context: TreeExecutionContext,
    snippet: Snippet,
    agent: Agent,
    imports: str,
    *,
    strict: bool = True,
    candidate_index: int,
) -> Vulnerable | Safe | None:
    candidate_id = "-".join(candidates_group)
    previous_result = await context.db_client.get_vulnerability(
        pk=f"ROOT#{snippet.root_id}#PATH#{snippet.where}",
        sk=f"SNIPPET#{snippet.snippet_hash}#CANDIDATE#{candidate_id}",
    )
    if previous_result:
        return None

    candidate_text = generate_candidate_text(candidates_group)
    code_enumerated = "\n".join(
        (
            f"{index}| {x}"
            for index, x in enumerate(
                (snippet.snippet_content or "").split("\n"),
                start=snippet.start_point[0] or 0,
            )
        ),
    )
    count = num_tokens_from_string(code_enumerated, "gpt-4o")
    if count > 3000:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too long to be processed: %s:%s, count: %s",
            snippet.where,
            snippet.start_point[0],
            count,
        )
        return None
    if count < 50:  # noqa: PLR2004
        LOGGER.debug(
            "Code is too short to be processed: %s:%s, count: %s",
            snippet.where,
            snippet.start_point[0],
            count,
        )
        return None
    first_message: ResponseInputItemParam = {
        "role": "user",
        "content": Template(
            MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["instructions"]
            if strict
            else MODEL_PARAMETERS["prompts"]["agents"]["vuln_loose"]["instructions"],
        ).safe_substitute(
            code=code_enumerated,
            functionName=snippet.name,
            vulnerability_knowledge=candidate_text,
            filePath=snippet.where,
            imports=imports,
        ),
    }
    trace_id = None
    with trace(
        "process_candidate_group",
        group_id=snippet.root_id,
        metadata={
            "where": snippet.where,
            "group": snippet.group_name,
            "candidate_id": candidate_id,
            "root_id": snippet.root_id,
            "snippet_hash": snippet.snippet_hash,
        },
    ) as _trace:
        trace_id = _trace.trace_id
        try:
            response = await Runner.run(
                starting_agent=agent,
                input=[first_message],
                max_turns=10,
                context=context,
            )
        except MaxTurnsExceeded:
            return None

    cost = calculate_cost(response.raw_responses[0].usage, str(response._last_agent.model))
    result: VulnerabilityAssessment = response.final_output
    if result.is_vulnerable:
        if snippet.name is not None and result.vulnerable_function != snippet.name:
            return None
        finding_code = candidates_group[0]
        return Vulnerable(
            function_hash=snippet.snippet_hash,
            defines_code=finding_code,
            defines_title=DEFINES_VULNERABILITIES[finding_code]["en"]["title"],
            description=result.explanation,
            where=snippet.where,
            specific=result.vulnerable_line,
            candidate_id=candidate_id,
            root_id=snippet.root_id,
            cost=cost,
            candidate_index=candidate_index,
            trace_id=trace_id,
        )
    return Safe(
        function_hash=snippet.snippet_hash,
        description=result.explanation,
        where=snippet.where,
        candidate_id=candidate_id,
        root_id=snippet.root_id,
        cost=cost,
        candidate_index=candidate_index,
        trace_id=trace_id,
    )


async def analyze_method_node(  # noqa: PLR0911
    *,
    context: TreeExecutionContext,
    where: Path,
    agent: Agent,
    method_node: Node,
    config: SiftsConfig,
) -> AsyncGenerator[Vulnerable | Safe | None, None]:
    try:
        async with aiofiles.open(config.analysis.working_dir / where, "rb") as f:
            file_content = await f.read()
        code = file_content[method_node.start_byte : method_node.end_byte].decode("utf-8")
        language = get_language_from_path(str(where))
        if not language or not code:
            return

        imports_nodes = extract_imports(
            await (await aiofiles.open(config.analysis.working_dir / where)).read(),
            language,
        )
        imports = "\n".join([(x.text or b"").decode() for x in imports_nodes])
    except FileNotFoundError:
        LOGGER.warning("File not found: %s", where)
        return
    except UnicodeDecodeError:
        LOGGER.warning("File is not UTF-8 encoded: %s", where)
        return

    snippet = await _create_snippet(
        root_id=config.context.root_id or "",
        group_name=config.context.group_name,
        where=str(where),
        method_node=method_node,
        language=language,
        code=code,
    )
    if snippet is None:
        return

    vulnerabilities = await context.db_client.get_vulnerabilities_by_snippet(
        root_id=config.context.root_id or "",
        path=snippet.where,
        snippet_hash=snippet.snippet_hash,
    )
    if vulnerabilities:
        return
    await context.db_client.insert_snippet(snippet)

    if not snippet.snippet_content:
        return

    abstract_propose, detailed_behavior = await _get_semantics_and_embeddings(
        snippet=snippet,
        router=context.router,
    )
    if not abstract_propose or not detailed_behavior:
        return

    candidate_codes = await _search_candidates(
        open_client=context.open_client,
        search_parameters=SearchParameters(
            include_vulnerabilities=config.analysis.include_vulnerabilities,
            exclude_vulnerabilities=config.analysis.exclude_vulnerabilities,
            group_name=config.context.group_name,
        ),
        snippet=snippet,
        abstract_propose=abstract_propose,
        detailed_behavior=detailed_behavior,
    )

    tasks = [
        _process_single_candidate_group(
            candidates_group=[candidate_code],
            snippet=snippet,
            agent=agent,
            context=context,
            imports=imports,
            candidate_index=index,
        )
        for index, candidate_code in enumerate(candidate_codes)
    ]

    async for result in limited_parallel(tasks, limit=10):
        yield result


def _is_top_level_function(node: Node, function_node_names: set[str]) -> bool:
    parent = node.parent
    while parent:
        if parent.type in function_node_names:
            return False  # It's nested
        parent = parent.parent
    return True  # It's top-level


async def _process_files_with_walk(
    working_dir: Path,
    exclude_patterns: list[str],
    dir_wide_file_trigger_patterns: list[str],
) -> AsyncGenerator[tuple[str, Node], None]:
    for root, dirs, files in walk(working_dir, topdown=True):
        root_path = Path(root)
        root_str = str(root_path)

        if _should_skip_all_files_in_dir(files, root_path, dir_wide_file_trigger_patterns):
            dirs[:] = []
            continue

        dirs[:] = [
            d_name
            for d_name in dirs
            if not any(
                fnmatch.fnmatch(str(root_path / d_name), ex_pat) for ex_pat in exclude_patterns
            )
        ]

        if any(fnmatch.fnmatch(root_str, ex_pat) for ex_pat in exclude_patterns):
            continue

        for file_name in files:
            file_path = root_path / file_name
            file_path_str = str(file_path)

            if _should_skip_file(file_path_str, exclude_patterns):
                continue

            async for result in process_file_for_functions(
                file_path=file_path,
                working_dir=working_dir,
            ):
                yield result


async def _process_included_files_directly(
    working_dir: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
    start_working_dir: Path,  # Assumed to be validated as not None by caller
) -> AsyncGenerator[tuple[str, Node], None]:
    for included_file_rel_path_str in include_patterns:
        file_to_check = (start_working_dir / included_file_rel_path_str).resolve()

        if not (
            file_to_check.exists() and file_to_check.is_file()
        ) or not file_to_check.is_relative_to(working_dir.resolve()):
            continue

        file_path_str = str(file_to_check)

        if _should_skip_file(file_path_str, exclude_patterns):
            continue

        parent_dir = file_to_check.parent
        try:
            [f.name for f in parent_dir.iterdir() if f.is_file()]

        except OSError:
            continue

        async for result in process_file_for_functions(
            file_path=file_to_check,
            working_dir=working_dir,
        ):
            yield result


def _should_skip_all_files_in_dir(
    files: list[str],
    root_path: Path,
    dir_wide_file_trigger_patterns: list[str],
) -> bool:
    if not dir_wide_file_trigger_patterns:
        return False
    for file_name in files:
        file_path_str_for_trigger_check = str(root_path / file_name)
        if any(
            fnmatch.fnmatch(file_path_str_for_trigger_check, trigger_pat)
            for trigger_pat in dir_wide_file_trigger_patterns
        ):
            return True
    return False


def _should_skip_file(file_path_str: str, exclude_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(file_path_str, ex_pat) for ex_pat in exclude_patterns)


async def iter_project_functions(
    working_dir: Path,
    exclude_patterns_param: list[str] | None,
    include_patterns_param: list[str] | None,
    start_working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    exclude_patterns = exclude_patterns_param if exclude_patterns_param is not None else []
    include_patterns = include_patterns_param if include_patterns_param is not None else []

    # Assuming TEST_FILES is defined in the global scope or imported
    dir_wide_file_trigger_patterns = [
        pat for pat in exclude_patterns if "." in pat and "*" in pat and pat not in TEST_FILES
    ]

    if include_patterns:
        if not start_working_dir:
            msg = "include_patterns were provided, but start_working_dir was not."
            raise ValueError(msg)
        # start_working_dir is confirmed to be Path here
        async for result in _process_included_files_directly(
            working_dir=working_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            start_working_dir=start_working_dir,
        ):
            yield result
    else:
        async for result in _process_files_with_walk(
            working_dir=working_dir,
            exclude_patterns=exclude_patterns,
            dir_wide_file_trigger_patterns=dir_wide_file_trigger_patterns,
        ):
            yield result


async def process_file_for_functions(
    file_path: Path,
    working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    language = get_language_from_path(str(file_path))
    if not language:
        return
    try:
        async with aiofiles.open(file=file_path, mode="rb") as f:
            content = await f.read()
            try:
                tree = parse_content_tree_sitter(content, language)
            except (OSError, InvalidFileType):
                return
    except FileNotFoundError:
        return

    function_node_names = TREE_SITTER_FUNCTION_DECLARATION_MAP[language]
    function_nodes = query_nodes_by_language(
        language,
        tree,
        TREE_SITTER_FUNCTION_DECLARATION_MAP,
    )
    if len(content.splitlines()) > 1000:  # noqa: PLR2004
        LOGGER.warning(
            "File is too long to be processed: %s, count: %s",
            file_path,
            len(content.splitlines()),
        )
        return
    # Prevent minified files
    if (
        len(function_nodes) > 1
        and len({node.start_point[0] for node in (y for x in function_nodes.values() for y in x)})
        == 1
    ):
        return
    for node in (y for x in function_nodes.values() for y in x):
        if _is_top_level_function(node, set(function_node_names)):
            # Yield relative path from working_dir
            if working_dir:
                yield (str(file_path.relative_to(working_dir)), node)
            else:
                yield (str(file_path), node)


def search_nodes_in_tree(root_node: Node, line: int, node_types: tuple[str, ...]) -> Node | None:
    # First check if the current node is of the desired type and contains the line
    if root_node.type in node_types and root_node.start_point[0] <= line <= root_node.end_point[0]:
        return root_node

    # If this node doesn't contain the line we're looking for, no need to search its children
    if line < root_node.start_point[0] or line > root_node.end_point[0]:
        return None

    # Search in the children of the current node
    for child in root_node.children:
        result = search_nodes_in_tree(child, line, node_types)
        if result:
            return result

    return None


def traverse_tree(tree: Node) -> Generator[Node, None, None]:
    cursor = tree.walk()
    cursor.goto_first_child()
    cursor.goto_parent()

    reached_root = False
    while reached_root is False:
        if not cursor.node:
            break
        yield cursor.node

        if cursor.goto_first_child():
            continue

        if cursor.goto_next_sibling():
            continue

        retracing = True
        while retracing:
            if not cursor.goto_parent():
                retracing = False
                reached_root = True

            if cursor.goto_next_sibling():
                retracing = False
