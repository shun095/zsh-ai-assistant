# AGENTS.md - Developer Guidelines for zsh-ai-assistant

This document provides guidelines for AI agents (like me) working on the zsh-ai-assistant project. It helps ensure consistency, proper testing, and understanding of the project structure.

## Project Overview

**zsh-ai-assistant** is a zsh plugin that integrates AI assistance directly into the shell. It consists of:
- **zsh frontend**: Shell script (`zsh-ai-assistant.plugin.zsh`) for user interaction
- **Python backend**: AI service using LangChain (`src/zsh_ai_assistant/`)
- **Tests**: Python tests (pytest)

## Development Tools

The project includes utility scripts to help with development:

### Type Annotation Helper

**Location:** `tools/add_type_annotations.py`

**Purpose:** Automatically adds `-> None` return type annotations to function definitions in test files.

**Usage:**
```bash
# Run the script to add return type annotations to all test files
python tools/add_type_annotations.py
```

**Note:** This is a helper tool and may not handle all edge cases. Manual review is recommended after using it.

---

## Development Environment Setup

### Prerequisites
- Python 3.10+
- zsh 5.9+
- uv (Python package manager)

### Setting up the environment
```bash
# Install uv if not already installed
pip install uv

# Create virtual environment
cd /home/vibeuser/project/zsh-ai-assistant
uv venv

# Activate virtual environment
eval "$(uv venv shell)"

# Install dependencies
uv sync --all-extras
```

### IMPORTANT: Package Management Guidelines

**ALL developers MUST use uv for package management.**

**Required commands:**
- `uv add <package>` - Add dependencies
- `uv remove <package>` - Remove dependencies  
- `uv sync` - Synchronize dependencies
- `uv run <command>` - Run commands in the virtual environment

**FORBIDDEN commands:**
- NEVER use `pip`
- NEVER use `python -m pip`
- NEVER use raw `pip install` commands

**Rationale:**
- uv provides faster dependency resolution
- uv ensures consistent dependency management
- uv integrates better with modern Python workflows
- Using pip can lead to dependency conflicts and inconsistent environments


## Running Tests

### Python Tests
```bash
# Run all Python tests with coverage
eval "$(uv venv shell)"
uv run pytest -v --cov=src --cov-report=html

# View coverage report
xdg-open htmlcov/index.html
```

### Shell Tests
```bash
# Run shell integration tests
uv run pytest tests/shell/ -v

# Run specific shell test
uv run pytest tests/shell/test_interactive.py::TestInteractive::test_command_generation -v
```

## Linting and Code Quality

The project uses three linters to ensure code quality:

### Linters Configuration
- **Black**: Code formatter (line-length: 88)
- **Flake8**: Style linter (line-length: 88, ignores E203, W503)
- **Mypy**: Type checker (Python 3.10+)

Configuration files:
- `pyproject.toml` - Black and Mypy configuration
- `setup.cfg` - Flake8 configuration

### Running Linters
```bash
# Run all linters
eval "$(uv venv shell)"
uv run black --check src tests
uv run flake8 src tests
uv run mypy src tests

# Auto-format code with Black
uv run black src tests

# Run linters and tests together (CI workflow simulation)
uv run black src tests && \
uv run flake8 src tests && \
uv run pytest tests/python/ tests/shell/ -q
```

### Linter Guidelines

**Black**:
- Automatically formats code to PEP 8 standards
- Line length: 88 characters
- Run `uv run black src tests` to format all files
- Run `uv run black --check src tests` to verify formatting

**Flake8**:
- Checks for style violations
- Ignores E203 (whitespace before ':') and W503 (line break before binary operator)
- Configuration in `setup.cfg`
- Common issues to fix:
  - Unused imports (F401)
  - Blank lines with whitespace (W293)
  - Line too long (E501)
  - Undefined names (F821)
  - Unused variables (F841)

**Mypy**:
- Type checking for Python code
- Python version: 3.10+
- Reports missing type annotations
- Run `uv run mypy src tests` to check types

### CI/CD Integration

The project has a GitHub Actions workflow for linting:
- `.github/workflows/lint.yml` - Runs on push and pull requests
- Executes Black, Flake8, and Mypy
- Must pass before code can be merged

