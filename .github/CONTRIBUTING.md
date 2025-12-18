# Contributing

This project uses GitHub Actions for continuous integration and delivery.

## CI Workflows

### Tests Workflow (`tests.yml`)

Runs on every push and pull request to the `main` branch.

- **Python versions tested**: 3.10, 3.11, 3.12
- **Commands executed**:
  - `uv sync --all-extras` - Installs all dependencies including test dependencies
  - `uv run pytest -v -s` - Runs pytest with verbose output

### Lint and Format Workflow (`lint.yml`)

Runs on every push and pull request to the `main` branch.

- **Python version**: 3.12
- **Tools used**:
  - `black` - Code formatter (check mode)
  - `flake8` - Code linter
  - `mypy` - Static type checker

## Local Development

To run tests locally:

```bash
# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest -v -s

# Run specific test file
uv run pytest tests/python/test_ai_service.py -v

# Run with coverage
uv run pytest --cov=src/zsh_ai_assistant --cov-report=html
```

To check code quality:

```bash
# Check formatting
uv run black --check src tests

# Format code
uv run black src tests

# Run linter
uv run flake8 src tests

# Run type checker
uv run mypy src tests
```
