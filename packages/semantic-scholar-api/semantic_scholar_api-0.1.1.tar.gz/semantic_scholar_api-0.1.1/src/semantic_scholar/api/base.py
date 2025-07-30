"""Base class for the async Semantic Scholar API client implementation."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict


class ResponseInfo(TypedDict):
    """Information about the API response."""

    headers: dict[str, str]
    status_code: int


class APIResponse(TypedDict):
    """API response data and metadata."""

    data: dict[str, Any]
    info: ResponseInfo


class BaseAsyncSemanticScholarClient(ABC):
    """
    Abstract base class defining the interface for the async API client.
    """

    def __init__(self, timeout: float = 30.0, api_key: str | None = None):
        """
        Initialize the API client.

        Args:
            timeout: Default request timeout in seconds
            api_key: The API key to use for the client
        """
        self.timeout = timeout
        self.api_key = api_key
        self.headers = {"x-api-key": api_key} if api_key else {}

    @abstractmethod
    async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:
        """
        Make a GET request to the specified URL.

        Args:
            url: The URL to request
            params: Optional query parameters to include in the request

        Returns:
            APIResponse containing the parsed JSON response data and response info

        Raises:
            NetworkError: When a network-related error occurs
            APIError: When the API returns an error response
            RateLimitError: When rate limit is exceeded
        """
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:
        """
        Make a POST request to the specified URL.

        Args:
            url: The URL to request
            json: Optional JSON data to include in the request

        Returns:
            APIResponse containing the parsed JSON response data and response info

        Raises:
            NetworkError: When a network-related error occurs
            APIError: When the API returns an error response
            RateLimitError: When rate limit is exceeded
        """
        raise NotImplementedError("Subclasses must implement this method")
