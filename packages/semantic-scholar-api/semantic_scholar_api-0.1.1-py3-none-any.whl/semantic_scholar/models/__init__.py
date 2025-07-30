"""Pydantic models for the Semantic Scholar API client."""

from semantic_scholar.models.author import Author, AuthorBatch, AuthorSearchBatch
from semantic_scholar.models.base import BaseModel, BaseResponse
from semantic_scholar.models.common import (
    CitationStyles,
    Embedding,
    FieldsOfStudy,
    Journal,
    OpenAccessPdf,
    PublicationVenue,
    Tldr,
)
from semantic_scholar.models.dataset import (
    DatasetAvailableReleases,
    DatasetDiff,
    DatasetDiffList,
    DatasetMetadata,
    DatasetReleaseMetadata,
    DatasetSummary,
)
from semantic_scholar.models.paper import (
    AutocompletePaper,
    Citation,
    CitationBatch,
    Paper,
    PaperAutocomplete,
    PaperBulkSearchBatch,
    PaperRecommendationBatch,
    PaperSearchBatch,
    PaperSearchMatch,
    PaperTitleSearchBatch,
    Reference,
    ReferenceBatch,
)
from semantic_scholar.models.snippet import Snippet, SnippetSearchResponse

# Add an __all__ list to indicate exports
__all__ = [
    "Author",
    "AuthorBatch",
    "AuthorSearchBatch",
    "AutocompletePaper",
    "BaseModel",
    "BaseResponse",
    "Citation",
    "CitationBatch",
    "CitationStyles",
    "DatasetAvailableReleases",
    "DatasetDiff",
    "DatasetDiffList",
    "DatasetMetadata",
    "DatasetReleaseMetadata",
    "DatasetSummary",
    "Embedding",
    "FieldsOfStudy",
    "Journal",
    "OpenAccessPdf",
    "Paper",
    "PaperAutocomplete",
    "PaperBulkSearchBatch",
    "PaperRecommendationBatch",
    "PaperSearchBatch",
    "PaperSearchMatch",
    "PaperTitleSearchBatch",
    "PublicationVenue",
    "Reference",
    "ReferenceBatch",
    "Snippet",
    "SnippetSearchResponse",
    "Tldr",
    "DatasetAvailableReleases",
    "DatasetReleaseMetadata",
    "DatasetSummary",
    "DatasetDiff",
    "DatasetDiffList",
    "DatasetMetadata",
]
