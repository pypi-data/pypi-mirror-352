# semantic-clustify

[![PyPI version](https://img.shields.io/pypi/v/semantic-clustify.svg)](https://pypi.org/project/semantic-clustify)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/semantic-clustify)](https://pepy.tech/projects/semantic-clustify)

A powerful and flexible Python tool for semantic clustering of text documents using vector embeddings with support for multiple algorithms and intelligent cluster optimization.

## 📋 Simple Description

**semantic-clustify** is a command-line tool and Python library that groups text documents by semantic similarity using pre-computed vector embeddings. It supports multiple clustering algorithms (KMeans, DBSCAN, Hierarchical), automatic cluster number optimization, and seamless JSONL processing for efficient document analysis pipelines.

## 🚀 Quick Start

```bash
pip install semantic-clustify

# Basic usage with vector embeddings
semantic-clustify \
  --input vectorized_data.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters 5

# Auto-detect optimal cluster number
semantic-clustify \
  --input data.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto

# Using stdin input
cat vectorized_data.jsonl | semantic-clustify \
  --embedding-field "embedding" \
  --method "dbscan"
```

## ✨ Features

- **🎯 Multiple Clustering Algorithms**: KMeans, DBSCAN, Hierarchical, Gaussian Mixture
- **🧠 Intelligent Cluster Optimization**: Automatic optimal cluster number detection
- **📊 Vector-Based Processing**: Works with pre-computed embeddings from any source
- **📁 JSONL Processing**: Seamless input/output in JSONL format
- **⚡ High Performance**: Optimized with Faiss for large-scale clustering
- **🛡️ Error Resilience**: Continue processing even if individual records fail
- **📥 Stdin Support**: Read input from pipes or stdin for flexible data processing
- **🎛️ Smart Defaults**: Default parameters optimized for common use cases
- **🔧 Flexible Input**: Support file input, stdin, or explicit stdin markers
- **📈 Cluster Quality Metrics**: Silhouette score, inertia, and cluster statistics
- **🚰 Pipeline Optimization**: Enhanced output formats for streaming and pipeline integration
- **📊 Context-Rich Outputs**: Enriched formats with cluster statistics for advanced filtering

## 📖 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Supported Algorithms](#supported-algorithms)
- [Examples](#examples)
- [Library Usage](#library-usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Method 1: pip install (Recommended)

```bash
# Install core package
pip install semantic-clustify

# Install with specific algorithm support
pip install semantic-clustify[faiss]          # Faiss support for large-scale clustering
pip install semantic-clustify[advanced]       # Advanced clustering algorithms
pip install semantic-clustify[all]            # All clustering algorithms and optimizations

# Install with development dependencies
pip install semantic-clustify[dev]
```

### Method 2: From source

```bash
# Clone repository
git clone https://github.com/changyy/py-semantic-clustify.git
cd py-semantic-clustify

# Automated development setup (recommended for contributors)
./setup.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package  
pip install -e .                # Core package only
# or
pip install -e ".[dev]"         # With development dependencies
# or  
pip install -e ".[all,dev]"     # With all optional dependencies
```

### Method 3: Development setup

```bash
# Automated setup for developers (recommended)
git clone https://github.com/changyy/py-semantic-clustify.git
cd py-semantic-clustify
./setup.sh

# Manual development setup
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify installation
python test_runner.py --quick
```

Install additional packages based on the clustering algorithms you plan to use:

```bash
# For high-performance clustering
pip install faiss-cpu  # or faiss-gpu for GPU support

# For advanced clustering algorithms
pip install scikit-learn>=1.0.0

# For visualization
pip install matplotlib seaborn plotly
```

## 📝 Usage

### Command Line Interface

```bash
semantic-clustify [OPTIONS]
```

#### Required Arguments

- `--embedding-field`: Name of the field containing vector embeddings
- `--method`: Clustering algorithm to use

#### Optional Arguments

- `--input`: Path to input JSONL file (use "-" for stdin, or omit to read from stdin)
- `--n-clusters`: Number of clusters (default: "auto" for automatic detection)
- `--min-cluster-size`: Minimum cluster size (default: 2)
- `--max-clusters`: Maximum clusters for auto-detection (default: 20)
- `--output-format`: Output format - "grouped", "labeled", "enriched-labeled", or "streaming-grouped" (default: "grouped")
- `--output`: Output file path (default: auto-generated)
- `--quality-metrics`: Show clustering quality metrics

### Quick Start Features

The tool supports smart defaults and flexible input methods for easier usage:

#### Default Algorithms
Each clustering method has optimized default parameters:
- **KMeans**: Automatic cluster number detection with elbow method
- **DBSCAN**: Adaptive eps and min_samples based on data characteristics
- **Hierarchical**: Ward linkage with automatic distance threshold
- **GMM**: Gaussian Mixture Model with BIC optimization

#### Flexible Input Methods
- **File input**: `--input data.jsonl`
- **Stdin (auto-detect)**: `cat data.jsonl | semantic-clustify ...`
- **Explicit stdin**: `--input -`

#### Minimal Example
```bash
# The simplest possible usage
cat vectorized_data.jsonl | semantic-clustify --embedding-field "embedding" --method "kmeans"
```

### Input Format

JSONL file with pre-computed vector embeddings:

```json
{"title": "Machine Learning Basics", "content": "Introduction to ML", "embedding": [0.1, 0.2, 0.3, ...]}
{"title": "Deep Learning Overview", "content": "Neural networks explained", "embedding": [0.15, 0.25, 0.35, ...]}
{"title": "Data Science Tools", "content": "Python libraries for data", "embedding": [0.8, 0.1, 0.2, ...]}
```

### Output Formats

#### Grouped Format (Default)
```json
[
  [
    {"title": "Machine Learning Basics", "content": "Introduction to ML", "embedding": [0.1, 0.2, 0.3, ...], "cluster_id": 0},
    {"title": "Deep Learning Overview", "content": "Neural networks explained", "embedding": [0.15, 0.25, 0.35, ...], "cluster_id": 0}
  ],
  [
    {"title": "Data Science Tools", "content": "Python libraries for data", "embedding": [0.8, 0.1, 0.2, ...], "cluster_id": 1}
  ]
]
```
**Best for**: Small-scale experimentation and analysis

#### Labeled Format
```json
{"title": "Machine Learning Basics", "content": "Introduction to ML", "embedding": [0.1, 0.2, 0.3, ...], "cluster_id": 0}
{"title": "Deep Learning Overview", "content": "Neural networks explained", "embedding": [0.15, 0.25, 0.35, ...], "cluster_id": 0}
{"title": "Data Science Tools", "content": "Python libraries for data", "embedding": [0.8, 0.1, 0.2, ...], "cluster_id": 1}
```
**Best for**: Basic pipeline processing with maximum memory efficiency

#### Enriched-Labeled Format
```json
{"title": "Machine Learning Basics", "content": "Introduction to ML", "embedding": [0.1, 0.2, 0.3, ...], "cluster_id": 0, "cluster_size": 150, "cluster_density": 0.85}
{"title": "Deep Learning Overview", "content": "Neural networks explained", "embedding": [0.15, 0.25, 0.35, ...], "cluster_id": 0, "cluster_size": 150, "cluster_density": 0.85}
{"title": "Data Science Tools", "content": "Python libraries for data", "embedding": [0.8, 0.1, 0.2, ...], "cluster_id": 1, "cluster_size": 75, "cluster_density": 0.72}
```
**Best for**: Context-rich pipelines where each document needs cluster statistics

#### Streaming-Grouped Format
```json
{"type": "clustering_metadata", "method": "kmeans", "n_clusters": 2, "timestamp": "2024-01-15T10:30:00Z"}
{"type": "cluster", "cluster_id": 0, "size": 150, "density": 0.85, "documents": [{"title": "ML Basics", ...}, {"title": "Deep Learning", ...}]}
{"type": "cluster", "cluster_id": 1, "size": 75, "density": 0.72, "documents": [{"title": "Data Science Tools", ...}]}
{"type": "clustering_summary", "total_clusters": 2, "total_documents": 225, "silhouette_score": 0.73}
```
**Best for**: Large-scale pipeline integration with structured metadata

## 🤖 Supported Algorithms

### KMeans Clustering
- **Best for**: Well-separated, spherical clusters
- **Auto-optimization**: Elbow method, silhouette analysis
- **Parameters**: n_clusters, init, max_iter
- **Performance**: Excellent for large datasets

### DBSCAN (Density-Based)
- **Best for**: Arbitrary shapes, noise detection
- **Auto-optimization**: Adaptive eps using k-distance graph
- **Parameters**: eps, min_samples
- **Performance**: Good for varying cluster densities

### Hierarchical Clustering
- **Best for**: Nested cluster structures
- **Auto-optimization**: Dendrogram analysis for optimal cuts
- **Parameters**: linkage, distance_threshold
- **Performance**: Good for small to medium datasets

### Gaussian Mixture Model (GMM)
- **Best for**: Overlapping clusters, probabilistic assignment
- **Auto-optimization**: BIC/AIC for component selection
- **Parameters**: n_components, covariance_type
- **Performance**: Good for probabilistic clustering

## 📚 Examples

### Example 1: Basic KMeans with automatic cluster detection

```bash
semantic-clustify \
  --input documents.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto \
  --quality-metrics \
  --output clustered_documents.jsonl
```

### Example 2: DBSCAN for density-based clustering

```bash
cat news_articles.jsonl | semantic-clustify \
  --embedding-field "vector" \
  --method "dbscan" \
  --min-cluster-size 3 \
  --output-format "labeled"
```

### Example 3: Hierarchical clustering with custom parameters

```bash
semantic-clustify \
  --input research_papers.jsonl \
  --embedding-field "text_embedding" \
  --method "hierarchical" \
  --n-clusters 8 \
  --output hierarchical_clusters.jsonl
```

### Example 3.1: Enhanced output formats for pipeline processing

```bash
# Enriched-labeled format with cluster statistics for filtering
semantic-clustify \
  --input documents.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto \
  --output-format "enriched-labeled" \
  --output enriched_clusters.jsonl

# Streaming-grouped format for large-scale pipeline integration
semantic-clustify \
  --input large_dataset.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto \
  --output-format "streaming-grouped" \
  --output pipeline_clusters.jsonl
```

### Example 4: Large-scale clustering with Faiss optimization

```bash
semantic-clustify \
  --input large_dataset.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto \
  --max-clusters 50 \
  --output-format "grouped"
```

### Example 5: Using stdin with quality metrics

```bash
echo '{"title": "Sample", "embedding": [0.1, 0.2, 0.3]}' | semantic-clustify \
  --input - \
  --embedding-field "embedding" \
  --method "kmeans" \
  --quality-metrics
```

### Example 6: GMM clustering for overlapping clusters

```bash
semantic-clustify \
  --input mixed_topics.jsonl \
  --embedding-field "semantic_vector" \
  --method "gmm" \
  --n-clusters auto \
  --output probabilistic_clusters.jsonl
```

### 🎯 CLI-First Development Workflow

For the most efficient development experience, we recommend starting with CLI experimentation:

```bash
# Step 1: Try the interactive workflow demo
python examples/cli_clustering_demo.py

# Step 2: Try the comprehensive clustering guide  
python examples/clustering_workflow_guide.py

# Step 3: Use your own vectorized data with CLI-first approach
```

**Benefits**: Fast iteration → Parameter tuning → Library integration → Optimal clustering

## 📚 Library Usage

For programmatic integration, `semantic-clustify` provides a powerful Python API that allows you to process data in-memory using List[Dict] format. **We recommend a CLI-first development workflow** for parameter optimization and result validation.

### 🔄 Recommended Development Workflow

#### Step 1: CLI Experimentation (Parameter Tuning)
Start with CLI commands on small datasets to find optimal parameters:

```bash
# Test different algorithms and parameters
semantic-clustify \
  --input small_sample.jsonl \
  --embedding-field "embedding" \
  --method "kmeans" \
  --n-clusters auto \
  --quality-metrics \
  --output test_kmeans.jsonl

# Compare with DBSCAN
semantic-clustify \
  --input small_sample.jsonl \
  --embedding-field "embedding" \
  --method "dbscan" \
  --quality-metrics \
  --output test_dbscan.jsonl

# Analyze results
head -10 test_kmeans.jsonl
python -c "import json; data=json.load(open('test_kmeans.jsonl')); print(f'Found {len(data)} clusters')"
```

#### Step 2: Library Integration (Optimized Parameters)
Switch to library usage with validated parameters:

```python
from semantic_clustify import SemanticClusterer

# Use parameters validated from CLI experiments
clusterer = SemanticClusterer(
    method="kmeans",
    n_clusters=5,  # From CLI optimization
    min_cluster_size=2
)

# Process data in memory
data = [
    {"title": "AI Research", "embedding": [0.1, 0.2, 0.3, ...]},
    {"title": "ML Applications", "embedding": [0.15, 0.25, 0.35, ...]},
    {"title": "Data Analysis", "embedding": [0.8, 0.1, 0.2, ...]}
]

# Perform clustering
clustered_groups = clusterer.fit_predict(data, vector_field="embedding")

# Results are grouped by cluster
for cluster_id, group in enumerate(clustered_groups):
    print(f"Cluster {cluster_id}: {len(group)} documents")
```

### 🚀 Quick Start with In-Memory Processing

```python
from semantic_clustify import SemanticClusterer

# Process data directly in memory
data = [
    {"title": "Python Programming", "content": "Learn Python", "embedding": [0.1, 0.2, 0.3]},
    {"title": "Machine Learning", "content": "ML concepts", "embedding": [0.15, 0.25, 0.35]},
    {"title": "Web Development", "content": "Build websites", "embedding": [0.8, 0.1, 0.2]},
    {"title": "Data Science", "content": "Analyze data", "embedding": [0.12, 0.22, 0.32]}
]

# Create clusterer with automatic cluster detection
clusterer = SemanticClusterer(
    method="kmeans",
    n_clusters="auto",
    min_cluster_size=2
)

# Perform clustering
clusters = clusterer.fit_predict(data, vector_field="embedding")

# Print results
for i, cluster in enumerate(clusters):
    print(f"\nCluster {i} ({len(cluster)} documents):")
    for doc in cluster:
        print(f"  - {doc['title']}")

# Get clustering metrics
metrics = clusterer.get_quality_metrics()
print(f"\nClustering Quality:")
print(f"Silhouette Score: {metrics['silhouette_score']:.3f}")
print(f"Number of Clusters: {metrics['n_clusters']}")
```

### 🔧 Advanced Library Integration

#### Batch Processing with Multiple Algorithms

```python
from semantic_clustify import SemanticClusterer, ClusteringComparator
from typing import List, Dict

def compare_clustering_methods(documents: List[Dict], 
                             vector_field: str = "embedding") -> Dict:
    """
    Compare different clustering algorithms and return best results.
    
    Args:
        documents: List of dictionaries with vector embeddings
        vector_field: Name of the field containing vectors
    
    Returns:
        Dictionary with comparison results and best clustering
    """
    
    methods = ["kmeans", "dbscan", "hierarchical", "gmm"]
    results = {}
    
    for method in methods:
        try:
            clusterer = SemanticClusterer(
                method=method,
                n_clusters="auto",
                min_cluster_size=2
            )
            
            clusters = clusterer.fit_predict(documents, vector_field=vector_field)
            metrics = clusterer.get_quality_metrics()
            
            results[method] = {
                "clusters": clusters,
                "metrics": metrics,
                "n_clusters": len(clusters),
                "silhouette_score": metrics.get("silhouette_score", 0)
            }
            
        except Exception as e:
            print(f"Method {method} failed: {e}")
            results[method] = None
    
    # Find best method by silhouette score
    best_method = max(
        [k for k, v in results.items() if v is not None],
        key=lambda k: results[k]["silhouette_score"]
    )
    
    return {
        "all_results": results,
        "best_method": best_method,
        "best_clusters": results[best_method]["clusters"],
        "comparison_summary": {
            method: {
                "n_clusters": res["n_clusters"] if res else 0,
                "silhouette": res["silhouette_score"] if res else 0
            } for method, res in results.items()
        }
    }

# Usage example
documents = [
    {"title": "AI Research", "embedding": [0.1, 0.2, 0.3]},
    {"title": "ML Applications", "embedding": [0.15, 0.25, 0.35]},
    {"title": "Data Analysis", "embedding": [0.8, 0.1, 0.2]},
    {"title": "Statistics", "embedding": [0.82, 0.12, 0.22]}
]

comparison = compare_clustering_methods(documents)
print(f"Best method: {comparison['best_method']}")
print(f"Best clustering has {len(comparison['best_clusters'])} clusters")
```

#### Dynamic Clustering Pipeline

```python
from semantic_clustify import SemanticClusterer
from typing import Dict, List, Optional
import logging

class DynamicClusteringPipeline:
    """
    Pipeline for adaptive clustering based on data characteristics.
    """
    
    def __init__(self, min_cluster_size: int = 2, max_clusters: int = 20):
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        self.clusterers = {}
        
    def analyze_data_characteristics(self, data: List[Dict], 
                                   vector_field: str) -> Dict:
        """Analyze data to suggest optimal clustering approach."""
        import numpy as np
        
        vectors = np.array([item[vector_field] for item in data])
        n_samples, n_features = vectors.shape
        
        # Calculate data characteristics
        characteristics = {
            "n_samples": n_samples,
            "n_features": n_features,
            "vector_std": float(np.std(vectors)),
            "vector_mean_norm": float(np.mean(np.linalg.norm(vectors, axis=1))),
            "suggested_method": self._suggest_method(n_samples, n_features)
        }
        
        return characteristics
    
    def _suggest_method(self, n_samples: int, n_features: int) -> str:
        """Suggest clustering method based on data size and characteristics."""
        if n_samples < 100:
            return "hierarchical"  # Good for small datasets
        elif n_samples < 1000:
            return "kmeans"  # Balanced approach
        else:
            return "kmeans"  # Scalable for large datasets
    
    def adaptive_clustering(self, data: List[Dict], 
                          vector_field: str,
                          method: Optional[str] = None) -> List[List[Dict]]:
        """Perform adaptive clustering based on data characteristics."""
        
        # Analyze data if method not specified
        if method is None:
            characteristics = self.analyze_data_characteristics(data, vector_field)
            method = characteristics["suggested_method"]
            logging.info(f"Auto-selected method: {method}")
        
        # Create or reuse clusterer
        if method not in self.clusterers:
            self.clusterers[method] = SemanticClusterer(
                method=method,
                n_clusters="auto",
                min_cluster_size=self.min_cluster_size,
                max_clusters=self.max_clusters
            )
        
        clusterer = self.clusterers[method]
        
        # Perform clustering
        clusters = clusterer.fit_predict(data, vector_field=vector_field)
        
        # Log results
        metrics = clusterer.get_quality_metrics()
        logging.info(f"Clustering completed: {len(clusters)} clusters, "
                    f"silhouette score: {metrics.get('silhouette_score', 'N/A')}")
        
        return clusters

# Usage example
pipeline = DynamicClusteringPipeline(min_cluster_size=3, max_clusters=15)

# Automatic method selection
clusters = pipeline.adaptive_clustering(documents, "embedding")

# Or force specific method
kmeans_clusters = pipeline.adaptive_clustering(documents, "embedding", method="kmeans")
```

### 🎯 Integration Patterns

#### Flask Web Application Integration

```python
# clustering_service.py
from semantic_clustify import SemanticClusterer
from flask import Flask, request, jsonify
from typing import List, Dict
import numpy as np

app = Flask(__name__)

class ClusteringService:
    """Service for real-time document clustering in web applications."""
    
    def __init__(self):
        # Pre-initialize clusterers for different scenarios
        self.clusterers = {
            "fast": SemanticClusterer(method="kmeans", n_clusters="auto"),
            "precise": SemanticClusterer(method="hierarchical", n_clusters="auto"),
            "density": SemanticClusterer(method="dbscan", min_cluster_size=3)
        }
    
    def cluster_documents(self, documents: List[Dict], 
                         vector_field: str = "embedding",
                         mode: str = "fast") -> Dict:
        """Cluster documents with specified quality mode."""
        
        if mode not in self.clusterers:
            mode = "fast"
        
        clusterer = self.clusterers[mode]
        
        try:
            clusters = clusterer.fit_predict(documents, vector_field=vector_field)
            metrics = clusterer.get_quality_metrics()
            
            return {
                "success": True,
                "clusters": clusters,
                "metrics": metrics,
                "n_clusters": len(clusters),
                "mode": mode
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mode": mode
            }
    
    def find_similar_clusters(self, query_vector: List[float], 
                            existing_clusters: List[List[Dict]],
                            vector_field: str = "embedding",
                            threshold: float = 0.7) -> List[int]:
        """Find clusters similar to a query vector."""
        similar_clusters = []
        
        for cluster_id, cluster in enumerate(existing_clusters):
            # Calculate cluster centroid
            vectors = [doc[vector_field] for doc in cluster]
            centroid = np.mean(vectors, axis=0)
            
            # Calculate similarity
            similarity = self._cosine_similarity(query_vector, centroid)
            
            if similarity >= threshold:
                similar_clusters.append(cluster_id)
        
        return similar_clusters
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_np, b_np = np.array(a), np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

# Initialize service
clustering_service = ClusteringService()

@app.route('/cluster', methods=['POST'])
def cluster_documents():
    """API endpoint for document clustering."""
    data = request.json
    
    documents = data.get('documents', [])
    vector_field = data.get('vector_field', 'embedding')
    mode = data.get('mode', 'fast')
    
    result = clustering_service.cluster_documents(
        documents, vector_field, mode
    )
    
    return jsonify(result)

@app.route('/find_similar', methods=['POST'])
def find_similar():
    """API endpoint for finding similar clusters."""
    data = request.json
    
    query_vector = data.get('query_vector')
    existing_clusters = data.get('clusters')
    threshold = data.get('threshold', 0.7)
    
    similar_clusters = clustering_service.find_similar_clusters(
        query_vector, existing_clusters, threshold=threshold
    )
    
    return jsonify({"similar_clusters": similar_clusters})

if __name__ == '__main__':
    app.run(debug=True)
```

#### Data Pipeline Integration

```python
import pandas as pd
from semantic_clustify import SemanticClusterer
from typing import Iterator, Dict

def clustering_pipeline(data_source: Iterator[Dict], 
                       output_path: str,
                       vector_field: str = "embedding",
                       method: str = "kmeans",
                       batch_size: int = 1000) -> None:
    """
    Process large datasets in batches with clustering.
    
    This approach handles memory efficiently for large datasets.
    """
    
    clusterer = SemanticClusterer(
        method=method,
        n_clusters="auto",
        min_cluster_size=2
    )
    
    batch = []
    processed_count = 0
    
    for item in data_source:
        batch.append(item)
        
        if len(batch) >= batch_size:
            # Process batch
            clusters = clusterer.fit_predict(batch, vector_field=vector_field)
            
            # Save batch results
            save_batch_clusters(clusters, output_path, processed_count)
            
            processed_count += len(batch)
            batch = []
            
            print(f"Processed {processed_count} items, found {len(clusters)} clusters")
    
    # Process remaining items
    if batch:
        clusters = clusterer.fit_predict(batch, vector_field=vector_field)
        save_batch_clusters(clusters, output_path, processed_count)

def save_batch_clusters(clusters: List[List[Dict]], 
                       output_path: str, 
                       batch_offset: int) -> None:
    """Save clustering results for a batch."""
    import json
    
    mode = 'a' if batch_offset > 0 else 'w'
    
    with open(output_path, mode) as f:
        for cluster_id, cluster in enumerate(clusters):
            cluster_data = {
                "batch_offset": batch_offset,
                "cluster_id": cluster_id,
                "documents": cluster,
                "size": len(cluster)
            }
            f.write(json.dumps(cluster_data) + '\n')

# Usage with pandas
def cluster_dataframe(df: pd.DataFrame, 
                     vector_column: str = "embedding",
                     method: str = "kmeans") -> pd.DataFrame:
    """Add cluster labels to a pandas DataFrame."""
    
    clusterer = SemanticClusterer(method=method, n_clusters="auto")
    
    # Convert DataFrame to list of dicts
    data = df.to_dict('records')
    
    # Perform clustering  
    clusters = clusterer.fit_predict(data, vector_field=vector_column)
    
    # Add cluster labels back to DataFrame
    cluster_labels = []
    for cluster_id, cluster in enumerate(clusters):
        for doc in cluster:
            # Find original index and assign cluster label
            original_idx = next(i for i, row in enumerate(data) if row == doc)
            cluster_labels.append((original_idx, cluster_id))
    
    # Sort by original index and extract labels
    cluster_labels.sort(key=lambda x: x[0])
    df['cluster_id'] = [label for _, label in cluster_labels]
    
    return df
```

### 🔍 Performance Optimization

#### Memory-Efficient Large-Scale Clustering

```python
from semantic_clustify import SemanticClusterer
import numpy as np
from typing import List, Dict, Generator

class LargeScaleClusterer:
    """
    Memory-efficient clustering for large datasets.
    """
    
    def __init__(self, method: str = "kmeans", 
                 chunk_size: int = 10000,
                 use_faiss: bool = True):
        self.method = method
        self.chunk_size = chunk_size
        self.use_faiss = use_faiss
        
    def cluster_large_dataset(self, data_generator: Generator[Dict, None, None],
                            vector_field: str = "embedding",
                            sample_ratio: float = 0.1) -> List[List[Dict]]:
        """
        Cluster large dataset using sampling and batch processing.
        
        Args:
            data_generator: Generator yielding data items
            vector_field: Field containing vector embeddings
            sample_ratio: Ratio of data to sample for initial clustering
        
        Returns:
            List of clusters
        """
        
        # Step 1: Sample data for initial clustering
        sample_data = self._sample_data(data_generator, sample_ratio)
        
        # Step 2: Perform clustering on sample
        sample_clusterer = SemanticClusterer(
            method=self.method,
            n_clusters="auto"
        )
        
        sample_clusters = sample_clusterer.fit_predict(
            sample_data, vector_field=vector_field
        )
        
        # Step 3: Extract cluster centroids
        centroids = self._extract_centroids(sample_clusters, vector_field)
        
        # Step 4: Assign remaining data to clusters
        full_clusters = self._assign_to_clusters(
            data_generator, centroids, vector_field
        )
        
        return full_clusters
    
    def _sample_data(self, data_generator: Generator, 
                    sample_ratio: float) -> List[Dict]:
        """Sample data from generator."""
        import random
        
        sample_data = []
        for item in data_generator:
            if random.random() < sample_ratio:
                sample_data.append(item)
                
            # Limit sample size
            if len(sample_data) >= 10000:
                break
        
        return sample_data
    
    def _extract_centroids(self, clusters: List[List[Dict]], 
                          vector_field: str) -> np.ndarray:
        """Extract cluster centroids."""
        centroids = []
        
        for cluster in clusters:
            vectors = np.array([doc[vector_field] for doc in cluster])
            centroid = np.mean(vectors, axis=0)
            centroids.append(centroid)
        
        return np.array(centroids)
    
    def _assign_to_clusters(self, data_generator: Generator,
                           centroids: np.ndarray,
                           vector_field: str) -> List[List[Dict]]:
        """Assign all data points to nearest centroids."""
        
        # Initialize clusters
        clusters = [[] for _ in range(len(centroids))]
        
        # Process data in chunks
        chunk = []
        for item in data_generator:
            chunk.append(item)
            
            if len(chunk) >= self.chunk_size:
                self._assign_chunk_to_clusters(chunk, centroids, clusters, vector_field)
                chunk = []
        
        # Process remaining chunk
        if chunk:
            self._assign_chunk_to_clusters(chunk, centroids, clusters, vector_field)
        
        return clusters
    
    def _assign_chunk_to_clusters(self, chunk: List[Dict],
                                 centroids: np.ndarray,
                                 clusters: List[List[Dict]],
                                 vector_field: str) -> None:
        """Assign chunk of data to clusters."""
        
        # Extract vectors from chunk
        vectors = np.array([item[vector_field] for item in chunk])
        
        # Calculate distances to centroids
        distances = np.linalg.norm(
            vectors[:, np.newaxis] - centroids[np.newaxis, :], 
            axis=2
        )
        
        # Assign to nearest centroid
        assignments = np.argmin(distances, axis=1)
        
        # Add to clusters
        for item, cluster_id in zip(chunk, assignments):
            item['cluster_id'] = int(cluster_id)
            clusters[cluster_id].append(item)

# Usage example
def process_large_jsonl(file_path: str, output_path: str):
    """Process large JSONL file with memory-efficient clustering."""
    
    def data_generator():
        import json
        with open(file_path, 'r') as f:
            for line in f:
                yield json.loads(line.strip())
    
    clusterer = LargeScaleClusterer(
        method="kmeans",
        chunk_size=5000,
        use_faiss=True
    )
    
    clusters = clusterer.cluster_large_dataset(
        data_generator(), 
        vector_field="embedding",
        sample_ratio=0.05  # Use 5% for initial clustering
    )
    
    # Save results
    import json
    with open(output_path, 'w') as f:
        json.dump(clusters, f, indent=2)
```

### 💡 Key Benefits of CLI-First + Library Workflow

1. **🔬 Fast Parameter Discovery**: CLI for quick algorithm and parameter testing
2. **📊 Quality Validation**: Easy visualization of clustering quality with CLI output
3. **🧪 Improved Reproducibility**: Validate parameters before library integration
4. **⚡ Optimized Performance**: Choose best algorithm based on data characteristics
5. **🎯 Custom Configuration**: Configure clustering per dataset or use case
6. **🔄 Seamless Transition**: Move from CLI prototyping to library integration
7. **🛡️ Production Ready**: Robust error handling and scalability options

### 🎯 CLI-First Workflow Benefits

- **Exploration Phase**: Use CLI with small datasets (100-1000 samples)
- **Parameter Tuning**: Test different algorithms and find optimal parameters
- **Quality Assessment**: Analyze silhouette scores and cluster distributions
- **Integration Phase**: Switch to library with validated configuration
- **Production Phase**: Scale up processing with optimized parameters

### 🔗 Next Steps

- Try the workflow: `python examples/clustering_workflow_guide.py`
- See [API Reference](#-api-reference) for detailed method documentation
- Check [Examples](#-examples) for more CLI usage patterns
- Review [Configuration](#️-configuration) for performance tuning

## 🔧 API Reference

### Python API Usage

```python
from semantic_clustify import SemanticClusterer

# Create clusterer
clusterer = SemanticClusterer(
    method="kmeans",
    n_clusters="auto",
    min_cluster_size=2,
    max_clusters=20
)

# Process data with vectors
data = [
    {"title": "Doc 1", "embedding": [0.1, 0.2, 0.3]},
    {"title": "Doc 2", "embedding": [0.15, 0.25, 0.35]}
]

clusters = clusterer.fit_predict(data, vector_field="embedding")

# Get quality metrics
metrics = clusterer.get_quality_metrics()
print(f"Silhouette Score: {metrics['silhouette_score']}")
```

### Available Clustering Methods

```python
from semantic_clustify import SemanticClusterer

# List all available methods
methods = SemanticClusterer.list_methods()
print(methods)
# ['kmeans', 'dbscan', 'hierarchical', 'gmm']

# Get method-specific parameters
params = SemanticClusterer.get_method_params("kmeans")
print(params)
```

### Core Classes

#### SemanticClusterer
```python
class SemanticClusterer:
    def __init__(self, method: str, n_clusters: Union[int, str] = "auto", 
                 min_cluster_size: int = 2, max_clusters: int = 20, **kwargs)
    
    def fit_predict(self, data: List[Dict], vector_field: str) -> List[List[Dict]]
    def get_quality_metrics(self) -> Dict[str, float]
    def predict_new_data(self, new_data: List[Dict], vector_field: str) -> List[int]
```

#### ClusteringComparator
```python
class ClusteringComparator:
    def compare_methods(self, data: List[Dict], vector_field: str, 
                       methods: List[str]) -> Dict[str, Dict]
    def get_best_method(self, comparison_results: Dict) -> str
```

## ⚙️ Configuration

### Algorithm Parameters

#### KMeans
```python
clusterer = SemanticClusterer(
    method="kmeans",
    n_clusters=5,          # Number of clusters
    init="k-means++",      # Initialization method
    max_iter=300,          # Maximum iterations
    random_state=42        # For reproducibility
)
```

#### DBSCAN
```python
clusterer = SemanticClusterer(
    method="dbscan",
    eps=0.5,               # Neighborhood radius
    min_samples=5,         # Minimum samples per cluster
    metric="cosine"        # Distance metric
)
```

#### Hierarchical
```python
clusterer = SemanticClusterer(
    method="hierarchical",
    n_clusters=5,          # Number of clusters
    linkage="ward",        # Linkage criterion
    distance_threshold=None # Distance threshold (alternative to n_clusters)
)
```

#### Gaussian Mixture Model
```python
clusterer = SemanticClusterer(
    method="gmm",
    n_components=5,        # Number of components
    covariance_type="full", # Covariance type
    max_iter=100           # Maximum iterations
)
```

### Performance Settings

```python
# For large datasets
clusterer = SemanticClusterer(
    method="kmeans",
    use_faiss=True,        # Enable Faiss optimization
    batch_size=10000,      # Batch processing size
    n_jobs=-1              # Use all CPU cores
)
```

### Output Formats

```python
# Configure output format
clusterer = SemanticClusterer(
    method="kmeans",
    output_format="grouped",    # or "labeled"
    include_metrics=True,       # Include quality metrics
    include_centroids=True      # Include cluster centroids
)
```

## 🔍 Performance Tips

1. **Algorithm Selection**: 
   - Use KMeans for well-separated clusters
   - Use DBSCAN for arbitrary shapes and noise detection
   - Use Hierarchical for nested structures
   - Use GMM for overlapping clusters

2. **Large Dataset Optimization**:
   - Enable Faiss for datasets >10k documents
   - Use sampling for initial parameter tuning
   - Process in batches to manage memory

3. **Vector Quality**:
   - Ensure vectors are normalized
   - Use appropriate embedding dimensions (384-768 recommended)
   - Consider dimensionality reduction for very high-dimensional vectors

4. **Parameter Tuning**:
   - Start with auto-detection for number of clusters
   - Use silhouette score for quality assessment
   - Validate with small samples before full processing

5. **Memory Management**:
   - Use batch processing for large datasets
   - Consider streaming processing for very large files

## 🐛 Troubleshooting

### Common Issues

**Import Error**: Missing dependencies
```bash
pip install scikit-learn faiss-cpu numpy
```

**Memory Error**: Large dataset processing
```bash
# Use batch processing or sampling
semantic-clustify --input large_file.jsonl --batch-size 5000
```

**Poor Clustering Quality**: Low silhouette score
- Try different algorithms (DBSCAN instead of KMeans)
- Adjust parameters (eps, min_samples)
- Check vector quality and normalization

**Empty Clusters**: No documents in some clusters
- Reduce number of clusters
- Increase min_cluster_size parameter
- Check for duplicate or invalid vectors

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Automated setup (recommended)
git clone https://github.com/changyy/py-semantic-clustify.git
cd py-semantic-clustify
./setup.sh

# Manual setup
git clone https://github.com/changyy/py-semantic-clustify.git
cd py-semantic-clustify
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

**Using the test runner (recommended):**
```bash
# Quick validation (fastest)
python test_runner.py --quick

# Core functionality tests
python test_runner.py --core

# Algorithm-specific tests
python test_runner.py --algorithms

# Performance tests
python test_runner.py --performance

# All tests
python test_runner.py --all

# Tests with coverage report
python test_runner.py --coverage
```

**Direct pytest commands:**
```bash
# Quick smoke tests
pytest -m "quick or smoke" -v

# Core clustering functionality
pytest -m "core" -v

# Algorithm-specific tests
pytest -m "kmeans" -v
pytest -m "dbscan" -v
pytest -m "hierarchical" -v

# Integration tests
pytest -m "integration" -v

# All tests
pytest -v

# With coverage
pytest --cov=semantic_clustify --cov-report=html -v
```

### Development Tools

The project includes a convenient development script and tools organized in the `tools/` directory:

```bash
# Quick development commands (using dev.py script)
python dev.py install      # Install in development mode
python dev.py test         # Run all tests
python dev.py test-quick   # Run quick smoke tests
python dev.py test-coverage # Run tests with coverage
python dev.py typecheck    # Run mypy type checking
python dev.py lint         # Run flake8 linting
python dev.py format       # Format code with black
python dev.py clean        # Clean build artifacts
python dev.py build        # Build distribution packages
python dev.py demo         # Run comprehensive demo

# Traditional pytest commands
pytest -v                  # All tests
pytest -m "quick or smoke" # Quick tests only
pytest --cov=semantic_clustify --cov-report=html -v  # With coverage

# Tools directory contains:
# - tools/demo_comprehensive.py     # Comprehensive feature demonstration
# - tools/test_runner.py           # Advanced test runner with options
# - tools/setup.sh                 # Development environment setup
# - tools/README.md                # Detailed tools documentation
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📊 Benchmarks

| Algorithm | Dataset Size | Time (seconds) | Memory (MB) | Silhouette Score |
|-----------|--------------|----------------|-------------|------------------|
| KMeans | 1,000 docs | 0.5 | 50 | 0.45 |
| KMeans | 10,000 docs | 3.2 | 200 | 0.42 |
| DBSCAN | 1,000 docs | 0.8 | 60 | 0.38 |
| DBSCAN | 10,000 docs | 8.5 | 250 | 0.35 |
| Hierarchical | 1,000 docs | 1.2 | 80 | 0.48 |
| GMM | 1,000 docs | 2.1 | 90 | 0.41 |

*Benchmarks on Intel i7, 16GB RAM, 768-dimensional vectors*

## 🔗 Related Projects

- [text-vectorify](https://github.com/changyy/py-text-vectorify) - Text vectorization preprocessing
- [scikit-learn](https://github.com/scikit-learn/scikit-learn) - Core clustering algorithms
- [Faiss](https://github.com/facebookresearch/faiss) - Efficient similarity search and clustering

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/changyy/py-semantic-clustify/issues)
- **Documentation**: [Full documentation](https://github.com/changyy/py-semantic-clustify/wiki)

## 🎯 Integration with text-vectorify

**semantic-clustify** is designed to work seamlessly with [text-vectorify](https://github.com/changyy/py-text-vectorify):

```bash
# Step 1: Generate embeddings
text-vectorify \
  --input articles.jsonl \
  --input-field-main "title" \
  --input-field-subtitle "content" \
  --process-method "BGEEmbedder" \
  --output vectorized_articles.jsonl

# Step 2: Cluster documents  
semantic-clustify \
  --input vectorized_articles.jsonl \
  --embedding-field "vector" \
  --method "kmeans" \
  --n-clusters auto \
  --output clustered_articles.jsonl
```

---

Made with ❤️ for the semantic analysis community
