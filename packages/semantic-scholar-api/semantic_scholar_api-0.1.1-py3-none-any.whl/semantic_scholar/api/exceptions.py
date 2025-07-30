"""Exceptions for the Semantic Scholar API client."""

from typing import Any


class SemanticScholarError(Exception):
    """Base exception class for all Semantic Scholar API client errors."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            cause: The original exception that caused this error
        """
        self.message = message
        self.cause = cause
        super().__init__(message)


class InvalidRequestError(SemanticScholarError):
    """Raised when the request contains invalid parameters."""

    def __init__(self, message: str, param: str | None = None, cause: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            param: The parameter that caused the error
            cause: The original exception that caused this error
        """
        self.param = param
        param_info = f" (parameter: {param})" if param else ""
        super().__init__(f"{message}{param_info}", cause)


class AuthenticationError(SemanticScholarError):
    """Raised when authentication fails."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            cause: The original exception that caused this error
        """
        super().__init__(message, cause)


class RateLimitError(SemanticScholarError):
    """Raised when the rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        reset_time: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            reset_time: The time when the rate limit will reset (Unix timestamp)
            limit: The rate limit ceiling for the given endpoint
            remaining: The number of requests left for the time window
            cause: The original exception that caused this error
        """
        self.reset_time = reset_time
        self.limit = limit
        self.remaining = remaining

        details: list[str] = []
        if limit is not None:
            details.append(f"limit: {limit}")
        if remaining is not None:
            details.append(f"remaining: {remaining}")
        if reset_time is not None:
            details.append(f"reset: {reset_time}")

        detail_str = f" ({', '.join(details)})" if details else ""
        super().__init__(f"{message}{detail_str}", cause)


class APIError(SemanticScholarError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            status_code: The HTTP status code
            response: The response body
            cause: The original exception that caused this error
        """
        self.status_code = status_code
        self.response = response

        status_info = f" (status: {status_code})" if status_code is not None else ""
        super().__init__(f"{message}{status_info}", cause)


class ServerError(APIError):
    """Raised when the API returns a 5xx status code."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            status_code: The HTTP status code
            response: The response body
            cause: The original exception that caused this error
        """
        super().__init__(message, status_code, response, cause)


class ResourceNotFoundError(APIError):
    """Raised when the requested resource is not found (404)."""

    def __init__(
        self,
        message: str,
        resource_id: str | None = None,
        status_code: int = 404,
        response: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            resource_id: The ID of the resource that was not found
            status_code: The HTTP status code (defaults to 404)
            response: The response body
            cause: The original exception that caused this error
        """
        self.resource_id = resource_id

        id_info = f" (id: {resource_id})" if resource_id is not None else ""
        super().__init__(f"{message}{id_info}", status_code, response, cause)


class NetworkError(SemanticScholarError):
    """Raised when a network error occurs."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: A description of the error
            cause: The original exception that caused this error
        """
        super().__init__(message, cause)
