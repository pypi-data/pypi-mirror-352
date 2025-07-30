"""
Clustering algorithms implementation for semantic-clustify.

This module provides implementations of different clustering algorithms
optimized for semantic text clustering with vector embeddings.
"""

from typing import Any, Dict, Optional, Union, TYPE_CHECKING, List, Tuple
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


class HybridDBSCANKMeansClusterer(BaseClusterer):
    """
    Hybrid DBSCAN + K-Means Clustering Algorithm
    
    Stage 1: Use DBSCAN to discover natural clusters and outliers
    Stage 2: Use K-Means to reorganize to target cluster count
    
    Use case: News event clustering - first naturally discover major events, 
    then reorganize minor events to target count
    """
    
    def __init__(
        self,
        target_clusters: Union[int, str] = 30,
        major_event_threshold: int = 10,
        dbscan_eps: Optional[float] = None,
        dbscan_min_samples: Optional[int] = None,
        kmeans_strategy: str = "remaining_slots",  # "remaining_slots" | "all_minor" | "adaptive"
        **kwargs
    ):
        # Remove n_clusters from kwargs to avoid duplication
        clean_kwargs = {k: v for k, v in kwargs.items() if k != 'n_clusters'}
        super().__init__(n_clusters=target_clusters, **clean_kwargs)
        self.target_clusters = target_clusters
        self.major_event_threshold = major_event_threshold
        self.dbscan_eps = dbscan_eps
        self.dbscan_min_samples = dbscan_min_samples
        self.kmeans_strategy = kmeans_strategy
        
        # Sub-clusterers
        self.dbscan_clusterer = None
        self.kmeans_clusterer = None
        
        # Result storage
        self.dbscan_labels_ = None
        self.final_cluster_mapping_ = None
        self.stage_info_ = {}

    def fit_predict(self, vectors: np.ndarray) -> np.ndarray:
        """Execute hybrid clustering"""
        
        # Stage 1: DBSCAN event discovery
        logger.info("Stage 1: DBSCAN event discovery...")
        dbscan_labels = self._stage1_dbscan_discovery(vectors)
        
        # Stage 2: Analysis and classification  
        logger.info("Stage 2: Analyzing cluster results...")
        major_clusters, minor_vectors, minor_indices = self._stage2_analyze_clusters(
            vectors, dbscan_labels
        )
        
        # Stage 3: K-Means reorganization
        logger.info("Stage 3: K-Means reorganization...")
        final_labels = self._stage3_kmeans_reorganization(
            vectors, dbscan_labels, major_clusters, minor_vectors, minor_indices
        )
        
        return final_labels
    
    def _stage1_dbscan_discovery(self, vectors: np.ndarray) -> np.ndarray:
        """Stage 1: DBSCAN discovery of natural clusters"""
        
        self.dbscan_clusterer = DBSCANClusterer(
            eps=self.dbscan_eps,
            min_samples=self.dbscan_min_samples or max(self.min_cluster_size, 3),
            min_cluster_size=self.min_cluster_size,
            **{k: v for k, v in self.kwargs.items() if k in ['metric']}
        )
        
        dbscan_labels = self.dbscan_clusterer.fit_predict(vectors)
        self.dbscan_labels_ = dbscan_labels
        
        # Statistics of DBSCAN results
        unique_labels = np.unique(dbscan_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = np.sum(dbscan_labels == -1)
        
        self.stage_info_['dbscan'] = {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'cluster_sizes': [np.sum(dbscan_labels == label) for label in unique_labels if label != -1]
        }
        
        logger.info(f"DBSCAN discovered {n_clusters} clusters, {n_noise} noise points")
        return dbscan_labels
    
    def _stage2_analyze_clusters(self, vectors: np.ndarray, dbscan_labels: np.ndarray) -> Tuple:
        """Stage 2: Analyze clusters, distinguish major events from minor events"""
        
        unique_labels = np.unique(dbscan_labels)
        major_clusters = []
        minor_indices = []
        
        for label in unique_labels:
            if label == -1:  # Skip noise
                minor_indices.extend(np.where(dbscan_labels == label)[0])
                continue
                
            cluster_mask = dbscan_labels == label
            cluster_size = np.sum(cluster_mask)
            
            if cluster_size >= self.major_event_threshold:
                # Major event, keep directly
                major_clusters.append(label)
                logger.info(f"Major event cluster {label}: {cluster_size} documents")
            else:
                # Minor event, add to re-clustering list
                minor_indices.extend(np.where(cluster_mask)[0])
        
        minor_vectors = vectors[minor_indices] if minor_indices else np.array([])
        
        self.stage_info_['analysis'] = {
            'major_clusters': len(major_clusters),
            'minor_documents': len(minor_indices),
            'major_cluster_labels': major_clusters
        }
        
        logger.info(f"Found {len(major_clusters)} major events, {len(minor_indices)} documents need re-clustering")
        return major_clusters, minor_vectors, minor_indices
    
    def _stage3_kmeans_reorganization(
        self, 
        vectors: np.ndarray, 
        dbscan_labels: np.ndarray,
        major_clusters: List[int],
        minor_vectors: np.ndarray,
        minor_indices: List[int]
    ) -> np.ndarray:
        """Stage 3: K-Means reorganization to target cluster count"""
        
        target_clusters = self._determine_target_clusters()
        final_labels = np.full(len(vectors), -1, dtype=int)
        current_cluster_id = 0
        
        # Process major events (directly assign cluster IDs)
        for major_label in major_clusters:
            major_mask = dbscan_labels == major_label
            final_labels[major_mask] = current_cluster_id
            current_cluster_id += 1
        
        # Process minor events and noise (using K-Means)
        if len(minor_vectors) > 0:
            remaining_clusters = target_clusters - len(major_clusters)
            
            if remaining_clusters > 0:
                # Ensure not exceeding data point count
                remaining_clusters = min(remaining_clusters, len(minor_vectors))
                
                if remaining_clusters > 1:
                    self.kmeans_clusterer = KMeansClusterer(
                        n_clusters=remaining_clusters,
                        min_cluster_size=1,  # Allow small clusters
                        random_state=self.random_state
                    )
                    
                    kmeans_labels = self.kmeans_clusterer.fit_predict(minor_vectors)
                    
                    # Map K-Means results to final labels
                    for i, minor_idx in enumerate(minor_indices):
                        final_labels[minor_idx] = current_cluster_id + kmeans_labels[i]
                else:
                    # Only one cluster remaining, assign all to the same one
                    for minor_idx in minor_indices:
                        final_labels[minor_idx] = current_cluster_id
            else:
                # No remaining space, assign to the smallest major event cluster
                if major_clusters:
                    # Find the smallest major event cluster
                    smallest_cluster = min(major_clusters, 
                                         key=lambda x: np.sum(dbscan_labels == x))
                    target_id = major_clusters.index(smallest_cluster)
                    
                    for minor_idx in minor_indices:
                        final_labels[minor_idx] = target_id
        
        # Renumber to ensure continuity
        final_labels = self._renumber_clusters(final_labels)
        
        self.stage_info_['kmeans'] = {
            'target_clusters': target_clusters,
            'final_clusters': len(np.unique(final_labels[final_labels >= 0]))
        }
        
        return final_labels
    
    def _determine_target_clusters(self) -> int:
        """Determine target cluster count"""
        if isinstance(self.target_clusters, int):
            return self.target_clusters
        elif self.target_clusters == "auto":
            # Can implement automatic detection logic
            return min(30, len(self.stage_info_['dbscan']['cluster_sizes']) * 2)
        else:
            return 30  # Default value
    
    def _renumber_clusters(self, labels: np.ndarray) -> np.ndarray:
        """Renumber cluster labels to ensure continuity"""
        unique_labels = np.unique(labels[labels >= 0])
        label_mapping = {old_label: new_label for new_label, old_label in enumerate(unique_labels)}
        
        new_labels = labels.copy()
        for old_label, new_label in label_mapping.items():
            new_labels[labels == old_label] = new_label
        
        return new_labels
    
    def get_params(self) -> Dict[str, Any]:
        """Get algorithm parameters"""
        params = {
            "algorithm": "hybrid-dbscan-kmeans",
            "target_clusters": self.target_clusters,
            "major_event_threshold": self.major_event_threshold,
            "dbscan_eps": self.dbscan_eps,
            "dbscan_min_samples": self.dbscan_min_samples,
            "kmeans_strategy": self.kmeans_strategy,
            "stage_info": self.stage_info_
        }
        
        # Add sub-clusterer parameters
        if self.dbscan_clusterer:
            params["dbscan_params"] = self.dbscan_clusterer.get_params()
        if self.kmeans_clusterer:
            params["kmeans_params"] = self.kmeans_clusterer.get_params()
            
        return params
    
    def get_stage_info(self) -> Dict[str, Any]:
        """Get detailed information for each stage"""
        return self.stage_info_.copy()
