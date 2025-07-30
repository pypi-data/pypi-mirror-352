"""Author-related models for the Semantic Scholar API client."""

from typing import Any

from semantic_scholar.models.base import BaseModel, BaseResponse
from semantic_scholar.models.paper import Paper


class Author(BaseModel):
    """Author model with basic information."""

    authorId: str
    """Semantic Scholar's unique ID for the author."""

    externalIds: dict[str, Any] | None = None
    """ORCID/DBLP IDs for the author, if known."""

    url: str | None = None
    """URL of the author on the Semantic Scholar website."""

    name: str | None = None
    """Author's name."""

    affiliations: list[str] | None = None
    """Organizational affiliations for the author."""

    homepage: str | None = None
    """The author's homepage."""

    paperCount: int | None = None
    """The author's total publications count."""

    citationCount: int | None = None
    """The author's total citations count."""

    hIndex: int | None = None
    """The author's h-index."""

    papers: list[Paper] | None = None
    """List of papers by the author."""


class AuthorBatch(BaseModel):
    """Response model for batch author retrieval."""

    data: list[Author]
    """List of authors."""


class AuthorSearchBatch(BaseResponse[Author]):
    """Response model for author search endpoint."""
