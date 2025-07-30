"""
Utility functions for semantic-clustify.

This module provides helper functions for data validation, vector processing,
quality metrics calculation, and other common operations.
"""

from typing import List, Dict, Any, Union, Tuple
import numpy as np
import logging
import json

logger = logging.getLogger(__name__)


def validate_input_data(data: List[Dict[str, Any]], vector_field: str) -> None:
    """
    Validate input data format and consistency.

    Args:
        data: List of dictionaries containing documents
        vector_field: Name of the field containing vector embeddings

    Raises:
        ValueError: If data format is invalid
    """
    if not data:
        raise ValueError("Input data is empty")

    if not isinstance(data, list):
        raise ValueError("Input data must be a list of dictionaries")

    # Check first few items for consistency
    sample_size = min(10, len(data))
    vector_dims = None

    for i, item in enumerate(data[:sample_size]):
        if not isinstance(item, dict):
            raise ValueError(f"Item {i} is not a dictionary")

        if vector_field not in item:
            raise ValueError(f"Item {i} missing required field '{vector_field}'")

        vector = item[vector_field]
        if not isinstance(vector, (list, np.ndarray)):
            raise ValueError(
                f"Item {i} field '{vector_field}' must be a list or numpy array"
            )

        # Check vector dimension consistency
        current_dims = len(vector)
        if vector_dims is None:
            vector_dims = current_dims
        elif vector_dims != current_dims:
            raise ValueError(
                f"Inconsistent vector dimensions: expected {vector_dims}, "
                f"got {current_dims} at item {i}"
            )

    logger.info(
        f"Data validation passed: {len(data)} documents, "
        f"vector dimension: {vector_dims}"
    )


def extract_vectors(data: List[Dict[str, Any]], vector_field: str) -> np.ndarray:
    """
    Extract vector embeddings from input data.

    Args:
        data: List of dictionaries containing documents
        vector_field: Name of the field containing vector embeddings

    Returns:
        Numpy array of shape (n_documents, n_features)
    """
    vectors = []

    for i, item in enumerate(data):
        try:
            vector = item[vector_field]
            if isinstance(vector, list):
                vector = np.array(vector, dtype=np.float32)
            elif isinstance(vector, np.ndarray):
                vector = vector.astype(np.float32)
            else:
                raise ValueError(f"Invalid vector type: {type(vector)}")

            vectors.append(vector)

        except Exception as e:
            logger.warning(f"Failed to extract vector from item {i}: {e}")
            raise ValueError(f"Failed to process item {i}: {e}")

    return np.array(vectors, dtype=np.float64)  # type: ignore[no-any-return]


def calculate_quality_metrics(
    vectors: np.ndarray, labels: np.ndarray, min_cluster_size: int = 2
) -> Dict[str, Any]:
    """
    Calculate clustering quality metrics.

    Args:
        vectors: Input vectors
        labels: Cluster labels
        min_cluster_size: Minimum cluster size for validation

    Returns:
        Dictionary containing quality metrics
    """
    from sklearn.metrics import (
        silhouette_score,
        calinski_harabasz_score,
        davies_bouldin_score,
    )

    # Basic cluster statistics
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)  # Exclude noise
    n_noise: int = np.sum(labels == -1)

    cluster_sizes: List[int] = []
    for label in unique_labels:
        if label != -1:  # Exclude noise
            cluster_sizes.append(np.sum(labels == label))

    metrics = {
        "n_clusters": n_clusters,
        "n_samples": len(vectors),
        "n_noise": n_noise,
        "cluster_sizes": cluster_sizes,
        "min_cluster_size": min(cluster_sizes) if cluster_sizes else 0,
        "max_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
        "avg_cluster_size": np.mean(cluster_sizes) if cluster_sizes else 0,
    }

    # Quality metrics (only if we have valid clusters)
    if n_clusters > 1 and len(np.unique(labels[labels != -1])) > 1:
        try:
            # Filter out noise points for quality metrics
            valid_mask = labels != -1
            if np.sum(valid_mask) > 1:
                valid_vectors = vectors[valid_mask]
                valid_labels = labels[valid_mask]

                if len(np.unique(valid_labels)) > 1:
                    metrics["silhouette_score"] = silhouette_score(
                        valid_vectors, valid_labels
                    )
                    metrics["calinski_harabasz_score"] = calinski_harabasz_score(
                        valid_vectors, valid_labels
                    )
                    metrics["davies_bouldin_score"] = davies_bouldin_score(
                        valid_vectors, valid_labels
                    )

        except Exception as e:
            logger.warning(f"Failed to calculate quality metrics: {e}")
            metrics["silhouette_score"] = None
            metrics["calinski_harabasz_score"] = None
            metrics["davies_bouldin_score"] = None
    else:
        metrics["silhouette_score"] = None
        metrics["calinski_harabasz_score"] = None
        metrics["davies_bouldin_score"] = None

    return metrics


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """
    Load data from JSONL file.

    Args:
        filepath: Path to JSONL file

    Returns:
        List of dictionaries
    """
    data = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    item = json.loads(line)
                    data.append(item)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON at line {line_num}: {e}")
                    continue

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Failed to load JSONL file {filepath}: {e}")

    logger.info(f"Loaded {len(data)} items from {filepath}")
    return data


