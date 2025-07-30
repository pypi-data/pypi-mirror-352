"""Tests for the base models."""

from semantic_scholar.models.base import BaseModel, BaseResponse


class TestBaseModel:
    """Tests for the BaseModel class."""

    def test_base_model_initialization(self):
        """Test that BaseModel can be initialized with valid data."""
        model = BaseModel()
        assert isinstance(model, BaseModel)

    def test_base_model_with_unknown_fields(self):
        """Test that BaseModel ignores unknown fields."""
        model = BaseModel(unknown_field="value")  # type: ignore
        assert isinstance(model, BaseModel)
        assert not hasattr(model, "unknown_field")


class TestBaseResponse:
    """Tests for the BaseResponse class."""

    def test_base_response_initialization(self):
        """Test that BaseResponse can be initialized with valid data."""
        response = BaseResponse[str]()
        assert isinstance(response, BaseResponse)
        assert response.data == []
        assert response.offset is None
        assert response.next is None
        assert response.total is None
        assert response.token is None

    def test_base_response_with_data(self):
        """Test that BaseResponse can be initialized with data."""
        response = BaseResponse[str](data=["item1", "item2"])
        assert isinstance(response, BaseResponse)
        assert response.data == ["item1", "item2"]

    def test_base_response_with_pagination(self):
        """Test that BaseResponse can be initialized with pagination data."""
        sample_response = {
            "offset": 0,
            "next": 100,
            "total": 500,
            "data": ["item1", "item2"],
            "token": "next_page_token",
        }

        response: BaseResponse[str] = BaseResponse.model_validate(sample_response)

        assert isinstance(response, BaseResponse)
        assert response.offset == 0
        assert response.next == 100
        assert response.total == 500
        assert response.data is not None
        assert response.data == ["item1", "item2"]
        assert response.token == "next_page_token"
