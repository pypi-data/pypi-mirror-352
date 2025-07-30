"""
semantic-clustify: A powerful and flexible Python tool for semantic clustering of text documents using vector embeddings.

This package provides both CLI and library interfaces for clustering text documents
based on their semantic similarity using pre-computed vector embeddings.
"""

__version__ = "1.0.0"
__author__ = "changyy"
__email__ = "changyy.csie@gmail.com"

from .core import SemanticClusterer
from .algorithms import (
    KMeansClusterer,
    DBSCANClusterer,
    HierarchicalClusterer,
    GMMClusterer,
)

__all__ = [
    "SemanticClusterer",
    "KMeansClusterer",
    "DBSCANClusterer",
    "HierarchicalClusterer",
    "GMMClusterer",
]
