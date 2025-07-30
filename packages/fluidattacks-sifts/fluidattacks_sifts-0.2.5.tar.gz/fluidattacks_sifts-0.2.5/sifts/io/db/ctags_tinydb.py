import asyncio
import logging
import os
import tempfile
from collections.abc import Generator
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path
from typing import Any

import orjson
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from sifts.core.types import Language
from sifts.io.file_system import should_exclude

LOGGER = logging.getLogger(__name__)


def chunked_reader(path: str, chunk_size: int) -> Generator[list[bytes], None, None]:
    with open(path, "rb", buffering=16 * 1024 * 1024) as f:  # noqa: PTH123
        it = iter(f)
        yield from iter(lambda: list(islice(it, chunk_size)), [])


async def create_tiny_db_from_ctags(  # noqa: PLR0913
    working_dir: Path,
    exclude: list[str] | None,
    language: Language,
    *,
    max_workers: int | None = None,
    chunk_size: int = 5000,
    max_in_flight: int = 4,
) -> TinyDB:
    executor = ProcessPoolExecutor(max_workers=max_workers)
    loop = asyncio.get_running_loop()
    tags_output: str | None = None

    try:
        # Generar archivo temporal para ctags
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json",
            dir=working_dir,
        ) as tags_output_file:
            tags_output = tags_output_file.name

        language_value = language.value
        if language == Language.JavaScript:
            language_value = "JavaScript,+TypeScript"
        if language == Language.CSharp:
            language_value = "C#"

        args = [
            "--fields=+n+N+S",
            "--output-format=json",
            "--excmd=number",
            "-R",
            "--tag-relative=always",
            f"--languages=-all,+{language_value}",
            "-f",
            tags_output,
            *[f"--exclude={excl}" for excl in exclude or []],
            str(working_dir),
        ]

        process = await asyncio.create_subprocess_exec("ctags", *args)
        _, stderr = await process.communicate()
        await process.wait()

        if process.returncode != 0:
            LOGGER.error("ctags failed: %s", stderr.decode(errors="ignore"))
            return TinyDB(storage=MemoryStorage)
        if stderr:
            LOGGER.warning("ctags stderr: %s", stderr.decode(errors="ignore"))

        tiny_db = TinyDB(storage=MemoryStorage)
        semaphore = asyncio.Semaphore(max_in_flight)

        async def schedule_chunk(chunk: list[bytes]) -> None:
            async with semaphore:
                parsed = await loop.run_in_executor(executor, parse_chunk, chunk)
                if parsed:
                    tiny_db.insert_multiple(parsed)
                    LOGGER.info("Inserted %d tags", len(parsed))

        tasks = [
            asyncio.create_task(schedule_chunk(chunk))
            for chunk in chunked_reader(tags_output, chunk_size)
        ]

        await asyncio.gather(*tasks)
        return tiny_db

    finally:
        if tags_output and Path(tags_output).exists():
            Path(tags_output).unlink()
        executor.shutdown(wait=False)


def find_files(
    working_dir: str | Path,
    exclusions: list[Path] | None = None,
) -> list[Path]:
    working_dir = Path(working_dir)
    results = []
    exclusions = exclusions or []

    for root, dirs, files in os.walk(working_dir):
        root_path = Path(root)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, exclusions)]

        # Find files with matching extensions
        for file in files:
            file_path = root_path / file

            if not should_exclude(file_path, exclusions):
                results.append(file_path.absolute())

    return results


def parse_chunk(lines: list[bytes]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            parsed = orjson.loads(line)
            # if not is_dependency_file(Path(parsed["path"])):
            out.append(parsed)
        except orjson.JSONDecodeError:
            LOGGER.debug("Skipping invalid JSON line: %r", line[:50])
    return out
