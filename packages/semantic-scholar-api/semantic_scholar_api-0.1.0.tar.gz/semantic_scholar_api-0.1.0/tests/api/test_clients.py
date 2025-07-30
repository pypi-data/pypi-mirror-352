"""Tests for the async Semantic Scholar API client."""

import asyncio
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from semantic_scholar.api.clients import AsyncSemanticScholarClient, handle_exception, process_response
from semantic_scholar.api.exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
)


@pytest.fixture
def mock_response() -> httpx.Response:
    """Create a mock successful HTTP response."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = 200
    mock.headers = {"Content-Type": "application/json"}
    mock.json.return_value = {"data": "test_data"}
    mock.raise_for_status = Mock()
    return mock


@pytest.fixture
def mock_client() -> AsyncSemanticScholarClient:
    """Create a client with mocked httpx client."""
    return AsyncSemanticScholarClient(timeout=1.0, api_key="test-key")


class TestAsyncSemanticScholarClient:
    @pytest.mark.asyncio
    async def test_get_success(self, mock_client: AsyncSemanticScholarClient, mock_response: httpx.Response):
        """Test successful GET request."""
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_async_client.return_value = mock_instance

            result = await mock_client.get("https://api.example.com", {"param": "value"})

            mock_instance.get.assert_called_once_with(
                "https://api.example.com", params={"param": "value"}, headers={"x-api-key": "test-key"}
            )
            assert result["data"] == {"data": "test_data"}
            assert result["info"]["status_code"] == 200
            assert result["info"]["headers"] == {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_post_success(self, mock_client: AsyncSemanticScholarClient, mock_response: httpx.Response):
        """Test successful POST request."""
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.post.return_value = mock_response
            mock_async_client.return_value = mock_instance

            post_data = {"key": "value"}
            result = await mock_client.post("https://api.example.com", json=post_data)

            mock_instance.post.assert_called_once_with(
                "https://api.example.com", params=None, json=post_data, headers={"x-api-key": "test-key"}
            )
            assert result["data"] == {"data": "test_data"}
            assert result["info"]["status_code"] == 200
            assert result["info"]["headers"] == {"Content-Type": "application/json"}

    @pytest.mark.asyncio
    async def test_get_without_api_key(self, mock_response: httpx.Response):
        """Test GET request without API key."""
        client = AsyncSemanticScholarClient(timeout=1.0)

        with patch("httpx.AsyncClient") as mock_async_client:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_async_client.return_value = mock_instance

            await client.get("https://api.example.com")

            mock_instance.get.assert_called_once_with("https://api.example.com", params=None, headers={})

    @pytest.mark.asyncio
    async def test_throttle_with_api_key(self, mock_client: AsyncSemanticScholarClient, mock_response: httpx.Response):
        """Test that requests are throttled when using API key."""
        with patch("httpx.AsyncClient") as mock_async_client, patch("asyncio.sleep") as mock_sleep:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_async_client.return_value = mock_instance

            # First request sets _last_request_time but doesn't sleep
            await mock_client.get("https://api.example.com")
            mock_sleep.assert_not_called()

            # Set _last_request_time to 0.3 seconds ago
            mock_client._last_request_time = time.time() - 0.3  # type: ignore[reportPrivateUsage]

            # Second request should sleep for remaining time (~0.7s)
            await mock_client.get("https://api.example.com")

            # Verify sleep was called with a value close to 0.7
            mock_sleep.assert_called_once()
            sleep_time = mock_sleep.call_args[0][0]
            assert 0.65 <= sleep_time <= 0.75

    @pytest.mark.asyncio
    async def test_no_throttle_without_api_key(self, mock_response: httpx.Response):
        """Test that requests are not throttled when not using API key."""
        client = AsyncSemanticScholarClient(timeout=1.0)

        with patch("httpx.AsyncClient") as mock_async_client, patch("asyncio.sleep") as mock_sleep:
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_async_client.return_value = mock_instance

            # Multiple requests should not trigger sleep
            await client.get("https://api.example.com")
            await client.get("https://api.example.com")

            mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_lock(self, mock_client: AsyncSemanticScholarClient, mock_response: httpx.Response):
        """Test that the request lock prevents concurrent requests."""
        with patch("httpx.AsyncClient") as mock_async_client, patch("asyncio.sleep"):
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance
            mock_instance.get.return_value = mock_response
            mock_async_client.return_value = mock_instance

            # Create two tasks that will try to make requests concurrently
            task1 = asyncio.create_task(mock_client.get("https://api.example.com/1"))
            task2 = asyncio.create_task(mock_client.get("https://api.example.com/2"))

            # Wait for both tasks to complete
            await asyncio.gather(task1, task2)

            # Check that get was called twice with different URLs
            assert mock_instance.get.call_count == 2
            call_args_list = mock_instance.get.call_args_list
            assert call_args_list[0][0][0] != call_args_list[1][0][0]

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_client: AsyncSemanticScholarClient):
        """Test that errors are properly handled and propagated."""
        with (
            patch("httpx.AsyncClient") as mock_async_client,
            patch("semantic_scholar.api.clients.handle_exception") as mock_handle_exception,
        ):
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance

            # Simulate a network error
            network_error = httpx.NetworkError("Connection failed")
            mock_instance.get.side_effect = network_error
            mock_async_client.return_value = mock_instance

            # Mock handle_exception to raise the exception
            def side_effect(e: Exception, **kwargs: Any) -> None:
                raise e

            mock_handle_exception.side_effect = side_effect

            with pytest.raises(httpx.NetworkError):
                await mock_client.get("https://api.example.com")

            # Verify handle_exception was called
            mock_handle_exception.assert_called_once()

            # Verify handle_exception was called with the NetworkError exception
            args, _ = mock_handle_exception.call_args
            assert isinstance(args[0], httpx.NetworkError)
            assert str(args[0]) == "Connection failed"

    @pytest.mark.asyncio
    async def test_post_error_handling(self, mock_client: AsyncSemanticScholarClient):
        """Test that errors in post requests are properly handled and propagated."""
        with (
            patch("httpx.AsyncClient") as mock_async_client,
            patch("semantic_scholar.api.clients.handle_exception") as mock_handle_exception,
        ):
            mock_instance = AsyncMock()
            mock_instance.__aenter__.return_value = mock_instance

            # Simulate a timeout error
            timeout_error = httpx.TimeoutException("Request timed out")
            mock_instance.post.side_effect = timeout_error
            mock_async_client.return_value = mock_instance

            # Mock handle_exception to raise the exception
            def side_effect(e: Exception, **kwargs: Any) -> None:
                raise e

            mock_handle_exception.side_effect = side_effect

            with pytest.raises(httpx.TimeoutException):
                await mock_client.post("https://api.example.com", json={"key": "value"})

            # Verify handle_exception was called
            mock_handle_exception.assert_called_once()

            # Verify handle_exception was called with the TimeoutException
            args, _ = mock_handle_exception.call_args
            assert isinstance(args[0], httpx.TimeoutException)
            assert str(args[0]) == "Request timed out"


class TestProcessResponse:
    def test_process_response_successful(self):
        """Test processing a successful response."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"key": "value"}

        result = process_response(mock_response)

        assert isinstance(result, dict)
        assert "data" in result
        assert "info" in result
        assert result["data"] == {"key": "value"}
        assert result["info"]["status_code"] == 200
        assert result["info"]["headers"] == {"Content-Type": "application/json"}

    def test_process_response_list(self):
        """Test processing a successful response with a list of data."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"key": "value1"}, {"key": "value2"}]

        result = process_response(mock_response)

        assert isinstance(result, dict)
        assert "data" in result
        assert "info" in result
        assert result["data"] == {"data": [{"key": "value1"}, {"key": "value2"}]}
        assert result["info"]["status_code"] == 200
        assert result["info"]["headers"] == {"Content-Type": "application/json"}


class TestHandleException:
    def test_timeout_exception(self):
        """Test handling a timeout exception."""
        exc = httpx.TimeoutException("Request timed out")

        with pytest.raises(NetworkError) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "Request timed out during GET request to https://api.example.com" in str(excinfo.value)
        assert excinfo.value.__cause__ == exc

    def test_network_error(self):
        """Test handling a network error."""
        exc = httpx.NetworkError("Connection failed")

        with pytest.raises(NetworkError) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "Connection error during GET request to https://api.example.com" in str(excinfo.value)
        assert excinfo.value.__cause__ == exc

    @pytest.mark.parametrize(
        "status_code,expected_exception",
        [
            (401, AuthenticationError),
            (403, AuthenticationError),
            (404, ResourceNotFoundError),
            (429, RateLimitError),
        ],
    )
    def test_mapped_http_errors(self, status_code: int, expected_exception: type[Exception]):
        """Test handling mapped HTTP status codes."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"message": "Error message"}

        exc = httpx.HTTPStatusError(
            "HTTP Error",
            request=MagicMock(),
            response=mock_response,
        )

        with pytest.raises(expected_exception) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "during GET request to https://api.example.com" in str(excinfo.value)
        assert excinfo.value.__cause__ == exc

    def test_server_error(self):
        """Test handling server errors (500+)."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}

        exc = httpx.HTTPStatusError(
            "HTTP Error",
            request=MagicMock(),
            response=mock_response,
        )

        with pytest.raises(ServerError) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "Server error during GET request to https://api.example.com" in str(excinfo.value)
        assert excinfo.value.status_code == 500
        assert excinfo.value.response == {"message": "Internal server error"}
        assert excinfo.value.__cause__ == exc

    def test_unmapped_http_error(self):
        """Test handling unmapped HTTP status codes."""
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_response.json.return_value = {"message": "I'm a teapot"}

        exc = httpx.HTTPStatusError(
            "HTTP Error",
            request=MagicMock(),
            response=mock_response,
        )

        with pytest.raises(APIError) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "API error during GET request to https://api.example.com (HTTP 418)" in str(excinfo.value)
        assert excinfo.value.status_code == 418
        assert excinfo.value.response == {"message": "I'm a teapot"}
        assert excinfo.value.__cause__ == exc

    def test_http_error_with_invalid_json(self):
        """Test handling HTTP errors when response doesn't contain valid JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Bad Request"

        exc = httpx.HTTPStatusError(
            "HTTP Error",
            request=MagicMock(),
            response=mock_response,
        )

        with pytest.raises(APIError) as excinfo:
            handle_exception(exc, url="https://api.example.com", method="GET")

        assert "API error during GET request to https://api.example.com (HTTP 400)" in str(excinfo.value)
        assert excinfo.value.status_code == 400
        assert excinfo.value.response == {"error": "Bad Request"}
        assert excinfo.value.__cause__ == exc

    def test_other_exception(self):
        """Test that other exceptions are re-raised."""
        exc = ValueError("Some other error")

        with pytest.raises(ValueError) as excinfo:
            handle_exception(exc)

        assert excinfo.value == exc
