# AGENTS.md - Developer Guidelines for zsh-ai-assistant

This document provides guidelines for AI agents (like me) working on the zsh-ai-assistant project. It helps ensure consistency, proper testing, and understanding of the project structure.

## Project Overview

**zsh-ai-assistant** is a zsh plugin that integrates AI assistance directly into the shell. It consists of:
- **zsh frontend**: Shell script (`zsh-ai-assistant.plugin.zsh`) for user interaction
- **Python backend**: AI service using LangChain (`src/zsh_ai_assistant/`)
- **Tests**: Python tests (pytest)

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
