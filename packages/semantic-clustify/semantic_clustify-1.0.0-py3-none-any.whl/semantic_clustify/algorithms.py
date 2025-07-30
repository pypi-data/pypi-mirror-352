"""
Clustering algorithms implementation for semantic-clustify.

This module provides implementations of different clustering algorithms
optimized for semantic text clustering with vector embeddings.
"""

from typing import Any, Dict, Optional, Union, TYPE_CHECKING
import numpy as np
import logging
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.mixture import GaussianMixture

logger = logging.getLogger(__name__)


class BaseClusterer(ABC):
    """Base class for all clustering algorithms."""

    def __init__(
        self,
        n_clusters: Union[int, str] = "auto",
        min_cluster_size: int = 2,
        max_clusters: int = 20,
        random_state: Optional[int] = 42,
        **kwargs: Any,
    ):
        self.n_clusters = n_clusters
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.random_state = random_state
        self.kwargs = kwargs
        self.model_: Optional[Any] = None
        self.optimal_clusters_: Optional[int] = None

    @abstractmethod
    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit the algorithm and predict cluster labels."""
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """Get algorithm parameters."""
        pass

    def _determine_optimal_clusters(self, vectors: np.ndarray) -> int:
        """Determine optimal number of clusters if n_clusters is 'auto'."""
        if isinstance(self.n_clusters, int):
            return self.n_clusters

        # Use elbow method as default
        return self._elbow_method(vectors)

    def _elbow_method(self, vectors: np.ndarray) -> int:
        """Find optimal clusters using elbow method."""
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score

        n_samples = len(vectors)
        max_k = min(self.max_clusters, n_samples // self.min_cluster_size)

        if max_k < 2:
            return 2

        best_score = -1
        best_k = 2

        for k in range(2, max_k + 1):
            try:
                kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
                labels = kmeans.fit_predict(vectors)

                if len(np.unique(labels)) > 1:  # Ensure we have multiple clusters
                    score = silhouette_score(vectors, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
            except Exception as e:
                logger.warning(f"Failed to evaluate k={k}: {e}")
                continue

        logger.info(
            f"Optimal clusters determined: {best_k} (silhouette score: {best_score:.3f})"
        )
        return best_k


class KMeansClusterer(BaseClusterer):
    """KMeans clustering algorithm optimized for semantic clustering."""

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit KMeans and predict cluster labels."""
        from sklearn.cluster import KMeans

        n_clusters = self._determine_optimal_clusters(vectors)

        # Create and fit KMeans model
        self.model_ = KMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            n_init=10,
            max_iter=300,
            **self.kwargs,
        )

        labels = self.model_.fit_predict(vectors)
        self.optimal_clusters_ = n_clusters

        logger.info(f"KMeans clustering completed with {n_clusters} clusters")
        return labels.astype(np.int32)  # type: ignore[no-any-return]

    def predict(self, vectors: np.ndarray) -> np.ndarray:
        """Predict cluster labels for new data."""
        if self.model_ is None:
            raise RuntimeError("Model must be fitted before prediction")
        return self.model_.predict(vectors).astype(np.int32)  # type: ignore

    def get_params(self) -> Dict[str, Any]:
        """Get KMeans parameters."""
        params = {
            "algorithm": "kmeans",
            "n_clusters": self.optimal_clusters_ or self.n_clusters,
            "min_cluster_size": self.min_cluster_size,
            "random_state": self.random_state,
        }
        if self.model_ is not None:
            params.update(
                {
                    "inertia": self.model_.inertia_,
                    "n_iter": self.model_.n_iter_,
                }
            )
        return params


