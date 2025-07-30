"""Dataset-related models for the Semantic Scholar API client."""

from typing import Any

from semantic_scholar.models.base import BaseModel


class DatasetAvailableReleases(BaseModel):
    """Information about available dataset releases."""

    data: list[str]
    """List of available releases."""

    def most_recent(self) -> str:
        """Most recent release."""
        return self.data[-1]

    def __getitem__(self, index: int) -> str:
        """Get a release by index."""
        return self.data[index]

    def __len__(self) -> int:
        """Length of the list of releases."""
        return len(self.data)

    def __repr__(self) -> str:
        """Representation of the list of releases."""
        return f"DatasetAvailableReleases(most_recent={self.most_recent()}, num_releases={len(self)})"


class DatasetSummary(BaseModel):
    """Summary information about a dataset within a release."""

    name: str
    """Dataset name, e.g., 'papers'."""

    description: str
    """Description of the data contained in the dataset."""

    README: str | None = None
    """Documentation and attribution for the dataset."""

    def __repr__(self) -> str:
        """Representation of the dataset summary."""
        return f"DatasetSummary(name={self.name}, description={self.description})"


class DatasetReleaseMetadata(BaseModel):
    """Metadata about a dataset release."""

    release_id: str
    """Release ID in the form of a date stamp, e.g., '2022-01-17'."""

    README: str | None = None
    """License and usage information."""

    datasets: list[DatasetSummary]
    """List of datasets available in this release."""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._datasets_by_name = {dataset.name: dataset for dataset in self.datasets}

    def __getitem__(self, key: str) -> DatasetSummary:
        """Get a dataset by key."""
        if key not in self._datasets_by_name:
            raise KeyError(f"Dataset {key} not found")
        return self._datasets_by_name[key]

    def __repr__(self) -> str:
        """Representation of the dataset release metadata."""
        return f"DatasetReleaseMetadata(release_id={self.release_id}, datasets={list(self._datasets_by_name.keys())})"

    def __str__(self) -> str:
        """String representation of the dataset release metadata."""
        text = f"Dataset Release: {self.release_id}\n"
        text += f"README: {self.README}\n\n"
        text += "Datasets:\n"
        for dataset in self.datasets:
            text += f"  {dataset.name}\n"
        return text


class DatasetMetadata(BaseModel):
    """Metadata and download links for a specific dataset."""

    name: str
    """Name of the dataset."""

    description: str
    """Description of the data contained in this dataset."""

    README: str | None = None
    """License and usage information."""

    files: list[str]
    """Temporary, pre-signed download links for dataset files."""

    def __repr__(self) -> str:
        """Representation of the dataset metadata."""
        return f"DatasetMetadata(name={self.name}, files={len(self.files)})"

    def __str__(self) -> str:
        """String representation of the dataset metadata."""
        text = f"Dataset: {self.name} [num_files={len(self.files)}]\n"
        text += f"Description: {self.description}\n\n"
        text += f"README: {self.README}\n\n"
        return text


class DatasetDiff(BaseModel):
    """Diff information between two sequential releases for a dataset."""

    from_release: str
    """Baseline release for this diff."""

    to_release: str
    """Target release for this diff."""

    update_files: list[str]
    """List of files that contain updates to be inserted or updated."""

    delete_files: list[str]
    """List of files that contain records to be deleted."""


class DatasetDiffList(BaseModel):
    """List of diffs required to update a dataset between releases."""

    dataset: str
    """Dataset name these diffs are for."""

    start_release: str
    """Beginning release currently held by the client."""

    end_release: str
    """Ending release the client wants to update to."""

    diffs: list[DatasetDiff]
    """List of diffs needed to bring the dataset up to date."""
