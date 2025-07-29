"""
Unit tests for the GitStatusPlugin in savecode.
"""

import sys
import subprocess
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

from savecode.plugins.git_status import _git_root, _git_changed, GitStatusPlugin


def test_git_root_found(tmp_path: Path) -> None:
    """Test that _git_root returns the correct path when in a git repository."""
    with patch("subprocess.check_output") as mock_output:
        mock_output.return_value = str(tmp_path) + "\n"
        result = _git_root(tmp_path)
        assert result == tmp_path
        mock_output.assert_called_once()


def test_git_root_not_found(tmp_path: Path) -> None:
    """Test that _git_root returns None when not in a git repository."""
    with patch("subprocess.check_output") as mock_output:
        mock_output.side_effect = subprocess.CalledProcessError(1, "git")
        result = _git_root(tmp_path)
        assert result is None
        mock_output.assert_called_once()


def test_git_changed(tmp_path: Path) -> None:
    """Test that _git_changed returns the correct list of files."""
    mock_output = """M  staged_modified.py
 M unstaged_modified.py
?? untracked.py
"""
    with patch("subprocess.check_output", return_value=mock_output):
        # Test both staged and unstaged
        result = _git_changed(tmp_path, True, True)
        assert len(result) == 3
        assert tmp_path / "staged_modified.py" in result
        assert tmp_path / "unstaged_modified.py" in result
        assert tmp_path / "untracked.py" in result

        # Test only staged
        with patch("subprocess.check_output", return_value="M  staged_modified.py\n"):
            result = _git_changed(tmp_path, True, False)
            assert len(result) == 1
            assert tmp_path / "staged_modified.py" in result

        # Test only unstaged
        result = _git_changed(tmp_path, False, True)
        assert len(result) == 2
        assert tmp_path / "unstaged_modified.py" in result
        assert tmp_path / "untracked.py" in result


def test_git_status_plugin_no_flag() -> None:
    """Test that GitStatusPlugin does nothing when --git is not set."""
    plugin = GitStatusPlugin()
    context: Dict[str, Any] = {"cli_opts": {"git": False}}
    plugin.run(context)
    assert "all_files" not in context


def test_git_status_plugin_not_in_repo() -> None:
    """Test that GitStatusPlugin handles not being in a git repository gracefully."""
    with patch("savecode.plugins.git_status._git_root", return_value=None):
        plugin = GitStatusPlugin()
        context: Dict[str, Any] = {"cli_opts": {"git": True}, "errors": []}
        plugin.run(context)
        assert len(context["errors"]) == 1
        assert "Not inside a Git repository" in context["errors"][0]


def test_git_status_plugin_with_files() -> None:
    """Test that GitStatusPlugin correctly populates all_files."""
    root = Path("/fake/repo")
    files = [
        root / "file1.py",
        root / "file2.js",
        root / "file3.py",
    ]

    with (
        patch("savecode.plugins.git_status._git_root", return_value=root),
        patch("savecode.plugins.git_status._git_changed", return_value=files),
        patch("savecode.plugins.git_status.normalize_path", side_effect=lambda x: x),
    ):
        plugin = GitStatusPlugin()
        context: Dict[str, Any] = {
            "cli_opts": {"git": True, "staged": False, "unstaged": False},
            "extensions": ["py", "js"],
            "errors": [],
        }
        plugin.run(context)

        assert "all_files" in context
        assert len(context["all_files"]) == 3
        assert str(root / "file1.py") in context["all_files"]
        assert str(root / "file2.js") in context["all_files"]
        assert str(root / "file3.py") in context["all_files"]


def test_git_status_plugin_with_all_ext_flag() -> None:
    """Test that GitStatusPlugin respects the all_ext flag."""
    root = Path("/fake/repo")
    files = [
        root / "file1.py",
        root / "file2.js",
        root / "file3.py",
        root / "file4.txt",  # This extension is not in the allowed list
        root / "file5.md",  # This extension is not in the allowed list
        root / "Makefile",  # No extension
    ]

    with (
        patch("savecode.plugins.git_status._git_root", return_value=root),
        patch("savecode.plugins.git_status._git_changed", return_value=files),
        patch("savecode.plugins.git_status.normalize_path", side_effect=lambda x: x),
    ):
        plugin = GitStatusPlugin()

        # First test: without all_ext flag (should filter by extension)
        context: Dict[str, Any] = {
            "cli_opts": {"git": True, "all_ext": False},
            "extensions": ["py", "js"],
            "errors": [],
        }
        plugin.run(context)

        assert "all_files" in context
        assert len(context["all_files"]) == 3  # Only py and js files
        assert str(root / "file1.py") in context["all_files"]
        assert str(root / "file2.js") in context["all_files"]
        assert str(root / "file3.py") in context["all_files"]
        assert str(root / "file4.txt") not in context["all_files"]
        assert str(root / "file5.md") not in context["all_files"]
        assert str(root / "Makefile") not in context["all_files"]

        # Second test: with all_ext flag (should include all files)
        context = {
            "cli_opts": {"git": True, "all_ext": True},
            "extensions": ["py", "js"],
            "errors": [],
        }
        plugin.run(context)

        assert "all_files" in context
        assert len(context["all_files"]) == 6  # All files included
        assert str(root / "file1.py") in context["all_files"]
        assert str(root / "file2.js") in context["all_files"]
        assert str(root / "file3.py") in context["all_files"]
        assert str(root / "file4.txt") in context["all_files"]
        assert str(root / "file5.md") in context["all_files"]
        assert str(root / "Makefile") in context["all_files"]