def save_jsonl(data: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save data to JSONL file.

    Args:
        data: List of dictionaries to save
        filepath: Output file path
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for item in data:
                json.dump(item, f, ensure_ascii=False)
                f.write("\n")

        logger.info(f"Saved {len(data)} items to {filepath}")

    except Exception as e:
        raise RuntimeError(f"Failed to save JSONL file {filepath}: {e}")


def save_grouped_jsonl(clusters: List[List[Dict[str, Any]]], filepath: str) -> None:
    """
    Save clustered data in grouped format (list of lists).

    Args:
        clusters: List of clusters, each containing documents
        filepath: Output file path
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(clusters)} clusters to {filepath}")

    except Exception as e:
        raise RuntimeError(f"Failed to save grouped JSONL file {filepath}: {e}")


def flatten_clusters(clusters: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Flatten clustered data to a single list with cluster_id field.

    Args:
        clusters: List of clusters

    Returns:
        Flattened list of documents with cluster_id
    """
    flattened = []

    for cluster_id, cluster in enumerate(clusters):
        for doc in cluster:
            doc_copy = doc.copy()
            doc_copy["cluster_id"] = cluster_id
            flattened.append(doc_copy)

    return flattened


def read_from_stdin() -> List[Dict[str, Any]]:
    """
    Read JSONL data from stdin.

    Returns:
        List of dictionaries
    """
    import sys

    data = []

    try:
        # Check if stdin has any data available
        if sys.stdin.isatty():
            # No piped input available
            raise RuntimeError("No data available from stdin")

        for line_num, line in enumerate(sys.stdin, 1):
            line = line.strip()
            if not line:
                continue

            try:
                item = json.loads(line)
                data.append(item)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON at stdin line {line_num}: {e}")
                continue

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        raise RuntimeError(f"Failed to read from stdin: {e}")

    if not data:
        raise RuntimeError("No valid data found in stdin")

    logger.info(f"Read {len(data)} items from stdin")
    return data


def generate_output_filename(
    input_filename: str, method: str, output_format: str = "grouped"
) -> str:
    """
    Generate output filename based on input filename and parameters.

    Args:
        input_filename: Input file name
        method: Clustering method
        output_format: Output format

    Returns:
        Generated output filename
    """
    import os
    import tempfile
    from datetime import datetime

    if input_filename in ["-", "stdin"]:
        base_name = "clustered_output"
    else:
        base_name = os.path.splitext(os.path.basename(input_filename))[0]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{base_name}_{method}_{output_format}_{timestamp}.jsonl"

    # For testing environments, use temp directory to avoid cluttering project root
    if "pytest" in os.environ.get("_", "") or "PYTEST_CURRENT_TEST" in os.environ:
        temp_dir = tempfile.gettempdir()
        output_filename = os.path.join(temp_dir, output_filename)

    return output_filename


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    import sys

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Set specific loggers
    logging.getLogger("semantic_clustify").setLevel(numeric_level)


def print_cluster_summary(
    clusters: List[List[Dict[str, Any]]], show_details: bool = False
) -> None:
    """
    Print a summary of clustering results.

    Args:
        clusters: List of clusters
        show_details: Whether to show detailed cluster information
    """
    print(f"\n📊 Clustering Summary:")
    print(f"   Total clusters: {len(clusters)}")
    print(f"   Total documents: {sum(len(cluster) for cluster in clusters)}")

    if clusters:
        cluster_sizes = [len(cluster) for cluster in clusters]
        print(
            f"   Cluster sizes: min={min(cluster_sizes)}, max={max(cluster_sizes)}, avg={np.mean(cluster_sizes):.1f}"
        )

    if show_details and clusters:
        print(f"\n📋 Cluster Details:")
        for i, cluster in enumerate(clusters):
            print(f"   Cluster {i}: {len(cluster)} documents")
            if len(cluster) <= 3:  # Show titles for small clusters
                for j, doc in enumerate(cluster):
                    title = doc.get("title", doc.get("content", "Unknown"))[:50]
                    print(f"     {j+1}. {title}...")
            elif len(cluster) <= 10:  # Show first few for medium clusters
                for j, doc in enumerate(cluster[:3]):
                    title = doc.get("title", doc.get("content", "Unknown"))[:50]
                    print(f"     {j+1}. {title}...")
                print(f"     ... and {len(cluster)-3} more")


def validate_vectors_dimension(vectors: np.ndarray, min_dim: int = 2) -> bool:
    """
    Validate vector dimensions for clustering.

    Args:
        vectors: Input vectors
        min_dim: Minimum required dimension

    Returns:
        True if valid, False otherwise
    """
    if len(vectors.shape) != 2:
        logger.error(f"Vectors must be 2D array, got shape: {vectors.shape}")
        return False

    n_samples, n_features = vectors.shape

    if n_samples < 2:
        logger.error(f"Need at least 2 samples for clustering, got: {n_samples}")
        return False

    if n_features < min_dim:
        logger.error(f"Need at least {min_dim} features, got: {n_features}")
        return False

    return True
