#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def add_return_type_annotations(file_path: str) -> None:
    """Add -> None return type annotations to all function definitions."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match function definitions without return type
    # Matches: def function_name(...)
    pattern = r'(def \s+ (?:test_|setup_|teardown_|fixture_)?\w+)\s*\([^)]*\)'
    
    # Also match multi-line function definitions
    multiline_pattern = r'(def \s+ (?:test_|setup_|teardown_|fixture_)?\w+)\s*\(\s*[^)]*\s*\)'
    
    def add_return_type(match: re.Match) -> str:
        func_def = match.group(1)
        # Check if it already has a return type
        if ' -> ' not in match.group(0):
            return f'{func_def}( -> None'
        return match.group(0)
    
    new_content = re.sub(pattern, add_return_type, content)
    
    if new_content != content:
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes: {file_path}")

if __name__ == '__main__':
    test_files = [
        'tests/python/test_config.py',
        'tests/python/test_chat_history.py', 
        'tests/python/test_interfaces.py',
        'tests/python/test_ai_service.py',
        'tests/python/test_cli.py',
        'tests/python/conftest.py'
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            add_return_type_annotations(file_path)
