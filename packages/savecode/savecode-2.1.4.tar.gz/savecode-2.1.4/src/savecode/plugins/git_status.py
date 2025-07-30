"""
savecode/plugins/git_status.py – gather files reported by `git status --porcelain`.

Note: Git porcelain format may include deleted files, so we filter to only include files
that still exist in the working tree.
"""

import subprocess
import logging
from pathlib import Path
from typing import Any, Dict, List

from savecode.plugin_manager.manager import register_plugin
from savecode.plugin_manager.decorators import handle_plugin_errors
from savecode.utils.path_utils import normalize_path
from savecode.utils.error_handler import log_and_record_error

logger = logging.getLogger("savecode.plugins.git_status")

__all__ = ["_git_root", "_git_changed", "_only_existing", "GitStatusPlugin"]


def _only_existing(paths: List[Path]) -> List[Path]:
    """Return only paths that still exist in the working tree."""
    # Use the *un-bound* Path.exists so the tests' mock (which expects
    # the path object as an argument) works without hitting a binding
    # mismatch.
    return [p for p in paths if Path.exists(p)]


def _git_root(start: Path) -> Path | None:
    """Return the repository root or None if not inside a repo."""
    try:
        root = subprocess.check_output(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return Path(root)
    except subprocess.CalledProcessError:
        return None


def _git_changed(root: Path, staged: bool, unstaged: bool) -> List[Path]:
    """Return a list of changed file Paths."""
    args = ["git", "-C", str(root), "status", "--porcelain"]
    if staged and not unstaged:
        args += ["--untracked-files=no"]
    lines = subprocess.check_output(args, text=True).splitlines()

    changed: List[Path] = []
    for line in lines:
        # porcelain format: XY <path>
        status = line[:2]
        # Ignore deletions (either staged or unstaged)
        if "D" in status:
            continue
        path = line[3:]
        if status == "??" and not staged:  # untracked
            changed.append(root / path)
        elif status.strip() and status[1] != " " and unstaged:  # unstaged mods
            changed.append(root / path)
        elif status.strip() and status[0] != " " and staged:  # staged mods
            changed.append(root / path)
    return changed


@register_plugin(order=15)  # run right after ExtraArgsPlugin, before GatherPlugin
class GitStatusPlugin:
    """Populate context['all_files'] from `git status` when --git is set."""

    @handle_plugin_errors
    def run(self, context: Dict[str, Any]) -> None:
        """
        Execute the git status file gathering process.

        Expects in context:
          - 'cli_opts': Dictionary containing CLI options.
          - 'extensions': List of file extensions to include.

        Populates context with:
          - 'all_files': List of files from git status matching the extension filter.

        Args:
            context (Dict[str, Any]): Shared context containing parameters and data.

        Returns:
            None
        """
        if not context.get("cli_opts", {}).get("git"):
            return  # flag not set

        repo_root = _git_root(Path.cwd())
        if repo_root is None:
            log_and_record_error(
                "Not inside a Git repository (ignored --git)",
                context,
                logger,
                level="warning",
            )
            return

        staged = context["cli_opts"].get("staged", False)
        unstaged = context["cli_opts"].get("unstaged", False)
        if not (staged or unstaged):
            # default: both
            staged = unstaged = True

        files = _git_changed(repo_root, staged, unstaged)
        # normalize paths from git output
        # Drop paths that have vanished from the working tree
        normalized = [normalize_path(str(p)) for p in _only_existing(files)]

        # apply extension filtering only if all_ext is not set
        cli_opts = context["cli_opts"]
        exts = context["extensions"]

        # New default: with --git we include everything **unless** the user
        # explicitly set --ext AND didn't override with --all-ext.
        ext_provided = cli_opts.get("ext_provided", False)
        include_all = cli_opts.get("all_ext") or not ext_provided

        allowed = (
            normalized
            if include_all
            else [p for p in normalized if Path(p).suffix.lstrip(".").lower() in exts]
        )

        # dedupe while keeping order
        context["all_files"] = list(dict.fromkeys(allowed))
        logger.info("GitStatusPlugin gathered %d files", len(context["all_files"]))
