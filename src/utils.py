"""
Utility functions used throughout the OCR pipeline.
"""

from pathlib import Path


def ensure_directory(path):
    """
    Creates directory if it doesn't exist.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def print_separator():
    print("-" * 60)


def file_exists(path):
    return Path(path).exists()