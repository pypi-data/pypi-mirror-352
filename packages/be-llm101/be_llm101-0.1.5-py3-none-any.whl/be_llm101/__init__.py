"""
be-llm101: A Python package for LLM-related utilities and functions.

This package provides utilities and functions for working with Large Language Models (LLMs).
"""

# Import main functions to make them available at package level
from .utils import get_data_path, load_data

# Version info - only available when package is installed
try:
    from importlib.metadata import version, metadata

    __version__ = version("be-llm101")

    # Get author info from package metadata
    _metadata = metadata("be-llm101")
    _authors = _metadata.get("Author", "").split(",") if _metadata.get("Author") else []
    __author__ = _authors[0].strip() if _authors else "Unknown"
    __email__ = _metadata.get("Author-email", "unknown@example.com")
except (ImportError, Exception):
    # Fallback when package is not installed or importlib_metadata not available
    __version__ = "dev"
    __author__ = "Unknown"
    __email__ = "unknown@example.com"
