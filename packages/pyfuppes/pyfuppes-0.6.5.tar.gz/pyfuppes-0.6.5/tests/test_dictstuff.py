# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import os
import sys
import tempfile
import tomllib
import unittest
from io import StringIO

from pyfuppes.dictstuff import DotDict, compare_dictionaries


class TestDotDict(unittest.TestCase):
    """Test cases for the enhanced DotDict class with TOML support."""

    def setUp(self):
        """Initialize test data and capture stdout for warning messages."""
        self.sample_dict = {
            "server": {"host": "localhost", "port": 8080},
            "database": {
                "credentials": {"username": "admin", "password": "secret123"},
                "settings": {"timeout": 30},
            },
            "users": [{"name": "Alice", "role": "admin"}, {"name": "Bob", "role": "user"}],
            "valid_key": "value",
            "invalid-key": "problematic",
            "123numeric": "starts with number",
            "get": "overrides method",
        }

        # Valid TOML content
        self.valid_toml = """
[server]
host = "localhost"
port = 8080

[database.credentials]
username = "admin"
password = "secret123"

[database.settings]
timeout = 30

[[users]]
name = "Alice"
role = "admin"

[[users]]
name = "Bob"
role = "user"

valid_key = "value"
invalid-key = "problematic"
123numeric = "starts with number"
get = "overrides method"
"""

        # Invalid TOML content (syntax error)
        self.invalid_toml = """
[server]
host = "localhost
port = 8080
"""

        # Create temporary files for TOML testing
        self.valid_toml_file = tempfile.NamedTemporaryFile(  # noqa: SIM115
            delete=False, mode="w", suffix=".toml"
        )
        self.valid_toml_file.write(self.valid_toml)
        self.valid_toml_file.close()

        self.invalid_toml_file = tempfile.NamedTemporaryFile(  # noqa: SIM115
            delete=False, mode="w", suffix=".toml"
        )
        self.invalid_toml_file.write(self.invalid_toml)
        self.invalid_toml_file.close()

        # Setup stdout capture
        self.captured_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        """Clean up temporary files and restore stdout."""
        os.unlink(self.valid_toml_file.name)
        os.unlink(self.invalid_toml_file.name)
        sys.stdout = self.original_stdout

    def test_init_with_dict(self):
        """Test initialization with a dictionary."""
        dot_dict = DotDict(self.sample_dict)

        # Test basic access
        self.assertEqual(dot_dict.server.host, "localhost")
        self.assertEqual(dot_dict.server.port, 8080)
        self.assertEqual(dot_dict.database.credentials.username, "admin")

        # Test list of dicts
        self.assertEqual(dot_dict.users[0].name, "Alice")
        self.assertEqual(dot_dict.users[1].role, "user")

        # Verify warnings were printed
        output = self.captured_output.getvalue()
        self.assertIn("Warning: 'invalid-key'", output)
        self.assertIn("Warning: '123numeric'", output)
        self.assertIn("Warning: 'get'", output)

    def test_load_valid_toml_file(self):
        """Test loading a valid TOML file."""
        # Temporarily reset stdout to avoid capturing import warnings
        sys.stdout = self.original_stdout

        # Restore stdout capture
        sys.stdout = self.captured_output

        # Load TOML file
        dot_dict = DotDict.from_toml_file(self.valid_toml_file.name)  # type: ignore

        # Test basic access
        self.assertEqual(dot_dict.server.host, "localhost")
        self.assertEqual(dot_dict.server.port, 8080)
        self.assertEqual(dot_dict.database.credentials.username, "admin")

        # Test list of dicts
        self.assertEqual(dot_dict.users[0].name, "Alice")
        self.assertEqual(dot_dict.users[1].role, "user")

        # Verify warnings were printed
        output = self.captured_output.getvalue()
        self.assertIn("Warning: 'invalid-key'", output)
        self.assertIn("Warning: '123numeric'", output)
        self.assertIn("Warning: 'get'", output)

    def test_load_invalid_toml_file(self):
        """Test loading an invalid TOML file raises appropriate exception."""
        # Reset and restore stdout to avoid capturing import warnings
        sys.stdout = self.original_stdout
        sys.stdout = self.captured_output

        # Try to load invalid TOML file
        with self.assertRaises(tomllib.TOMLDecodeError):
            DotDict.from_toml_file(self.invalid_toml_file.name)  # type: ignore

    def test_access_invalid_keys(self):
        """Test accessing keys that are not valid Python identifiers."""
        dot_dict = DotDict(self.sample_dict)

        # These should work with dictionary access
        self.assertEqual(dot_dict["invalid-key"], "problematic")
        self.assertEqual(dot_dict["123numeric"], "starts with number")
        self.assertEqual(dot_dict["get"], "overrides method")

        # But fail with attribute access
        with self.assertRaises(AttributeError):
            _ = dot_dict.invalid - key  # noqa # type: ignore

        # This might work in Python, but it's a subtraction operation
        # dot_dict.invalid-key is interpreted as (dot_dict.invalid) - key
        with self.assertRaises(AttributeError):
            _ = dot_dict.invalid

        # with self.assertRaises(NameError):
        #     _ = dot_dict.123numeric  # SyntaxError at compile time

    def test_deep_nesting(self):
        """Test deeply nested structures."""
        deep_dict = {"level1": {"level2": {"level3": {"level4": {"value": "deep"}}}}}

        dot_dict = DotDict(deep_dict)
        self.assertEqual(dot_dict.level1.level2.level3.level4.value, "deep")

    def test_update_nested_attribute(self):
        """Test updating a nested attribute."""
        dot_dict = DotDict(self.sample_dict)

        # Update nested attribute
        dot_dict.server.host = "new-host"
        self.assertEqual(dot_dict.server.host, "new-host")
        self.assertEqual(dot_dict["server"]["host"], "new-host")

        # Update with a new dictionary should convert to DotDict
        dot_dict.server = {"host": "another-host", "new_key": "value"}
        self.assertEqual(dot_dict.server.host, "another-host")  # type: ignore
        self.assertEqual(dot_dict.server.new_key, "value")  # type: ignore

        # Verify it's a DotDict
        self.assertIsInstance(dot_dict.server, DotDict)

    def test_from_toml(self):
        """Test creating DotDict from already parsed TOML data."""
        try:
            # Reset and restore stdout to avoid capturing import warnings
            sys.stdout = self.original_stdout
            with open(self.valid_toml_file.name, "rb") as f:
                toml_data = tomllib.load(f)

            sys.stdout = self.captured_output

            # Create DotDict from parsed TOML
            dot_dict = DotDict.from_toml_data(toml_data)

            # Test access
            self.assertEqual(dot_dict.server.host, "localhost")
            self.assertEqual(dot_dict.users[0].name, "Alice")

        except ImportError:
            self.skipTest("TOML library not available")

    def test_nested_list_handling(self):
        """Test handling of nested lists with dictionaries."""
        complex_dict = {
            "nested_lists": [
                [{"name": "item1"}, {"name": "item2"}],
                [{"name": "item3"}, {"name": "item4"}],
            ]
        }

        dot_dict = DotDict(complex_dict)

        # Test that dictionaries in nested lists are converted
        self.assertEqual(dot_dict.nested_lists[0][0].name, "item1")
        self.assertEqual(dot_dict.nested_lists[1][1].name, "item4")

        # Verify outer list items are DotDict instances
        self.assertIsInstance(dot_dict.nested_lists[0][0], DotDict)


