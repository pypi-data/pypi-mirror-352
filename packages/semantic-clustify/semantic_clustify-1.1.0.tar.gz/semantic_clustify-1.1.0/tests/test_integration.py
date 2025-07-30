"""
Integration tests for semantic-clustify.

These tests verify that different components work together correctly
and that the complete clustering workflow functions as expected.
"""

import pytest
import numpy as np
import json
import tempfile
from pathlib import Path

from semantic_clustify import SemanticClusterer
from semantic_clustify.utils import save_jsonl, load_jsonl


class TestClusteringWorkflow:
    """Test complete clustering workflows."""

    def test_end_to_end_clustering(self, sample_documents, temp_jsonl_file):
        """Test complete clustering workflow from file to results."""
        # Load data
        data = load_jsonl(temp_jsonl_file)
        assert len(data) == len(sample_documents)

        # Create clusterer
        clusterer = SemanticClusterer(method="kmeans", n_clusters=3)

        # Perform clustering
        clustered_data = clusterer.fit_predict(data)

        # Verify results
        assert isinstance(clustered_data, list)
        assert len(clustered_data) > 0

        # Check that we have clusters
        total_docs = sum(len(cluster) for cluster in clustered_data)
        assert total_docs <= len(data)  # Some docs might be noise in DBSCAN

        # Check that metrics are available
        assert hasattr(clusterer, "quality_metrics_")
        assert "silhouette_score" in clusterer.quality_metrics_

    def test_clustering_with_all_algorithms(self, sample_documents, all_algorithms):
        """Test that all algorithms can process the same data."""
        # Skip DBSCAN for this simple test as it might not find clusters
        if all_algorithms == "dbscan":
            pytest.skip("DBSCAN might not find clusters in simple test data")

        if all_algorithms == "kmeans":
            clusterer = SemanticClusterer(method=all_algorithms, n_clusters=3)
        elif all_algorithms == "gmm":
            clusterer = SemanticClusterer(method=all_algorithms, n_components=3)
        elif all_algorithms == "hierarchical":
            clusterer = SemanticClusterer(method=all_algorithms, n_clusters=3)
        else:
            clusterer = SemanticClusterer(method=all_algorithms)

        # Should not raise an exception
        clustered_data = clusterer.fit_predict(sample_documents)
        assert isinstance(clustered_data, list)

    def test_save_and_load_results(self, sample_documents, temp_jsonl_file):
        """Test saving and loading clustering results."""
        # Perform clustering
        clusterer = SemanticClusterer(method="kmeans", n_clusters=2)
        data = load_jsonl(temp_jsonl_file)
        clustered_data = clusterer.fit_predict(data)

        # Save results to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            output_path = f.name

        try:
            # Add labels to original data based on clustering results
            labeled_data = []
            cluster_id = 0
            for cluster in clustered_data:
                for doc in cluster:
                    doc_with_label = doc.copy()
                    doc_with_label["cluster_label"] = cluster_id
                    labeled_data.append(doc_with_label)
                cluster_id += 1

            save_jsonl(labeled_data, output_path)

            # Load and verify
            loaded_data = load_jsonl(output_path)
            assert len(loaded_data) > 0
            assert all("cluster_label" in doc for doc in loaded_data)

        finally:
            Path(output_path).unlink(missing_ok=True)


class TestDataValidation:
    """Test data validation and error handling."""

    def test_empty_data_handling(self):
        """Test handling of empty input data."""
        clusterer = SemanticClusterer(method="kmeans")

        with pytest.raises((ValueError, IndexError)):
            clusterer.fit_predict([])

    def test_invalid_embedding_dimensions(self):
        """Test handling of inconsistent embedding dimensions."""
        invalid_data = [
            {"text": "doc1", "embedding": [1, 2, 3]},
            {"text": "doc2", "embedding": [1, 2]},  # Different dimension
        ]

        clusterer = SemanticClusterer(method="kmeans")

        with pytest.raises(ValueError):
            clusterer.fit_predict(invalid_data)

    def test_missing_embeddings(self):
        """Test handling of documents without embeddings."""
        invalid_data = [
            {"text": "doc1", "embedding": [1, 2, 3]},
            {"text": "doc2"},  # Missing embedding
        ]

        clusterer = SemanticClusterer(method="kmeans")

        with pytest.raises((KeyError, ValueError)):
            clusterer.fit_predict(invalid_data)


class TestClusteringQuality:
    """Test clustering quality and metrics."""

    def test_silhouette_score_calculation(self, sample_documents):
        """Test that silhouette scores are reasonable."""
        clusterer = SemanticClusterer(method="kmeans", n_clusters=3)
        clustered_data = clusterer.fit_predict(sample_documents)

        # Check that metrics are available
        assert hasattr(clusterer, "quality_metrics_")
        metrics = clusterer.quality_metrics_
        assert "silhouette_score" in metrics

        # Silhouette score should be between -1 and 1
        silhouette = metrics["silhouette_score"]
        assert -1 <= silhouette <= 1

    def test_cluster_distribution(self, sample_documents):
        """Test that clusters are reasonably distributed."""
        clusterer = SemanticClusterer(method="kmeans", n_clusters=3)
        clustered_data = clusterer.fit_predict(sample_documents)

        # Check that we have clusters
        assert isinstance(clustered_data, list)
        assert len(clustered_data) > 0

        # Check that labels are available in clusterer
        assert hasattr(clusterer, "labels_")
        labels = clusterer.labels_
        unique_labels = np.unique(labels)

        # Should have the expected number of clusters
        assert len(unique_labels) <= 3

        # No cluster should have too few points (unless data is very small)
        for label in unique_labels:
            cluster_size = np.sum(labels == label)
            assert cluster_size >= 1