To test locally before pushing:
```bash
# Simulate CI workflow
eval "$(uv venv shell)"
uv sync --all-extras
uv run black src tests
uv run flake8 src tests
uv run mypy src tests
uv run pytest tests/python/ tests/shell/ -q
```

## STRICT DOCUMENT CLEANUP POLICY

### Document Cleanup Is MANDATORY

**ALL developers MUST remove unnecessary documentation files before committing.** This includes:
- Summary files (e.g., `FINAL_SUMMARY.md`, `COMPLETION_SUMMARY.md`)
- Temporary notes or scratch files
- Outdated documentation
- Redundant or duplicate files

### Why Document Cleanup Is Required

1. **Codebase Hygiene**: Unnecessary files clutter the repository and confuse new contributors
2. **Version Control Efficiency**: Large documentation files bloat the git history
3. **Professionalism**: A clean repository demonstrates attention to detail
4. **Maintainability**: Reduces the risk of outdated information being referenced

### Document Cleanup Guidelines

#### What to Remove

- **Project summary files**: Any `.md` files that document completion status, final summaries, or project wrap-ups
- **Temporary files**: Files with names like `NOTES.md`, `TEMP.md`, `DRAFT.md`, or `TODO.md`
- **Redundant documentation**: Files that duplicate information already in `README.md` or `AGENTS.md`
- **Outdated files**: Documentation that references old versions, deprecated features, or completed tasks

#### What to Keep

- **Essential documentation**: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, and other core documentation files
- **API documentation**: Type stubs, docstrings, and inline documentation
- **Configuration files**: `pyproject.toml`, `setup.cfg`, and other build configuration files
- **Test documentation**: Test case descriptions and test-specific documentation

#### Cleanup Checklist Before Committing

Before committing any changes, run:
```bash
# 1. List all markdown files to review
find . -name "*.md" -type f

# 2. List all text files to review
find . -name "*.txt" -type f

# 3. List all temporary/scratch files
find . \( -name "*.tmp" -o -name "*.bak" -o -name "*.old" -o -name "NOTES*" -o -name "TEMP*" -o -name "DRAFT*" \) -type f

# 4. Review each file and remove unnecessary ones
```

### Forbidden Practices

**NEVER do any of the following:**

1. **Committing summary files:**
```bash
# FORBIDDEN - Never commit these
FINAL_SUMMARY.md
COMPLETION_SUMMARY.md
PROJECT_NOTES.md
```

2. **Leaving temporary files:**
```bash
# FORBIDDEN - Always clean up
NOTES.md
TEMP.md
DRAFT.md
*.bak
*.tmp
```

3. **Creating redundant documentation:**
```bash
# FORBIDDEN - Don't duplicate existing docs
README_BACKUP.md
AGENTS_COPY.md
```

### Consequences of Violating This Policy

- Unnecessary files will be removed during code review
- Repeated violations may result in manual cleanup by maintainers
- PRs with unnecessary files may be rejected
- Contributors are expected to maintain a clean repository

This strict policy ensures the codebase remains organized, professional, and easy to navigate.

---

## STRICT TYPE ANNOTATION POLICY

### Type Annotations Are MANDATORY

**ALL Python code MUST have complete type annotations.** This includes:
- Source code (`src/` directory)
- Tests (`tests/` directory)
- Configuration files
- Utility scripts

### Why Type Annotations Are Required

1. **Code Quality**: Type annotations catch bugs early and make code more maintainable
2. **IDE Support**: Better autocomplete and refactoring support
3. **Documentation**: Type hints serve as self-documenting code
4. **CI/CD Reliability**: Consistent type checking prevents regressions

### Mypy Configuration

The project uses strict mypy settings:
- `disallow_untyped_defs = true` - All functions must have type annotations
- `disallow_incomplete_defs = true` - All function parameters and return types must be annotated
- `warn_return_any = true` - No `Any` return types allowed
- `warn_unused_configs = true` - Detect unused mypy configurations
- `warn_redundant_casts = true` - Detect unnecessary type casts
- `warn_unused_ignores = true` - Detect unused `# type: ignore` comments