class TestCompareDictionaries(unittest.TestCase):

    def test_empty_dictionaries(self):
        missing, extra, failed = compare_dictionaries({}, {})
        self.assertEqual(missing, [])
        self.assertEqual(extra, [])
        self.assertFalse(failed)

    def test_identical_dictionaries(self):
        ref = {"a": 1, "b": 2}
        cand = {"a": 1, "b": 2}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, [])
        self.assertEqual(extra, [])
        self.assertFalse(failed)

    def test_missing_key(self):
        ref = {"a": 1, "b": 2}
        cand = {"a": 1}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, ["b"])
        self.assertEqual(extra, [])
        self.assertTrue(failed)

    def test_extra_key(self):
        ref = {"a": 1}
        cand = {"a": 1, "b": 2}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, [])
        self.assertEqual(extra, ["b"])
        self.assertFalse(failed)  # No missing keys, so comparison doesn't fail

    def test_nested_dictionaries_missing_key(self):
        ref = {"a": 1, "b": {"c": 2, "d": 3}}
        cand = {"a": 1, "b": {"c": 2}}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, ["b.d"])
        self.assertEqual(extra, [])
        self.assertTrue(failed)

    def test_nested_dictionaries_extra_key(self):
        ref = {"a": 1, "b": {"c": 2}}
        cand = {"a": 1, "b": {"c": 2, "d": 3}}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, [])
        self.assertEqual(extra, ["b.d"])
        self.assertFalse(failed)

    def test_nested_dictionaries_different_keys(self):
        ref = {"a": 1, "b": {"c": 2, "d": 3}}
        cand = {"a": 1, "b": {"e": 4, "f": 5}}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, ["b.c", "b.d"])
        self.assertEqual(extra, ["b.e", "b.f"])
        self.assertTrue(failed)

    def test_complex_nested(self):
        ref = {"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}}, "g": 5}
        cand = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "h": 6}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, ["b.d.f", "g"])
        self.assertEqual(extra, ["h"])
        self.assertTrue(failed)

    def test_nested_extra_key_within_existing_key(self):
        ref = {"a": 1, "b": {"c": 2}}
        cand = {"a": 1, "b": {"c": 2, "d": 3}}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, [])
        self.assertEqual(extra, ["b.d"])
        self.assertFalse(failed)

    def test_nested_extra_key_within_existing_key_2(self):
        ref = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        cand = {"a": 1, "b": {"c": 2, "d": {"e": 3, "f": 4}, "g": 5}}
        missing, extra, failed = compare_dictionaries(ref, cand)
        self.assertEqual(missing, [])
        self.assertEqual(extra, ["b.d.f", "b.g"])
        self.assertFalse(failed)


if __name__ == "__main__":
    unittest.main()
