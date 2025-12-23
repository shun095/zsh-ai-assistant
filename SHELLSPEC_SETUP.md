# ShellSpec Testing Framework Setup

## Overview

This document describes the ShellSpec testing framework setup for the zsh-ai-assistant plugin.

## Installation

ShellSpec 0.28.1 has been installed using the web installer:

```bash
curl -fsSL https://git.io/shellspec | sh
```

The installer placed ShellSpec at: `/home/vibeuser/.local/bin/shellspec`

## Test Structure

```
tests/shell/
├── .shellspec                  # ShellSpec project marker
├── spec/                       # Test specifications
│   ├── spec_helper.sh          # Test helper and loader
│   ├── support/                # Test support files
│   │   └── before_all.sh        # Setup hook
│   └── directory_detection_spec.sh  # Main test file
└── run_shellspec.sh           # Wrapper script to run tests
```

## Running Tests

### Using the wrapper script (recommended):

```bash
./run_shellspec.sh
```

### Directly with ShellSpec:

```bash
cd tests/shell
shellspec --shell zsh
```

### With zsh directly:

```bash
cd tests/shell
export SHELLSPEC_SHELL=zsh
shellspec
```

## Test Coverage

The test suite currently covers:

- **Directory detection**: 5 test cases
- **Comment detection**: 6 test cases  
- **Comment extraction**: 4 test cases
- **Animation frame counting**: 2 test cases
- **Animation start time tracking**: 2 test cases

**Total: 19 test cases, all passing**

## Test File Details

### `spec/directory_detection_spec.sh`

This is the main test file containing comprehensive unit tests for the zsh plugin functions:

```zsh
Describe "Directory Detection"
  It "should detect plugin directory from script path"
  It "should detect plugin directory from $0"
  It "should detect plugin directory from current directory"
  It "should return error when directory cannot be detected"
  It "should handle edge cases"

Describe "Comment Detection"
  It "should detect comment in string"
  It "should detect comment at start of string"
  It "should detect comment at end of string"
  It "should detect comment in middle of string"
  It "should return false when no comment found"
  It "should handle empty string"

Describe "Comment Extraction"
  It "should extract comment from string"
  It "should extract comment at start"
  It "should extract comment at end"
  It "should handle string without comment"

Describe "Animation Frame Counting"
  It "should get and set animation frame count"
  It "should increment animation frame count"

Describe "Animation Start Time"
  It "should get and set animation start time"
  It "should handle animation start time"
```

## Test Helper

### `spec/spec_helper.sh`

The test helper sources the plugin before running tests:

```zsh
# Source the plugin
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR/../../.."

# Source the plugin
source "$PLUGIN_DIR/zsh-ai-assistant.plugin.zsh"
```

## Test Setup Hook

### `spec/support/before_all.sh`

This hook runs before all tests and sets up the test environment:

```zsh
# Setup test environment
setup_test_environment() {
  # Create temporary directory for tests
  export TEST_DIR="$(mktemp -d)"
  
  # Set up test variables
  export TEST_PLUGIN_DIR="$TEST_DIR/plugin"
  mkdir -p "$TEST_PLUGIN_DIR"
  
  # Copy plugin to test directory
  cp "$PLUGIN_DIR/zsh-ai-assistant.plugin.zsh" "$TEST_PLUGIN_DIR/"
}

setup_test_environment
```

## Wrapper Script

### `run_shellspec.sh`

The wrapper script ensures tests run with zsh:

```bash
#!/bin/bash
# Wrapper script to run ShellSpec tests with zsh

cd "$(dirname "$0")/tests/shell"
export SHELLSPEC_SHELL=zsh
shellspec --shell zsh
```

## Test-Driven Development Workflow

1. **Write tests first**: Create test cases in `spec/directory_detection_spec.sh`
2. **Run tests**: Execute `./run_shellspec.sh` to verify tests fail
3. **Implement code**: Add or modify functions in `zsh-ai-assistant.plugin.zsh`
4. **Run tests again**: Verify tests pass
5. **Refactor**: Improve code while keeping tests passing

## Integration with Existing Tests

The ShellSpec tests complement the existing pytest test suite:

- **Python tests**: 116 tests covering Python backend functionality
- **ShellSpec tests**: 19 tests covering zsh plugin functionality
- **Shell integration tests**: Existing pexpect-based tests

All test suites can be run together:

```bash
# Run Python tests
uv run pytest tests/python/ -v

# Run ShellSpec tests
./run_shellspec.sh

# Run shell integration tests
uv run pytest tests/shell/test_interactive.py -v -s
```

## CI/CD Integration

To integrate ShellSpec tests into CI/CD:

```yaml
- name: Run ShellSpec tests
  run: |
    cd tests/shell
    export SHELLSPEC_SHELL=zsh
    shellspec --shell zsh
```

## Troubleshooting

### ShellSpec uses /bin/sh instead of zsh

Ensure you specify the shell:

```bash
shellspec --shell zsh
```

### Functions not found in tests

Make sure the plugin is sourced in `spec/spec_helper.sh`:

```zsh
source "$PLUGIN_DIR/zsh-ai-assistant.plugin.zsh"
```

### Test environment issues

Check the `before_all.sh` hook for proper setup:

```zsh
setup_test_environment() {
  export TEST_DIR="$(mktemp -d)"
  # ... setup code
}
```

## Resources

- [ShellSpec Documentation](https://github.com/shellspec/shellspec)
- [ShellSpec GitHub](https://github.com/shellspec/shellspec)
- [ShellSpec Examples](https://github.com/shellspec/examples)
