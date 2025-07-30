"""
Basic smoke tests for semantic-clustify.

These tests verify that the basic functionality works correctly
and that imports are properly configured.
"""

import pytest
import numpy as np
from semantic_clustify import SemanticClusterer
from semantic_clustify.algorithms import (
    KMeansClusterer,
    DBSCANClusterer,
    HierarchicalClusterer,
    GMMClusterer,
)
from semantic_clustify.utils import validate_input_data, extract_vectors


@pytest.mark.smoke
def test_import():
    """Test that we can import the main classes."""
    assert SemanticClusterer is not None
    assert KMeansClusterer is not None
    assert DBSCANClusterer is not None


@pytest.mark.smoke
def test_clusterer_creation():
    """Test basic clusterer creation."""
    clusterer = SemanticClusterer(method="kmeans")
    assert clusterer is not None
    assert clusterer.method == "kmeans"


@pytest.mark.quick
def test_supported_methods():
    """Test that all supported methods are available."""
    expected_methods = ["kmeans", "dbscan", "hierarchical", "gmm"]

    for method in expected_methods:
        clusterer = SemanticClusterer(method=method)
        assert clusterer.method == method


@pytest.mark.quick
def test_invalid_method():
    """Test that invalid methods raise errors."""
    with pytest.raises(ValueError):
        SemanticClusterer(method="invalid_method")


@pytest.mark.core
def test_basic_clustering():
    """Test basic clustering functionality."""
    # Sample data with vectors
    data = [
        {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
        {"title": "Doc 2", "embedding": [0.15, 0.25, 0.35]},
        {"title": "Doc 3", "embedding": [0.8, 0.1, 0.2]},
        {"title": "Doc 4", "embedding": [0.85, 0.15, 0.25]},
    ]

    clusterer = SemanticClusterer(method="kmeans", n_clusters=2)
    clusters = clusterer.fit_predict(data, vector_field="embedding")

    assert isinstance(clusters, list)
    assert len(clusters) <= 2  # Should have at most 2 clusters
    assert sum(len(cluster) for cluster in clusters) == len(data)

    # Check that cluster_id is added to documents
    for cluster in clusters:
        for doc in cluster:
            assert "cluster_id" in doc
            assert isinstance(doc["cluster_id"], int)


@pytest.mark.core
def test_validation():
    """Test input data validation."""
    # Valid data
    valid_data = [
        {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
        {"title": "Doc 2", "embedding": [0.15, 0.25, 0.35]},
    ]

    # Should not raise
    validate_input_data(valid_data, "embedding")

    # Invalid data - empty
    with pytest.raises(ValueError):
        validate_input_data([], "embedding")

    # Invalid data - missing field
    invalid_data = [{"title": "Doc 1"}]
    with pytest.raises(ValueError):
        validate_input_data(invalid_data, "embedding")

    # Invalid data - inconsistent dimensions
    inconsistent_data = [
        {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
        {"title": "Doc 2", "embedding": [0.15, 0.25]},  # Different dimension
    ]
    with pytest.raises(ValueError):
        validate_input_data(inconsistent_data, "embedding")


@pytest.mark.core
def test_vector_extraction():
    """Test vector extraction functionality."""
    data = [
        {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
        {"title": "Doc 2", "embedding": [0.15, 0.25, 0.35]},
    ]

    vectors = extract_vectors(data, "embedding")

    assert isinstance(vectors, np.ndarray)
    assert vectors.shape == (2, 3)
    # Allow both float32 and float64 as they're both valid
    assert vectors.dtype in [np.float32, np.float64]


@pytest.mark.core
def test_quality_metrics():
    """Test quality metrics calculation."""
    data = [
        {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
        {"title": "Doc 2", "embedding": [0.15, 0.25, 0.35]},
        {"title": "Doc 3", "embedding": [0.8, 0.1, 0.2]},
        {"title": "Doc 4", "embedding": [0.85, 0.15, 0.25]},
    ]

    clusterer = SemanticClusterer(method="kmeans", n_clusters=2)
    clusters = clusterer.fit_predict(data, vector_field="embedding")

    metrics = clusterer.get_quality_metrics()

    assert isinstance(metrics, dict)
    assert "n_clusters" in metrics
    assert "silhouette_score" in metrics
    assert "n_samples" in metrics

    # Should have valid silhouette score for this data
    if metrics["silhouette_score"] is not None:
        assert -1 <= metrics["silhouette_score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__])
