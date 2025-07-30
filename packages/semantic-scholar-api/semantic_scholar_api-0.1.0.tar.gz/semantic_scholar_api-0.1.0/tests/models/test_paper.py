"""Tests for the paper models."""

from datetime import date
from typing import Any

import pytest

from semantic_scholar.models.paper import (
    AuthorRef,
    AutocompletePaper,
    BasePaper,
    Citation,
    CitationBatch,
    CitationStyles,
    FieldsOfStudy,
    Journal,
    OpenAccessPdf,
    Paper,
    PaperAutocomplete,
    PaperBatch,
    PaperBulkSearchBatch,
    PaperSearchBatch,
    PaperSearchMatch,
    PublicationVenue,
    Reference,
    ReferenceBatch,
)


class TestBasePaper:
    """Tests for the BasePaper model."""

    def test_real_response(self, mock_server_paper_response: dict[str, Any]):
        paper = BasePaper.model_validate(mock_server_paper_response)

        assert paper.paperId == "p123456"

    def test_required_fields(self):
        """Test that paperId is required."""
        with pytest.raises(ValueError):
            BasePaper.model_validate({})

        # Other fields are optional
        paper = BasePaper.model_validate({"paperId": "p123456"})
        assert paper.paperId == "p123456"
        assert paper.title is None


class TestPaper:
    """Tests for the Paper model.

    Also serves as a hierarchical model test for the Paper model, parsing all
    nested models.
    """

    @pytest.fixture(scope="class")
    def paper(self, mock_server_paper_response: dict[str, Any]) -> Paper:
        """Create a Paper instance from mock response for all tests in this class."""
        return Paper.model_validate(mock_server_paper_response)

    def test_basic_fields(self, paper: Paper) -> None:
        """Test basic paper fields."""
        assert paper.paperId == "p123456"
        assert paper.corpusId == 7890123
        assert paper.url == "https://example.org/papers/p123456/open-access.pdf"
        assert paper.title == "Advances in Machine Learning Theory"
        assert (
            paper.abstract == "We describe a deployed scalable system for organizing published scientific literature..."
        )
        assert paper.venue == "International Conference on Machine Learning"
        assert paper.year == 2018
        assert paper.referenceCount == 35
        assert paper.citationCount == 12
        assert paper.influentialCitationCount == 10
        assert paper.isOpenAccess is True
        assert paper.openAccessPdf is not None
        assert paper.fieldsOfStudy == ["Computer Science"]
        assert paper.publicationTypes == ["Review", "Journal Article"]
        assert paper.publicationDate == date(2018, 6, 1)

    def test_external_ids(self, paper: Paper) -> None:
        """Test paper external IDs."""
        assert paper.externalIds is not None
        assert paper.externalIds["DOI"] == "10.1007/978-3-319-96417-9_1"
        assert paper.externalIds["ArXiv"] == "1234.56789"

    def test_publication_venue(self, paper: Paper) -> None:
        """Test paper publication venue."""
        assert paper.publicationVenue is not None
        assert isinstance(paper.publicationVenue, PublicationVenue)
        assert paper.publicationVenue.id == "v123456"
        assert paper.publicationVenue.name == "International Conference on Machine Learning"
        assert paper.publicationVenue.type == "conference"
        assert paper.publicationVenue.alternate_names == ["ICML", "Intl. Conf. on ML"]
        assert paper.publicationVenue.url == "https://example.org/conferences/icml"

    def test_open_access_pdf(self, paper: Paper) -> None:
        """Test paper open access PDF."""
        assert paper.openAccessPdf is not None
        assert isinstance(paper.openAccessPdf, OpenAccessPdf)
        assert paper.openAccessPdf.url == "https://example.org/papers/p123456/open-access.pdf"
        assert paper.openAccessPdf.status == "GREEN"

    def test_s2_fields_of_study(self, paper: Paper) -> None:
        """Test paper S2 fields of study."""
        assert paper.s2FieldsOfStudy is not None
        assert len(paper.s2FieldsOfStudy) == 3
        assert isinstance(paper.s2FieldsOfStudy[0], FieldsOfStudy)
        assert paper.s2FieldsOfStudy[0].category == "Computer Science"
        assert paper.s2FieldsOfStudy[0].source == "external"
        assert paper.s2FieldsOfStudy[1].category == "Computer Science"
        assert paper.s2FieldsOfStudy[1].source == "s2-fos-model"
        assert paper.s2FieldsOfStudy[2].category == "Mathematics"
        assert paper.s2FieldsOfStudy[2].source == "s2-fos-model"

    def test_journal(self, paper: Paper) -> None:
        """Test paper journal."""
        assert paper.journal is not None
        assert isinstance(paper.journal, Journal)
        assert paper.journal.name == "Journal of Artificial Intelligence Research"
        assert paper.journal.volume == "42"
        assert paper.journal.pages == "123-145"

    def test_citation_styles(self, paper: Paper) -> None:
        """Test paper citation styles."""
        assert paper.citationStyles is not None
        assert isinstance(paper.citationStyles, CitationStyles)
        assert (
            paper.citationStyles.bibtex
            == "@article{smith2018advances, title={Advances in Machine Learning Theory}, author={Smith, Jane}}"
        )

    def test_authors(self, paper: Paper) -> None:
        """Test paper authors."""
        assert paper.authors is not None
        assert len(paper.authors) == 2
        assert isinstance(paper.authors[0], AuthorRef)
        assert paper.authors[0].authorId == "a12345"
        assert paper.authors[0].name == "Jane Smith"

    def test_citations(self, paper: Paper) -> None:
        """Test paper citations."""
        citations = paper.citations
        assert citations is not None

        cited_paper = citations[0]
        assert isinstance(cited_paper, BasePaper)
        assert cited_paper.paperId == "p234567"
        assert cited_paper.title == "An Overview of Machine Learning Methods"
        assert cited_paper.year == 2019
        assert cited_paper.authors is not None
        assert len(cited_paper.authors) == 1
        assert cited_paper.authors[0].name == "Alice Johnson"

    def test_references(self, paper: Paper) -> None:
        """Test paper references."""
        references = paper.references
        assert references is not None

        cited_paper = references[0]
        assert isinstance(cited_paper, BasePaper)
        assert cited_paper.paperId == "p7891011"
        assert cited_paper.title == "Foundations of Deep Learning"
        assert cited_paper.year == 2017
        assert cited_paper.authors is not None

    def test_embeddingr(self, paper: Paper) -> None:
        """Test paper embedding and tldr."""
        assert paper.embedding is not None
        assert paper.embedding.model == "sample-embedding-model@v1.0"
        assert paper.embedding.vector is not None
        assert len(paper.embedding.vector) == 5
        assert sum(paper.embedding.vector) != 0

    def test_tldr(self, paper: Paper) -> None:
        assert paper.tldr is not None
        assert paper.tldr.model == "tldr-model@v1.0"
        assert paper.tldr.text == "This paper introduces a new approach to machine learning that improves accuracy."


