"""Semantic Scholar API client."""

from semantic_scholar.api.exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    SemanticScholarError,
    ServerError,
)
from semantic_scholar.semantic_scholar import SemanticScholar

__all__ = [
    "APIError",
    "AuthenticationError",
    "InvalidRequestError",
    "NetworkError",
    "RateLimitError",
    "ResourceNotFoundError",
    "SemanticScholarError",
    "ServerError",
    "SemanticScholar",
]
