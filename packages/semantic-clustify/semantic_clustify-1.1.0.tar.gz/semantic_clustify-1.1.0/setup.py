#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

def read_file(file_path):
    """Read file content."""
    return Path(file_path).read_text(encoding="utf-8").strip()

def get_version():
    """Extract version from __init__.py."""
    init_file = Path("semantic_clustify") / "__init__.py"
    content = read_file(init_file)
    for line in content.split('\n'):
        if line.startswith('__version__'):
            return line.split('=')[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")

# Read version
version = get_version()

# Read README
long_description = read_file("README.md")

setup(
    name="semantic-clustify",
    version=version,
    author="changyy",
    author_email="changyy.csie@gmail.com",
    description="A powerful and flexible Python tool for semantic clustering of text documents using vector embeddings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/changyy/py-semantic-clustify",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "click>=8.0.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "faiss": ["faiss-cpu>=1.7.0"],
        "advanced": [
            "scipy>=1.7.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
        "all": [
            "faiss-cpu>=1.7.0",
            "scipy>=1.7.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "semantic-clustify=semantic_clustify.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