class TestPaperBatch:
    """Tests for the PaperBatch model."""

    def test_real_response(self):
        sample_response = {"ids": ["p123456", "p234567", "p345678"]}
        batch = PaperBatch.model_validate(sample_response)

        assert len(batch.ids) == 3
        assert batch.ids[0] == "p123456"
        assert batch.ids[2] == "p345678"

    def test_required_fields(self):
        """Test that ids is required."""
        with pytest.raises(ValueError):
            PaperBatch.model_validate({})


class TestCitation:
    """Tests for the Citation model."""

    def test_real_response(self, mock_server_paper_citations_response: dict[str, Any]):
        citation = Citation.model_validate(mock_server_paper_citations_response["data"][0])

        assert citation.contexts == ["...as shown by Smith (2018)..."]
        assert citation.intents == ["methodology"]
        assert citation.isInfluential is True
        assert citation.citingPaper.paperId == "p234567"

    def test_required_fields(self):
        """Test that citingPaper is required."""
        with pytest.raises(ValueError):
            Citation.model_validate({})

        # Other fields are optional
        citation = Citation.model_validate({"citingPaper": {"paperId": "p234567"}})
        assert citation.citingPaper.paperId == "p234567"
        assert citation.contexts is None


class TestCitationBatch:
    """Tests for the CitationBatch model."""

    def test_real_response(self, mock_server_paper_citations_response: dict[str, Any]):
        batch = CitationBatch.model_validate(mock_server_paper_citations_response)

        assert batch.offset == 0
        assert batch.next == 10
        assert batch.total == 25
        assert len(batch.data) == 2
        assert batch.data[0].citingPaper.paperId == "p234567"
        assert batch.data[1].citingPaper.title == "Citing Paper 2"


