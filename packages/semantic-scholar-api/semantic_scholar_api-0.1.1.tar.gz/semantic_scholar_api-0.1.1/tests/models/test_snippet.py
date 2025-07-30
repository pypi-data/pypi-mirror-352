"""Tests for the snippet models."""

from typing import Any

import pytest

from semantic_scholar.models.snippet import (
    OpenAccessInfo,
    RefMention,
    Sentence,
    Snippet,
    SnippetAnnotations,
    SnippetMatch,
    SnippetOffset,
    SnippetPaper,
    SnippetSearchResponse,
)


class TestSnippet:
    """Tests for the Snippet model.

    Also serves as a hierarchical model test for the Snippet model, parsing all
    nested models.
    """

    @pytest.fixture(scope="class")
    def snippet(self, mock_server_snippet_search_response: dict[str, Any]) -> Snippet:
        """Create a Snippet instance from mock response for all tests in this class."""
        response = SnippetSearchResponse.model_validate(mock_server_snippet_search_response)
        return response.data[0].snippet

    def test_snippet_basic_fields(self, snippet: Snippet):
        """Test snippet basic fields."""
        assert snippet.text == "In this paper, we discuss the construction of a graph..."
        assert snippet.snippetKind == "body"
        assert snippet.section == "Introduction"

    def test_snippet_annotations(self, snippet: Snippet):
        """Test snippet annotations."""
        assert snippet.annotations is not None
        assert isinstance(snippet.annotations, SnippetAnnotations)

        assert snippet.annotations.sentences is not None
        assert len(snippet.annotations.sentences) == 1
        sentence = snippet.annotations.sentences[0]
        assert isinstance(sentence, Sentence)
        assert sentence.start == 0
        assert sentence.end == 120

        assert snippet.annotations.refMentions is not None
        assert len(snippet.annotations.refMentions) == 1
        mention = snippet.annotations.refMentions[0]
        assert isinstance(mention, RefMention)
        assert mention.start == 377
        assert mention.end == 402
        assert mention.matchedPaperCorpusId == "7377848"

    def test_snippet_offset(self, snippet: Snippet):
        """Test snippet offset."""
        assert snippet.snippetOffset is not None
        assert isinstance(snippet.snippetOffset, SnippetOffset)
        assert snippet.snippetOffset.start == 24506
        assert snippet.snippetOffset.end == 25694


class TestSnippetRequiredFields:
    def test_required_fields(self):
        """Test that text is required."""
        with pytest.raises(ValueError):
            Snippet.model_validate({})

        # Other fields are optional
        snippet = Snippet.model_validate({"text": "Sample text."})
        assert snippet.text == "Sample text."
        assert snippet.snippetKind is None
        assert snippet.section is None


class TestSnippetOffset:
    """Tests for the SnippetOffset model."""

    def test_required_fields(self):
        """Test that start and end are required."""
        with pytest.raises(ValueError):
            SnippetOffset.model_validate({})

        with pytest.raises(ValueError):
            SnippetOffset.model_validate({"start": 120})

        with pytest.raises(ValueError):
            SnippetOffset.model_validate({"end": 350})


class TestSentence:
    """Tests for the Sentence model."""

    def test_required_fields(self):
        """Test that start and end are required."""
        with pytest.raises(ValueError):
            Sentence.model_validate({})


class TestRefMention:
    """Tests for the RefMention model."""

    def test_required_fields(self):
        """Test that start and end are required."""
        with pytest.raises(ValueError):
            RefMention.model_validate({})

        # matchedPaperCorpusId is optional
        mention = RefMention.model_validate({"start": 45, "end": 65})
        assert mention.start == 45
        assert mention.end == 65
        assert mention.matchedPaperCorpusId is None


class TestSnippetAnnotations:
    """Tests for the SnippetAnnotations model."""

    def test_optional_fields(self):
        """Test that all fields are optional."""
        annotations = SnippetAnnotations()
        assert annotations.sentences is None
        assert annotations.refMentions is None


class TestOpenAccessInfo:
    """Tests for the OpenAccessInfo model."""

    def test_real_response(self):
        """Test with realistic data."""
        sample_response = {
            "license": "CC-BY",
            "status": "GOLD",
            "disclaimer": "This content is made available under the terms of the Creative Commons Attribution License.",
        }

        info = OpenAccessInfo.model_validate(sample_response)

        assert info.license == "CC-BY"
        assert info.status == "GOLD"
        assert (
            info.disclaimer
            == "This content is made available under the terms of the Creative Commons Attribution License."
        )

    def test_optional_fields(self):
        """Test that all fields are optional."""
        info = OpenAccessInfo()
        assert info.license is None
        assert info.status is None
        assert info.disclaimer is None


class TestSnippetPaper:
    """Tests for the SnippetPaper model."""

    @pytest.fixture(scope="class")
    def paper(self, mock_server_snippet_search_response: dict[str, Any]) -> SnippetPaper:
        """Create a SnippetPaper instance from mock response for all tests in this class."""
        response = SnippetSearchResponse.model_validate(mock_server_snippet_search_response)
        return response.data[0].paper

    def test_real_response(self, paper: SnippetPaper):
        assert paper.corpusId == "123456"
        assert paper.title == "Advances in Machine Learning Theory"
        assert paper.authors == ["Jane Smith", "John Doe"]
        assert paper.openAccessInfo is not None
        assert paper.openAccessInfo.license == "CC-BY"
        assert paper.openAccessInfo.status == "GREEN"
        assert paper.openAccessInfo.disclaimer == (
            "Notice: This snippet is extracted from the open access paper or abstract available at "
            "https://arxiv.org/abs/1805.02262, which is subject to the license by the author or copyright owner "
            "provided with this content. Please go to the source to verify the license and copyright "
            "information for your use."
        )

    def test_required_fields(self):
        """Test that corpusId is required."""
        with pytest.raises(ValueError):
            SnippetPaper.model_validate({})


class TestSnippetMatch:
    """Tests for the SnippetMatch model."""

    def test_real_response(self, mock_server_snippet_search_response: dict[str, Any]):
        response = SnippetSearchResponse.model_validate(mock_server_snippet_search_response)
        match = response.data[0]

        assert match.score == 0.562
        assert isinstance(match.snippet, Snippet)
        assert isinstance(match.paper, SnippetPaper)

    def test_required_fields(self):
        """Test that snippet and paper are required."""
        with pytest.raises(ValueError):
            SnippetMatch.model_validate({})

        with pytest.raises(ValueError):
            SnippetMatch.model_validate({"snippet": {"text": "Sample text."}})

        with pytest.raises(ValueError):
            SnippetMatch.model_validate({"paper": {"corpusId": "p123456"}})

        # Score is optional
        match = SnippetMatch.model_validate({"snippet": {"text": "Sample text."}, "paper": {"corpusId": "p123456"}})
        assert match.snippet.text == "Sample text."
        assert match.paper.corpusId == "p123456"
        assert match.score is None


class TestSnippetSearchResponse:
    """Tests for the SnippetSearchResponse model."""

    def test_real_response(self, mock_server_snippet_search_response: dict[str, Any]):
        response = SnippetSearchResponse.model_validate(mock_server_snippet_search_response)

        assert isinstance(response, SnippetSearchResponse)

    def test_default_values(self):
        """Test default values."""
        response = SnippetSearchResponse()
        assert response.data == []
        assert response.retrievalVersion is None
