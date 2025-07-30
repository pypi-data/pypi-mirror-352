"""API clients for the Semantic Scholar API."""

from semantic_scholar.api.base import (
    APIResponse,
    BaseAsyncSemanticScholarClient,
    ResponseInfo,
)
from semantic_scholar.api.clients import AsyncSemanticScholarClient
from semantic_scholar.api.exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
)

__all__ = [
    "APIError",
    "APIResponse",
    "AsyncSemanticScholarClient",
    "AuthenticationError",
    "BaseAsyncSemanticScholarClient",
    "InvalidRequestError",
    "NetworkError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ResponseInfo",
    "ServerError",
]
