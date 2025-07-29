"""
tests/test_extra_args.py - Unit tests for extra arguments parsing functionality.
"""

import unittest
from savecode.plugins.extra_args import parse_extra_args


class TestExtraArgs(unittest.TestCase):
    def test_parse_key_value(self) -> None:
        args = ["key1=value1", "key2=value2"]
        parsed = parse_extra_args(args)
        self.assertEqual(parsed, {"key1": "value1", "key2": "value2"})

    def test_parse_boolean_flags(self) -> None:
        args = ["flag1", "flag2"]
        parsed = parse_extra_args(args)
        self.assertEqual(parsed, {"flag1": True, "flag2": True})

    def test_reserved_keys_are_skipped(self) -> None:
        # Reserved keys: 'roots', 'files', 'skip', 'output', 'errors', 'parsed_extra_args'
        args = ["roots=value", "custom=value", "errors=true", "flag"]
        parsed = parse_extra_args(args)
        # 'roots' and 'errors' should be skipped.
        self.assertNotIn("roots", parsed)
        self.assertNotIn("errors", parsed)
        self.assertIn("custom", parsed)
        self.assertIn("flag", parsed)


if __name__ == "__main__":
    unittest.main()
