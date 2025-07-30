import asyncio
import logging
import os
import sys
from pathlib import Path

import click
import click.testing
import litellm
from litellm.caching.caching import Cache
from litellm.types.caching import LiteLLMCacheType

from sifts.analysis.orchestrator import scan_projects
from sifts.config import AnalysisConfig, ExecutionContext, SiftsConfig
from sifts.llm.usage import generate_price_counter

LOGGER = logging.getLogger(__name__)


litellm.cache = Cache(type=LiteLLMCacheType.DISK)

# Configure logging globally
# Remove existing handlers to avoid duplication
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure a common formatter for all loggers
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")

# Handler for stdout (INFO and WARNING)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
stdout_handler.addFilter(lambda record: record.levelno < logging.INFO)

# Handler for stderr (only ERROR and CRITICAL)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.INFO)
stderr_handler.setFormatter(formatter)

# Configure the root logger to use both handlers
logging.root.setLevel(logging.INFO)
logging.root.addHandler(stdout_handler)
logging.root.addHandler(stderr_handler)

# Get the logger for this module
LOGGER = logging.getLogger(__name__)

os.environ["AWS_REGION_NAME"] = os.environ.get("AWS_REGION_NAME", "us-east-1")
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("LiteLLM Router").setLevel(logging.WARNING)
logging.disable(logging.WARNING)


@click.group()
def main_cli() -> None:
    pass


@main_cli.command()
@click.argument("analysis-dir")
@click.option("--group-name", required=True)
@click.option("--root-id", required=True)
def scan(analysis_dir: str, group_name: str, root_id: str) -> None:
    """Scan code in the specified directory."""
    try:
        litellm.success_callback = [generate_price_counter(group_name, root_id)]
        asyncio.run(
            scan_projects(
                SiftsConfig(
                    analysis=AnalysisConfig(
                        working_dir=Path(analysis_dir).resolve(),
                    ),
                    context=ExecutionContext(
                        group_name=group_name,
                        root_id=root_id,
                    ),
                ),
            ),
        )
    except Exception:
        LOGGER.exception("Error during scan")
        sys.exit(1)


@main_cli.command()
@click.argument(
    "config-file",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
)
def run_with_config(config_file: str) -> None:
    """Run analysis using a YAML configuration file."""
    try:
        config = SiftsConfig.from_yaml(config_file)
        LOGGER.info("Running with configuration from %s", config_file)

        # Configure runtime settings
        if config.runtime.parallel:
            LOGGER.info("Running with %d threads in parallel mode", config.runtime.threads)
            # You would implement parallel processing logic here

        # Create output directory if it doesn't exist
        if config.output.path:
            output_path = Path(config.output.path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

        asyncio.run(scan_projects(config))

    except Exception:
        LOGGER.exception("Error running with config file %s", config_file)
        sys.exit(1)
