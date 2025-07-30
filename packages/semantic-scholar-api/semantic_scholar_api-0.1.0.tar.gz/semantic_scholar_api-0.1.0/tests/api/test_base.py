"""Tests for the base API client functionality."""

from typing import Any

import pytest

from semantic_scholar.api.base import (
    APIResponse,
    BaseAsyncSemanticScholarClient,
)


class TestBaseAsyncSemanticScholarClient:
    def test_init(self):
        """Test client initialization."""

        # Create a concrete subclass for testing
        class ConcreteClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:  # pyright: ignore[reportReturnType]
                pass

            async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:  # pyright: ignore[reportReturnType]
                pass

        # Test without API key
        client = ConcreteClient(timeout=60.0)
        assert client.timeout == 60.0
        assert client.api_key is None
        assert client.headers == {}

        # Test with API key
        client = ConcreteClient(timeout=30.0, api_key="test-api-key")
        assert client.timeout == 30.0
        assert client.api_key == "test-api-key"
        assert client.headers == {"x-api-key": "test-api-key"}

    def test_cant_instantiate_abstract_class(self):
        """Test that the abstract class cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseAsyncSemanticScholarClient()  # pyright: ignore[reportAbstractUsage]

    def test_abstract_methods_must_be_implemented(self):
        """Test that subclasses must implement abstract methods."""

        # Define a subclass that doesn't implement all abstract methods
        class IncompleteClient(BaseAsyncSemanticScholarClient):
            # Not implementing get() or post()
            pass

        # Attempting to instantiate the subclass should fail
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteClient()  # pyright: ignore[reportAbstractUsage]

        # Define a subclass that implements only get()
        class GetOnlyClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:  # pyright: ignore[reportReturnType]
                pass

            # Not implementing post()

        # It should still fail
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            GetOnlyClient()  # pyright: ignore[reportAbstractUsage]

        # Define a complete subclass
        class CompleteClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:  # pyright: ignore[reportReturnType]
                pass

            async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:  # pyright: ignore[reportReturnType]
                pass

        # This should succeed
        client = CompleteClient()  # pyright: ignore[reportAbstractUsage]
        assert isinstance(client, BaseAsyncSemanticScholarClient)
        assert hasattr(client, "get")
        assert hasattr(client, "post")

    def test_headers_with_api_key(self):
        """Test that headers are correctly set with API key."""

        # Create a concrete subclass for testing
        class ConcreteClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:
                # Implementation that doesn't call super()
                raise NotImplementedError("Test implementation")

            async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:
                # Implementation that doesn't call super()
                raise NotImplementedError("Test implementation")

        client = ConcreteClient(api_key="test-key")
        assert client.headers == {"x-api-key": "test-key"}

    def test_headers_without_api_key(self):
        """Test that headers are empty without API key."""

        # Create a concrete subclass for testing
        class ConcreteClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:
                # Implementation that doesn't call super()
                raise NotImplementedError("Test implementation")

            async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:
                # Implementation that doesn't call super()
                raise NotImplementedError("Test implementation")

        client = ConcreteClient()
        assert client.headers == {}

    @pytest.mark.asyncio
    async def test_abstract_methods_raise_not_implemented(self):
        """Test that abstract methods raise NotImplementedError when called."""

        # Create a concrete subclass that calls super() methods
        class MinimalClient(BaseAsyncSemanticScholarClient):
            async def get(self, url: str, params: dict[str, Any] | None = None) -> APIResponse:
                return await super().get(url, params)  # pyright: ignore[reportAbstractUsage]

            async def post(self, url: str, json: dict[str, Any] | None = None) -> APIResponse:
                return await super().post(url, json)  # pyright: ignore[reportAbstractUsage]

        client = MinimalClient()

        # Test get method
        with pytest.raises(NotImplementedError) as excinfo:
            await client.get("https://example.com")
        assert "Subclasses must implement this method" in str(excinfo.value)

        # Test post method
        with pytest.raises(NotImplementedError) as excinfo:
            await client.post("https://example.com")
        assert "Subclasses must implement this method" in str(excinfo.value)
