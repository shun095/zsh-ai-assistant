# AGENTS.md - Developer Guidelines for zsh-ai-assistant

## Project layout

* zsh frontend: `zsh-ai-assistant.plugin.zsh`
* Python backend: `src/zsh_ai_assistant/`
* Tests: `tests/python/` and `tests/shell/`

## Environment setup

```bash
uv venv
eval "$(uv venv shell)"
uv sync --all-extras
```

All development and CI commands must run inside `uv`'s virtual environment.

## Package management

* Mandatory: use `uv` for all dependency operations.

  * Allowed: `uv add`, `uv remove`, `uv sync`, `uv run`.
  * Forbidden: `pip`, `python -m pip`, `pip install` or any direct pip usage.

## Tests and coverage

* Run tests with coverage:

```bash
eval "$(uv venv shell)"
uv run pytest -v --cov=. --cov-report=html
```

* Shell tests:

```bash
uv run pytest tests/shell/ -v -s --cov=. --cov-report=html
```

* Shell tests with timeout (for slow tests):

```bash
timeout 120 uv run pytest tests/shell/ -v -s --cov=. --cov-report=html
```

> [!NOTE]
> You MUST always specify timeout parameter for bash tool. (Not in command parameter)

* Requirement: Python coverage must be 90% or higher. PRs that do not meet this are rejected.

## Linting and formatting

* Pre-commit checks and CI must include:

  * Black (line-length 88)
  * Flake8 (keep ignores E203 and W503)
  * Mypy
* Commands:

```bash
eval "$(uv venv shell)"
uv run black --check src tests
uv run flake8 src tests
uv run mypy src tests
```

* CI must fail if any check fails.

## Type annotation policy

* All Python code and tests must have complete type annotations. No untyped defs allowed.
* Mypy project settings must include:

  * disallow_untyped_defs = True
  * disallow_incomplete_defs = True
  * warn_return_any = True
  * warn_unused_ignores = True
* For untyped external libs, use targeted ignores:

```python
import pexpect  # type: ignore[import-untyped]
```

* Forbidden: global `ignore_missing_imports = true`, indiscriminate `# type: ignore`, and unnecessary use of `Any`.

## Documentation cleanup

* Remove temporary, draft, and redundant docs before committing. Examples to remove: `FINAL_SUMMARY.md`, `TEMP*.md`, `*.bak`, `*.tmp`.
* Keep only essential docs: `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, API docs.

## LLM agent operation rules

* Follow instructions literally. When ambiguous, make minimal necessary assumptions and produce a complete, immediate result.
* Do not claim asynchronous or background work. Deliver results in the same response.
* Always run tests, formatters, and type checks before creating a PR or submitting output.

## CI requirements

A PR must pass:

* Black formatting
* Flake8
* Mypy
* Pytest with coverage threshold
  Do not alter or bypass `.github/workflows/` without explicit maintainer approval.

## Forbidden actions and consequences

* Forbidden: direct pip usage, disabling type checks, disabling linters, adding or modifying linter configuration to ignore additional Flake8 errors or rules, falsifying coverage, committing temporary files, broad ignore comments.
* If a proposed change would add or expand Flake8 ignores **solely to resolve a conflict with Black**, it **requires explicit approval from a repository maintainer** before merging.
* Violations result in PR rejection and required fixes. Repeated violations may restrict merge permissions.

## Enforcement

* Automated CI enforces checks. Reviewers will reject noncompliant PRs. Exceptions require explicit maintainer approval in PR comments.

## Workflows

- Before starting the task, always create a comprehensive plan for the task as todo list.
- Before getting stuck in a debugging loop, you should always do thorough web research. If that fails, immediately stop debugging and do web research before trying a different approach. Web research is cheap and time-consuming, but getting yourself stuck in a loop is a waste of time and money.
- When debugging, always include a temporary debug log. Debugging based on imagination is a waste of time and money.
