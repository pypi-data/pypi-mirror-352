"""Tests for the author models."""

from typing import Any

import pytest

from semantic_scholar.models.author import (
    Author,
    AuthorBatch,
    AuthorSearchBatch,
    Paper,
)


class TestAuthor:
    """Tests for the Author model with realistic data."""

    @pytest.fixture(scope="class")
    def author(self, mock_server_author_response: dict[str, Any]) -> Author:
        """Create an Author instance from mock response for all tests in this class."""
        return Author.model_validate(mock_server_author_response)

    def test_author_basic_fields(self, author: Author):
        """Test parsing a realistic author response."""
        assert author.authorId == "a12345"
        assert author.name == "Jane Smith"
        assert author.url == "https://example.org/author/a12345"
        assert author.affiliations == ["Sample University"]
        assert author.paperCount == 300
        assert author.citationCount == 34803
        assert author.hIndex == 86

    def test_author_papers(self, author: Author):
        """Test author papers."""
        assert author.papers is not None
        assert len(author.papers) == 2
        paper = author.papers[0]
        assert isinstance(paper, Paper)
        assert paper.paperId == "p123456"
        assert paper.title == "Advances in Machine Learning Theory"
        assert paper.year == 2018
        assert paper.authors is not None
        assert len(paper.authors) == 2
        assert paper.authors[0].authorId == "a12345"
        assert paper.authors[1].authorId == "a67890"

    def test_external_ids(self, author: Author):
        """Test author external IDs."""
        assert author.externalIds is not None
        assert author.externalIds["GoogleScholar"] == ["1234567890"]

    def test_missing_required_fields(self):
        """Test that models fail when required fields are missing."""
        # Author requires authorId
        with pytest.raises(ValueError):
            Author.model_validate({})

        # But works with just authorId
        author = Author.model_validate({"authorId": "a12345"})
        assert author.authorId == "a12345"


class TestAuthorBatch:
    """Tests for the AuthorBatch model."""

    def test_author_batch_response(self, mock_server_author_batch_response: list[dict[str, Any]]):
        """Test parsing a batch of authors."""
        batch = AuthorBatch.model_validate({"data": mock_server_author_batch_response})

        assert len(batch.data) == 2
        assert batch.data[0].authorId == "a12345"
        assert batch.data[1].name == "John Doe"


class TestAuthorSearchBatch:
    """Tests for the AuthorSearchBatch model."""

    def test_author_search_batch(self, mock_server_author_search_response: dict[str, Any]):
        """Test parsing a search batch of authors with papers."""
        batch = AuthorSearchBatch.model_validate(mock_server_author_search_response)

        assert batch.offset == 0
        assert batch.next == 10
        assert batch.total == 490
        assert len(batch.data) == 2
        assert batch.data[0].authorId == "a12345"
        assert batch.data[0].papers is not None
        assert len(batch.data[0].papers) == 1
        assert batch.data[0].papers[0].title == "Advances in Machine Learning Theory"
