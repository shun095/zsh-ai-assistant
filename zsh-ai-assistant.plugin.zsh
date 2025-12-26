# zsh-ai-assistant plugin

# Configuration
# Determine the plugin directory from the script location
PLUGIN_FILE="$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")"
ZSH_AI_ASSISTANT_DIR="${PLUGIN_FILE:h}"

# Ensure we have the correct path
if [[ -d "$ZSH_AI_ASSISTANT_DIR" ]]; then
    ZSH_AI_ASSISTANT_DIR="$(cd "$ZSH_AI_ASSISTANT_DIR" && pwd)"
else
    echo "Error: Could not determine plugin directory" >&2
    return 1
fi

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required for zsh-ai-assistant" >&2
    return 1
fi

zsh_ai_assistant_detect_plugin_dir() {
    # Check if plugin directory exists relative to current working directory
    # This handles development/testing scenarios where the plugin is in a subdirectory
    if [[ -d "zsh-ai-assistant" ]] && [[ -f "zsh-ai-assistant/zsh-ai-assistant.plugin.zsh" ]]; then
        echo "zsh-ai-assistant"
        return
    fi
    
    PLUGIN_FILE="$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")"
    local dir="${PLUGIN_FILE:h}"
    if [[ -d "$dir" ]]; then
        dir="$(cd "$dir" && pwd)"
    fi
    echo "$dir"
}

# This is the version used for testing and in the zle wrapper
zsh_ai_assistant_check_for_comment() {
    local line="$1"
    
    # Check if the input contains newlines (multiline input)
    if [[ "$line" == *$'\n'* ]]; then
        # This is a multiline input, don't process with AI
        return 1
    fi
    
    local trimmed_line="${line#\"${line%%[![:space:]]*}\"}"
    if [[ "$trimmed_line" =~ ^[[:space:]]*# ]]; then
        # Found a comment, check if there's content after #
        local comment_content="${trimmed_line#\#}"
        comment_content="${comment_content# }"  # Remove leading space
        if [[ -n "${comment_content%%[[:space:]]*}" ]]; then
            # Check if this is an error message (should not be transformed again)
            if [[ "$trimmed_line" =~ ^[[:space:]]*#.*Error: ]]; then
                # This is an error message, don't transform it
                return 1
            fi
            # Found a comment with content, return 0
            return 0
        fi
        return 1
    fi
    
    return 1
}

# Global variable to track animation process
zsh_ai_assistant_animation_pid=""

# Background animation function
zsh_ai_assistant_background_animation() {
    local loading_flames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    local loading_flames_sub=("." ".." "...")
    local flame_count=${#loading_flames}
    local flame_sub_count=${#loading_flames_sub}
    local index=0
    local index_sub=0
    
    while true; do
        index=$(( (index) % flame_count + 1 ))
        index_sub=$(( (index_sub) % flame_sub_count + 1 ))
        echo -ne "\033[2K\033[G"
        echo -ne "${loading_flames[$index]} Generating command${loading_flames_sub[$index_sub]}\r"
        sleep 0.1
    done
}

# Show loading animation
zsh_ai_assistant_show_loading() {
    setopt no_notify no_monitor
    trap zsh_ai_assistant_hide_loading INT
    zsh_ai_assistant_background_animation &
    zsh_ai_assistant_animation_pid=$!
}

# Hide loading animation
zsh_ai_assistant_hide_loading() {
    if [[ -n "$zsh_ai_assistant_animation_pid" ]]; then
        kill "$zsh_ai_assistant_animation_pid" 2>/dev/null || true
        wait "$zsh_ai_assistant_animation_pid"
    fi
    trap - INT
    zsh_ai_assistant_animation_pid=""
    unset notify monitor
}

# Generate command from comment
zsh_ai_assistant_generate_command() {
    local comment="$1"
    local generated_command=""
    local stderr_output=""
    local stdout_file=$(mktemp)
    local stderr_file=$(mktemp)
    
    local original_dir=$(pwd)
    
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" command "$comment" > "$stdout_file" 2> "$stderr_file"
    
    cd "$original_dir" >/dev/null 2>&1 || true
    
    local uv_exit_code=$?
    
    if [[ -f "$stdout_file" ]]; then
        generated_command=$(cat "$stdout_file")
    fi
    if [[ -f "$stderr_file" ]]; then
        stderr_output=$(cat "$stderr_file")
    fi
    
    rm -f "$stdout_file" "$stderr_file"
    
    if [[ $uv_exit_code -eq 0 ]] && [[ -n "$generated_command" ]]; then
        echo "$generated_command"
        return 0
    else
        if [[ -n "$stderr_output" ]]; then
            echo "# Error: $stderr_output"
        else
            echo "# Error: Failed to generate command"
        fi
        return 1
    fi
}

# Command transformation function (zle-dependent wrapper)
zsh_ai_assistant_transform_command() {
    local prompt="$1"
    
    # Phase 1: Show animation
    zsh_ai_assistant_show_loading
    
    # Phase 2: Generate command
    local generated_command=""
    generated_command=$(zsh_ai_assistant_generate_command "$prompt")
    
    # Phase 3: Hide animation
    zsh_ai_assistant_hide_loading
    
    # Phase 4: Replace BUFFER
    if [[ -n "$generated_command" ]]; then
        BUFFER="$generated_command"
        CURSOR=${#BUFFER}
        if [[ -n "${ZLE_STATE:-}" ]]; then
            zle .redisplay
        fi
        return 0
    else
        if [[ -n "${ZLE_STATE:-}" ]]; then
            zle .accept-line
        fi
        return 0
    fi
}

# AI chat function - minimal wrapper that delegates to Python
zsh_ai_assistant_chat() {
    local original_dir=$(pwd)
    
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" interactive
    
    cd "$original_dir" >/dev/null 2>&1 || true
}

# Only set up zle bindings if zle is available (interactive shell)
if [[ -n "$ZSH_VERSION" ]] && command -v zle >/dev/null 2>&1; then
    # Define the accept-line wrapper function
    zsh_ai_assistant_accept_line_wrapper() {
        if zsh_ai_assistant_check_for_comment "$BUFFER"; then
            zsh_ai_assistant_transform_command "$BUFFER"
            if [[ -n "${ZLE_STATE:-}" ]]; then
                zle -R
            fi
            return
        fi
        
        if [[ -n "${ZLE_STATE:-}" ]]; then
            zle .accept-line
        fi
    }
    
    # Register the function as a zle widget
    zle -N zsh_ai_assistant_accept_line_wrapper
    
    # Bind the accept-line wrapper to the Enter key
    bindkey "^M" zsh_ai_assistant_accept_line_wrapper
else
    echo "zle is not available" >&2
fi

# Add aiask command
aiask() {
    zsh_ai_assistant_chat
}

# Add aitrans command
aitrans() {
    local text=""
    local target_language="japanese"
    
    # Check if text is provided as first argument
    if [[ $# -gt 0 ]]; then
        text="$*"
    # Read text to translate from stdin or prompt
    elif [[ -p /dev/stdin ]]; then
        text=$(cat)
    else
        echo "Text to translate (Ctrl+D to finish):"
        # Read multiline input from terminal
        while IFS= read -r line; do
            text+="$line"$'\n'
        done
    fi
    
    local original_dir=$(pwd)
    
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    # Call Python translation function
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" translate "$target_language" "$text"
    
    cd "$original_dir" >/dev/null 2>&1 || true
}
