"""Tests for the API retry mechanisms."""

import logging
from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from tenacity import RetryCallState, wait_none

from semantic_scholar.api.exceptions import NetworkError, RateLimitError, ServerError
from semantic_scholar.api.retry import (
    DecoratorT,
    create_async_retry_decorator,
    exponential_wait,
    log_retry_async,
)


# Test fixtures and helper classes
class MockRetryState:
    """Mock for RetryCallState to use in testing."""

    def __init__(
        self, exception: Exception | None = None, attempt_number: int = 1, next_action_sleep: float | None = None
    ):
        self.attempt_number = attempt_number
        self._exception = exception
        self._next_action_sleep = next_action_sleep

    @property
    def outcome(self) -> Mock | None:
        if self._exception is None:
            return None

        mock_outcome = MagicMock()
        mock_outcome.exception.return_value = self._exception
        return mock_outcome

    @property
    def next_action(self) -> Mock | None:
        if self._next_action_sleep is None:
            return None

        mock_action = MagicMock()
        mock_action.sleep = self._next_action_sleep
        return mock_action


@pytest.fixture
def mock_sleep():
    """Fixture to patch asyncio.sleep for all tests."""
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def test_retry_decorator():
    """Fixture providing a non-waiting retry decorator for tests."""
    return create_async_retry_decorator(
        max_attempts=3,
        max_timeout=60.0,
        wait_strategy=wait_none(),
    )


class TestRetryMechanism:
    @pytest.mark.asyncio
    async def test_log_retry_async(self, caplog: pytest.LogCaptureFixture):
        """Test that retry attempts are logged correctly."""
        caplog.set_level(logging.INFO)

        # Case 1: No outcome, should not log
        state = MockRetryState(exception=None)
        await log_retry_async(cast(RetryCallState, state))
        assert len(caplog.records) == 0

        # Case 2: Has outcome with exception and next action
        state = MockRetryState(exception=NetworkError("Connection error"), attempt_number=2, next_action_sleep=1.5)
        await log_retry_async(cast(RetryCallState, state))

        # Check the log message
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "INFO"
        assert "Retrying after 1.50s due to NetworkError (attempt 2)" in record.message

    @pytest.mark.asyncio
    async def test_create_async_retry_decorator(self, test_retry_decorator: DecoratorT):
        """Test creating and using a custom retry decorator."""
        # Create a mock function that fails twice then succeeds
        mock_fn = AsyncMock()
        mock_fn.side_effect = [NetworkError("Connection error"), NetworkError("Another error"), "Success"]

        # Create a custom retry decorator with 3 max attempts and no wait strategy
        # Apply the decorator
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        result = await decorated_fn("arg1", kwarg1="value1")

        # Verify it was called 3 times and returned success
        assert mock_fn.call_count == 3
        assert result == "Success"

        # Verify the function was called with the right arguments each time
        for call in mock_fn.call_args_list:
            args, kwargs = call
            assert args == ("arg1",)
            assert kwargs == {"kwarg1": "value1"}

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, test_retry_decorator: DecoratorT):
        """Test retrying on NetworkError."""
        # Create a mock function that fails with NetworkError then succeeds
        mock_fn = AsyncMock()
        mock_fn.side_effect = [NetworkError("Connection error"), "Success"]

        # Apply the default retry decorator
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        result = await decorated_fn()

        # Verify it was called twice and returned success
        assert mock_fn.call_count == 2
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, test_retry_decorator: DecoratorT):
        """Test retrying on ServerError."""
        # Create a mock function that fails with ServerError then succeeds
        mock_fn = AsyncMock()
        mock_fn.side_effect = [ServerError("Server error", status_code=500), "Success"]

        # Apply the default retry decorator
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        result = await decorated_fn()

        # Verify it was called twice and returned success
        assert mock_fn.call_count == 2
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit_error(self, test_retry_decorator: DecoratorT):
        """Test retrying on RateLimitError."""
        # Create a mock function that fails with RateLimitError then succeeds
        mock_fn = AsyncMock()
        mock_fn.side_effect = [RateLimitError("Rate limit exceeded"), "Success"]

        # Apply the default retry decorator
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        result = await decorated_fn()

        # Verify it was called twice and returned success
        assert mock_fn.call_count == 2
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_no_retry_on_other_exceptions(self, test_retry_decorator: DecoratorT):
        """Test that other exceptions don't trigger retries."""
        # Create a mock function that fails with ValueError
        mock_fn = AsyncMock()
        mock_fn.side_effect = ValueError("Some other error")

        # Apply the default retry decorator
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        with pytest.raises(ValueError):
            await decorated_fn()

        # Verify it was called only once
        assert mock_fn.call_count == 1

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self, test_retry_decorator: DecoratorT):
        """Test that function fails after max attempts."""
        # Create a mock function that always fails with NetworkError
        mock_fn = AsyncMock()
        mock_fn.side_effect = NetworkError("Connection error")

        # Apply the default retry decorator (max 3 attempts)
        decorated_fn = test_retry_decorator(mock_fn)

        # Call the decorated function
        with pytest.raises(NetworkError):
            await decorated_fn()

        # Verify it was called 4 times (initial + 3 retries)
        assert mock_fn.call_count == 4

    @pytest.mark.asyncio
    async def test_integration_with_wait_strategy(self, test_retry_decorator: DecoratorT, mock_sleep: AsyncMock):
        """Test the decorator uses the correct wait strategy."""

        # Create a mock function that always fails
        mock_fn = AsyncMock()
        mock_fn.side_effect = [
            NetworkError("Error 1"),
            NetworkError("Error 2"),
            NetworkError("Error 3"),
            NetworkError("Error 4"),
        ]

        # Use small values to test exponential backoff without waiting too long
        custom_decorator = create_async_retry_decorator(
            max_attempts=3,
            max_timeout=60.0,
            wait_strategy=exponential_wait(
                initial=0.0001,
                max_value=0.001,
                exp_base=2,
                jitter=0.0,
            ),
        )

        # Apply the default retry decorator
        decorated_fn = custom_decorator(mock_fn)

        # Call the decorated function (will fail)
        with pytest.raises(NetworkError):
            await decorated_fn()

        # Verify asyncio.sleep was called for each retry with increasing values
        assert mock_sleep.call_count == 3  # 3 retries

        # Get the sleep durations
        sleep_durations = [call.args[0] for call in mock_sleep.call_args_list]

        # Verify they increase (exponential backoff)
        assert sleep_durations[0] < sleep_durations[1] < sleep_durations[2]
