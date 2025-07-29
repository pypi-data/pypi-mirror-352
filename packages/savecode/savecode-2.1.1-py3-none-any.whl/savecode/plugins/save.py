"""
savecode/plugins/save.py - Plugin to save code from source files to an output file.
This module defines a plugin that reads source files and writes their contents along with a summary
to a designated output file, aggregating any errors encountered during file operations.
"""

import logging
from typing import Any, Dict, List
from pathlib import Path
from tqdm import tqdm
from savecode.plugin_manager.manager import register_plugin
from savecode.plugin_manager.decorators import handle_plugin_errors
from savecode.utils.path_utils import relative_path
from savecode.utils.error_handler import log_and_record_error
from savecode.utils.clipboard import copy as copy_clipboard

logger = logging.getLogger("savecode.plugins.save")

# Maximum file size to process (in MB)
MAX_SIZE_MB = 5


@register_plugin(order=30)
class SavePlugin:
    """Plugin that saves the content of source files to a single output file."""

    @handle_plugin_errors
    def run(self, context: Dict[str, Any]) -> None:
        """Execute the saving process in a single pass.

        Expects in context:
          - 'all_files': List of source file paths.
          - 'output': Output file path.

        Aggregates errors in context['errors'].

        Args:
            context (Dict[str, Any]): Shared context containing file lists, output path, etc.

        Returns:
            None
        """
        gathered: List[str] = context.get("all_files", [])
        output_file: str = context.get("output", "./temp.txt")
        try:
            summary_lines = ["Files saved:"]

            # Open output file for both reading and writing
            with open(output_file, "w+", encoding="utf-8") as out:
                # Write the initial summary header
                for file in tqdm(gathered, desc="Processing files", unit="file"):
                    rel_path = relative_path(file)
                    summary_lines.append(f"- {rel_path}")

                    # Check file size before processing
                    if Path(file).stat().st_size > MAX_SIZE_MB * 1024 * 1024:
                        log_and_record_error(
                            f"Skipped {file} (>{MAX_SIZE_MB} MB)",
                            context,
                            logger,
                            level="warning",
                        )
                        continue

                    try:
                        # Write the file header
                        header = f"\nFile: {rel_path}\n\n"
                        out.write(header)

                        # Stream the file content in chunks
                        with open(file, "r", encoding="utf-8", errors="replace") as f:
                            for chunk in iter(lambda: f.read(8192), ""):  # 8 KB chunks
                                out.write(chunk)

                        # Add a separator after each file
                        out.write("\n\n")
                    except Exception as e:
                        error_msg = f"Error reading {file}: {e}"
                        log_and_record_error(error_msg, context, logger, exc_info=True)

                # Write the summary at the beginning of the file
                # Go back to the beginning of the file
                out.seek(0)

                # Write the summary with file count
                file_count = len(summary_lines) - 1  # Subtract 1 for the header line
                summary_lines[0] = f"Files saved ({file_count}):"
                summary_text = "\n".join(summary_lines) + "\n\n"
                out.write(summary_text)

                # Go to the end of the file to add a footer
                out.seek(0, 2)  # Seek to the end of the file
                footer = f"\nSaved code from {file_count} files to {output_file}\n"
                out.write(footer)

                # Read complete output for clipboard
                out.seek(0)
                complete_output = out.read()

                # Copy to clipboard
                copy_clipboard(complete_output)
                logger.info("Copied concatenated code to clipboard.")

        except Exception as e:
            error_msg = f"Error writing to output file {output_file}: {e}"
            log_and_record_error(error_msg, context, logger, exc_info=True)


# End of savecode/plugins/save.py