### Type Annotation Guidelines

#### Function Definitions
```python
# CORRECT - Full type annotations
def calculate_sum(a: int, b: int) -> int:
    return a + b

# INCORRECT - Missing return type
def calculate_sum(a: int, b: int):
    return a + b

# INCORRECT - Missing parameter types
def calculate_sum(a, b) -> int:
    return a + b
```

#### Method Definitions
```python
# CORRECT - Full type annotations
class Calculator:
    def __init__(self, value: int) -> None:
        self.value = value
    
    def add(self, amount: int) -> int:
        return self.value + amount

# INCORRECT - Missing return type on __init__
class Calculator:
    def __init__(self, value: int):
        self.value = value
```

#### Test Functions
```python
# CORRECT - Full type annotations
import pytest

def test_addition() -> None:
    assert 1 + 1 == 2

class TestCalculator:
    def test_sum(self) -> None:
        assert sum([1, 2, 3]) == 6

# INCORRECT - Missing return type
class TestCalculator:
    def test_sum():
        assert sum([1, 2, 3]) == 6
```

#### Handling External Libraries Without Type Stubs

For external libraries that don't have type stubs (e.g., `pexpect`), you MUST:

1. **Add `# type: ignore` comment** on the import line:
```python
import pexpect  # type: ignore[import-untyped]
```

2. **Use `object` type** for unknown types:
```python
class PexpectPrefixLogger:
    def __init__(self, prefix: str, stream: object) -> None:
        self.prefix = prefix
        self.stream = stream
```

3. **DO NOT** use `ignore_missing_imports` or `disallow_untyped_defs = false` in mypy config

### Forbidden Practices

**NEVER do any of the following:**

1. **Adding overrides to disable type checking:**
```python
# FORBIDDEN - This disables type checking entirely
[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false
```

2. **Using `# type: ignore` without specific error code:**
```python
# FORBIDDEN - Too broad
result = some_function()  # type: ignore

# CORRECT - Specific error code
result = some_function()  # type: ignore[no-any-return]
```

3. **Using `Any` type unnecessarily:**
```python
# FORBIDDEN - Avoid Any when possible
from typing import Any

def process_data(data: Any) -> Any:
    return data

# CORRECT - Use specific types
from typing import Union

def process_data(data: Union[str, int]) -> str:
    return str(data)
```

4. **Using `ignore_missing_imports` in mypy config:**
```python
# FORBIDDEN - This hides all import errors
[mypy]
ignore_missing_imports = true
```

### Fixing Type Errors

When you encounter type errors:

1. **First, understand the error:**
   ```bash
   uv run mypy src tests --show-error-codes
   ```

2. **Add proper type annotations:**
   - Add missing parameter types
   - Add missing return type annotations
   - Use specific types instead of `Any`

3. **For external libraries:**
   - Add `# type: ignore[import-untyped]` on the import line
   - Use `object` type for unknown attributes

4. **Test your changes:**
   ```bash
   uv run mypy src tests
   ```

### Example: Fixing a Type Error

**Before (has type errors):**
```python
class Logger:
    def __init__(self, stream):
        self.stream = stream
    
    def write(self, data):
        self.stream.write(data)
```

**After (fixed):**
```python
class Logger:
    def __init__(self, stream: object) -> None:
        self.stream = stream
    
    def write(self, data: str) -> None:
        self.stream.write(data)  # type: ignore[attr-defined]
```

### Final Checklist Before Committing

Before committing any changes, run:
```bash
# 1. Check all type annotations
uv run mypy src tests

# 2. Verify code formatting
uv run black --check src tests

# 3. Run style checks
uv run flake8 src tests

# 4. Run all tests
uv run pytest tests/python/ tests/shell/ -q

# 5. All checks must pass with ZERO errors
```

**If any check fails, fix the issues before committing.**

### Consequences of Violating This Policy

- Code with missing type annotations will be rejected in code review
- CI/CD pipeline will fail
- PRs will not be merged until all type errors are fixed
- Repeated violations may result in removal from contributor access

This strict policy ensures the codebase remains maintainable, reliable, and professional.
