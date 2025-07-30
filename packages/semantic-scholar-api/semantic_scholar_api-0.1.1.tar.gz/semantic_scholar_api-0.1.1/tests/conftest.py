from typing import Any

import pytest

# Disable long lines check for this file
# ruff: noqa: E501


@pytest.fixture(scope="class")
def mock_server_paper_response() -> dict[str, Any]:
    """Raw server response for single paper endpoint."""
    return {
        "paperId": "p123456",
        "corpusId": 7890123,
        "externalIds": {
            "DOI": "10.1007/978-3-319-96417-9_1",
            "ArXiv": "1234.56789",
        },
        "url": "https://example.org/papers/p123456/open-access.pdf",
        "title": "Advances in Machine Learning Theory",
        "abstract": "We describe a deployed scalable system for organizing published scientific literature...",
        "venue": "International Conference on Machine Learning",
        "publicationVenue": {
            "id": "v123456",
            "name": "International Conference on Machine Learning",
            "type": "conference",
            "alternate_names": ["ICML", "Intl. Conf. on ML"],
            "url": "https://example.org/conferences/icml",
        },
        "year": 2018,
        "referenceCount": 35,
        "citationCount": 12,
        "influentialCitationCount": 10,
        "isOpenAccess": True,
        "openAccessPdf": {
            "url": "https://example.org/papers/p123456/open-access.pdf",
            "status": "GREEN",
        },
        "fieldsOfStudy": ["Computer Science"],
        "s2FieldsOfStudy": [
            {"category": "Computer Science", "source": "external"},
            {"category": "Computer Science", "source": "s2-fos-model"},
            {"category": "Mathematics", "source": "s2-fos-model"},
        ],
        "publicationTypes": ["Review", "Journal Article"],
        "publicationDate": "2018-06-01",
        "journal": {
            "name": "Journal of Artificial Intelligence Research",
            "volume": "42",
            "pages": "123-145",
        },
        "citationStyles": {
            "bibtex": "@article{smith2018advances, title={Advances in Machine Learning Theory}, author={Smith, Jane}}"
        },
        "authors": [{"authorId": "a12345", "name": "Jane Smith"}, {"authorId": "a67890", "name": "John Doe"}],
        "citations": [
            {
                "paperId": "p234567",
                "title": "An Overview of Machine Learning Methods",
                "year": 2019,
                "authors": [{"authorId": "a23456", "name": "Alice Johnson"}],
            }
        ],
        "references": [
            {
                "paperId": "p7891011",
                "title": "Foundations of Deep Learning",
                "year": 2017,
                "authors": [{"authorId": "a34567", "name": "Bob Williams"}],
            },
        ],
        "embedding": {
            "model": "sample-embedding-model@v1.0",
            "vector": [0.1, -0.2, 0.3, -0.4, 0.5],
        },
        "tldr": {
            "model": "tldr-model@v1.0",
            "text": "This paper introduces a new approach to machine learning that improves accuracy.",
        },
    }


@pytest.fixture(scope="class")
def mock_server_author_response() -> dict[str, Any]:
    """Raw server response for single author endpoint."""
    return {
        "authorId": "a12345",
        "externalIds": {
            "GoogleScholar": ["1234567890"],
        },
        "url": "https://example.org/author/a12345",
        "name": "Jane Smith",
        "affiliations": ["Sample University"],
        "paperCount": 300,
        "citationCount": 34803,
        "hIndex": 86,
        "papers": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "year": 2018,
                "authors": [
                    {"authorId": "a12345", "name": "Jane Smith"},
                    {"authorId": "a67890", "name": "John Doe"},
                ],
            },
            {"paperId": "p789012", "title": "Neural Network Applications", "year": 2021},
        ],
    }


@pytest.fixture
def mock_server_author_papers_response() -> dict[str, Any]:
    """Raw server response for author papers endpoint."""
    return {
        "offset": 0,
        "next": 10,
        "data": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "year": 2018,
                "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
            },
            {
                "paperId": "p789012",
                "title": "Neural Network Applications",
                "year": 2019,
                "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
            },
        ],
    }


@pytest.fixture
def mock_server_paper_search_response() -> dict[str, Any]:
    """Raw server response for paper search endpoint."""
    return {
        "total": 15117,
        "offset": 0,
        "next": 10,
        "data": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "abstract": "We describe a deployed scalable system...",
                "year": 2018,
                "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
            },
            {
                "paperId": "p789012",
                "title": "Neural Network Applications",
                "abstract": "Another abstract...",
                "year": 2019,
                "authors": [{"authorId": "a67890", "name": "John Doe"}],
            },
        ],
    }


@pytest.fixture
def mock_server_paper_title_search_response() -> dict[str, Any]:
    """Raw server response for paper title search endpoint."""
    return {"data": [{"paperId": "p123456", "title": "Advances in Machine Learning Theory", "matchScore": 174.2298}]}


