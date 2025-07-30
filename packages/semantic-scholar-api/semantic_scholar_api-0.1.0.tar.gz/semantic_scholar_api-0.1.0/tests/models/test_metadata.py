"""Tests for the dataset models."""

import pytest

from semantic_scholar.models.dataset import (
    DatasetAvailableReleases,
    DatasetDiff,
    DatasetDiffList,
    DatasetMetadata,
    DatasetReleaseMetadata,
    DatasetSummary,
)


class TestDatasetAvailableReleases:
    """Tests for the DatasetAvailableReleases model."""

    def test_initialization(self):
        """Test initialization and properties."""
        releases = DatasetAvailableReleases(data=["2023-01-01", "2023-02-01", "2023-03-01"])

        assert len(releases) == 3
        assert releases[0] == "2023-01-01"
        assert releases[1] == "2023-02-01"
        assert releases[2] == "2023-03-01"
        assert releases.most_recent() == "2023-03-01"

        # Test representation
        repr_str = repr(releases)
        assert "most_recent=2023-03-01" in repr_str
        assert "num_releases=3" in repr_str

    def test_empty_releases(self):
        """Test with empty releases list."""
        with pytest.raises(IndexError):
            DatasetAvailableReleases(data=[]).most_recent()


class TestDatasetSummary:
    """Tests for the DatasetSummary model."""

    def test_initialization(self):
        """Test initialization with all fields."""
        summary = DatasetSummary(
            name="papers",
            description="Core paper metadata",
            README="This dataset contains comprehensive metadata for research papers...",
        )

        assert summary.name == "papers"
        assert summary.description == "Core paper metadata"
        assert summary.README == "This dataset contains comprehensive metadata for research papers..."

        # Test representation
        repr_str = repr(summary)
        assert "name=papers" in repr_str
        assert "description=Core paper metadata" in repr_str

    def test_minimal_initialization(self):
        """Test initialization with only required fields."""
        summary = DatasetSummary(name="papers", description="Core paper metadata")

        assert summary.name == "papers"
        assert summary.description == "Core paper metadata"
        assert summary.README is None


class TestDatasetReleaseMetadata:
    """Tests for the DatasetReleaseMetadata model."""

    def test_initialization(self):
        """Test initialization with all fields."""
        dataset_summary1 = DatasetSummary(name="papers", description="Core paper metadata")
        dataset_summary2 = DatasetSummary(name="abstracts", description="Paper abstract text")

        metadata = DatasetReleaseMetadata(
            release_id="2023-03-28",
            README="Subject to the following terms of use...",
            datasets=[dataset_summary1, dataset_summary2],
        )

        assert metadata.release_id == "2023-03-28"
        assert metadata.README == "Subject to the following terms of use..."
        assert len(metadata.datasets) == 2
        assert metadata.datasets[0].name == "papers"
        assert metadata.datasets[1].name == "abstracts"

        # Test dictionary access
        assert metadata["papers"].description == "Core paper metadata"
        assert metadata["abstracts"].description == "Paper abstract text"

        # Test error on missing dataset
        with pytest.raises(KeyError):
            metadata["nonexistent"]

        # Test representation
        repr_str = repr(metadata)
        assert "release_id=2023-03-28" in repr_str
        assert "datasets=['papers', 'abstracts']" in repr_str

        # Test string representation
        str_output = str(metadata)
        assert "Dataset Release: 2023-03-28" in str_output
        assert "Datasets:" in str_output
        assert "  papers" in str_output
        assert "  abstracts" in str_output


class TestDatasetMetadata:
    """Tests for the DatasetMetadata model."""

    def test_initialization(self):
        """Test initialization with all fields."""
        metadata = DatasetMetadata(
            name="abstracts",
            description="Paper abstract text, where available.",
            README="Subject to terms of use as follows...",
            files=[
                "https://example-bucket.s3.amazonaws.com/files/1.jsonl.gz",
                "https://example-bucket.s3.amazonaws.com/files/2.jsonl.gz",
            ],
        )

        assert metadata.name == "abstracts"
        assert metadata.description == "Paper abstract text, where available."
        assert metadata.README == "Subject to terms of use as follows..."
        assert len(metadata.files) == 2

        # Test representation
        repr_str = repr(metadata)
        assert "name=abstracts" in repr_str
        assert "files=2" in repr_str

        # Test string representation
        str_output = str(metadata)
        assert "Dataset: abstracts [num_files=2]" in str_output
        assert "Description: Paper abstract text" in str_output


class TestDatasetDiff:
    """Tests for the DatasetDiff model."""

    def test_initialization(self):
        """Test initialization with all fields."""
        diff = DatasetDiff(
            from_release="2023-08-01",
            to_release="2023-08-07",
            update_files=[
                "https://example-bucket.s3.amazonaws.com/diffs/updates_1.jsonl.gz",
                "https://example-bucket.s3.amazonaws.com/diffs/updates_2.jsonl.gz",
            ],
            delete_files=["https://example-bucket.s3.amazonaws.com/diffs/deletes_1.jsonl.gz"],
        )

        assert diff.from_release == "2023-08-01"
        assert diff.to_release == "2023-08-07"
        assert len(diff.update_files) == 2
        assert len(diff.delete_files) == 1


class TestDatasetDiffList:
    """Tests for the DatasetDiffList model."""

    def test_initialization(self):
        """Test initialization with all fields."""
        diff1 = DatasetDiff(
            from_release="2023-08-01",
            to_release="2023-08-07",
            update_files=["https://example.com/update1.jsonl.gz"],
            delete_files=["https://example.com/delete1.jsonl.gz"],
        )

        diff2 = DatasetDiff(
            from_release="2023-08-07",
            to_release="2023-08-14",
            update_files=["https://example.com/update2.jsonl.gz"],
            delete_files=[],
        )

        diff_list = DatasetDiffList(
            dataset="papers", start_release="2023-08-01", end_release="2023-08-14", diffs=[diff1, diff2]
        )

        assert diff_list.dataset == "papers"
        assert diff_list.start_release == "2023-08-01"
        assert diff_list.end_release == "2023-08-14"
        assert len(diff_list.diffs) == 2
