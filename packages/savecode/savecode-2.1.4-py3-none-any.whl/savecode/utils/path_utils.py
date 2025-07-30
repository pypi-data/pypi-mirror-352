"""
savecode/utils/path_utils.py - Utility functions for path manipulation.
Provides functions to normalize file paths and get relative paths.
"""

import os


def normalize_path(path: str) -> str:
    """
    Returns a normalized absolute path for the given path.

    :param path: The input file path.
    :return: A normalized absolute file path.
    """
    return os.path.normpath(os.path.abspath(path))


def relative_path(path: str) -> str:
    """
    Returns the relative path of the given absolute path relative to the current working directory.

    :param path: The absolute file path.
    :return: The file path relative to the current working directory.
    """
    return os.path.relpath(path, os.getcwd())