def test_git_flag_integration(monkeypatch: Any, tmp_path: Path) -> None:
    """Integration test for the --git flag."""
    # create a fake repo with one modified file
    js_file = tmp_path / "file.js"
    js_file.write_text("foo")

    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "file.js"], check=True)
    js_file.write_text("bar")  # unstaged change

    # simulate CLI
    argv = ["savecode", "--git", "--ext", "js"]
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", argv)
        from savecode.cli import main

        with patch("builtins.print"):  # suppress output
            main()


def test_all_ext_flag_integration(monkeypatch: Any, tmp_path: Path) -> None:
    """Integration test for the --all-ext flag with --git."""
    # Create a fake repo with multiple file types
    js_file = tmp_path / "file.js"
    py_file = tmp_path / "script.py"
    txt_file = tmp_path / "readme.txt"
    md_file = tmp_path / "readme.md"
    makefile = tmp_path / "Makefile"

    # Write content to all files
    js_file.write_text("console.log('hello');")
    py_file.write_text("print('hello')")
    txt_file.write_text("Hello world")
    md_file.write_text("# Hello world")
    makefile.write_text(".PHONY: all\nall:\n\techo hello")

    # Setup git repo and add files
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "add", "."], check=True)

    # Make some changes to create git status
    js_file.write_text("console.log('updated');")
    txt_file.write_text("Updated content")

    # Variable to store collected files for assertions
    collected_files = []

    # Define a mock for the SavePlugin.run method
    def mock_save_plugin_run(self: Any, context: Dict[str, Any]) -> None:
        nonlocal collected_files
        # Simply store the file list and don't actually write anything
        collected_files = context.get("all_files", [])

    # Test 1: Normal git behavior (should only include files with extensions in the default list)
    with patch("savecode.plugins.git_status._git_root", return_value=tmp_path):
        with monkeypatch.context() as m:
            # Import SavePlugin and patch its run method
            from savecode.plugins.save import SavePlugin

            # Use monkeypatch to patch the method
            monkeypatch.setattr(SavePlugin, "run", mock_save_plugin_run)

            # Run the CLI with normal extension filtering
            m.setattr(sys, "argv", ["savecode", "--git", "--ext", "py", "js"])

            from savecode.cli import main

            with patch("builtins.print"):  # suppress output
                main()

            # Verify only py and js files were included
            assert len(collected_files) == 2
            file_paths = [str(f) for f in collected_files]
            assert any(str(js_file) in f for f in file_paths)
            assert any(str(py_file) in f for f in file_paths)
            assert not any(str(txt_file) in f for f in file_paths)
            assert not any(str(md_file) in f for f in file_paths)
            assert not any(str(makefile) in f for f in file_paths)

    # Test 2: With --all-ext flag (should include all git-reported files)
    with patch("savecode.plugins.git_status._git_root", return_value=tmp_path):
        with monkeypatch.context() as m:
            # Reset collected files
            collected_files = []

            # Run the CLI with the all-ext flag
            m.setattr(sys, "argv", ["savecode", "--git", "--all-ext"])

            from savecode.cli import main

            with patch("builtins.print"):  # suppress output
                main()

            # Verify all files were collected regardless of extension
            assert len(collected_files) == 5
            file_paths = [str(f) for f in collected_files]
            assert any(str(js_file) in f for f in file_paths)
            assert any(str(py_file) in f for f in file_paths)
            assert any(str(txt_file) in f for f in file_paths)
            assert any(str(md_file) in f for f in file_paths)
            assert any(str(makefile) in f for f in file_paths)

    # Restore happens automatically when monkeypatch context exits
