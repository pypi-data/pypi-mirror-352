"""Common models shared across different response types."""

from semantic_scholar.models.base import BaseModel


class AuthorRef(BaseModel):
    """Minimal author reference used in paper models."""

    authorId: str
    name: str | None = None


class OpenAccessPdf(BaseModel):
    """Information about the open access PDF of a paper."""

    url: str | None = None
    """URL to the PDF file."""

    status: str | None = None
    """The type of open access (e.g., 'HYBRID', 'BRONZE', 'GREEN', 'GOLD')."""


class Embedding(BaseModel):
    """Vector embedding for a paper."""

    model: str | None = None
    """The embedding model used (e.g., 'specter@v0.1.1')."""

    vector: list[float] | None = None
    """The embedding vector."""


class Tldr(BaseModel):
    """Too Long; Didn't Read summary of a paper."""

    model: str | None = None
    """The model used to generate the summary."""

    text: str | None = None
    """The summary text."""


class PublicationVenue(BaseModel):
    """Information about a publication venue (journal or conference)."""

    id: str | None = None
    """The venue's unique ID."""

    name: str | None = None
    """The venue's name."""

    type: str | None = None
    """The type of venue (e.g., 'journal', 'conference')."""

    alternate_names: list[str] | None = None
    """Alternative names for the venue."""

    url: str | None = None
    """URL of the venue's website."""


class Journal(BaseModel):
    """Information about a journal publication."""

    name: str | None = None
    """The journal name."""

    volume: str | None = None
    """The journal volume."""

    pages: str | None = None
    """The page range in the journal."""


class CitationStyles(BaseModel):
    """Bibliographic citation formats."""

    bibtex: str | None = None
    """The BibTeX citation."""


class FieldsOfStudy(BaseModel):
    """Field of study with source information."""

    category: str
    """The field of study category."""

    source: str
    """The source of the classification (e.g., 'external', 's2-fos-model')."""
