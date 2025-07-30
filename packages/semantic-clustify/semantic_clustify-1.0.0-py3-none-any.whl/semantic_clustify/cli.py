"""
Command Line Interface for semantic-clustify.

This module provides the CLI interface for the semantic clustering tool,
supporting both file input and stdin processing with flexible output formats.
"""

import click
import sys
import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

from .core import SemanticClusterer
from .utils import (
    load_jsonl,
    save_jsonl,
    save_grouped_jsonl,
    flatten_clusters,
    read_from_stdin,
    generate_output_filename,
    setup_logging,
    print_cluster_summary,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    type=str,
    default=None,
    help="Path to input JSONL file (use '-' for stdin, or omit to auto-detect stdin)",
)
@click.option(
    "--embedding-field",
    "--vector-field",  # Keep for backward compatibility
    type=str,
    required=True,
    help="Name of the field containing vector embeddings",
)
@click.option(
    "--method",
    "-m",
    type=click.Choice(["kmeans", "dbscan", "hierarchical", "gmm"]),
    required=True,
    help="Clustering algorithm to use",
)
@click.option(
    "--n-clusters",
    "-k",
    type=str,
    default="auto",
    help="Number of clusters (integer or 'auto' for automatic detection)",
)
@click.option(
    "--min-cluster-size", type=int, default=2, help="Minimum cluster size (default: 2)"
)
@click.option(
    "--max-clusters",
    type=int,
    default=20,
    help="Maximum clusters for auto-detection (default: 20)",
)
@click.option(
    "--output-format",
    type=click.Choice(["grouped", "labeled"]),
    default="grouped",
    help="Output format: 'grouped' (list of lists) or 'labeled' (flat with cluster_id)",
)
@click.option(
    "--output",
    "-o",
    type=str,
    default=None,
    help="Output file path (default: auto-generated)",
)
@click.option(
    "--quality-metrics",
    is_flag=True,
    default=False,
    help="Show clustering quality metrics",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging"
)
@click.option(
    "--eps",
    type=float,
    default=None,
    help="DBSCAN epsilon parameter (auto-estimated if not provided)",
)
@click.option(
    "--min-samples",
    type=int,
    default=None,
    help="DBSCAN min_samples parameter (defaults to min_cluster_size)",
)
@click.option(
    "--linkage",
    type=click.Choice(["ward", "complete", "average", "single"]),
    default="ward",
    help="Hierarchical clustering linkage method (default: ward)",
)
@click.option(
    "--covariance-type",
    type=click.Choice(["full", "tied", "diag", "spherical"]),
    default="full",
    help="GMM covariance type (default: full)",
)
@click.option(
    "--random-state",
    type=int,
    default=42,
    help="Random state for reproducibility (default: 42)",
)
def main(
    input: Optional[str],
    embedding_field: str,
    method: str,
    n_clusters: str,
    min_cluster_size: int,
    max_clusters: int,
    output_format: str,
    output: Optional[str],
    quality_metrics: bool,
    verbose: bool,
    eps: Optional[float],
    min_samples: Optional[int],
    linkage: str,
    covariance_type: str,
    random_state: int,
) -> None:
    """
    Semantic clustering tool for text documents using vector embeddings.

    This tool groups text documents by semantic similarity using pre-computed
    vector embeddings. It supports multiple clustering algorithms and automatic
    parameter optimization.

    Examples:

        # Basic usage with file input
        semantic-clustify --input data.jsonl --embedding-field "embedding" --method "kmeans"

        # Using stdin input
        cat data.jsonl | semantic-clustify --embedding-field "embedding" --method "kmeans"

        # Auto-detect optimal cluster number
        semantic-clustify --input data.jsonl --embedding-field "vector" --method "kmeans" --n-clusters auto

        # DBSCAN with custom parameters
        semantic-clustify --input data.jsonl --embedding-field "embedding" --method "dbscan" --eps 0.5
    """

    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    try:
        # Parse n_clusters parameter
        n_clusters_param: Union[int, str]
        if n_clusters.lower() == "auto":
            n_clusters_param = "auto"
        else:
            try:
                n_clusters_val = int(n_clusters)
                if n_clusters_val < 2:
                    raise click.BadParameter("n_clusters must be at least 2 or 'auto'")
                n_clusters_param = n_clusters_val
            except ValueError:
                raise click.BadParameter("n_clusters must be an integer or 'auto'")

        # Determine input source
        if input is None:
            # Auto-detect stdin if no input specified
            if not sys.stdin.isatty():
                logger.info("Auto-detected stdin input")
                data = read_from_stdin()
                input_name = "stdin"
            else:
                raise click.ClickException(
                    "No input provided. Use --input <file> or pipe data to stdin."
                )
        elif input == "-":
            # Explicit stdin
            logger.info("Reading from stdin")
            data = read_from_stdin()
            input_name = "stdin"
        else:
            # File input
            if not Path(input).exists():
                raise click.ClickException(f"Input file not found: {input}")
            logger.info(f"Reading from file: {input}")
            data = load_jsonl(input)
            input_name = input

        if not data:
            raise click.ClickException("No data loaded from input")

        logger.info(f"Loaded {len(data)} documents")

        # Prepare algorithm-specific parameters
        algo_kwargs = {}
        if method == "dbscan":
            if eps is not None:
                algo_kwargs["eps"] = eps
            if min_samples is not None:
                algo_kwargs["min_samples"] = min_samples
        elif method == "hierarchical":
            algo_kwargs["linkage"] = linkage  # type: ignore[assignment]
        elif method == "gmm":
            algo_kwargs["covariance_type"] = covariance_type  # type: ignore[assignment]

        # Create clusterer
        clusterer = SemanticClusterer(
            method=method,
            n_clusters=n_clusters_param,
            min_cluster_size=min_cluster_size,
            max_clusters=max_clusters,
            random_state=random_state,
            **algo_kwargs,
        )

        # Perform clustering
        logger.info(f"Starting {method} clustering...")
        clusters = clusterer.fit_predict(data, vector_field=embedding_field)

        # Print summary
        print_cluster_summary(clusters, show_details=verbose)

        # Show quality metrics if requested
        if quality_metrics:
            metrics = clusterer.get_quality_metrics()
            print(f"\n📈 Quality Metrics:")
            print(f"   Silhouette Score: {metrics.get('silhouette_score', 'N/A')}")
            print(
                f"   Calinski-Harabasz Score: {metrics.get('calinski_harabasz_score', 'N/A')}"
            )
            print(
                f"   Davies-Bouldin Score: {metrics.get('davies_bouldin_score', 'N/A')}"
            )
            print(f"   Number of Clusters: {metrics.get('n_clusters', 'N/A')}")
            print(f"   Number of Noise Points: {metrics.get('n_noise', 'N/A')}")

        # Determine output filename
        if output is None:
            output = generate_output_filename(input_name, method, output_format)

        # Save results
        if output_format == "grouped":
            save_grouped_jsonl(clusters, output)
        else:  # labeled
            flattened = flatten_clusters(clusters)
            save_jsonl(flattened, output)

        print(f"\n✅ Clustering completed successfully!")
        print(f"   Output saved to: {output}")
        print(f"   Format: {output_format}")
        print(f"   Clusters: {len(clusters)}")
        print(f"   Documents: {sum(len(cluster) for cluster in clusters)}")

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