@pytest.fixture
def mock_server_author_search_response() -> dict[str, Any]:
    """Raw server response for author search endpoint."""
    return {
        "total": 490,
        "offset": 0,
        "next": 10,
        "data": [
            {
                "authorId": "a12345",
                "name": "Jane Smith",
                "url": "https://example.org/author/a12345",
                "paperCount": 300,
                "citationCount": 34803,
                "hIndex": 86,
                "papers": [{"paperId": "p123456", "title": "Advances in Machine Learning Theory"}],
            },
            {
                "authorId": "a67890",
                "name": "John Doe",
                "url": "https://example.org/author/a67890",
                "paperCount": 280,
                "citationCount": 35526,
                "hIndex": 89,
            },
        ],
    }


@pytest.fixture
def mock_server_paper_autocomplete_response() -> dict[str, Any]:
    """Raw server response for paper autocomplete endpoint."""
    return {
        "matches": [
            {
                "id": "p123456",
                "title": "Advances in Machine Learning Theory",
                "authorsYear": "Smith et al., 2018",
            },
            {
                "id": "p789012",
                "title": "Neural Network Applications",
                "authorsYear": "Doe et al., 2019",
            },
        ]
    }


@pytest.fixture
def mock_server_paper_bulk_search_response() -> dict[str, Any]:
    """Raw server response for paper bulk search endpoint."""
    return {
        "total": 15117,
        "token": "NEXT_PAGE_TOKEN",
        "data": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "year": 2018,
            },
            {"paperId": "p789012", "title": "Neural Network Applications", "year": 2019},
        ],
    }


@pytest.fixture
def mock_server_paper_citations_response() -> dict[str, Any]:
    """Raw server response for paper citations endpoint."""
    return {
        "offset": 0,
        "next": 10,
        "total": 25,
        "data": [
            {
                "contexts": ["...as shown by Smith (2018)..."],
                "intents": ["methodology"],
                "isInfluential": True,
                "citingPaper": {"paperId": "p234567", "title": "An Overview of Machine Learning Methods", "year": 2019},
            },
            {
                "contexts": ["...building on the work of Smith et al. (2018)..."],
                "intents": ["background"],
                "isInfluential": False,
                "citingPaper": {"paperId": "p345678", "title": "Citing Paper 2", "year": 2020},
            },
        ],
    }


@pytest.fixture
def mock_server_paper_references_response() -> dict[str, Any]:
    """Raw server response for paper references endpoint."""
    return {
        "offset": 0,
        "next": 10,
        "total": 35,
        "data": [
            {
                "contexts": ["...as described by Johnson (2015)..."],
                "intents": ["background"],
                "isInfluential": True,
                "citedPaper": {"paperId": "p456789", "title": "Referenced Paper 1", "year": 2015},
            },
            {
                "contexts": ["...using methods from Williams (2016)..."],
                "intents": ["methodology"],
                "isInfluential": False,
                "citedPaper": {"paperId": "p567890", "title": "Referenced Paper 2", "year": 2016},
            },
        ],
    }


@pytest.fixture
def mock_server_paper_authors_response() -> dict[str, Any]:
    """Raw server response for paper authors endpoint."""
    return {
        "offset": 0,
        "next": 10,
        "data": [
            {"authorId": "a12345", "name": "Jane Smith", "affiliations": ["Sample University"]},
            {"authorId": "a67890", "name": "John Doe", "affiliations": ["Research Institute"]},
        ],
    }


@pytest.fixture(scope="class")
def mock_server_snippet_search_response() -> dict[str, Any]:
    """Raw server response for snippet search endpoint."""
    return {
        "data": [
            {
                "snippet": {
                    "text": "In this paper, we discuss the construction of a graph...",
                    "snippetKind": "body",
                    "section": "Introduction",
                    "snippetOffset": {"start": 24506, "end": 25694},
                    "annotations": {
                        "sentences": [{"start": 0, "end": 120}],
                        "refMentions": [{"start": 377, "end": 402, "matchedPaperCorpusId": "7377848"}],
                    },
                },
                "score": 0.562,
                "paper": {
                    "corpusId": "123456",
                    "title": "Advances in Machine Learning Theory",
                    "authors": ["Jane Smith", "John Doe"],
                    "openAccessInfo": {
                        "license": "CC-BY",
                        "status": "GREEN",
                        "disclaimer": "Notice: This snippet is extracted from the open access paper or abstract available at https://arxiv.org/abs/1805.02262, which is subject to the license by the author or copyright owner provided with this content. Please go to the source to verify the license and copyright information for your use.",
                    },
                },
            }
        ],
        "retrievalVersion": "v1.0",
    }


