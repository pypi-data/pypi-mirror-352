"""
savecode/tests/test_cli_args.py - Module for testing CLI argument parsing and skip functionality.
Tests for the new positional argument handling for source inputs, merging of -r and -f arguments,
and the robustness of --skip functionality.
"""

import os
import sys
import tempfile
import unittest
from savecode.utils.cli_args import parse_arguments
from savecode.plugins.gather import should_skip
from savecode.utils.path_utils import normalize_path


class TestCLIArgs(unittest.TestCase):
    def test_only_toml_when_specified(self) -> None:
        """
        Ensure that specifying --ext toml results in args.ext == ["toml"]
        """
        orig_argv = sys.argv
        sys.argv = ["prog", "--ext", "toml"]
        args, _ = parse_arguments()
        self.assertEqual(args.ext, ["toml"])
        sys.argv = orig_argv

    def test_positional_source_directory(self) -> None:
        """
        Test that a positional source directory is correctly added to roots.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_argv = sys.argv
            sys.argv = ["prog", tmpdir]
            args, extra = parse_arguments()
            # Normalize and check that the temp directory is in roots.
            norm_roots = [normalize_path(x) for x in args.roots]
            norm_tmpdir = normalize_path(tmpdir)
            self.assertIn(norm_tmpdir, norm_roots)
            sys.argv = orig_argv

    def test_mixed_roots_and_files(self) -> None:
        """
        Test that -r and -f options correctly process directories and file paths interchangeably.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.py")
            with open(file_path, "w") as f:
                f.write("print('hello')")
            orig_argv = sys.argv
            sys.argv = ["prog", "-r", file_path, "-f", tmpdir]
            args, extra = parse_arguments()
            norm_files = [normalize_path(x) for x in args.files]
            norm_roots = [normalize_path(x) for x in args.roots]
            norm_file_path = normalize_path(file_path)
            norm_tmpdir = normalize_path(tmpdir)
            self.assertIn(norm_file_path, norm_files)
            self.assertIn(norm_tmpdir, norm_roots)
            sys.argv = orig_argv

    def test_skip_patterns_parsing(self) -> None:
        """
        Test that --skip arguments are parsed correctly.
        """
        orig_argv = sys.argv
        sys.argv = ["prog", "--skip", "tests", "/tests/", "tests/filename.py"]
        args, extra = parse_arguments()
        self.assertEqual(args.skip, ["tests", "/tests/", "tests/filename.py"])
        sys.argv = orig_argv

    def test_should_skip_function(self) -> None:
        """
        Test the should_skip helper function with various skip patterns.
        """
        # Construct a sample file path that includes a 'tests' directory.
        sample_path = os.path.join(os.getcwd(), "tests", "filename.py")
        self.assertTrue(should_skip(sample_path, ["tests"]))
        self.assertTrue(should_skip(sample_path, ["/tests/"]))
        self.assertTrue(should_skip(sample_path, ["tests/filename.py"]))
        self.assertFalse(should_skip(sample_path, ["nonsense"]))

    def test_all_ext_flag(self) -> None:
        """
        Test that the --all-ext flag is correctly parsed and defaults to False.
        """
        # Test default value (should be False)
        orig_argv = sys.argv
        sys.argv = ["prog", "--git"]
        args, _ = parse_arguments()
        self.assertFalse(args.all_ext)

        # Test explicit setting to True
        sys.argv = ["prog", "--git", "--all-ext"]
        args, _ = parse_arguments()
        self.assertTrue(args.all_ext)

        # Restore original argv
        sys.argv = orig_argv


if __name__ == "__main__":
    unittest.main()

# End of savecode/tests/test_cli_args.py
