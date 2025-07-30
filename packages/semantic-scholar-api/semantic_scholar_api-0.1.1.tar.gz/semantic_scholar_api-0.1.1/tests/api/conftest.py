"""Shared fixtures for API tests."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx.Response object with configurable parameters."""

    def _create_response(
        status_code: int = 200,
        json_data: Any = None,
        headers: Any = None,
        raise_error: bool = False,
    ) -> MagicMock:
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.headers = headers or {"Content-Type": "application/json"}

        if raise_error:
            response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "HTTP Error", request=MagicMock(), response=response
            )
        else:
            response.raise_for_status.return_value = None

        return response

    return _create_response


@pytest.fixture
def mock_async_client():
    """Create a mock httpx.AsyncClient that can be configured with predefined responses."""

    def _create_client(responses: Any = None) -> AsyncMock:
        client = AsyncMock(spec=httpx.AsyncClient)
        client.__aenter__.return_value = client

        if responses is not None:
            client.get.side_effect = responses
            client.post.side_effect = responses
        else:
            # Default response if none provided
            default_response = MagicMock(spec=httpx.Response)
            default_response.status_code = 200
            default_response.headers = {"Content-Type": "application/json"}
            default_response.json.return_value = {"data": "default"}
            default_response.raise_for_status.return_value = None

            client.get.return_value = default_response
            client.post.return_value = default_response

        return client

    return _create_client
