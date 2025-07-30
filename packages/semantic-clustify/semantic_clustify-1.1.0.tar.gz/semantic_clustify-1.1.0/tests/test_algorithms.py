"""
Tests for clustering algorithms.
"""

import pytest
import numpy as np
from semantic_clustify.algorithms import (
    KMeansClusterer,
    DBSCANClusterer,
    HierarchicalClusterer,
    GMMClusterer,
)


@pytest.fixture
def sample_vectors():
    """Sample vectors for testing."""
    # Create two clear clusters
    np.random.seed(42)
    cluster1 = np.random.normal([0, 0], 0.1, (20, 2))
    cluster2 = np.random.normal([2, 2], 0.1, (20, 2))
    return np.vstack([cluster1, cluster2])


@pytest.mark.kmeans
def test_kmeans_clustering(sample_vectors):
    """Test KMeans clustering algorithm."""
    clusterer = KMeansClusterer(n_clusters=2, random_state=42)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    assert len(np.unique(labels)) == 2

    # Test prediction on new data
    new_vectors = np.array([[0.1, 0.1], [1.9, 1.9]])
    new_labels = clusterer.predict(new_vectors)
    assert len(new_labels) == 2


@pytest.mark.kmeans
def test_kmeans_auto_clusters(sample_vectors):
    """Test KMeans with automatic cluster detection."""
    clusterer = KMeansClusterer(n_clusters="auto", max_clusters=5, random_state=42)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    n_clusters = len(np.unique(labels))
    assert 2 <= n_clusters <= 5


@pytest.mark.dbscan
def test_dbscan_clustering(sample_vectors):
    """Test DBSCAN clustering algorithm."""
    clusterer = DBSCANClusterer(eps=0.3, min_samples=3)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    # DBSCAN can have noise points (-1)
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    assert n_clusters >= 0


@pytest.mark.dbscan
def test_dbscan_auto_params(sample_vectors):
    """Test DBSCAN with automatic parameter estimation."""
    clusterer = DBSCANClusterer()  # No parameters provided
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    params = clusterer.get_params()
    assert "eps" in params
    assert "min_samples" in params


@pytest.mark.hierarchical
def test_hierarchical_clustering(sample_vectors):
    """Test hierarchical clustering algorithm."""
    clusterer = HierarchicalClusterer(n_clusters=2)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    assert len(np.unique(labels)) == 2


@pytest.mark.hierarchical
def test_hierarchical_distance_threshold(sample_vectors):
    """Test hierarchical clustering with distance threshold."""
    clusterer = HierarchicalClusterer(distance_threshold=1.0)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    n_clusters = len(np.unique(labels))
    assert n_clusters >= 1


@pytest.mark.gmm
def test_gmm_clustering(sample_vectors):
    """Test Gaussian Mixture Model clustering."""
    clusterer = GMMClusterer(n_clusters=2, random_state=42)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    assert len(np.unique(labels)) == 2

    # Test prediction on new data
    new_vectors = np.array([[0.1, 0.1], [1.9, 1.9]])
    new_labels = clusterer.predict(new_vectors)
    assert len(new_labels) == 2

    # Test probability prediction
    proba = clusterer.predict_proba(new_vectors)
    assert proba.shape == (2, 2)
    assert np.allclose(proba.sum(axis=1), 1.0)  # Probabilities should sum to 1


@pytest.mark.gmm
def test_gmm_auto_components(sample_vectors):
    """Test GMM with automatic component detection."""
    clusterer = GMMClusterer(n_clusters="auto", max_clusters=5, random_state=42)
    labels = clusterer.fit_predict(sample_vectors)

    assert len(labels) == len(sample_vectors)
    n_clusters = len(np.unique(labels))
    assert 2 <= n_clusters <= 5


@pytest.mark.performance
def test_algorithm_parameters():
    """Test that all algorithms return proper parameters."""
    vectors = np.random.random((10, 3))

    algorithms = [
        KMeansClusterer(n_clusters=2),
        DBSCANClusterer(eps=0.5, min_samples=2),
        HierarchicalClusterer(n_clusters=2),
        GMMClusterer(n_clusters=2),
    ]

    for algorithm in algorithms:
        labels = algorithm.fit_predict(vectors)
        params = algorithm.get_params()

        assert isinstance(params, dict)
        assert "algorithm" in params
        assert len(labels) == len(vectors)


@pytest.mark.core
def test_edge_cases():
    """Test edge cases for clustering algorithms."""
    # Very small dataset
    small_vectors = np.array([[0, 0], [1, 1]])

    # Should work with minimum data
    clusterer = KMeansClusterer(n_clusters=2)
    labels = clusterer.fit_predict(small_vectors)
    assert len(labels) == 2

    # Single cluster case
    same_vectors = np.array([[0, 0], [0, 0], [0, 0]])
    clusterer = DBSCANClusterer(eps=0.1, min_samples=2)
    labels = clusterer.fit_predict(same_vectors)
    assert len(labels) == 3
