import asyncio
import contextlib
import functools
import time
from collections.abc import AsyncGenerator, Callable
from typing import ParamSpec, TypeVar

from litellm import RouterRateLimitError

from sifts.common_types.snippets import ItemAnalysisResult

TVar = TypeVar("TVar")

P = ParamSpec("P")


def retry_on_exceptions(
    *,
    exceptions: tuple[type[Exception], ...],
    max_attempts: int = 5,
    sleep_seconds: float = 0,
) -> Callable[[Callable[P, TVar]], Callable[P, TVar]]:
    def decorator(
        func: Callable[P, TVar],
    ) -> Callable[P, TVar]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> TVar:
                for _ in range(max_attempts - 1):
                    try:
                        return await func(*args, **kwargs)  # type: ignore  # noqa: PGH003
                    except exceptions as exc:
                        if isinstance(exc, RouterRateLimitError):
                            sleep_seconds = exc.cooldown_time
                        await asyncio.sleep(sleep_seconds)
                return await func(*args, **kwargs)  # type: ignore  # noqa: PGH003

            return wrapper  # type: ignore  # noqa: PGH003

        @functools.wraps(func)
        def wrapper1(*args: P.args, **kwargs: P.kwargs) -> TVar:
            for _ in range(max_attempts - 1):
                with contextlib.suppress(*exceptions):
                    return func(*args, **kwargs)
                time.sleep(sleep_seconds)
            return func(*args, **kwargs)

        return wrapper1

    return decorator


async def merge_async_generators_concurrent(
    generators: list[AsyncGenerator[ItemAnalysisResult, None]],
) -> AsyncGenerator[ItemAnalysisResult, None]:
    """Merge multiple async generators and process them concurrently."""
    if not generators:
        return

    # Track completion with a simple counter
    pending = len(generators)
    queue: asyncio.Queue[ItemAnalysisResult | Exception] = asyncio.Queue()

    async def process_generator(generator: AsyncGenerator[ItemAnalysisResult, None]) -> None:
        nonlocal pending
        try:
            async for item in generator:
                await queue.put(item)
        except Exception as e:  # noqa: BLE001
            await queue.put(e)  # Just pass the exception directly
        finally:
            pending -= 1

    # Start all generator tasks
    for generator in generators:
        asyncio.create_task(process_generator(generator))  # noqa: RUF006

    # Process results until all generators are done and queue is empty
    while pending > 0 or not queue.empty():
        try:
            # Use a shorter timeout and simpler waiting logic
            item = await asyncio.wait_for(queue.get(), 0.05)
            if isinstance(item, Exception):
                raise item  # Re-raise any exceptions from generators
            yield item
        except TimeoutError:
            # Just continue the loop - no need for additional checks here
            pass
