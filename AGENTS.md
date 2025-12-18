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
