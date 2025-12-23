# AGENTS.md - Developer Guidelines for zsh-ai-assistant

## Project layout

* zsh frontend: `zsh-ai-assistant.plugin.zsh`
* Python backend: `src/zsh_ai_assistant/`
* Tests: `tests/python/`, `tests/shell/` and `tests/integration`

## Environment setup

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras
```

All development and CI commands must run inside `uv`'s virtual environment.

## Package management

* Mandatory: use `uv` for all dependency operations.

  * Allowed: `uv add`, `uv remove`, `uv sync`, `uv run`.
  * Forbidden: `pip`, `python -m pip`, `pip install` or any direct pip usage.

## Tests and coverage

### Python Tests

Run all Python tests with coverage:

```bash
source .venv/bin/activate
uv run pytest -v --cov=. --cov-report=html
```

Run specific Python test files:

```bash
source .venv/bin/activate
uv run pytest tests/python/test_cli.py -v
```

### ShellSpec Tests (zsh functions)

The project uses ShellSpec for unit testing zsh functions. ShellSpec is a BDD-style testing framework for shell scripts.

**Prerequisites:**
- ShellSpec 0.28.1 must be installed (installed via web installer)
- Tests must run with zsh (not bash)

**Running ShellSpec tests:**

Using the wrapper script (recommended):

```bash
./run_shellspec.sh
```

Directly with ShellSpec:

```bash
cd tests/shell
export SHELLSPEC_SHELL=zsh
shellspec --shell zsh
```

**Test structure:**

```
tests/shell/
├── .shellspec                  # ShellSpec project marker
├── spec/                       # Test specifications
│   ├── spec_helper.sh          # Test helper (sources plugin)
│   ├── support/                # Test support files
│   │   └── before_all.sh        # Setup hook
│   └── directory_detection_spec.sh  # Test file
```

**Writing ShellSpec tests:**

ShellSpec uses a BDD-style DSL:

```zsh
Describe "Feature Name"
  It "should do something"
    When run some_command
    The output should include "expected output"
    The status should be success
  End
End
```

### Integration Tests

Run integration tests with pexpect:

```bash
source .venv/bin/activate
uv run pytest tests/integration/ -vs
```

* Requirement: Python coverage must be 90% or higher. PRs that do not meet this are rejected.
* Requirement: You MUST always use -s for integration test to check actual shell output.
* Requirement: You MUST run all test suites (ShellSpec, Python unit, and integration) before submitting PRs.

## Linting and formatting

* Pre-commit checks and CI must include:

  * Black (line-length 88)
  * Flake8 (keep ignores E203 and W503)
  * Mypy
* Commands:

```bash
source .venv/bin/activate
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

* Remove temporary, draft, and redundant docs before committing. Examples to remove: `FINAL_SUMMARY.md`, `TEMP*.md`, `*.bak`, `*.tmp`, `*_TASK_SPECIFIC.md`.
* Do NOT create any documents or report only for the current task. You can create it only when it is unavoidable, and in that case, make sure to name it `*_TASK_SPECIFIC.md`.
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

## Workflow

You MUST follow all rules below:

- You MUST create and maintain a comprehensive plan using the todo tool.
- You MUST follow Kent Beck’s Test-Driven Development (TDD) workflow:
  1. You MUST create a test list for the specification (for example, `test_list.txt`).
  2. You MUST select one test and write the test first. The test MUST fail initially (red).
  3. You MUST implement the minimal production code required to make the test pass (green).
  4. You MUST refactor the code.
  5. You MUST update the test list when necessary.
  6. You MUST select the next test and repeat the process starting from step 2.
- You MUST always specify a `timeout` parameter when invoking the `bash` tool.
- You MUST add temporal debug logs (for example, timestamped logs) during debugging.
- You MUST perform thorough research using web search or fetch tools when appropriate.
- You MUST remove all unnecessary files after completing each debugging session.
