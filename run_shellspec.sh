#!/bin/bash
# Wrapper script to run ShellSpec tests with zsh

cd "$(dirname "$0")/tests/shell"
export SHELLSPEC_SHELL=zsh
/home/vibeuser/.local/bin/shellspec --shell zsh
