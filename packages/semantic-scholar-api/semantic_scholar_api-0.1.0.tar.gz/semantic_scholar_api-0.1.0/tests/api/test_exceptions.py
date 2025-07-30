"""Tests for the exceptions module."""

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


class TestExceptionHierarchy:
    """Test the exception hierarchy."""

    def test_base_exception(self):
        """Test that SemanticScholarError is a subclass of Exception."""
        assert issubclass(SemanticScholarError, Exception)

    def test_subclass_hierarchy(self):
        """Test that all exceptions inherit from SemanticScholarError."""
        assert issubclass(InvalidRequestError, SemanticScholarError)
        assert issubclass(AuthenticationError, SemanticScholarError)
        assert issubclass(RateLimitError, SemanticScholarError)
        assert issubclass(APIError, SemanticScholarError)
        assert issubclass(NetworkError, SemanticScholarError)

    def test_api_error_subclasses(self):
        """Test that API error subclasses inherit from APIError."""
        assert issubclass(ServerError, APIError)
        assert issubclass(ResourceNotFoundError, APIError)


class TestExceptionInstantiation:
    """Test exception instantiation and properties."""

    def test_semantic_scholar_error(self):
        """Test SemanticScholarError instantiation."""
        error = SemanticScholarError("An error occurred")
        assert str(error) == "An error occurred"
        assert error.message == "An error occurred"
        assert error.cause is None

        cause = ValueError("Original error")
        error_with_cause = SemanticScholarError("An error occurred", cause=cause)
        assert error_with_cause.cause == cause

    def test_invalid_request_error(self):
        """Test InvalidRequestError instantiation."""
        error = InvalidRequestError("Invalid parameter")
        assert str(error) == "Invalid parameter"
        assert error.param is None

        error_with_param = InvalidRequestError("Invalid parameter", param="query")
        assert str(error_with_param) == "Invalid parameter (parameter: query)"
        assert error_with_param.param == "query"

    def test_authentication_error(self):
        """Test AuthenticationError instantiation."""
        error = AuthenticationError("Authentication failed")
        assert str(error) == "Authentication failed"

    def test_rate_limit_error(self):
        """Test RateLimitError instantiation."""
        error = RateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert error.reset_time is None
        assert error.limit is None
        assert error.remaining is None

        error_with_details = RateLimitError("Rate limit exceeded", reset_time=1600000000, limit=100, remaining=0)
        assert "limit: 100" in str(error_with_details)
        assert "remaining: 0" in str(error_with_details)
        assert "reset: 1600000000" in str(error_with_details)
        assert error_with_details.reset_time == 1600000000
        assert error_with_details.limit == 100
        assert error_with_details.remaining == 0

    def test_api_error(self):
        """Test APIError instantiation."""
        error = APIError("API error")
        assert str(error) == "API error"
        assert error.status_code is None
        assert error.response is None

        error_with_status = APIError("API error", status_code=500)
        assert str(error_with_status) == "API error (status: 500)"
        assert error_with_status.status_code == 500

        response = {"error": "Internal server error"}
        error_with_response = APIError("API error", status_code=500, response=response)
        assert error_with_response.response == response

    def test_server_error(self):
        """Test ServerError instantiation."""
        error = ServerError("Server error", status_code=500)
        assert str(error) == "Server error (status: 500)"
        assert error.status_code == 500

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError instantiation."""
        error = ResourceNotFoundError("Resource not found")
        assert str(error) == "Resource not found (status: 404)"
        assert error.status_code == 404
        assert error.resource_id is None

        error_with_id = ResourceNotFoundError("Paper not found", resource_id="paper123")
        assert str(error_with_id) == "Paper not found (id: paper123) (status: 404)"
        assert error_with_id.resource_id == "paper123"

    def test_network_error(self):
        """Test NetworkError instantiation."""
        error = NetworkError("Connection error")
        assert str(error) == "Connection error"

        cause = ConnectionError("Failed to connect")
        error_with_cause = NetworkError("Connection error", cause=cause)
        assert error_with_cause.cause == cause


class TestExceptionChaining:
    """Test exception chaining."""

    def test_chaining_exceptions(self):
        """Test chaining exceptions."""
        original = ValueError("Original error")
        network = NetworkError("Network error", cause=original)
        api = APIError("API error", cause=network)

        assert api.cause == network
        assert network.cause == original
