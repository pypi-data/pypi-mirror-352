"""
Core clustering functionality for semantic-clustify.

This module provides the main SemanticClusterer class that orchestrates
different clustering algorithms and handles the high-level clustering workflow.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import logging
from abc import ABC, abstractmethod

from .algorithms import (
    KMeansClusterer,
    DBSCANClusterer,
    HierarchicalClusterer,
    GMMClusterer,
)
from .utils import (
    extract_vectors,
    validate_input_data,
    calculate_quality_metrics,
)

logger = logging.getLogger(__name__)


class ClusteringAlgorithm(ABC):
    """Abstract base class for clustering algorithms."""

    @abstractmethod
    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit the algorithm and predict cluster labels."""
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        pass


class SemanticClusterer:
    """
    Main class for semantic clustering of text documents using vector embeddings.

    This class provides a unified interface for different clustering algorithms
    and handles automatic parameter optimization and quality assessment.
    """

    SUPPORTED_METHODS = {
        "kmeans": KMeansClusterer,
        "dbscan": DBSCANClusterer,
        "hierarchical": HierarchicalClusterer,
        "gmm": GMMClusterer,
    }

    def __init__(
        self,
        method: str = "kmeans",
        n_clusters: Union[int, str] = "auto",
        min_cluster_size: int = 2,
        max_clusters: int = 20,
        random_state: Optional[int] = 42,
        **kwargs: Any,
    ):
        """
        Initialize the SemanticClusterer.

        Args:
            method: Clustering algorithm to use ('kmeans', 'dbscan', 'hierarchical', 'gmm')
            n_clusters: Number of clusters or 'auto' for automatic detection
            min_cluster_size: Minimum size for a valid cluster
            max_clusters: Maximum number of clusters for auto-detection
            random_state: Random state for reproducibility
            **kwargs: Additional parameters passed to the clustering algorithm
        """
        if method not in self.SUPPORTED_METHODS:
            raise ValueError(
                f"Unsupported method: {method}. "
                f"Supported methods: {list(self.SUPPORTED_METHODS.keys())}"
            )

        self.method = method
        self.n_clusters = n_clusters
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.random_state = random_state
        self.kwargs = kwargs

        # Initialize algorithm
        self.algorithm = self._create_algorithm()

        # Storage for results
        self.labels_: Optional[np.ndarray] = None
        self.vectors_: Optional[np.ndarray] = None
        self.quality_metrics_: Optional[Dict[str, Any]] = None

    def _create_algorithm(self) -> Any:  # type: ignore
        """Create the clustering algorithm instance."""
        algorithm_class = self.SUPPORTED_METHODS[self.method]

        # Prepare parameters
        params = {
            "n_clusters": self.n_clusters,
            "min_cluster_size": self.min_cluster_size,
            "max_clusters": self.max_clusters,
            "random_state": self.random_state,
            **self.kwargs,
        }

        return algorithm_class(**params)

    def fit_predict(
        self, data: List[Dict[str, Any]], vector_field: str = "embedding"
    ) -> List[List[Dict[str, Any]]]:
        """
        Fit the clustering algorithm and predict cluster assignments.

        Args:
            data: List of dictionaries containing documents with vector embeddings
            vector_field: Name of the field containing vector embeddings

        Returns:
            List of clusters, where each cluster is a list of documents
        """
        # Validate input data
        validate_input_data(data, vector_field)

        # Extract vectors
        self.vectors_ = extract_vectors(data, vector_field)
        logger.info(
            f"Extracted {len(self.vectors_)} vectors of dimension {self.vectors_.shape[1]}"
        )

        # Perform clustering
        self.labels_ = self.algorithm.fit_predict(self.vectors_)

        # Group documents by cluster
        clustered_data = self._group_by_clusters(data, self.labels_)

        # Calculate quality metrics
        self.quality_metrics_ = calculate_quality_metrics(
            self.vectors_, self.labels_, self.min_cluster_size
        )

        logger.info(
            f"Clustering completed: {len(clustered_data)} clusters, "
            f"silhouette score: {self.quality_metrics_.get('silhouette_score', 'N/A')}"
        )

        return clustered_data

    def _group_by_clusters(
        self, data: List[Dict[str, Any]], labels: np.ndarray
    ) -> List[List[Dict[str, Any]]]:
        """Group documents by cluster labels."""
        clusters: Dict[int, List[Dict[str, Any]]] = {}

        for doc, label in zip(data, labels):
            if label == -1:  # Noise in DBSCAN
                continue

            if label not in clusters:
                clusters[label] = []

            # Add cluster_id to document
            doc_with_cluster = doc.copy()
            doc_with_cluster["cluster_id"] = int(label)
            clusters[label].append(doc_with_cluster)

        # Filter out small clusters and sort by cluster size
        valid_clusters = [
            cluster
            for cluster in clusters.values()
            if len(cluster) >= self.min_cluster_size
        ]

        # Sort clusters by size (largest first)
        valid_clusters.sort(key=len, reverse=True)

        return valid_clusters

    def get_quality_metrics(self) -> Dict[str, Any]:
        """
        Get clustering quality metrics.

        Returns:
            Dictionary containing quality metrics
        """
        if self.quality_metrics_ is None:
            raise RuntimeError(
                "No clustering has been performed yet. Call fit_predict() first."
            )

        return self.quality_metrics_.copy()

    def get_algorithm_params(self) -> Dict[str, Any]:
        """Get the parameters of the underlying clustering algorithm."""
        return self.algorithm.get_params()  # type: ignore[no-any-return]

    def predict_new_documents(
        self, new_data: List[Dict[str, Any]], vector_field: str = "embedding"
    ) -> List[int]:
        """
        Predict cluster assignments for new documents.

        Note: This is only supported for some algorithms (e.g., KMeans, GMM).

        Args:
            new_data: List of new documents with vector embeddings
            vector_field: Name of the field containing vector embeddings

        Returns:
            List of cluster labels for new documents
        """
        if not hasattr(self.algorithm, "predict"):
            raise NotImplementedError(f"Prediction not supported for {self.method}")

        new_vectors = extract_vectors(new_data, vector_field)
        return self.algorithm.predict(new_vectors).tolist()  # type: ignore

    def save_model(self, filepath: str) -> None:
        """Save the trained clustering model."""
        import pickle

        model_data = {
            "method": self.method,
            "algorithm": self.algorithm,
            "quality_metrics": self.quality_metrics_,
            "params": self.get_algorithm_params(),
        }

        with open(filepath, "wb") as f:
            pickle.dump(model_data, f)

        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load_model(cls, filepath: str) -> "SemanticClusterer":
        """Load a trained clustering model."""
        import pickle

        with open(filepath, "rb") as f:
            model_data = pickle.load(f)

        # Recreate clusterer
        clusterer = cls(method=model_data["method"])
        clusterer.algorithm = model_data["algorithm"]
        clusterer.quality_metrics_ = model_data["quality_metrics"]

        logger.info(f"Model loaded from {filepath}")
        return clusterer