@pytest.fixture
def mock_server_paper_batch_response() -> list[dict[str, Any]]:
    """Raw server response for paper batch endpoint."""
    return [
        {
            "paperId": "p123456",
            "title": "Advances in Machine Learning Theory",
            "abstract": "We describe a deployed scalable system...",
            "year": 2018,
            "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
        },
        {
            "paperId": "p789012",
            "title": "Neural Network Applications",
            "abstract": "Another abstract...",
            "year": 2019,
            "authors": [{"authorId": "a67890", "name": "John Doe"}],
        },
    ]


@pytest.fixture
def mock_server_author_batch_response() -> list[dict[str, Any]]:
    """Raw server response for author batch endpoint."""
    return [
        {
            "authorId": "a12345",
            "name": "Jane Smith",
            "url": "https://example.org/author/a12345",
            "paperCount": 300,
            "citationCount": 34803,
            "hIndex": 86,
        },
        {
            "authorId": "a67890",
            "name": "John Doe",
            "url": "https://example.org/author/a67890",
            "paperCount": 280,
            "citationCount": 35526,
            "hIndex": 89,
        },
    ]


@pytest.fixture
def mock_server_paper_recommendations_response() -> dict[str, Any]:
    """Raw server response for paper recommendations endpoint."""
    return {
        "recommendedPapers": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "year": 2018,
                "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
            },
            {
                "paperId": "p789012",
                "title": "Neural Network Applications",
                "year": 2019,
                "authors": [{"authorId": "a67890", "name": "John Doe"}],
            },
        ]
    }


@pytest.fixture
def mock_server_paper_list_recommendations_response() -> dict[str, Any]:
    """Raw server response for paper list recommendations endpoint."""
    return {
        "recommendedPapers": [
            {
                "paperId": "p123456",
                "title": "Advances in Machine Learning Theory",
                "year": 2018,
                "authors": [{"authorId": "a12345", "name": "Jane Smith"}],
            },
            {
                "paperId": "p789012",
                "title": "Neural Network Applications",
                "year": 2019,
                "authors": [{"authorId": "a67890", "name": "John Doe"}],
            },
        ]
    }


@pytest.fixture
def mock_server_dataset_releases_response() -> list[str]:
    """Raw server response for dataset releases endpoint."""
    return ["2023-03-14", "2023-03-21", "2023-03-28"]


@pytest.fixture
def mock_server_dataset_release_response() -> dict[str, Any]:
    """Raw server response for dataset release endpoint."""
    return {
        "release_id": "2023-03-28",
        "README": "Subject to the following terms of use...",
        "datasets": [
            {
                "name": "abstracts",
                "description": "Paper abstract text, where available. 100M records in 30 1.8GB files.",
                "README": 'Semantic Scholar Academic Graph Datasets The "abstracts" dataset provides...',
            },
            {
                "name": "papers",
                "description": "Core paper metadata",
                "README": "This dataset contains comprehensive metadata for research papers...",
            },
        ],
    }


@pytest.fixture
def mock_server_dataset_metadata_response() -> dict[str, Any]:
    """Raw server response for dataset metadata endpoint."""
    return {
        "name": "abstracts",
        "description": "Paper abstract text, where available. 100M records in 30 1.8GB files.",
        "README": "Subject to terms of use as follows...",
        "files": [
            "https://example-bucket.s3.amazonaws.com/datasets/2023-03-28/abstracts/20230331_0.jsonl.gz",
            "https://example-bucket.s3.amazonaws.com/datasets/2023-03-28/abstracts/20230331_1.jsonl.gz",
        ],
    }


@pytest.fixture
def mock_server_dataset_diffs_response() -> dict[str, Any]:
    """Raw server response for dataset diffs endpoint."""
    return {
        "dataset": "papers",
        "start_release": "2023-08-01",
        "end_release": "2023-08-29",
        "diffs": [
            {
                "from_release": "2023-08-01",
                "to_release": "2023-08-07",
                "update_files": [
                    "https://example-bucket.s3.amazonaws.com/diffs/2023-08-01/to/2023-08-07/papers/updates_1.jsonl.gz",
                    "https://example-bucket.s3.amazonaws.com/diffs/2023-08-01/to/2023-08-07/papers/updates_2.jsonl.gz",
                ],
                "delete_files": [
                    "https://example-bucket.s3.amazonaws.com/diffs/2023-08-01/to/2023-08-07/papers/deletes_1.jsonl.gz"
                ],
            },
            {
                "from_release": "2023-08-07",
                "to_release": "2023-08-14",
                "update_files": [
                    "https://example-bucket.s3.amazonaws.com/diffs/2023-08-07/to/2023-08-14/papers/updates_1.jsonl.gz"
                ],
                "delete_files": [],
            },
        ],
    }
