#!/usr/bin/env python3
"""Tests for add_type_annotations.py tool."""

import os
import tempfile
import unittest
from pathlib import Path

# Import the function we're testing
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_type_annotations import add_return_type_annotations


class TestAddTypeAnnotations(unittest.TestCase):
    """Test cases for the add_type_annotations tool."""

    def setUp(self):
        """Create a temporary file for testing."""
        self.temp_file_path = tempfile.mktemp(suffix=".py")

    def tearDown(self):
        """Clean up the temporary file."""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_add_return_type_to_simple_function(self):
        """Test adding return type to a simple function."""
        content = """def test_simple():
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertIn("def test_simple() -> None:", result)

    def test_add_return_type_to_function_with_params(self):
        """Test adding return type to a function with parameters."""
        content = """def test_with_params(a, b, c):
    return a + b + c
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertIn("def test_with_params(a, b, c) -> None:", result)

    def test_do_not_modify_function_with_existing_return_type(self):
        """Test that functions with existing return types are not modified."""
        content = """def test_with_return_type() -> int:
    return 42
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertEqual(result, content)

    def test_add_return_type_to_setup_function(self):
        """Test adding return type to setup_* functions."""
        content = """def setup_method():
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertIn("def setup_method() -> None:", result)

    def test_add_return_type_to_teardown_function(self):
        """Test adding return type to teardown_* functions."""
        content = """def teardown_class():
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertIn("def teardown_class() -> None:", result)

    def test_add_return_type_to_fixture_function(self):
        """Test adding return type to fixture_* functions."""
        content = """def fixture_data():
    return {}
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        self.assertIn("def fixture_data() -> None:", result)

    def test_do_not_modify_non_test_functions(self):
        """Test that non-test functions are not modified."""
        content = """def helper_function():
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        # Should not modify helper_function (doesn't start with test_/setup_/teardown_/fixture_)
        self.assertEqual(result, content)

    def test_multiline_function_signature(self):
        """Test handling of multiline function signatures."""
        content = """def test_multiline(
    param1,
    param2,
    param3
):
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        # Should add -> None after the closing parenthesis
        self.assertIn("def test_multiline(\n    param1,\n    param2,\n    param3\n) -> None:", result)

    def test_class_methods(self):
        """Test handling of class methods."""
        content = """class TestClass:
    def test_method(self):
        pass
    
    def helper_method(self):
        pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        add_return_type_annotations(self.temp_file_path)

        with open(self.temp_file_path, "r") as f:
            result = f.read()

        # Should only modify test_method (starts with test_), not helper_method
        self.assertIn("def test_method(self) -> None:", result)
        self.assertIn("def helper_method(self):", result)

    def test_no_changes_when_already_correct(self):
        """Test that no changes are made when file is already correct."""
        content = """def test_correct() -> None:
    pass
"""
        with open(self.temp_file_path, "w") as f:
            f.write(content)

        # Read original content
        with open(self.temp_file_path, "r") as f:
            original_content = f.read()

        # Run the function
        add_return_type_annotations(self.temp_file_path)

        # Read modified content
        with open(self.temp_file_path, "r") as f:
            modified_content = f.read()

        # Should be identical
        self.assertEqual(original_content, modified_content)


if __name__ == "__main__":
    unittest.main()
