"""
savecode/utils/__init__.py - Initializes the utils module for savecode.

This module now re-exports selected functions from path_utils.
"""

__all__ = ["normalize_path", "relative_path"]
from .path_utils import normalize_path, relative_path
