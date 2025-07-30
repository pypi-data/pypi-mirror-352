"""Tests for the Semantic Scholar client."""

from typing import Any
from unittest.mock import patch

import pytest

from semantic_scholar.api.clients import APIResponse
from semantic_scholar.models import (
    Author,
    AuthorBatch,
    AuthorSearchBatch,
    CitationBatch,
    DatasetAvailableReleases,
    DatasetDiffList,
    DatasetMetadata,
    DatasetReleaseMetadata,
    Paper,
    PaperAutocomplete,
    PaperBulkSearchBatch,
    PaperRecommendationBatch,
    PaperSearchBatch,
    ReferenceBatch,
    SnippetSearchResponse,
)
from semantic_scholar.semantic_scholar import SemanticScholar


def mock_api_response(data: dict[str, Any]) -> APIResponse:
    return APIResponse(data=data, info={"status_code": 200, "headers": {}})


def mock_api_response_for_lists(data: list[Any]) -> APIResponse:
    return APIResponse(data={"data": data}, info={"status_code": 200, "headers": {}})


class TestSemanticScholar:
    """Tests for the SemanticScholar class."""

    @pytest.mark.asyncio
    async def test_get_paper(self, mock_server_paper_response: dict[str, Any]):
        """Test getting a paper by ID."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_response)

            result = await client.get_paper("p123456")

            # Check the URL and params
            mock_get.assert_called_once_with("https://api.semanticscholar.org/graph/v1/paper/p123456", params={})

            # Check the result
            assert isinstance(result, Paper)
            assert result.paperId == "p123456"
            assert result.title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_get_paper_with_fields(self, mock_server_paper_response: dict[str, Any]):
        """Test getting a paper with specific fields."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_response)

            result = await client.get_paper("p123456", fields=["title", "abstract", "authors"])

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/p123456",
                params={"fields": "title,abstract,authors"},
            )

            # Check the result
            assert isinstance(result, Paper)
            assert result.paperId == "p123456"
            assert result.title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_search_papers(self, mock_server_paper_search_response: dict[str, Any]):
        """Test searching for papers."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_search_response)

            result = await client.search_papers("machine learning", limit=10)

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={
                    "query": "machine learning",
                    "limit": 10,
                    "offset": 0,
                    "fields": "title,abstract,isOpenAccess,openAccessPdf",
                },
            )

            # Check the result
            assert isinstance(result, PaperSearchBatch)
            assert result.total == 15117
            assert len(result.data) == 2
            assert result.data[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_search_papers_with_filters(self, mock_server_paper_search_response: dict[str, Any]):
        """Test searching for papers with filters."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_search_response)

            result = await client.search_papers(
                "semantic scholar",
                limit=2,
                fields=["title", "year"],
                publication_types=["JournalArticle", "Conference"],
                open_access_pdf=True,
                min_citation_count=10,
                year="2018-2020",
                venue=["Nature", "Science"],
                fields_of_study=["Computer Science"],
            )

            # Check the params
            assert mock_get.call_args[1]["params"]["query"] == "semantic scholar"
            assert mock_get.call_args[1]["params"]["limit"] == 2
            assert mock_get.call_args[1]["params"]["fields"] == "title,year"
            assert mock_get.call_args[1]["params"]["publicationTypes"] == "JournalArticle,Conference"
            assert mock_get.call_args[1]["params"]["openAccessPdf"] == ""
            assert mock_get.call_args[1]["params"]["minCitationCount"] == "10"
            assert mock_get.call_args[1]["params"]["year"] == "2018-2020"
            assert mock_get.call_args[1]["params"]["venue"] == "Nature,Science"
            assert mock_get.call_args[1]["params"]["fieldsOfStudy"] == "Computer Science"

            # Check the result
            assert isinstance(result, PaperSearchBatch)

    @pytest.mark.asyncio
    async def test_search_authors(self, mock_server_author_search_response: dict[str, Any]):
        """Test searching for authors."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_author_search_response)

            result = await client.search_authors("Jane Smith", limit=5)

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/author/search",
                params={"query": "Jane Smith", "limit": 5, "offset": 0},
            )

            # Check the result
            assert isinstance(result, AuthorSearchBatch)
            assert result.total == 490
            assert len(result.data) == 2
            assert result.data[0].name == "Jane Smith"

    @pytest.mark.asyncio
    async def test_get_author(self, mock_server_author_response: dict[str, Any]):
        """Test getting an author by ID."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_author_response)

            result = await client.get_author("a12345")

            # Check the URL and params
            mock_get.assert_called_once_with("https://api.semanticscholar.org/graph/v1/author/a12345", params={})

            # Check the result
            assert isinstance(result, Author)
            assert result.authorId == "a12345"
            assert result.name == "Jane Smith"

    @pytest.mark.asyncio
    async def test_get_author_papers(self, mock_server_author_papers_response: dict[str, Any]):
        """Test getting papers by a specific author."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_author_papers_response)

            result = await client.get_author_papers("a12345", limit=10)

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/author/a12345/papers", params={"limit": 10, "offset": 0}
            )

            # Check the result
            assert isinstance(result, PaperSearchBatch)
            assert result.next == 10
            assert len(result.data) == 2
            assert result.data[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_autocomplete_paper(self, mock_server_paper_autocomplete_response: dict[str, Any]):
        """Test paper title autocomplete."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_autocomplete_response)

            result = await client.autocomplete_paper("machine learning")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/autocomplete",
                params={"query": "machine learning"},
            )

            # Check the result
            assert isinstance(result, PaperAutocomplete)
            assert len(result.matches) == 2
            assert result.matches[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_search_papers_bulk(self, mock_server_paper_bulk_search_response: dict[str, Any]):
        """Test bulk search for papers."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_bulk_search_response)

            result = await client.search_papers_bulk("machine learning")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
                params={"query": "machine learning"},
            )

            # Check the result
            assert isinstance(result, PaperBulkSearchBatch)
            assert result.token == "NEXT_PAGE_TOKEN"
            assert len(result.data) == 2
            assert result.data[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_match_paper(
        self, mock_server_paper_title_search_response: dict[str, Any], mock_server_paper_response: dict[str, Any]
    ):
        """Test matching a paper by title."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            # First call returns the search results, second call returns the paper details
            mock_get.side_effect = [
                mock_api_response(mock_server_paper_title_search_response),
                mock_api_response(mock_server_paper_response),
            ]

            result = await client.match_paper("Advances in Machine Learning Theory")

            # Check the URL and params for the search call
            assert mock_get.call_args_list[0][0][0] == "https://api.semanticscholar.org/graph/v1/paper/search/match"
            assert mock_get.call_args_list[0][1]["params"]["query"] == "Advances in Machine Learning Theory"

            # Check the URL and params for the paper details call
            assert mock_get.call_args_list[1][0][0] == "https://api.semanticscholar.org/graph/v1/paper/p123456"

            # Check the result
            assert isinstance(result, Paper)
            assert result.paperId == "p123456"
            assert result.title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_get_paper_authors(self, mock_server_paper_authors_response: dict[str, Any]):
        """Test getting authors for a paper."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_authors_response)

            result = await client.get_paper_authors("p123456")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/p123456/authors",
                params={"offset": 0, "limit": 100},
            )

            # Check the result
            assert isinstance(result, AuthorBatch)
            assert len(result.data) == 2
            assert result.data[0].name == "Jane Smith"
            assert result.data[1].name == "John Doe"

    @pytest.mark.asyncio
    async def test_get_paper_citations(self, mock_server_paper_citations_response: dict[str, Any]):
        """Test getting citations for a paper."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_citations_response)

            result = await client.get_paper_citations("p123456")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/p123456/citations",
                params={"offset": 0, "limit": 100},
            )

            # Check the result
            assert isinstance(result, CitationBatch)
            assert len(result.data) == 2
            assert result.data[0].citingPaper.title == "An Overview of Machine Learning Methods"
            assert result.data[0].isInfluential is True
            assert result.data[1].citingPaper.title == "Citing Paper 2"

    @pytest.mark.asyncio
    async def test_get_paper_references(self, mock_server_paper_references_response: dict[str, Any]):
        """Test getting references for a paper."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_references_response)

            result = await client.get_paper_references("p123456")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/p123456/references",
                params={"offset": 0, "limit": 100},
            )

            # Check the result
            assert isinstance(result, ReferenceBatch)
            assert len(result.data) == 2
            assert result.data[0].citedPaper.title == "Referenced Paper 1"
            assert result.data[0].isInfluential is True
            assert result.data[1].citedPaper.title == "Referenced Paper 2"

    @pytest.mark.asyncio
    async def test_search_snippets(self, mock_server_snippet_search_response: dict[str, Any]):
        """Test searching for snippets."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_snippet_search_response)

            result = await client.search_snippets("machine learning")

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/snippet/search",
                params={"query": "machine learning", "limit": 10},
            )

            # Check the result
            assert isinstance(result, SnippetSearchResponse)
            assert len(result.data) == 1
            assert result.data[0].paper.title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_get_paper_batch(self, mock_server_paper_batch_response: list[dict[str, Any]]):
        """Test getting a batch of papers."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "post") as mock_post:
            # The raw server response is sufficient here
            mock_post.return_value = mock_api_response_for_lists(mock_server_paper_batch_response)

            result = await client.get_paper_batch(["p123456"], fields=["title", "year"])

            # Check the URL and params
            mock_post.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/batch",
                params={"fields": "title,year"},
                json={"ids": ["p123456"]},
            )

            # Check the result
            assert len(result.data) == 2
            assert result.data[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_get_paper_batch_without_fields(self, mock_server_paper_batch_response: list[dict[str, Any]]):
        """Test getting a batch of papers without specifying fields."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "post") as mock_post:
            mock_post.return_value = mock_api_response_for_lists(mock_server_paper_batch_response)

            result = await client.get_paper_batch(["p123456"])

            # Check the URL and params
            mock_post.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/paper/batch",
                params=None,
                json={"ids": ["p123456"]},
            )

            # Check the result
            assert len(result.data) == 2
            assert result.data[0].title == "Advances in Machine Learning Theory"

    @pytest.mark.asyncio
    async def test_get_author_batch(self, mock_server_author_batch_response: list[dict[str, Any]]):
        """Test getting a batch of authors by their IDs."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "post") as mock_post:
            mock_post.return_value = mock_api_response_for_lists(mock_server_author_batch_response)
            author_ids = ["a12345", "b12345"]
            result = await client.get_author_batch(author_ids, fields=["name", "paperCount"])

            # Check the URL, params, and JSON data
            mock_post.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/author/batch",
                params={"fields": "name,paperCount"},
                json={"ids": author_ids},
            )

            # Check the result
            assert isinstance(result, AuthorBatch)
            assert len(result.data) == 2
            assert result.data[0].authorId == "a12345"

    @pytest.mark.asyncio
    async def test_get_author_batch_without_fields(self, mock_server_author_batch_response: list[dict[str, Any]]):
        """Test getting a batch of authors by their IDs without specifying fields."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "post") as mock_post:
            mock_post.return_value = mock_api_response_for_lists(mock_server_author_batch_response)

            author_ids = ["a12345", "b12345"]
            result = await client.get_author_batch(author_ids)

            # Check the URL, params, and JSON data
            mock_post.assert_called_once_with(
                "https://api.semanticscholar.org/graph/v1/author/batch",
                params=None,
                json={"ids": author_ids},
            )

            # Check the result
            assert isinstance(result, AuthorBatch)
            assert len(result.data) == 2
            assert result.data[0].authorId == "a12345"

    @pytest.mark.asyncio
    async def test_get_recommendations_from_paper(self, mock_server_paper_recommendations_response: dict[str, Any]):
        """Test getting recommendations based on a paper."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_recommendations_response)

            result = await client.get_recommendations_from_paper("p123456", fields=["title", "year"])

            # Check the URL and params
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/recommendations/v1/papers/forpaper/p123456",
                params={"fields": "title,year"},
            )

            # Check the result
            assert isinstance(result, PaperRecommendationBatch)
            assert len(result.recommendedPapers) == 2

    @pytest.mark.asyncio
    async def test_get_recommendations_from_paper_list(
        self, mock_server_paper_list_recommendations_response: dict[str, Any]
    ):
        """Test getting recommendations based on a list of papers."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "post") as mock_post:
            mock_post.return_value = mock_api_response(mock_server_paper_list_recommendations_response)

            positive_paper_ids = ["p123456"]
            negative_paper_ids = ["p789012"]

            result = await client.get_recommendations_from_paper_list(
                positive_paper_ids=positive_paper_ids,
                negative_paper_ids=negative_paper_ids,
                fields=["title", "year"],
            )

            # Check the URL, params, and JSON data
            mock_post.assert_called_once_with(
                "https://api.semanticscholar.org/recommendations/v1/papers",
                params={"fields": "title,year", "limit": 100},
                json={
                    "positivePaperIds": positive_paper_ids,
                    "negativePaperIds": negative_paper_ids,
                },
            )

            # Check the result
            assert isinstance(result, PaperRecommendationBatch)
            assert len(result.recommendedPapers) == 2

    @pytest.mark.asyncio
    async def test_search_papers_bulk_with_token(self, mock_server_paper_bulk_search_response: dict[str, Any]):
        """Test bulk searching papers with token parameter."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_bulk_search_response)

            result = await client.search_papers_bulk("test query", token="next-page-token")

            # Check the URL and params
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert "token" in call_args["params"]
            assert call_args["params"]["token"] == "next-page-token"

            # Check the result
            assert isinstance(result, PaperBulkSearchBatch)

    @pytest.mark.asyncio
    async def test_search_snippets_with_paper_ids(self, mock_server_snippet_search_response: dict[str, Any]):
        """Test searching snippets with paper_ids filter."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_snippet_search_response)

            paper_ids = ["paper1", "paper2"]
            result = await client.search_snippets("test query", paper_ids=paper_ids)

            # Check the URL and params
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert "paperIds" in call_args["params"]
            assert call_args["params"]["paperIds"] == "paper1,paper2"

            # Check the result
            assert isinstance(result, SnippetSearchResponse)

    @pytest.mark.asyncio
    async def test_get_paper_authors_with_fields(self, mock_server_paper_authors_response: dict[str, Any]):
        """Test getting paper authors with fields parameter."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_authors_response)

            fields = ["authorId", "name", "affiliations"]
            result = await client.get_paper_authors("paper123", fields=fields)

            # Check the URL and params
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert "fields" in call_args["params"]
            assert call_args["params"]["fields"] == "authorId,name,affiliations"

            # Check the result
            assert isinstance(result, AuthorBatch)

    @pytest.mark.asyncio
    async def test_make_paginated_request_with_additional_params(
        self, mock_server_paper_authors_response: dict[str, Any]
    ):
        """Test _make_paginated_request with additional_params."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_paper_authors_response)

            # Call _make_paginated_request directly with additional_params
            additional_params = {"sort": "relevance"}
            result = await client._make_paginated_request(  # pyright: ignore[reportPrivateUsage]
                endpoint="paper/123/authors",
                offset=0,
                limit=10,
                fields=["authorId", "name"],
                additional_params=additional_params,
            )

            # Check that the additional_params were included in the request
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert call_args["params"]["sort"] == "relevance"
            assert call_args["params"]["fields"] == "authorId,name"
            assert call_args["params"]["offset"] == 0
            assert call_args["params"]["limit"] == 10

            # Check that we got a response
            assert result is not None

    @pytest.mark.asyncio
    async def test_search_authors_with_fields(self, mock_server_author_search_response: dict[str, Any]):
        """Test searching authors with fields parameter."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_author_search_response)

            fields = ["authorId", "name", "affiliations"]
            result = await client.search_authors("John Doe", fields=fields)

            # Check the URL and params
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert "fields" in call_args["params"]
            assert call_args["params"]["fields"] == "authorId,name,affiliations"

            # Check the result
            assert isinstance(result, AuthorSearchBatch)

    @pytest.mark.asyncio
    async def test_build_common_filter_params_open_access_pdf(self):
        """Test that _build_common_filter_params correctly handles open_access_pdf."""
        client = SemanticScholar(api_key="test-key")

        # Test with open_access_pdf=True
        params = client._build_common_filter_params(  # pyright: ignore[reportPrivateUsage]
            query="test",
            open_access_pdf=True,
        )
        assert "openAccessPdf" in params
        assert params["openAccessPdf"] == ""

        # Test with open_access_pdf=False
        params = client._build_common_filter_params(  # pyright: ignore[reportPrivateUsage]
            query="test",
            open_access_pdf=False,
        )
        assert "openAccessPdf" not in params

    @pytest.mark.asyncio
    async def test_build_common_filter_params_sort(self):
        """Test that _build_common_filter_params correctly handles sort."""
        client = SemanticScholar(api_key="test-key")

        params = client._build_common_filter_params(  # pyright: ignore[reportPrivateUsage]
            query="test",
            sort="relevance",
        )
        assert "sort" in params
        assert params["sort"] == "relevance"

    @pytest.mark.asyncio
    async def test_build_common_filter_params_publication_date(self):
        """Test that _build_common_filter_params correctly handles publication_date_or_year."""
        client = SemanticScholar(api_key="test-key")

        params = client._build_common_filter_params(  # pyright: ignore[reportPrivateUsage]
            query="test",
            publication_date_or_year="2020-01-01:2022-12-31",
        )
        assert "publicationDateOrYear" in params
        assert params["publicationDateOrYear"] == "2020-01-01:2022-12-31"

    @pytest.mark.asyncio
    async def test_api_key_required_error(self):
        """Test that methods requiring an API key raise ValueError when no API key is provided."""
        client = SemanticScholar(api_key=None)

        with pytest.raises(ValueError, match="API key is required for this operation"):
            await client.search_snippets("")


class TestDatasetAPI:
    """Tests for the dataset-related methods of the SemanticScholar class."""

    @pytest.mark.asyncio
    async def test_get_dataset_releases(self, mock_server_dataset_releases_response: list[str]):
        """Test getting a list of available dataset releases."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response_for_lists(mock_server_dataset_releases_response)

            result = await client.get_dataset_releases()

            # Check the URL
            mock_get.assert_called_once_with("https://api.semanticscholar.org/datasets/v1/release/")

            # Check the result
            assert isinstance(result, DatasetAvailableReleases)
            assert len(result) == 3
            assert result[0] == "2023-03-14"

    @pytest.mark.asyncio
    async def test_get_dataset_release(self, mock_server_dataset_release_response: dict[str, Any]):
        """Test getting information about a specific dataset release."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_dataset_release_response)

            result = await client.get_dataset_release_metadata("2023-03-28")

            # Check the URL
            mock_get.assert_called_once_with("https://api.semanticscholar.org/datasets/v1/release/2023-03-28")

            # Check the result
            assert isinstance(result, DatasetReleaseMetadata)
            assert result.release_id == "2023-03-28"
            assert len(result.datasets) == 2
            assert result.datasets[0].name == "abstracts"

    @pytest.mark.asyncio
    async def test_get_dataset_metadata(self, mock_server_dataset_metadata_response: dict[str, Any]):
        """Test getting metadata for a specific dataset within a release."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_dataset_metadata_response)

            result = await client.get_dataset_metadata("2023-03-28", "abstracts")

            # Check the URL
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/datasets/v1/release/2023-03-28/dataset/abstracts"
            )

            # Check the result
            assert isinstance(result, DatasetMetadata)
            assert result.name == "abstracts"
            assert len(result.files) == 2

    @pytest.mark.asyncio
    async def test_get_dataset_diffs(self, mock_server_dataset_diffs_response: dict[str, Any]):
        """Test getting diffs between dataset releases."""
        client = SemanticScholar(api_key="test-key")

        with patch.object(client.client, "get") as mock_get:
            mock_get.return_value = mock_api_response(mock_server_dataset_diffs_response)

            result = await client.get_dataset_diffs("2023-08-01", "2023-08-29", "papers")

            # Check the URL
            mock_get.assert_called_once_with(
                "https://api.semanticscholar.org/datasets/v1/diffs/2023-08-01/to/2023-08-29/papers"
            )

            # Check the result
            assert isinstance(result, DatasetDiffList)
            assert result.dataset == "papers"
            assert result.start_release == "2023-08-01"
            assert result.end_release == "2023-08-29"
            assert len(result.diffs) == 2