class TestReference:
    """Tests for the Reference model."""

    def test_real_response(self, mock_server_paper_references_response: dict[str, Any]):
        reference = Reference.model_validate(mock_server_paper_references_response["data"][0])

        assert reference.contexts == ["...as described by Johnson (2015)..."]
        assert reference.intents == ["background"]
        assert reference.isInfluential is True
        assert reference.citedPaper.paperId == "p456789"

    def test_required_fields(self):
        """Test that citedPaper is required."""
        with pytest.raises(ValueError):
            Reference.model_validate({})


class TestReferenceBatch:
    """Tests for the ReferenceBatch model."""

    def test_real_response(self, mock_server_paper_references_response: dict[str, Any]):
        batch = ReferenceBatch.model_validate(mock_server_paper_references_response)

        assert batch.offset == 0
        assert batch.next == 10
        assert batch.total == 35
        assert len(batch.data) == 2
        assert batch.data[0].citedPaper.paperId == "p456789"
        assert batch.data[1].citedPaper.title == "Referenced Paper 2"


class TestPaperSearchBatch:
    """Tests for the PaperSearchBatch model."""

    def test_real_response(self, mock_server_paper_search_response: dict[str, Any]):
        batch = PaperSearchBatch.model_validate(mock_server_paper_search_response)

        assert batch.offset == 0
        assert batch.next == 10
        assert batch.total == 15117
        assert len(batch.data) == 2
        assert batch.data[0].paperId == "p123456"
        assert batch.data[1].title == "Neural Network Applications"


class TestPaperBulkSearchBatch:
    """Tests for the PaperBulkSearchBatch model."""

    def test_real_response(self, mock_server_paper_bulk_search_response: dict[str, Any]):
        batch = PaperBulkSearchBatch.model_validate(mock_server_paper_bulk_search_response)

        assert batch.total == 15117
        assert batch.token == "NEXT_PAGE_TOKEN"
        assert len(batch.data) == 2
        assert batch.data[0].paperId == "p123456"
        assert batch.data[1].title == "Neural Network Applications"


class TestAutocompletePaper:
    """Tests for the AutocompletePaper model."""

    def test_real_response(self, mock_server_paper_autocomplete_response: dict[str, Any]):
        paper = AutocompletePaper.model_validate(mock_server_paper_autocomplete_response["matches"][0])

        assert paper.id == "p123456"
        assert paper.title == "Advances in Machine Learning Theory"
        assert paper.authorsYear == "Smith et al., 2018"

    def test_required_fields(self):
        """Test that id is required."""
        with pytest.raises(ValueError):
            AutocompletePaper.model_validate({})

        # Other fields are optional
        paper = AutocompletePaper.model_validate({"id": "p123456"})
        assert paper.id == "p123456"
        assert paper.title is None


class TestPaperAutocomplete:
    """Tests for the PaperAutocomplete model."""

    def test_real_response(self, mock_server_paper_autocomplete_response: dict[str, Any]):
        autocomplete = PaperAutocomplete.model_validate(mock_server_paper_autocomplete_response)

        assert len(autocomplete.matches) == 2
        assert autocomplete.matches[0].id == "p123456"
        assert autocomplete.matches[1].title == "Neural Network Applications"

    def test_default_values(self):
        """Test default values."""
        autocomplete = PaperAutocomplete()
        assert autocomplete.matches == []


class TestPaperSearchMatch:
    """Tests for the PaperSearchMatch model."""

    def test_real_response(self, mock_server_paper_title_search_response: dict[str, Any]):
        match = PaperSearchMatch.model_validate(mock_server_paper_title_search_response["data"][0])

        assert match.paperId == "p123456"
        assert match.title == "Advances in Machine Learning Theory"
        assert match.matchScore == 174.2298

    def test_required_fields(self):
        """Test that paperId is required."""
        with pytest.raises(ValueError):
            PaperSearchMatch.model_validate({})
