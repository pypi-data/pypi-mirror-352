"""
savecode/cli.py - Entry point for the savecode CLI tool with enhanced global error handling.
This module provides the main() function to parse command-line arguments,
build a shared context, execute registered plugins, display a summary of saved files,
and handle any errors encountered during execution.
"""

import sys
import logging
from typing import Any, Dict

# Import the plugins package to ensure all plugins are registered.
from savecode.plugin_manager.manager import run_plugins
from savecode.utils.path_utils import (
    normalize_path,
)  # Updated import: use normalize_path directly.
from savecode.utils.display import display_summary
from savecode.utils.logger import configure_logging
from savecode.utils.cli_args import parse_arguments


def main() -> None:
    """
    Main entry point for the savecode CLI.

    Parses command-line arguments, builds a shared context, executes registered plugins,
    displays a summary of the saved files, and reports any errors encountered.

    Returns:
        None
    """
    args, extra_args = parse_arguments()

    # Convert log level string to corresponding logging level integer.
    log_level = getattr(logging, args.log_level.upper(), logging.WARNING)
    # Configure logging with the dynamic log level.
    configure_logging(level=log_level)

    # Build a shared context for all plugins.
    context: Dict[str, Any] = {
        "roots": args.roots,
        "files": args.files,
        "skip": args.skip,
        "output": normalize_path(args.output),  # Directly call normalize_path.
        "extensions": [ext.lower().lstrip(".") for ext in args.ext],
        "extra_args": extra_args,
        "errors": [],  # Initialize error aggregation list
        "cli_opts": {  # NEW: pass raw flags so plugins can see them
            "git": args.git,
            "staged": args.staged,
            "unstaged": args.unstaged,
            "all_ext": args.all_ext,
        },
    }

    try:
        run_plugins(context)
    except KeyboardInterrupt:
        print("\nInterrupted by user – finishing up...")

    # If errors were aggregated during plugin execution, report and exit with error.
    if context["errors"]:
        print("\nErrors encountered:")
        for error in context["errors"]:
            print(f"- {error}")
        sys.exit(1)

    # Display a summary of the saved files using the centralized display function.
    display_summary(context)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        # Log the unexpected error with a traceback and exit gracefully.
        logger = logging.getLogger("savecode")
        logger.exception("Unhandled exception in main: %s", err)
        sys.exit(1)
