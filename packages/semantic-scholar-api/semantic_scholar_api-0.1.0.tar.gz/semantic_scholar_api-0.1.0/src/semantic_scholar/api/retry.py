"""Retry strategies for HTTP clients using tenacity."""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential_jitter,
)
from tenacity.wait import WaitBaseT

from semantic_scholar.api.exceptions import NetworkError, RateLimitError, ServerError

# Logger for retry events
logger = logging.getLogger("semantic_scholar.retry")


async def log_retry_async(retry_state: RetryCallState) -> None:
    """
    Log retry attempts for async functions.

    Args:
        retry_state: The current retry state
    """
    if retry_state.outcome is None:
        return

    exception = retry_state.outcome.exception()
    if exception and retry_state.next_action is not None:
        wait_time = retry_state.next_action.sleep
        attempt = retry_state.attempt_number
        logger.info(f"Retrying after {wait_time:.2f}s due to {exception.__class__.__name__} (attempt {attempt})")


DecoratorT = Callable[[Callable[..., Any]], Callable[..., Any]]


def create_async_retry_decorator(
    max_attempts: int = 3,
    max_timeout: float = 60.0,
    wait_strategy: WaitBaseT | None = None,
) -> DecoratorT:
    """
    Create an async retry decorator with the specified configuration.

    Args:
        max_attempts: Maximum number of retry attempts (excludes initial attempt)
        max_timeout: Maximum total retry duration in seconds

    Returns:
        A configured retry decorator for async functions
    """
    if wait_strategy is None:
        wait_strategy = exponential_wait()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            retry_config = AsyncRetrying(
                retry=retry_if_exception_type((NetworkError, ServerError, RateLimitError)),
                stop=(stop_after_attempt(max_attempts + 1) | stop_after_delay(max_timeout)),
                wait=wait_strategy,
                after=log_retry_async,
                reraise=True,
            )

            async for attempt in retry_config:
                with attempt:
                    return await func(*args, **kwargs)

        return wrapper

    return decorator


def exponential_wait(
    initial: float = 0.5, max_value: float = 60.0, exp_base: float = 2, jitter: float = 0.1
) -> WaitBaseT:
    """
    Create a wait strategy that exponentially increases with a maximum value.

    Args:
        initial: The initial wait time
        max_value: The maximum wait time
        exp_base: The base of the exponential function
        jitter: The jitter factor
    """

    return wait_exponential_jitter(initial, max_value, exp_base, jitter)


# Default decorator for async API requests
retry_async = create_async_retry_decorator(max_attempts=3, max_timeout=60.0)
"""Default retry decorator for async API requests with 3 attempts and 60s timeout."""
