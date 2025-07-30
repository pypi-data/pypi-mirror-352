"""Base models for the Semantic Scholar API client."""

from typing import Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base model for all models in the API client."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
        frozen=False,
    )


T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API endpoints."""

    offset: int | None = None
    """Starting position for this batch."""

    next: int | None = None
    """Starting position of the next batch. Absent if no more data exists."""

    total: int | None = None
    """Approximate number of matching search results."""

    data: list[T] = Field(default_factory=lambda: [])
    """Contents of this batch."""

    token: str | None = None
    """Continuation token for bulk search endpoints."""
