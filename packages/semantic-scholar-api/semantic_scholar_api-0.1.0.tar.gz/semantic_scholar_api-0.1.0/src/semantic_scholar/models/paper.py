"""Paper-related models for the Semantic Scholar API client."""

from datetime import date
from typing import Any, TypeVar

from pydantic import Field

from semantic_scholar.models.base import BaseModel, BaseResponse
from semantic_scholar.models.common import (
    AuthorRef,
    CitationStyles,
    Embedding,
    FieldsOfStudy,
    Journal,
    OpenAccessPdf,
    PublicationVenue,
    Tldr,
)


class BasePaper(BaseModel):
    """Base paper model with common fields."""

    paperId: str
    """Semantic Scholar's primary unique identifier for a paper."""

    corpusId: int | None = None
    """Semantic Scholar's secondary unique identifier for a paper."""

    externalIds: dict[str, Any] | None = None
    """The paper's unique identifiers in external sources."""

    url: str | None = None
    """URL of the paper on the Semantic Scholar website."""

    title: str | None = None
    """Title of the paper."""

    abstract: str | None = None
    """The paper's abstract."""

    venue: str | None = None
    """The name of the paper's publication venue."""

    publicationVenue: PublicationVenue | None = None
    """Detailed information about the publication venue."""

    year: int | None = None
    """The year the paper was published."""

    referenceCount: int | None = None
    """The total number of papers this paper references."""

    citationCount: int | None = None
    """The total number of papers that reference this paper."""

    influentialCitationCount: int | None = None
    """A subset of the citation count for significant impact."""

    isOpenAccess: bool | None = None
    """Whether the paper is open access."""

    openAccessPdf: OpenAccessPdf | None = None
    """Information about the open access PDF if available."""

    fieldsOfStudy: list[str] | None = None
    """A list of the paper's high-level academic categories."""

    s2FieldsOfStudy: list[FieldsOfStudy] | None = None
    """Detailed fields of study with source information."""

    publicationTypes: list[str] | None = None
    """The types of this publication."""

    publicationDate: date | None = None
    """The date when this paper was published."""

    journal: Journal | None = None
    """Journal information if published in a journal."""

    citationStyles: CitationStyles | None = None
    """Bibliographic citation formats."""

    authors: list[AuthorRef] | None = None
    """List of the paper's authors."""


class Paper(BasePaper):
    """Complete paper model with all available fields."""

    citations: list[BasePaper] | None = None
    """Papers that cite this paper."""

    references: list[BasePaper] | None = None
    """Papers that this paper cites."""

    embedding: Embedding | None = None
    """Vector embedding for the paper."""

    tldr: Tldr | None = None
    """Too Long; Didn't Read summary of the paper."""


P = TypeVar("P", bound=BasePaper)


class PaperBatch(BaseModel):
    """Request model for batch paper retrieval."""

    ids: list[str]
    """List of paper IDs to retrieve."""


class Citation(BaseModel):
    """Information about a citation relationship."""

    contexts: list[str] | None = None
    """Text snippets where the reference to the paper is mentioned."""

    intents: list[str] | None = None
    """Citation intents that summarize how the reference is mentioned."""

    isInfluential: bool | None = None
    """Whether the citing paper is highly influential."""

    citingPaper: BasePaper
    """The paper that cites the target paper."""


class CitationBatch(BaseResponse[Citation]):
    """Response model for paper citations endpoint."""


class Reference(BaseModel):
    """Information about a reference relationship."""

    contexts: list[str] | None = None
    """Text snippets where the reference to the paper is mentioned."""

    intents: list[str] | None = None
    """Citation intents that summarize how the reference is mentioned."""

    isInfluential: bool | None = None
    """Whether the reference is highly influential."""

    citedPaper: BasePaper
    """The paper that is cited by the target paper."""


class ReferenceBatch(BaseResponse[Reference]):
    """Response model for paper references endpoint."""


class AutocompletePaper(BaseModel):
    """Paper result from autocomplete endpoint."""

    id: str
    """The paper's primary unique identifier."""

    title: str | None = None
    """Title of the paper."""

    authorsYear: str | None = None
    """Summary of the authors and year of publication."""


class PaperAutocomplete(BaseModel):
    """Response model for paper autocomplete endpoint."""

    matches: list[AutocompletePaper] = Field(default_factory=list)
    """List of matching papers for autocomplete."""


class PaperSearchMatch(BaseModel):
    """Paper match from title search endpoint."""

    paperId: str
    """The paper's primary unique identifier."""

    title: str | None = None
    """Title of the paper."""

    matchScore: float | None = None
    """Score indicating match quality."""


class PaperTitleSearchBatch(BaseResponse[PaperSearchMatch]):
    """Response model for paper title search endpoint."""


class PaperSearchBatch(BaseResponse[Paper]):
    """Response model for paper search endpoint."""


class PaperBulkSearchBatch(BaseResponse[BasePaper]):
    """Response model for paper bulk search endpoint."""


class PaperRecommendationBatch(BaseModel):
    """Response model for paper recommendation endpoints."""

    recommendedPapers: list[BasePaper]
    """List of recommended papers."""