@click.command()
@click.option("--input", "-i", type=str, required=True, help="Path to input JSONL file")
@click.option(
    "--embedding-field",
    "--vector-field",  # Keep for backward compatibility
    type=str,
    required=True,
    help="Name of the field containing vector embeddings",
)
@click.option(
    "--methods",
    type=str,
    default="kmeans,dbscan,hierarchical",
    help="Comma-separated list of methods to compare (default: kmeans,dbscan,hierarchical)",
)
@click.option(
    "--output-dir",
    type=str,
    default="comparison_results",
    help="Output directory for comparison results",
)
@click.option(
    "--max-clusters", type=int, default=10, help="Maximum clusters for comparison"
)
def compare(
    input: str,
    embedding_field: str,
    methods: str,
    output_dir: str,
    max_clusters: int,
) -> None:
    """
    Compare different clustering algorithms on the same dataset.

    This command runs multiple clustering algorithms and compares their results,
    providing quality metrics and visualizations for each method.
    """
    setup_logging("INFO")

    try:
        # Load data
        data = load_jsonl(input)
        logger.info(f"Loaded {len(data)} documents for comparison")

        # Parse methods
        method_list = [m.strip() for m in methods.split(",")]
        valid_methods = ["kmeans", "dbscan", "hierarchical", "gmm"]

        for method in method_list:
            if method not in valid_methods:
                raise click.BadParameter(
                    f"Invalid method: {method}. Valid methods: {valid_methods}"
                )

        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        results = {}

        # Run each method
        for method in method_list:
            logger.info(f"Running {method} clustering...")

            try:
                clusterer = SemanticClusterer(
                    method=method,
                    n_clusters="auto",
                    max_clusters=max_clusters,
                    random_state=42,
                )

                clusters = clusterer.fit_predict(data, vector_field=embedding_field)
                metrics = clusterer.get_quality_metrics()

                # Save results
                output_file = Path(output_dir) / f"{method}_clusters.jsonl"
                save_grouped_jsonl(clusters, str(output_file))

                results[method] = {
                    "clusters": len(clusters),
                    "total_docs": sum(len(cluster) for cluster in clusters),
                    "silhouette_score": metrics.get("silhouette_score"),
                    "calinski_harabasz_score": metrics.get("calinski_harabasz_score"),
                    "davies_bouldin_score": metrics.get("davies_bouldin_score"),
                    "output_file": str(output_file),
                }

                logger.info(f"{method} completed: {len(clusters)} clusters")

            except Exception as e:
                logger.error(f"Failed to run {method}: {e}")
                results[method] = {"error": str(e)}

        # Print comparison results
        print(f"\n📊 Clustering Algorithm Comparison:")
        print(
            f"{'Method':<12} {'Clusters':<10} {'Silhouette':<12} {'CH Score':<12} {'DB Score':<12}"
        )
        print("-" * 70)

        for method, result in results.items():
            if "error" in result:
                print(f"{method:<12} {'ERROR':<10} {result['error']}")
            else:
                sil = (
                    f"{result['silhouette_score']:.3f}"
                    if result["silhouette_score"]
                    else "N/A"
                )
                ch = (
                    f"{result['calinski_harabasz_score']:.1f}"
                    if result["calinski_harabasz_score"]
                    else "N/A"
                )
                db = (
                    f"{result['davies_bouldin_score']:.3f}"
                    if result["davies_bouldin_score"]
                    else "N/A"
                )

                print(
                    f"{method:<12} {result['clusters']:<10} {sil:<12} {ch:<12} {db:<12}"
                )

        # Save comparison summary
        summary_file = Path(output_dir) / "comparison_summary.json"
        import json

        with open(summary_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Comparison completed!")
        print(f"   Results saved to: {output_dir}")
        print(f"   Summary: {summary_file}")

    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        sys.exit(1)


# Create a CLI group to support multiple commands
@click.group()
def cli() -> None:
    """semantic-clustify: Semantic clustering tool for text documents."""
    pass


# Add commands to the group
cli.add_command(main, name="cluster")
cli.add_command(compare)


# For backward compatibility, also export main directly
def main_entry() -> None:
    """Entry point for the semantic-clustify CLI."""
    main()


if __name__ == "__main__":
    main()
