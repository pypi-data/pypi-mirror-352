"""
savecode/utils/display.py - Module for displaying file list and summary in CLI.
"""

import os
from collections import defaultdict
from typing import Any, Dict, List
from savecode.utils.colors import BLUE, WHITE, BG_CYAN, RESET
from savecode.utils.path_utils import relative_path


def display_summary(context: Dict[str, Any]) -> None:
    """
    Displays a summary of the saved source files, grouped by directory.

    Expects the context to have:
      - 'all_files': list of source file paths.
      - 'output': the output file path.

    The function groups files by their directory, prints a header for each group with a newline
    separation, and then prints a summary line indicating the total number of files saved and the output file path.
    """
    all_files: List[str] = context.get("all_files", [])
    output = context.get("output", "./temp.txt")

    # Group files by their directory.
    grouped_files = defaultdict(list)
    for file in all_files:
        rel_path = relative_path(file)
        dir_name = os.path.dirname(rel_path)
        # Use "root" as header if file is in the current directory.
        header = dir_name if dir_name else "root"
        grouped_files[header].append(rel_path)

    # Print the grouped files.
    print(f"\n{WHITE}{BG_CYAN}Files saved ({len(all_files)}):{RESET}")
    # Sort groups for consistent ordering.
    for group in sorted(grouped_files.keys()):
        # Add a newline between groups.
        print()
        print(f"{WHITE}{group}:{RESET}")
        for file in grouped_files[group]:
            print(f"{BLUE}- {file}{RESET}")

    # Print the summary line at the bottom.
    print(
        f"\n{WHITE}{BG_CYAN}Saved code from {len(all_files)} files to {output}{RESET}\n"
    )


# End of savecode/utils/display.py
