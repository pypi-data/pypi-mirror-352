"""
Test basic functionality of HybridDBSCANKMeansClusterer
"""

import pytest
import numpy as np
from typing import List, Dict, Any
from tests.test_utils import create_sample_news_data, get_test_embedding_model, cleanup_test_files

def test_hybrid_clusterer_import():
    """Test if hybrid clusterer can be imported correctly"""
    try:
        from semantic_clustify.algorithms import HybridDBSCANKMeansClusterer
        assert HybridDBSCANKMeansClusterer is not None
        print("✅ HybridDBSCANKMeansClusterer imported successfully")
    except ImportError as e:
        pytest.fail(f"Cannot import HybridDBSCANKMeansClusterer: {e}")

def test_hybrid_clusterer_initialization():
    """Test hybrid clusterer initialization"""
    from semantic_clustify.algorithms import HybridDBSCANKMeansClusterer
    
    # Test default parameters
    clusterer = HybridDBSCANKMeansClusterer()
    assert clusterer.target_clusters == 30
    assert clusterer.major_event_threshold == 10
    assert clusterer.kmeans_strategy == "remaining_slots"
    
    # Test custom parameters
    clusterer = HybridDBSCANKMeansClusterer(
        target_clusters=25,
        major_event_threshold=8,
        dbscan_eps=0.3,
        kmeans_strategy="adaptive"
    )
    assert clusterer.target_clusters == 25
    assert clusterer.major_event_threshold == 8
    assert clusterer.dbscan_eps == 0.3
    assert clusterer.kmeans_strategy == "adaptive"
    
    print("✅ HybridDBSCANKMeansClusterer initialization test passed")

def test_core_semantic_clusterer_with_hybrid():
    """Test if SemanticClusterer supports hybrid algorithm"""
    try:
        from semantic_clustify.core import SemanticClusterer
        
        # Test if hybrid algorithm is in supported list
        assert "hybrid-dbscan-kmeans" in SemanticClusterer.SUPPORTED_METHODS
        
        # Test creating hybrid clusterer
        clusterer = SemanticClusterer(
            method="hybrid-dbscan-kmeans",
            target_clusters=25,
            major_event_threshold=8
        )
        assert clusterer.method == "hybrid-dbscan-kmeans"
        
        print("✅ SemanticClusterer hybrid algorithm support test passed")
    except Exception as e:
        pytest.fail(f"SemanticClusterer hybrid algorithm test failed: {e}")

def create_sample_vectors(n_samples: int = 100) -> np.ndarray:
    """Create sample vector data"""
    np.random.seed(42)
    
    # Create several cluster centers
    centers = [
        np.array([1.0, 0.0, 0.0, 0.0, 0.0]),  # Cluster 1
        np.array([0.0, 1.0, 0.0, 0.0, 0.0]),  # Cluster 2
        np.array([0.0, 0.0, 1.0, 0.0, 0.0]),  # Cluster 3
        np.array([0.0, 0.0, 0.0, 1.0, 0.0]),  # Cluster 4
    ]
    
    vectors = []
    for i in range(n_samples):
        center = centers[i % len(centers)]
        noise = np.random.normal(0, 0.1, 5)
        vector = center + noise
        vectors.append(vector)
    
    return np.array(vectors)

def test_hybrid_clusterer_basic_functionality():
    """Test basic clustering functionality of hybrid clusterer"""
    try:
        from semantic_clustify.algorithms import HybridDBSCANKMeansClusterer
        
        # Create test data
        vectors = create_sample_vectors(100)
        
        # Create clusterer
        clusterer = HybridDBSCANKMeansClusterer(
            target_clusters=10,
            major_event_threshold=5,
            min_cluster_size=2
        )
        
        # Perform clustering
        labels = clusterer.fit_predict(vectors)
        
        # Basic checks
        assert len(labels) == len(vectors)
        assert len(np.unique(labels[labels >= 0])) <= 10  # Not exceeding target cluster count
        
        # Check stage information
        stage_info = clusterer.get_stage_info()
        assert 'dbscan' in stage_info
        assert 'analysis' in stage_info
        assert 'kmeans' in stage_info
        
        print("✅ HybridDBSCANKMeansClusterer basic functionality test passed")
        print(f"   - Number of clusters: {len(np.unique(labels[labels >= 0]))}")
        print(f"   - DBSCAN discovered clusters: {stage_info['dbscan']['n_clusters']}")
        print(f"   - Major events: {stage_info['analysis']['major_clusters']}")
        
    except Exception as e:
        pytest.fail(f"Hybrid clusterer basic functionality test failed: {e}")

def test_get_params():
    """Test parameter retrieval functionality"""
    from semantic_clustify.algorithms import HybridDBSCANKMeansClusterer
    
    clusterer = HybridDBSCANKMeansClusterer(
        target_clusters=25,
        major_event_threshold=8,
        dbscan_eps=0.3
    )
    
    params = clusterer.get_params()
    assert params["algorithm"] == "hybrid-dbscan-kmeans"
    assert params["target_clusters"] == 25
    assert params["major_event_threshold"] == 8
    assert params["dbscan_eps"] == 0.3
    
    print("✅ Parameter retrieval functionality test passed")

if __name__ == "__main__":
    print("🧪 Starting HybridDBSCANKMeansClusterer tests")
    print("=" * 50)
    
    # Run tests
    test_hybrid_clusterer_import()
    test_hybrid_clusterer_initialization()
    test_core_semantic_clusterer_with_hybrid()
    test_hybrid_clusterer_basic_functionality()
    test_get_params()
    
    print("=" * 50)
    print("✅ All tests passed! Hybrid clustering algorithm implementation complete")
