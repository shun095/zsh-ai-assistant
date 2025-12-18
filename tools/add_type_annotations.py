#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def add_return_type_annotations(file_path: str) -> None:
    """Add -> None return type annotations to test function definitions."""
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern to match test function definitions without return type
    # Matches: def test_*(...), def setup_*(...), def teardown_*(...), def fixture_*(...)
    # This pattern matches only test-related function definitions
    # It matches the entire function signature including return type if present
    # Handles multiline function signatures properly
    pattern = r"(def\s+(test_|setup_|teardown_|fixture_)\w+\s*\((?:[^()\n]+|\n(?:\s+[^)]+)?)*\))(?:\s*->\s*([^:]+))?:"

    def add_return_type(match: re.Match) -> str:
        func_sig = match.group(1)
        return_type = match.group(3)
        # If no return type exists, add -> None
        if not return_type:
            return f"{func_sig} -> None:"
        return match.group(0)

    new_content = re.sub(pattern, add_return_type, content, flags=re.MULTILINE)

    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes: {file_path}")


if __name__ == "__main__":
    # Get the project root directory (parent of tools/)
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    test_files = [
        os.path.join(project_root, "tests/python/test_config.py"),
        os.path.join(project_root, "tests/python/test_chat_history.py"),
        os.path.join(project_root, "tests/python/test_interfaces.py"),
        os.path.join(project_root, "tests/python/test_ai_service.py"),
        os.path.join(project_root, "tests/python/test_cli.py"),
        os.path.join(project_root, "tests/python/conftest.py"),
    ]

    for file_path in test_files:
        if Path(file_path).exists():
            add_return_type_annotations(file_path)
