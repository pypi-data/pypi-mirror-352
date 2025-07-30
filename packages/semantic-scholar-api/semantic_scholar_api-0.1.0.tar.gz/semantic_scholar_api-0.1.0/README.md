# Semantic Scholar Python Client

A Python client for the [Semantic Scholar API](https://www.semanticscholar.org/product/api).

## Installation

```bash
pip install semantic-scholar-api
```

## Quick Start

```python
from semantic_scholar import SemanticScholar

# Initialize client (API key optional for basic usage)
client = SemanticScholar(api_key="your-api-key")

# Search for papers
papers = await client.search_papers("machine learning", limit=10)

# Get paper details
paper = await client.get_paper("paper-id")
```

## Features

- Async/await support
- Comprehensive API coverage
- Type hints throughout
- Robust error handling
- Rate limiting built-in
