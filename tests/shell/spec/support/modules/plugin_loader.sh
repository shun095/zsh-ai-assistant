#!/usr/bin/env zsh

# This module sources the zsh-ai-assistant plugin to make its functions available
# to ShellSpec tests

# Find the plugin file
if [[ -f "zsh-ai-assistant.plugin.zsh" ]]; then
    PLUGIN_PATH="zsh-ai-assistant.plugin.zsh"
elif [[ -f "../../../../zsh-ai-assistant.plugin.zsh" ]]; then
    PLUGIN_PATH="../../../../zsh-ai-assistant.plugin.zsh"
elif [[ -f "$PWD/zsh-ai-assistant.plugin.zsh" ]]; then
    PLUGIN_PATH="$PWD/zsh-ai-assistant.plugin.zsh"
else
    # Try to find it relative to this module
    SCRIPT_DIR="${0:a:h}"
    PROJECT_ROOT="${SCRIPT_DIR:h:h:h:h}"
    if [[ -f "$PROJECT_ROOT/zsh-ai-assistant.plugin.zsh" ]]; then
        PLUGIN_PATH="$PROJECT_ROOT/zsh-ai-assistant.plugin.zsh"
    else
        echo "ERROR: Could not find zsh-ai-assistant.plugin.zsh" >&2
        return 1
    fi
fi

# Source the plugin
if [[ -f "$PLUGIN_PATH" ]]; then
    source "$PLUGIN_PATH"
    echo "Loaded plugin from: $PLUGIN_PATH" >&2
else
    echo "ERROR: Plugin file not found at $PLUGIN_PATH" >&2
    return 1
fi
