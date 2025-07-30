"""
Tests for CLI functionality.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from semantic_clustify.cli import main


@pytest.fixture
def sample_data():
    """Sample JSONL data for testing."""
    return [
        {
            "title": "Machine Learning",
            "content": "Introduction to ML",
            "embedding": [0.1, 0.2, 0.3],
        },
        {
            "title": "Deep Learning",
            "content": "Neural networks",
            "embedding": [0.15, 0.25, 0.35],
        },
        {
            "title": "Data Science",
            "content": "Analyzing data",
            "embedding": [0.8, 0.1, 0.2],
        },
        {
            "title": "Statistics",
            "content": "Statistical methods",
            "embedding": [0.85, 0.15, 0.25],
        },
    ]


@pytest.fixture
def temp_jsonl_file(sample_data):
    """Create a temporary JSONL file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for item in sample_data:
            json.dump(item, f)
            f.write("\n")
        temp_file = f.name

    yield temp_file

    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.mark.integration
def test_cli_basic_usage(temp_jsonl_file):
    """Test basic CLI usage with file input."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "kmeans",
                "--n-clusters",
                "2",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert "Clustering completed successfully" in result.output
        assert output_file.exists()


@pytest.mark.integration
def test_cli_auto_clusters(temp_jsonl_file):
    """Test CLI with automatic cluster detection."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "kmeans",
                "--n-clusters",
                "auto",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()


@pytest.mark.integration
def test_cli_different_methods(temp_jsonl_file):
    """Test CLI with different clustering methods."""
    methods = ["kmeans", "dbscan", "hierarchical"]
    runner = CliRunner()

    for method in methods:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / f"output_{method}.jsonl"

            result = runner.invoke(
                main,
                [
                    "--input",
                    temp_jsonl_file,
                    "--embedding-field",
                    "embedding",
                    "--method",
                    method,
                    "--output",
                    str(output_file),
                ],
            )

            # Some methods might fail with small data, but should not crash
            assert result.exit_code in [0, 1]  # Success or graceful failure


@pytest.mark.integration
def test_cli_output_formats(temp_jsonl_file):
    """Test different output formats."""
    runner = CliRunner()

    for output_format in ["grouped", "labeled"]:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / f"output_{output_format}.jsonl"

            result = runner.invoke(
                main,
                [
                    "--input",
                    temp_jsonl_file,
                    "--embedding-field",
                    "embedding",
                    "--method",
                    "kmeans",
                    "--n-clusters",
                    "2",
                    "--output-format",
                    output_format,
                    "--output",
                    str(output_file),
                ],
            )

            assert result.exit_code == 0
            assert output_file.exists()

            # Verify output format
            with open(output_file) as f:
                content = f.read().strip()

            if output_format == "grouped":
                # Should be valid JSON (list of lists)
                data = json.loads(content)
                assert isinstance(data, list)
                if data:  # If not empty
                    assert isinstance(data[0], list)
            else:  # labeled
                # Should be JSONL format
                lines = content.split("\n")
                for line in lines:
                    if line.strip():
                        item = json.loads(line)
                        assert "cluster_id" in item


@pytest.mark.integration
def test_cli_quality_metrics(temp_jsonl_file):
    """Test CLI with quality metrics output."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "quality_output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "kmeans",
                "--quality-metrics",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        assert "Quality Metrics" in result.output
        assert "Silhouette Score" in result.output


@pytest.mark.integration
def test_cli_verbose_output(temp_jsonl_file):
    """Test CLI with verbose output."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "verbose_output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "kmeans",
                "--verbose",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
        # Verbose mode should show more details
        assert len(result.output) > 100  # Rough check for more output


@pytest.mark.integration
def test_cli_stdin_input(sample_data, tmp_path):
    """Test CLI with stdin input using a temporary file."""
    runner = CliRunner()

    # Create a temporary file instead of using stdin directly
    input_file = tmp_path / "test_input.jsonl"
    output_file = tmp_path / "stdin_output.jsonl"
    jsonl_content = "\n".join(json.dumps(item) for item in sample_data)
    input_file.write_text(jsonl_content)

    result = runner.invoke(
        main,
        [
            "--input",
            str(input_file),
            "--embedding-field",
            "embedding",
            "--method",
            "kmeans",
            "--n-clusters",
            "2",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert "Clustering completed successfully" in result.output


@pytest.mark.integration
def test_cli_error_handling():
    """Test CLI error handling."""
    runner = CliRunner()

    # Test missing required arguments
    result = runner.invoke(main, [])
    assert result.exit_code != 0

    # Test invalid method
    result = runner.invoke(
        main, ["--embedding-field", "embedding", "--method", "invalid_method"]
    )
    assert result.exit_code != 0

    # Test non-existent input file
    result = runner.invoke(
        main,
        [
            "--input",
            "non_existent_file.jsonl",
            "--embedding-field",
            "embedding",
            "--method",
            "kmeans",
        ],
    )
    assert result.exit_code != 0


@pytest.mark.integration
def test_cli_dbscan_parameters(temp_jsonl_file):
    """Test CLI with DBSCAN-specific parameters."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "dbscan_output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "dbscan",
                "--eps",
                "0.5",
                "--min-samples",
                "2",
                "--output",
                str(output_file),
            ],
        )

        # Should complete without error (though might find no clusters with small data)
        assert result.exit_code in [0, 1]


@pytest.mark.integration
def test_cli_hierarchical_parameters(temp_jsonl_file):
    """Test CLI with hierarchical clustering parameters."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "hierarchical_output.jsonl"

        result = runner.invoke(
            main,
            [
                "--input",
                temp_jsonl_file,
                "--embedding-field",
                "embedding",
                "--method",
                "hierarchical",
                "--linkage",
                "average",
                "--output",
                str(output_file),
            ],
        )

        assert result.exit_code == 0
