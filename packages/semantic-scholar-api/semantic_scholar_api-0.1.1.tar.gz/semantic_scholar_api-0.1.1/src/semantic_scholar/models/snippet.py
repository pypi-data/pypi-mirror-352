"""Snippet-related models for the Semantic Scholar API client."""

from semantic_scholar.models.base import BaseModel


class SnippetOffset(BaseModel):
    """Position information for a snippet in a paper."""

    start: int
    """Start position of the snippet."""

    end: int
    """End position of the snippet."""


class Sentence(BaseModel):
    """Sentence boundary information."""

    start: int
    """Start position of the sentence."""

    end: int
    """End position of the sentence."""


class RefMention(BaseModel):
    """Information about a reference mention in a snippet."""

    start: int
    """Start position of the reference mention."""

    end: int
    """End position of the reference mention."""

    matchedPaperCorpusId: str | None = None
    """Corpus ID of the referenced paper."""


class SnippetAnnotations(BaseModel):
    """Annotations for a snippet."""

    sentences: list[Sentence] | None = None
    """List of sentence boundaries in the snippet."""

    refMentions: list[RefMention] | None = None
    """List of reference mentions in the snippet."""


class OpenAccessInfo(BaseModel):
    """Open access information for a paper."""

    license: str | None = None
    """The license attached to the paper."""

    status: str | None = None
    """Paper's open access status."""

    disclaimer: str | None = None
    """Disclaimer about open access use."""


class SnippetPaper(BaseModel):
    """Paper information included with a snippet."""

    corpusId: str
    """Semantic Scholar's identifier for the paper."""

    title: str | None = None
    """Title of the paper."""

    authors: list[str] | None = None
    """List of author names."""

    openAccessInfo: OpenAccessInfo | None = None
    """Open access information for the paper."""


class Snippet(BaseModel):
    """Text snippet from a paper."""

    text: str
    """The direct quote or snippet from the paper."""

    snippetKind: str | None = None
    """Where the snippet is located (title, abstract, or body)."""

    section: str | None = None
    """The section of the paper where the snippet is located."""

    snippetOffset: SnippetOffset | None = None
    """Position information for the snippet."""

    annotations: SnippetAnnotations | None = None
    """Annotations for the snippet."""


class SnippetMatch(BaseModel):
    """Match result from snippet search."""

    snippet: Snippet
    """The matching text snippet."""

    score: float | None = None
    """Relevance score of the match."""

    paper: SnippetPaper
    """Information about the paper containing the snippet."""


class SnippetSearchResponse(BaseModel):
    """Response model for snippet search endpoint."""

    data: list[SnippetMatch] = []
    """List of matching snippets."""

    retrievalVersion: str | None = None
    """Version identifier for the retrieval algorithm."""
