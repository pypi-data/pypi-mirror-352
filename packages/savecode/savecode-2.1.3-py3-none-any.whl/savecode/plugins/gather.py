"""
savecode/plugins/gather.py - Module for gathering source files with robust skip filtering.
This module defines a plugin that searches specified directories and files for source files with the specified extensions,
while skipping those that match provided skip patterns.
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, List
from savecode.plugin_manager.manager import register_plugin
from savecode.plugin_manager.decorators import handle_plugin_errors
from savecode.utils.path_utils import normalize_path
from savecode.utils.error_handler import log_and_record_error

logger = logging.getLogger("savecode.plugins.gather")


def should_skip(path: str, skip_patterns: List[str]) -> bool:
    """
    Determines whether a given path (directory or file) should be skipped based on provided skip patterns.

    For each skip pattern:
      - If the pattern contains a path separator, normalize and check if it is a substring of the normalized path.
      - Otherwise, check if the basename of the normalized pattern is present in the path's components.

    Args:
        path (str): The file or directory path to check.
        skip_patterns (List[str]): List of skip patterns.

    Returns:
        bool: True if the path should be skipped, False otherwise.
    """
    norm_path = normalize_path(path)
    for pattern in skip_patterns:
        norm_pattern = normalize_path(pattern)
        if os.sep in pattern:
            if norm_pattern in norm_path:
                return True
        else:
            if os.path.basename(norm_pattern) in norm_path.split(os.sep):
                return True
    return False


@register_plugin(order=20)
class GatherPlugin:
    """Plugin for gathering Python files from directories and individual file paths."""

    @handle_plugin_errors
    def run(self, context: Dict[str, Any]) -> None:
        """
        Execute the gathering process.

        Expects in context:
          - 'roots': List of directories or file paths.
          - 'files': List of directories or file paths.
          - 'skip': List of skip patterns (for directories or files to ignore).

        Populates context with:
          - 'all_files': Deduplicated list of gathered source files with specified extensions.

        Args:
            context (Dict[str, Any]): Shared context containing parameters and data.

        Returns:
            None
        """
        # Skip if all_files is already populated by another plugin (e.g. GitStatusPlugin)
        if context.get("all_files") is not None:
            return

        gathered_files: List[str] = []
        # Combine roots and files into a single list.
        entries = context.get("roots", []) + context.get("files", [])
        skip_patterns = context.get("skip", [])
        for entry in entries:
            normalized_entry = normalize_path(entry)
            if should_skip(normalized_entry, skip_patterns):
                continue
            if os.path.isdir(normalized_entry):
                gathered_files.extend(
                    self.gather_files(normalized_entry, skip_patterns, context)
                )
            elif os.path.isfile(normalized_entry) and self._matches(
                normalized_entry, context["extensions"]
            ):
                gathered_files.append(normalized_entry)
            else:
                warning_msg = f"{entry} is not a valid source file or directory."
                log_and_record_error(warning_msg, context, logger)
        # Deduplicate while preserving order.
        deduped_files = list(dict.fromkeys(gathered_files))
        context["all_files"] = deduped_files
        logger.info("Gathered %d unique source files.", len(deduped_files))

    def gather_files(
        self, root_dir: str, skip_patterns: List[str], context: Dict[str, Any]
    ) -> List[str]:
        """
        Recursively gather all source files with specified extensions from a normalized directory, skipping specified directories and files.

        Args:
            root_dir (str): Normalized absolute directory path to search for source files.
            skip_patterns (List[str]): List of skip patterns for directories or files.
            context (Dict[str, Any]): Context containing extensions and for error aggregation.

        Returns:
            List[str]: List of gathered source file paths.
        """
        py_files: List[str] = []
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Filter out directories that match the skip patterns.
            dirnames[:] = [
                d
                for d in dirnames
                if not should_skip(os.path.join(dirpath, d), skip_patterns)
            ]
            for fname in filenames:
                file_path = os.path.join(dirpath, fname)
                if self._matches(file_path, context["extensions"]) and not should_skip(
                    file_path, skip_patterns
                ):
                    py_files.append(file_path)
        return py_files

    @staticmethod
    def _matches(path: str, exts: List[str]) -> bool:
        """Check if a file path has an extension matching any in the provided list.

        Args:
            path: The file path to check
            exts: List of extensions (without dots)

        Returns:
            True if the file has a matching extension
        """
        file_ext = Path(path).suffix.lstrip(".").lower()
        return file_ext in exts


# End of savecode/plugins/gather.py
