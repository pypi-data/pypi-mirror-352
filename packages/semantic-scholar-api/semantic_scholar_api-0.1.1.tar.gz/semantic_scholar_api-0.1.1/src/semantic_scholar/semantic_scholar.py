import logging
from typing import Any

from semantic_scholar.api.clients import APIResponse, AsyncSemanticScholarClient
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
    PaperTitleSearchBatch,
    ReferenceBatch,
    SnippetSearchResponse,
)

logger = logging.getLogger(__name__)


class SemanticScholar:
    """Semantic Scholar API client."""

    base_url = "https://api.semanticscholar.org"
    graph_url = f"{base_url}/graph/v1"
    recommendations_url = f"{base_url}/recommendations/v1"
    datasets_url = f"{base_url}/datasets/v1"

    def __init__(self, api_key: str | None = None):
        self.client = AsyncSemanticScholarClient(api_key=api_key)

    @staticmethod
    def _prepare_fields_param(fields: list[str] | None = None) -> dict[str, Any]:
        """Prepare fields parameter for API requests."""
        if fields:
            return {"fields": ",".join(fields)}
        return {}

    def _ensure_api_key(self):
        if self.client.api_key is None:
            raise ValueError("API key is required for this operation")

    def _build_common_filter_params(
        self,
        query: str | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
        token: str | None = None,
        sort: str | None = None,
        paper_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Build a dictionary of common filter parameters for API requests.

        Args:
            query: Search query
            fields: Optional list of fields to include
            limit: Maximum number of results
            offset: Pagination offset
            publication_types: Filter by publication types
            open_access_pdf: Filter to only include papers with a public PDF
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study
            token: Continuation token for pagination
            sort: Sort field and direction
            paper_ids: Filter to specific papers

        Returns:
            Dictionary of parameters for API request
        """
        params: dict[str, Any] = {}

        if query is not None:
            params["query"] = query
        if fields is not None:
            params["fields"] = ",".join(fields)
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if publication_types is not None:
            params["publicationTypes"] = ",".join(publication_types)
        if open_access_pdf:
            params["openAccessPdf"] = ""  # Parameter does not accept values
        if min_citation_count is not None:
            params["minCitationCount"] = str(min_citation_count)
        if publication_date_or_year is not None:
            params["publicationDateOrYear"] = publication_date_or_year
        if year is not None:
            params["year"] = year
        if venue is not None:
            params["venue"] = ",".join(venue)
        if fields_of_study is not None:
            params["fieldsOfStudy"] = ",".join(fields_of_study)
        if token is not None:
            params["token"] = token
        if sort is not None:
            params["sort"] = sort
        if paper_ids is not None:
            params["paperIds"] = ",".join(paper_ids)

        return params

    async def _make_paginated_request(
        self,
        endpoint: str,
        offset: int = 0,
        limit: int = 100,
        fields: list[str] | None = None,
        additional_params: dict[str, Any] | None = None,
    ) -> APIResponse:
        """
        Make a paginated API request.

        Args:
            endpoint: API endpoint
            offset: Pagination offset
            limit: Maximum number of results
            fields: Optional list of fields to include
            additional_params: Additional query parameters

        Returns:
            Validated response data
        """
        params: dict[str, Any] = {
            "offset": offset,
            "limit": limit,
        }

        if fields:
            params["fields"] = ",".join(fields)

        if additional_params:
            params.update(additional_params)

        url = f"{self.graph_url}/{endpoint}"

        result = await self.client.get(url, params=params)
        return result

    async def _make_paper_search_request(
        self,
        endpoint: str,
        query: str,
        fields: list[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
        token: str | None = None,
        sort: str | None = None,
    ) -> APIResponse:
        """
        Make a paper search request with common filters.

        Args:
            endpoint: API endpoint
            query: Search query
            fields: Optional list of fields to include
            limit: Maximum number of results
            offset: Pagination offset
            publication_types: Filter by publication types
            open_access_pdf: Filter to only include papers with a public PDF
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study
            token: Continuation token for pagination
            sort: Sort field and direction

        Returns:
            Validated response data
        """
        params = self._build_common_filter_params(
            query=query,
            fields=fields,
            limit=limit,
            offset=offset,
            publication_types=publication_types,
            open_access_pdf=open_access_pdf,
            min_citation_count=min_citation_count,
            publication_date_or_year=publication_date_or_year,
            year=year,
            venue=venue,
            fields_of_study=fields_of_study,
            token=token,
            sort=sort,
        )

        url = f"{self.graph_url}/{endpoint}"

        return await self.client.get(url, params=params)

    async def autocomplete_paper(self, query: str) -> PaperAutocomplete:
        """
        Get paper query completions.

        Args:
            query: Partial search query string

        Returns:
            List of matching papers for autocomplete
        """
        params = {
            "query": query,
        }

        url = f"{self.graph_url}/paper/autocomplete"

        response = await self.client.get(url, params=params)
        return PaperAutocomplete.model_validate(response["data"])

    async def get_paper_batch(self, paper_ids: list[str], fields: list[str] | None = None) -> PaperSearchBatch:
        """
        Get a batch of papers by their IDs.

        Args:
            paper_ids: List of paper IDs
            fields: Optional list of fields to include

        Returns:
            Batch of papers
        """
        params = None
        if fields:
            params = {"fields": ",".join(fields)}

        url = f"{self.graph_url}/paper/batch"

        result = await self.client.post(url, params=params, json={"ids": paper_ids})
        return PaperSearchBatch.model_validate(result["data"])

    async def search_papers(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
        fields: list[str] | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
    ) -> PaperSearchBatch:
        """
        Search for papers.

        Args:
            query: Search query
            limit: Maximum number of results (default 10, max 100)
            offset: Pagination offset (default 0)
            fields: Optional list of fields to include
            publication_types: Filter by publication types (e.g., "Review", "JournalArticle")
            open_access_pdf: Filter to only include papers with a public PDF
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study

        Returns:
            Batch of paper search results
        """
        if fields is None:
            fields = ["title", "abstract", "isOpenAccess", "openAccessPdf"]

        result = await self._make_paper_search_request(
            endpoint="paper/search",
            query=query,
            fields=fields,
            limit=limit,
            offset=offset,
            publication_types=publication_types,
            open_access_pdf=open_access_pdf,
            min_citation_count=min_citation_count,
            publication_date_or_year=publication_date_or_year,
            year=year,
            venue=venue,
            fields_of_study=fields_of_study,
        )
        return PaperSearchBatch.model_validate(result["data"])

    async def search_papers_bulk(
        self,
        query: str,
        fields: list[str] | None = None,
        token: str | None = None,
        sort: str | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
    ) -> PaperBulkSearchBatch:
        """
        Bulk search for papers with advanced filtering.

        Args:
            query: Search query with boolean operators
            fields: Optional list of fields to include
            token: Continuation token for pagination
            sort: Sort field and direction (e.g., "publicationDate:asc")
            publication_types: Filter by publication types
            open_access_pdf: Filter to only include papers with a public PDF
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study

        Returns:
            Batch of paper search results with pagination token
        """
        result = await self._make_paper_search_request(
            endpoint="paper/search/bulk",
            query=query,
            fields=fields,
            token=token,
            sort=sort,
            publication_types=publication_types,
            open_access_pdf=open_access_pdf,
            min_citation_count=min_citation_count,
            publication_date_or_year=publication_date_or_year,
            year=year,
            venue=venue,
            fields_of_study=fields_of_study,
        )
        return PaperBulkSearchBatch.model_validate(result["data"])

    async def paper_title_search(
        self,
        query: str,
        fields: list[str] | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
    ) -> PaperTitleSearchBatch:
        """
        Search for the paper with the closest title match to the given query.

        Behaves similarly to search_papers, but is intended for retrieval of a single
        paper based on closest title match to given query.
        """
        result = await self._make_paper_search_request(
            endpoint="paper/search/match",
            query=query,
            fields=fields,
            publication_types=publication_types,
            open_access_pdf=open_access_pdf,
            min_citation_count=min_citation_count,
            publication_date_or_year=publication_date_or_year,
            year=year,
            venue=venue,
            fields_of_study=fields_of_study,
        )
        return PaperTitleSearchBatch.model_validate(result["data"])

    async def get_paper(self, paper_id: str, fields: list[str] | None = None) -> Paper:
        """
        Get paper details by ID.

        Args:
            paper_id: The paper identifier
            fields: Optional list of fields to include

        Returns:
            Paper data dictionary
        """
        params = self._prepare_fields_param(fields)
        url = f"{self.graph_url}/paper/{paper_id}"
        result = await self.client.get(url, params=params)
        return Paper.model_validate(result["data"])

    async def get_paper_authors(
        self, paper_id: str, offset: int = 0, limit: int = 100, fields: list[str] | None = None
    ) -> AuthorBatch:
        """
        Get authors of a specific paper.

        Args:
            paper_id: The paper identifier
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 100, max 1000)
            fields: Optional list of fields to include

        Returns:
            Batch of paper authors
        """
        result = await self._make_paginated_request(
            endpoint=f"paper/{paper_id}/authors",
            offset=offset,
            limit=limit,
            fields=fields,
        )
        return AuthorBatch.model_validate(result["data"])

    async def get_paper_citations(
        self, paper_id: str, offset: int = 0, limit: int = 100, fields: list[str] | None = None
    ) -> CitationBatch:
        """
        Get papers that cite the specified paper.

        Args:
            paper_id: The paper identifier
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 100, max 1000)
            fields: Optional list of fields to include

        Returns:
            Batch of papers citing the specified paper
        """
        result = await self._make_paginated_request(
            endpoint=f"paper/{paper_id}/citations",
            offset=offset,
            limit=limit,
            fields=fields,
        )
        return CitationBatch.model_validate(result["data"])

    async def get_paper_references(
        self, paper_id: str, offset: int = 0, limit: int = 100, fields: list[str] | None = None
    ) -> ReferenceBatch:
        """
        Get papers cited by the specified paper.

        Args:
            paper_id: The paper identifier
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 100, max 1000)
            fields: Optional list of fields to include

        Returns:
            Batch of papers referenced by the specified paper
        """
        result = await self._make_paginated_request(
            endpoint=f"paper/{paper_id}/references",
            offset=offset,
            limit=limit,
            fields=fields,
        )
        return ReferenceBatch.model_validate(result["data"])

    async def get_author_batch(self, author_ids: list[str], fields: list[str] | None = None) -> AuthorBatch:
        """
        Get authors by their IDs.

        Args:
            author_ids: List of author IDs
            fields: Optional list of fields to include

        Returns:
            Batch of authors
        """
        params = None
        if fields:
            params = {"fields": ",".join(fields)}

        url = f"{self.graph_url}/author/batch"

        result = await self.client.post(url, params=params, json={"ids": author_ids})
        return AuthorBatch.model_validate(result["data"])

    async def search_authors(
        self, query: str, offset: int = 0, limit: int = 100, fields: list[str] | None = None
    ) -> AuthorSearchBatch:
        """
        Search for authors by name.

        Args:
            query: Search query string
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 100, max 1000)
            fields: Optional list of fields to include

        Returns:
            Batch of author search results
        """
        params = {
            "query": query,
            "offset": offset,
            "limit": limit,
        }

        if fields:
            params["fields"] = ",".join(fields)

        url = f"{self.graph_url}/author/search"
        result = await self.client.get(url, params=params)
        return AuthorSearchBatch.model_validate(result["data"])

    async def get_author(self, author_id: str, fields: list[str] | None = None) -> Author:
        """
        Get author details by ID.

        Args:
            author_id: The author identifier
            fields: Optional list of fields to include

        Returns:
            Author details
        """
        params = self._prepare_fields_param(fields)
        url = f"{self.graph_url}/author/{author_id}"
        result = await self.client.get(url, params=params)
        return Author.model_validate(result["data"])

    async def get_author_papers(
        self, author_id: str, offset: int = 0, limit: int = 100, fields: list[str] | None = None
    ) -> PaperSearchBatch:
        """
        Get papers authored by a specific author.

        Args:
            author_id: The author identifier
            offset: Pagination offset (default 0)
            limit: Maximum number of results (default 100, max 1000)
            fields: Optional list of fields to include

        Returns:
            Batch of papers by the author
        """
        result = await self._make_paginated_request(
            endpoint=f"author/{author_id}/papers",
            offset=offset,
            limit=limit,
            fields=fields,
        )
        return PaperSearchBatch.model_validate(result["data"])

    async def search_snippets(
        self,
        query: str,
        limit: int = 10,
        fields: list[str] | None = None,
        paper_ids: list[str] | None = None,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
    ) -> SnippetSearchResponse:
        """
        Search for snippets.

        Args:
            query: Search query
            limit: Maximum number of results (default 10, max 1000)
            fields: Optional list of fields to include
            paper_ids: Filter to snippets from specific papers
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study

        Returns:
            Snippet search results
        """
        self._ensure_api_key()

        params = self._build_common_filter_params(
            query=query,
            limit=limit,
            fields=fields,
            paper_ids=paper_ids,
            min_citation_count=min_citation_count,
            publication_date_or_year=publication_date_or_year,
            year=year,
            venue=venue,
            fields_of_study=fields_of_study,
        )

        url = f"{self.graph_url}/snippet/search"
        result = await self.client.get(url, params=params)
        return SnippetSearchResponse.model_validate(result["data"])

    async def match_paper(
        self,
        query: str,
        fields: list[str] | None = None,
        publication_types: list[str] | None = None,
        open_access_pdf: bool = False,
        min_citation_count: int | None = None,
        publication_date_or_year: str | None = None,
        year: str | None = None,
        venue: list[str] | None = None,
        fields_of_study: list[str] | None = None,
    ) -> Paper:
        """
        Find a single paper based on closest title match.

        Args:
            query: Title search query
            fields: Optional list of fields to include
            publication_types: Filter by publication types
            open_access_pdf: Filter to only include papers with a public PDF
            min_citation_count: Filter to only include papers with the minimum number of citations
            publication_date_or_year: Filter by publication date range
            year: Filter by publication year range
            venue: Filter by publication venues
            fields_of_study: Filter by fields of study

        Returns:
            Best matching paper
        """
        psm: PaperTitleSearchBatch = await self.paper_title_search(
            query,
            fields,
            publication_types,
            open_access_pdf,
            min_citation_count,
            publication_date_or_year,
            year,
            venue,
            fields_of_study,
        )

        return await self.get_paper(psm.data[0].paperId, fields)

    async def get_recommendations_from_paper(
        self, paper_id: str, fields: list[str] | None = None
    ) -> PaperRecommendationBatch:
        """
        Get recommendations for a paper.

        Args:
            paper_id: The paper identifier
            fields: Optional list of fields to include

        Returns:
            Recommended papers data
        """

        params = {"fields": ",".join(fields)} if fields else None

        url = f"{self.recommendations_url}/papers/forpaper/{paper_id}"
        response = await self.client.get(url, params=params)
        return PaperRecommendationBatch.model_validate(response["data"])

    async def get_recommendations_from_paper_list(
        self,
        positive_paper_ids: list[str],
        negative_paper_ids: list[str],
        fields: list[str] | None = None,
        limit: int = 100,
    ) -> PaperRecommendationBatch:
        """
        Get recommendations for a list of papers.

        Args:
            positive_paper_ids: List of positive paper IDs
            negative_paper_ids: List of negative paper IDs
            fields: Optional list of fields to include
            limit: Maximum number of results (default 100, max 1000)

        Returns:
            Recommended papers data
        """
        data = {
            "positivePaperIds": positive_paper_ids,
            "negativePaperIds": negative_paper_ids,
        }

        params: dict[str, Any] = {
            "limit": limit,
        }

        if fields:
            params["fields"] = ",".join(fields)

        url = f"{self.recommendations_url}/papers"
        response = await self.client.post(url, params=params, json=data)
        return PaperRecommendationBatch.model_validate(response["data"])

    async def get_dataset_releases(self) -> DatasetAvailableReleases:
        """
        Get a list of available dataset releases.

        Releases are identified by a date stamp such as "2023-08-01".
        Each release contains full data for each dataset.

        Returns:
            List of release IDs in chronological order
        """
        url = f"{self.datasets_url}/release/"
        response = await self.client.get(url)
        return DatasetAvailableReleases.model_validate(response["data"])

    async def get_dataset_release_metadata(self, release_id: str) -> DatasetReleaseMetadata:
        """
        Get metadata about a specific dataset release.

        Args:
            release_id: ID of the release (e.g., "2023-08-01") or "latest" for the most recent release

        Returns:
            Release metadata including available datasets
        """
        self._ensure_api_key()
        url = f"{self.datasets_url}/release/{release_id}"
        response = await self.client.get(url)
        return DatasetReleaseMetadata.model_validate(response["data"])

    async def get_dataset_metadata(self, release_id: str, dataset_name: str) -> DatasetMetadata:
        """
        Get metadata and download links for a specific dataset within a release.

        Args:
            release_id: ID of the release (e.g., "2023-08-01") or "latest" for the most recent release
            dataset_name: Name of the dataset (e.g., "papers", "abstracts")

        Returns:
            Dataset metadata including pre-signed download links
        """
        self._ensure_api_key()
        url = f"{self.datasets_url}/release/{release_id}/dataset/{dataset_name}"
        response = await self.client.get(url)
        return DatasetMetadata.model_validate(response["data"])

    async def get_dataset_diffs(self, start_release_id: str, end_release_id: str, dataset_name: str) -> DatasetDiffList:
        """
        Get incremental diffs between dataset releases.

        This method returns links to files that contain changes needed to update a dataset
        from one release to another, avoiding the need to download the entire dataset again.

        Args:
            start_release_id: ID of the starting release (the release currently held)
            end_release_id: ID of the ending release or "latest" for the most recent release
            dataset_name: Name of the dataset (e.g., "papers", "abstracts")

        Returns:
            Diff metadata including update and delete file links
        """
        self._ensure_api_key()
        url = f"{self.datasets_url}/diffs/{start_release_id}/to/{end_release_id}/{dataset_name}"
        response = await self.client.get(url)
        return DatasetDiffList.model_validate(response["data"])
