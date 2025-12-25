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
    
    # DEBUG: Log that animation started
    echo "DEBUG: Animation started" >&2
    
    # Check if we should use plain text mode (for tests or macOS)
    # This avoids terminal control code issues with pexpect on macOS
    local use_plain_text=0
    if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        use_plain_text=1
        echo "DEBUG: Using plain text animation mode" >&2
    fi
    
    while true; do
        index=$(( (index) % flame_count + 1 ))
        index_sub=$(( (index_sub) % flame_sub_count + 1 ))
        
        if [[ $use_plain_text -eq 1 ]]; then
            # Plain text mode - no terminal control codes
            echo "${loading_flames[$index]} Generating command${loading_flames_sub[$index_sub]}" >&2
        else
            # Normal mode with terminal control codes
            echo -ne "\033[2K\033[G"
            echo -ne "${loading_flames[$index]} Generating command${loading_flames_sub[$index_sub]}\r"
        fi
        
        # DEBUG: Log each frame
        echo "DEBUG: Animation frame: ${loading_flames[$index]}" >&2
        
        sleep 0.1
    done
}

# Show loading animation
zsh_ai_assistant_show_loading() {
    # DEBUG: Log that show_loading was called
    echo "DEBUG: show_loading called" >&2
    
    setopt no_notify no_monitor
    trap zsh_ai_assistant_hide_loading INT
    zsh_ai_assistant_background_animation &
    zsh_ai_assistant_animation_pid=$!
    
    # DEBUG: Log animation PID
    echo "DEBUG: Animation PID = $zsh_ai_assistant_animation_pid" >&2
}

# Hide loading animation
zsh_ai_assistant_hide_loading() {
    # DEBUG: Log that hide_loading was called
    echo "DEBUG: hide_loading called" >&2
    
    if [[ -n "$zsh_ai_assistant_animation_pid" ]]; then
        echo "DEBUG: Killing animation PID = $zsh_ai_assistant_animation_pid" >&2
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
    
    # DEBUG: Log that generate_command was called
    echo "DEBUG: generate_command called with comment: $comment" >&2
    
    local original_dir=$(pwd)
    
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    local test_flag=""
    if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
        test_flag="--test"
    fi
    
    echo "DEBUG: Running: uv run python ${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py $test_flag command \"$comment\"" >&2
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag command "$comment" > "$stdout_file" 2> "$stderr_file"
    
    cd "$original_dir" >/dev/null 2>&1 || true
    
    local uv_exit_code=$?
    
    # DEBUG: Log exit code and file contents
    echo "DEBUG: uv exit code = $uv_exit_code" >&2
    if [[ -f "$stdout_file" ]]; then
        echo "DEBUG: stdout_file contents: $(cat "$stdout_file")" >&2
    fi
    if [[ -f "$stderr_file" ]]; then
        echo "DEBUG: stderr_file contents: $(cat "$stderr_file")" >&2
    fi
    
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
    
    # DEBUG: Log that transform_command was called
    echo "DEBUG: transform_command called with prompt: $prompt" >&2
    
    # Phase 1: Show animation
    zsh_ai_assistant_show_loading
    
    # Phase 2: Generate command
    local generated_command=""
    generated_command=$(zsh_ai_assistant_generate_command "$prompt")
    
    # DEBUG: Log generated command
    echo "DEBUG: generated_command = $generated_command" >&2
    
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
    local test_flag=""
    if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
        test_flag="--test"
    fi
    
    local original_dir=$(pwd)
    
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag interactive
    
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
