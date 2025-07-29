"""
savecode/tests/test_plugins.py - Unit tests for plugins error handling and edge cases.
Tests for GatherPlugin and SavePlugin, including non-existent directories, invalid file paths,
and output error conditions.
"""

import os
import tempfile
import unittest
from importlib import reload
from savecode.plugin_manager.manager import run_plugins, clear_registry
from savecode.plugins.save import SavePlugin


class TestPlugins(unittest.TestCase):
    def setUp(self) -> None:
        # Clear the plugin registry and reload plugins to ensure test isolation.
        clear_registry()
        import savecode.plugins.extra_args
        import savecode.plugins.gather
        import savecode.plugins.save

        # Reload the modules to ensure fresh state for each test
        reload(savecode.plugins.extra_args)
        reload(savecode.plugins.gather)
        reload(savecode.plugins.save)

    def tearDown(self) -> None:
        # Clear the registry after each test to ensure isolation.
        clear_registry()

    def test_nonexistent_directory(self) -> None:
        """
        Verify that a non-existent directory in roots records an error and yields no gathered files.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")
            context = {
                "roots": ["/non/existent/directory"],
                "files": [],
                "skip": [],
                "output": output_file,
                "extensions": ["py"],
                "extra_args": [],
                "errors": [],
            }
            run_plugins(context)
            self.assertTrue(len(context["errors"]) > 0)
            self.assertEqual(context.get("all_files", []), [])

    def test_invalid_file_in_files(self) -> None:
        """
        Verify that an invalid file in the 'files' list is logged as an error and not gathered.
        """
        # Create temporary invalid file (non-.py) and valid .py file, ensuring they are cleaned up.
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            invalid_file = tmp.name
        self.addCleanup(
            lambda: os.remove(invalid_file) if os.path.exists(invalid_file) else None
        )

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp2:
            valid_file = tmp2.name
        self.addCleanup(
            lambda: os.remove(valid_file) if os.path.exists(valid_file) else None
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")
            context = {
                "roots": [],
                "files": [invalid_file, valid_file],
                "skip": [],
                "output": output_file,
                "extensions": ["py"],
                "extra_args": [],
                "errors": [],
            }
            run_plugins(context)
            # The valid file should be gathered; the invalid file should generate an error.
            self.assertIn(valid_file, context.get("all_files", []))
            self.assertNotIn(invalid_file, context.get("all_files", []))
            self.assertTrue(
                any(
                    "is not a valid source file" in error for error in context["errors"]
                )
            )

    def test_valid_directory_gathering(self) -> None:
        """
        Verify that a directory containing a Python file is correctly processed,
        and non-Python files are ignored without errors.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = os.path.join(tmpdir, "test.py")
            with open(py_file, "w", encoding="utf-8") as f:
                f.write("print('Hello')")
            non_py_file = os.path.join(tmpdir, "readme.txt")
            with open(non_py_file, "w", encoding="utf-8") as f:
                f.write("Not python")

            output_file = os.path.join(tmpdir, "output.txt")
            context = {
                "roots": [tmpdir],
                "files": [],
                "skip": [],
                "output": output_file,
                "extensions": ["py"],
                "extra_args": [],
                "errors": [],
            }
            run_plugins(context)
            self.assertIn(py_file, context.get("all_files", []))
            # No error should be recorded for the non-Python file.
            self.assertFalse(any("readme.txt" in error for error in context["errors"]))

    def test_saveplugin_output_error(self) -> None:
        """
        Verify that SavePlugin records an error when the output file cannot be written to.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Set output to a directory to simulate a write error.
            context = {
                "roots": [],
                "files": [],
                "skip": [],
                "output": tmpdir,  # Directory used as file path.
                "extensions": ["py"],
                "extra_args": [],
                "errors": [],
            }
            plugin = SavePlugin()
            plugin.run(context)
            self.assertTrue(len(context["errors"]) > 0)
            self.assertTrue(
                any(
                    "Error writing to output file" in error
                    for error in context["errors"]
                )
            )

    def test_gather_toml_files(self) -> None:
        """
        Verify that a TOML file is correctly gathered when the toml extension is specified.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            toml = os.path.join(tmpdir, "pyproject.toml")
            with open(toml, "w", encoding="utf-8") as f:
                f.write('[tool]\nname = "demo"\n')
            context = {
                "roots": [tmpdir],
                "files": [],
                "skip": [],
                "output": os.path.join(tmpdir, "output.txt"),
                "extensions": ["toml"],
                "extra_args": [],
                "errors": [],
            }
            run_plugins(context)
            self.assertIn(toml, context["all_files"])


if __name__ == "__main__":
    unittest.main()

# End of savecode/tests/test_plugins.py
