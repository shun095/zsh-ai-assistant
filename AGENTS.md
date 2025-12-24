# AGENTS.md — Mandatory Developer & Agent Rules

## Purpose
This document defines **mandatory rules** for developers and automated agents (including LLMs) working on **zsh-ai-assistant**.  
Goals: strict compliance, reduced token usage, and lower human review cost.

---

## Scope
Applies to local development, CI, PRs, and LLM-based agents.  
Any exception requires **explicit maintainer approval recorded in PR comments**.

---

## 1. Core Principles (Highest Priority)
* **Strict compliance**: All “MUST” requirements are mandatory. Violations result in PR rejection.
* **Synchronous delivery only**: Do not claim background, async, or deferred work. Deliver complete results in a single response.
* **Minimal assumptions**: Resolve ambiguity with the smallest reasonable assumption and produce an executable result.
* **Automation-first**: CI checks are authoritative. No implicit exceptions.

---

## 2. Project Layout
* zsh frontend: `zsh-ai-assistant.plugin.zsh`
* Python backend: `src/zsh_ai_assistant/`
* Tests: `tests/python/`, `tests/shell/`, `tests/integration/`

---

## 3. Development Environment (Required)
```bash
uv venv
source .venv/bin/activate
uv sync --all-extras
````

* **All development and CI commands for Python code MUST run inside the `uv` virtual environment.**
* **The code must always run on machines with different directory structures and on both Linux and Mac platforms.** Please keep the use of absolute paths, APIs that work only on a specific OS, and commands that behave differently between GNU and BSD to a minimum.

---

## 4. Package Management (Strict)

* **All Python dependency operations MUST use `uv`.**

  * Allowed: `uv add`, `uv remove`, `uv sync`, `uv run`
  * Forbidden: `pip`, `python -m pip`, or any direct pip usage

* `sudo apt-get` can be used to install development tools like shellspec and kcov etc.

---

## 5. Testing (Required)

* **Minimum Python coverage: 90%**. Below this threshold, PRs are rejected.
* **Minimum shell coverage: 90%**. Below this threshold, PRs are rejected.
* **All test suites MUST be run before PR submission**:

  * ShellSpec with kcov coverage
  * Python unit tests
  * Integration tests
* **Integration tests MUST use `-s`** to validate real shell output.

Examples:

```bash
uv run pytest -v --cov=. --cov-report=html
uv run pytest tests/integration/ -vs
cd tests/shell && shellspec -s zsh --kcov --kcov-options "--include-path=../../libs/,../../zsh-ai-assistant.plugin.zsh --include-pattern=.zsh,.sh"
```

---

## 6. Formatting & Static Analysis (Required)

CI MUST run and pass all of the following:

* Black (line-length = 88)
* Flake8 (only ignores: E203, W503)
* Mypy (strict)

Examples:

```bash
uv run black --check src tests
uv run flake8 src tests
uv run mypy src tests
```

---

## 7. Type Annotations (Part of Linting, Strict)

* Type checking is part of static analysis; rules must not be duplicated elsewhere.
* **All Python code and tests MUST have complete type annotations.**

  * Untyped `def` is forbidden.
* Required Mypy settings (minimum):

  * `disallow_untyped_defs = True`
  * `disallow_incomplete_defs = True`
  * `warn_return_any = True`
  * `warn_unused_ignores = True`
* External untyped libraries may use **targeted** ignores only:

  ```python
  import pexpect  # type: ignore[import-untyped]
  ```
* Forbidden:

  * Global `ignore_missing_imports = true`
  * Indiscriminate `# type: ignore`
  * Excessive or unnecessary use of `Any`

---

## 8. Documentation Management

* **Remove all temporary or redundant files before committing**, including:

  * `FINAL_SUMMARY.md`, `TEMP*.md`, `*.bak`, `*.tmp`, etc.
* **Only the following documents are allowed**:

  * `README.md`
  * `AGENTS.md`
  * `CHANGELOG.md`
  * API documentation
* Task-specific documents are allowed **only if unavoidable** and MUST be named:

  * `*_TASK_SPECIFIC.md`

---

## 9. LLM Agent Operational Rules (Mandatory)

* Follow instructions **literally**. If ambiguous, make minimal assumptions and return a complete result.
* **Do not claim async, background, or deferred work.**
* **Test-Driven Development (TDD) is mandatory**:
  1. Create a test list (e.g. `test_list.txt`).
  2. Select one test and write it first; confirm it fails.
  3. Implement the minimal code to pass the test.
  4. Refactor and update the test list.
  5. Repeat from step 2.
* **Tool usage**:
  * Every `bash` tool invocation MUST specify a `timeout`.
  * During debugging, add temporary timestamped logs.
  * Remove all unnecessary files after debugging.
  * Maintain and update a comprehensive plan using the `todo` tool.
* Perform external research when required and provide evidence when possible.
* **Before producing final output**, run tests, formatting, type checks, clean up unnecessary documents or snippets.

---

## 10. CI Requirements

A PR MUST pass:

* Black, Flake8 (restricted ignores only), and Mypy
* Pytest with coverage ≥ 90%
* Any modification to `.github/workflows/` requires explicit maintainer approval (recorded in PR comments)

---

## 11. Forbidden Actions & PR Checklist (Unified)

### Forbidden Actions (Complete List)

* Using `pip`, `python -m pip`, or any non-`uv` dependency management.
* Claiming async/background work or splitting results across responses.
* Disabling or bypassing linters, formatters, or type checks.
* Global or broad ignores in Mypy or Flake8.
* Adding or expanding Flake8 ignores without approval.
  * **Exception**: resolving a Black conflict requires explicit maintainer approval.
* Falsifying or manipulating coverage or test results.
* Committing temporary, draft, or task-artifact files.
* Modifying CI workflows to bypass checks without approval.
* Invoking the `bash` tool without a `timeout`.
* Working outside the `uv` virtual environment.
* Skipping any required test suite before PR submission.
* Running integration tests without `-s`.
* Including vulnable codes or documents like absolute path of the local machine, api key, user name or the other secret informations etc.
* Ignoring TDD or `todo` tool requirements (for agents).

### Mandatory Pre-PR Checklist

1. All work done inside a `uv` virtual environment.
2. ShellSpec, Python unit, and integration tests (`-s`) executed.
3. Coverage ≥ 90%.
4. Black, Flake8, and Mypy all pass with required settings.
5. All `bash` tool invocations include `timeout`.
6. Temporary and redundant files removed.
7. `.github/workflows/` changes approved by a maintainer (if applicable).
8. `todo` plan updated (agent workflows).
9. All vulnable codes or documents MUST NOT be published on the Internet removed.
10. Final output produced only after all checks pass.

---

## Appendix: Common Commands

```bash
# Environment
uv venv
source .venv/bin/activate
uv sync --all-extras

# Tests
uv run pytest -v --cov=. --cov-report=html
uv run pytest tests/integration/ -vs
cd tests/shell && shellspec --shell zsh

# Formatting & Analysis
uv run black --check src tests
uv run flake8 src tests
uv run mypy src tests
```
