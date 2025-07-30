"""
Unit tests for deletion handling in GitStatusPlugin.
"""

from pathlib import Path
from unittest.mock import patch

from savecode.plugins.git_status import _only_existing, _git_changed


def test_only_existing_filter() -> None:
    """Test that _only_existing helper properly filters out non-existent paths."""
    # Create test paths
    existing_path = Path("/fake/existing.py")
    deleted_path = Path("/fake/deleted.js")

    # Test paths to check
    test_paths = [existing_path, deleted_path]

    # Test the _only_existing function with our mock
    with patch.object(Path, "exists") as mock_exists:
        # Configure the mock to return True only for existing_path
        mock_exists.side_effect = lambda self: self == existing_path
        # Run the function
        result = _only_existing(test_paths)

        # Verify only the existing path is returned
        assert len(result) == 1
        assert existing_path in result
        assert deleted_path not in result


def test_git_changed_skips_deletions(tmp_path: Path) -> None:
    """Test that _git_changed doesn't include deleted files."""
    # Sample git status output with a deleted file
    status_output = "M  modified.py\n D deleted.js\n"

    # Mock the subprocess call
    with patch("subprocess.check_output", return_value=status_output):
        # Get changed files
        result = _git_changed(tmp_path, True, True)

        # Should only include the modified file, not the deleted one
        assert len(result) == 1
        assert (tmp_path / "modified.py") in result
        assert (tmp_path / "deleted.js") not in result