class DBSCANClusterer(BaseClusterer):
    """DBSCAN clustering algorithm for density-based clustering."""

    def __init__(
        self,
        eps: Optional[float] = None,
        min_samples: Optional[int] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.eps = eps
        self.min_samples = min_samples

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit DBSCAN and predict cluster labels."""
        from sklearn.cluster import DBSCAN
        from sklearn.neighbors import NearestNeighbors

        # Auto-determine parameters if not provided
        eps = self.eps or self._estimate_eps(vectors)
        min_samples = self.min_samples or max(self.min_cluster_size, 2)

        # Create and fit DBSCAN model
        self.model_ = DBSCAN(eps=eps, min_samples=min_samples, **self.kwargs)

        labels = self.model_.fit_predict(vectors)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise = list(labels).count(-1)

        logger.info(
            f"DBSCAN clustering completed: {n_clusters} clusters, {n_noise} noise points"
        )
        return labels.astype(np.int32)  # type: ignore[no-any-return]

    def _estimate_eps(self, vectors: np.ndarray) -> float:
        """Estimate optimal eps parameter using k-distance graph."""
        from sklearn.neighbors import NearestNeighbors

        k = max(
            self.min_cluster_size, 4
        )  # Use min_cluster_size or 4, whichever is larger

        # Fit nearest neighbors
        nn = NearestNeighbors(n_neighbors=k)
        nn.fit(vectors)
        distances, _ = nn.kneighbors(vectors)

        # Sort distances to k-th neighbor
        k_distances = np.sort(distances[:, -1])

        # Find elbow point (simplified approach)
        # Use the 90th percentile as a reasonable estimate
        eps = np.percentile(k_distances, 90)

        logger.info(f"Estimated eps parameter: {eps:.4f}")
        return float(eps)

    def get_params(self) -> Dict[str, Any]:
        """Get DBSCAN parameters."""
        params = {
            "algorithm": "dbscan",
            "eps": self.eps,
            "min_samples": self.min_samples,
            "min_cluster_size": self.min_cluster_size,
        }
        if self.model_ is not None:
            params.update(
                {
                    "core_sample_indices": (  # type: ignore[dict-item]
                        self.model_.core_sample_indices_.tolist()
                        if hasattr(self.model_, "core_sample_indices_")
                        else []
                    ),
                    "components": (  # type: ignore[dict-item]
                        self.model_.components_.tolist()
                        if hasattr(self.model_, "components_")
                        else []
                    ),
                }
            )
        return params


class HierarchicalClusterer(BaseClusterer):
    """Hierarchical clustering algorithm for nested cluster structures."""

    def __init__(
        self,
        linkage: str = "ward",
        distance_threshold: Optional[float] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.linkage = linkage
        self.distance_threshold = distance_threshold

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit hierarchical clustering and predict cluster labels."""
        from sklearn.cluster import AgglomerativeClustering

        # Determine parameters
        if self.distance_threshold is not None:
            # Use distance threshold (n_clusters will be None)
            n_clusters = None
            distance_threshold = self.distance_threshold
        else:
            # Use predetermined number of clusters
            n_clusters = self._determine_optimal_clusters(vectors)
            distance_threshold = None

        # Create and fit hierarchical clustering
        self.model_ = AgglomerativeClustering(
            n_clusters=n_clusters,
            distance_threshold=distance_threshold,
            linkage=self.linkage,
            **self.kwargs,
        )

        labels = self.model_.fit_predict(vectors)

        actual_clusters = len(np.unique(labels))
        logger.info(
            f"Hierarchical clustering completed with {actual_clusters} clusters"
        )
        return labels.astype(np.int32)  # type: ignore[no-any-return]

    def get_params(self) -> Dict[str, Any]:
        """Get hierarchical clustering parameters."""
        params = {
            "algorithm": "hierarchical",
            "linkage": self.linkage,
            "distance_threshold": self.distance_threshold,
            "min_cluster_size": self.min_cluster_size,
        }
        if self.model_ is not None:
            params.update(
                {
                    "n_clusters": self.model_.n_clusters_,
                    "n_leaves": self.model_.n_leaves_,
                }
            )
        return params


class GMMClusterer(BaseClusterer):
    """Gaussian Mixture Model clustering for probabilistic clustering."""

    def __init__(
        self, covariance_type: str = "full", init_params: str = "kmeans", **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.covariance_type = covariance_type
        self.init_params = init_params

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Fit GMM and predict cluster labels."""
        from sklearn.mixture import GaussianMixture

        n_components = self._determine_optimal_clusters(vectors)

        # Remove n_components from kwargs if it exists to avoid conflict
        clean_kwargs = {k: v for k, v in self.kwargs.items() if k != "n_components"}

        # Create and fit GMM
        self.model_ = GaussianMixture(
            n_components=n_components,
            covariance_type=self.covariance_type,
            init_params=self.init_params,
            random_state=self.random_state,
            **clean_kwargs,
        )

        self.model_.fit(vectors)
        labels = self.model_.predict(vectors)

        # Calculate and store AIC/BIC for later retrieval
        self.model_.aic_ = self.model_.aic(vectors)
        self.model_.bic_ = self.model_.bic(vectors)

        logger.info(f"GMM clustering completed with {n_components} components")
        return labels.astype(np.int32)  # type: ignore[no-any-return]

    def predict(self, vectors: np.ndarray) -> np.ndarray:
        """Predict cluster labels for new data."""
        if self.model_ is None:
            raise RuntimeError("Model must be fitted before prediction")
        return self.model_.predict(vectors).astype(np.int32)  # type: ignore

    def predict_proba(self, vectors: np.ndarray) -> np.ndarray:
        """Predict cluster probabilities for new data."""
        if self.model_ is None:
            raise RuntimeError("Model must be fitted before prediction")
        return self.model_.predict_proba(vectors).astype(np.float64)  # type: ignore

    def get_params(self) -> Dict[str, Any]:
        """Get GMM parameters."""
        params = {
            "algorithm": "gmm",
            "n_components": self.optimal_clusters_ or self.n_clusters,
            "covariance_type": self.covariance_type,
            "init_params": self.init_params,
            "random_state": self.random_state,
        }
        if self.model_ is not None and hasattr(self.model_, "means_"):
            # Use the original training data for AIC calculation
            try:
                aic_value = getattr(self.model_, "aic_", None)
                bic_value = getattr(self.model_, "bic_", None)
            except AttributeError:
                aic_value = None
                bic_value = None

            params.update(
                {
                    "aic": aic_value,
                    "bic": bic_value,
                    "converged": self.model_.converged_,
                    "n_iter": self.model_.n_iter_,
                }
            )
        return params
