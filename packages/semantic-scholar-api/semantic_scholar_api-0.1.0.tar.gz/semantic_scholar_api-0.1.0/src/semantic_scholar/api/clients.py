"""Asynchronous HTTP client implementation for the Semantic Scholar API."""

import asyncio
import logging
import time
from typing import Any, NoReturn

import httpx

from semantic_scholar.api.base import (
    APIResponse,
    BaseAsyncSemanticScholarClient,
)
from semantic_scholar.api.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
)
from semantic_scholar.api.retry import retry_async

# Create logger for this module
logger = logging.getLogger("semantic_scholar")


class AsyncSemanticScholarClient(BaseAsyncSemanticScholarClient):
    """Asynchronous implementation of the Semantic Scholar API client."""

    def __init__(self, timeout: float = 30.0, api_key: str | None = None):
        super().__init__(timeout, api_key)
        # For rate limiting - track last request time for authenticated requests
        self._last_request_time: float | None = None
        self._request_lock = asyncio.Lock()

    async def _throttle_if_needed(self) -> None:
        """
        Ensure authenticated requests are throttled to max 1 per second.
        Only applies when using an API key.
        """
        if not self.api_key or not self._last_request_time:
            return

        # Calculate time since last request
        now = time.time()
        elapsed = now - self._last_request_time

        # If less than 1 second has passed, sleep for the remaining time
        if elapsed < 1.0:
            wait_time = 1.0 - elapsed
            logger.debug(f"Rate limiting: waiting {wait_time:.3f}s before next request")
            await asyncio.sleep(wait_time)

    @retry_async
    async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:
        async with self._request_lock:
            await self._throttle_if_needed()

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params, headers=self.headers)
                    result = process_response(response)
                    self._last_request_time = time.time()
                    return result
            except Exception as e:
                handle_exception(e)

    @retry_async
    async def post(
        self, url: str, params: dict[str, Any] | None = None, json: dict[str, Any] | None = None
    ) -> APIResponse:
        async with self._request_lock:
            await self._throttle_if_needed()

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, params=params, json=json, headers=self.headers)
                    result = process_response(response)
                    self._last_request_time = time.time()
                    return result
            except Exception as e:
                handle_exception(e)


def process_response(response: httpx.Response) -> APIResponse:
    """Process an httpx response into the standard APIResponse format."""
    response.raise_for_status()

    # NOTE: `post` returns are list of objects, not a dict with a `data` key and
    # `model_validate` expects a dict.
    data: dict[str, Any] | list[Any] = response.json()
    if isinstance(data, list):
        data = {"data": data}

    return {
        "data": data,
        "info": {"headers": dict(response.headers), "status_code": response.status_code},
    }


EXCEPTION_MAP = {
    401: (AuthenticationError, "Authentication failed"),
    403: (AuthenticationError, "Permission denied"),
    404: (ResourceNotFoundError, "Resource not found"),
    429: (RateLimitError, "Rate limit exceeded"),
}


def handle_exception(exc: Exception, url: str | None = None, method: str | None = None) -> NoReturn:
    """Handle common httpx exceptions with context."""
    # Build context string for better error messages
    context = ""
    if method and url:
        context = f" during {method} request to {url}"

    if isinstance(exc, httpx.TimeoutException):
        raise NetworkError(f"Request timed out{context}", cause=exc) from exc
    elif isinstance(exc, httpx.NetworkError):
        raise NetworkError(f"Connection error{context}", cause=exc) from exc
    elif isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        response_data: dict[str, Any] | None = None
        try:
            response_data = exc.response.json()
        except (ValueError, TypeError):
            # Capture raw text instead of losing context
            response_data = {"error": exc.response.text}

        error_context = f"{context} (HTTP {status_code})"

        # Handle mapped exceptions
        if status_code in EXCEPTION_MAP:
            exception_class, message = EXCEPTION_MAP[status_code]
            raise exception_class(f"{message}{error_context}", cause=exc) from exc

        # Server errors
        if 500 <= status_code < 600:
            raise ServerError(
                f"Server error{error_context}", status_code=status_code, response=response_data, cause=exc
            ) from exc

        # Generic API error for any unmapped status codes
        error_message: str = "Unknown error"
        if response_data:
            error_message = response_data.get("message", str(response_data))

        raise APIError(
            f"API error{error_context}: {error_message}", status_code=status_code, response=response_data, cause=exc
        ) from exc
    else:
        raise exc
