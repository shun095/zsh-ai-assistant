# zsh-ai-assistant plugin
# Main plugin file for oh-my-zsh

# Configuration
# Determine the plugin directory properly when loaded by oh-my-zsh
# Try multiple methods to find the plugin directory

# Method 1: Check if we're in oh-my-zsh custom plugins
if [[ -n "$ZSH_CUSTOM" ]] && [[ "$0" == *"$ZSH_CUSTOM"* ]]; then
    ZSH_AI_ASSISTANT_DIR="${0:h}"
# Method 2: Check if we're in oh-my-zsh standard plugins  
elif [[ -n "$ZSH" ]] && [[ "$0" == *"$ZSH"* ]]; then
    ZSH_AI_ASSISTANT_DIR="${0:h}"
# Method 3: Try to find plugin relative to current working directory
elif [[ -d "zsh-ai-assistant" ]] && [[ -f "zsh-ai-assistant/zsh-ai-assistant.plugin.zsh" ]]; then
    ZSH_AI_ASSISTANT_DIR="zsh-ai-assistant"
# Method 4: Use realpath as fallback
else
    PLUGIN_FILE="$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")"
    ZSH_AI_ASSISTANT_DIR="${PLUGIN_FILE:h}"
fi

# Ensure we have the correct path
# Only use cd if the directory exists
if [[ -d "$ZSH_AI_ASSISTANT_DIR" ]]; then
    ZSH_AI_ASSISTANT_DIR="$(cd "$ZSH_AI_ASSISTANT_DIR" && pwd)"
else
    # Fallback: try to find the plugin in common locations
    # Try to find plugin relative to home directory
    local home_dir="${HOME:-}"
    if [[ -n "$home_dir" ]]; then
        if [[ -d "$home_dir/.oh-my-zsh/custom/plugins/zsh-ai-assistant" ]]; then
            ZSH_AI_ASSISTANT_DIR="$home_dir/.oh-my-zsh/custom/plugins/zsh-ai-assistant"
        elif [[ -d "$home_dir/.oh-my-zsh/plugins/zsh-ai-assistant" ]]; then
            ZSH_AI_ASSISTANT_DIR="$home_dir/.oh-my-zsh/plugins/zsh-ai-assistant"
        fi
    fi
    
    # If still not found, try to find it using git
    if [[ -z "$ZSH_AI_ASSISTANT_DIR" ]]; then
        local git_root=""
        git_root=$(git rev-parse --show-toplevel 2>/dev/null)
        if [[ -n "$git_root" ]] && [[ -f "$git_root/zsh-ai-assistant.plugin.zsh" ]]; then
            ZSH_AI_ASSISTANT_DIR="$git_root"
        fi
    fi
    
    if [[ -z "$ZSH_AI_ASSISTANT_DIR" ]]; then
        echo "Error: Could not determine plugin directory" >&2
        return 1
    fi
fi

# Check if Python backend is available
ZSH_AI_ASSISTANT_PYTHON_BIN="${ZSH_AI_ASSISTANT_DIR}/.venv/bin/python"
if [[ ! -f "${ZSH_AI_ASSISTANT_PYTHON_BIN}" ]]; then
    # Try to find the virtual environment
    if [[ -d "${ZSH_AI_ASSISTANT_DIR}/.venv" ]]; then
        ZSH_AI_ASSISTANT_PYTHON_BIN="${ZSH_AI_ASSISTANT_DIR}/.venv/bin/python"
    fi
fi

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required for zsh-ai-assistant" >&2
    return 1
fi

# Use system Python if virtual environment not found
if [[ ! -f "${ZSH_AI_ASSISTANT_PYTHON_BIN}" ]]; then
    ZSH_AI_ASSISTANT_PYTHON_BIN="python3"
fi

# Check if required Python modules are available
# This check will be done when functions are called, not during plugin load

# Show loading message in buffer
zsh_ai_assistant_show_loading() {
    # Only show loading message if ZLE is active
    if [[ -n "${ZLE_STATE:-}" ]]; then
        # Show loading message in buffer
        BUFFER="🤖 Generating command..."
        # Move cursor to end
        CURSOR=${#BUFFER}
        # Use zle -R for buffer update only (not reset-prompt)
        zle -R
    fi
}

# Hide loading message (no-op, buffer is already restored)
zsh_ai_assistant_hide_loading() {
    # No action needed as buffer is restored in show_loading
    # This function is kept for API consistency
    :
}

# Core command transformation logic (testable without zle)
zsh_ai_assistant_convert_comment_to_command() {
    local prompt="$1"
    
    # Check if line starts with # (after trimming leading whitespace)
    local trimmed_prompt="${prompt#"${prompt%%[![:space:]]*}"}"
    if [[ ! "$trimmed_prompt" =~ ^[[:space:]]*# ]]; then
        # Not a comment, return 1
        return 1
    fi
    
    # Extract comment content (remove leading # and whitespace)
    local comment="${prompt#\#}"
    
    # Trim leading and trailing whitespace
    comment="${comment#"${comment%%[![:space:]]*}"}"
    comment=$(echo "$comment" | sed 's/[[:space:]]*$//')
    
    if [[ -z "$comment" ]]; then
        return 1
    fi
    
    # Call Python backend to generate command using uv run
    # Add --test flag if ZSH_AI_ASSISTANT_TEST_MODE is set
    local test_flag=""
    if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
        test_flag="--test"
    fi
    
    local generated_command=""
    generated_command=$(uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag command "$comment" 2>/dev/null)
    
    if [[ -n "$generated_command" ]]; then
        echo "$generated_command"
        return 0
    else
        return 1
    fi
}

# Command transformation function (zle-dependent wrapper)
zsh_ai_assistant_transform_command() {
    local prompt="$1"
    
    zsh_ai_assistant_show_loading
    
    local generated_command=""
    generated_command=$(zsh_ai_assistant_convert_comment_to_command "$prompt")
    
    # Hide loading message after generation
    zsh_ai_assistant_hide_loading
    
    if [[ -n "$generated_command" ]]; then
        # Replace the current prompt with the generated command
        BUFFER="$generated_command"
        # Move cursor to end of command
        CURSOR=${#BUFFER}
        # Only call zle commands if ZLE is active
        if [[ -n "${ZLE_STATE:-}" ]]; then
            # Use zle -R for buffer update only (not reset-prompt)
            zle -R
        fi
        # Don't execute the command, just show it in the prompt
        return 0
    else
        # If no command was generated, execute the original line
        if [[ -n "${ZLE_STATE:-}" ]]; then
            zle .accept-line
        fi
        return 0
    fi
}

# AI chat function
zsh_ai_assistant_chat() {
    # Continuous chat loop
    # Use OpenAI API compatible JSON format throughout
    # Initialize chat history as JSON array
    local chat_history='[]'
    while true; do
        printf "Me: "
        
        # Read user input
        local user_input=""
        read -r user_input
        
        # Exit on empty input or 'quit'/'exit'
        if [[ -z "$user_input" ]] || [[ "$user_input" =~ ^(quit|exit|q)$ ]]; then
            echo "Goodbye!"
            break
        fi
        
        # Add user message to chat history using jq
        # This maintains OpenAI API compatible format: {"role": "user", "content": "message"}
        chat_history=$(jq --arg role "user" --arg content "$user_input" '. + [$ARGS.named]' <<< "$chat_history")
        
        # Add --test flag if ZSH_AI_ASSISTANT_TEST_MODE is set
        local test_flag=""
        if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
            test_flag="--test"
        fi
        
        # Call Python backend for AI response using uv run
        # Pass the complete chat history in OpenAI format
        local ai_response=""
        ai_response=$(printf "%s" "$chat_history" | uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag chat 2>/dev/null)
        
        if [[ -n "$ai_response" ]]; then
            # Handle multi-line AI responses properly
            # Use echo with -e to interpret escape sequences
            echo -e "AI: $ai_response"
            
            # Add AI response to chat history using jq
            # Maintain OpenAI API format: {"role": "assistant", "content": "response"}
            # Use jq to properly handle multi-line content
            chat_history=$(jq --arg role "assistant" --arg content "$ai_response" '. + [$ARGS.named]' <<< "$chat_history")
        fi
    done
}

# Widget for command transformation
zle -N zsh_ai_assistant_transform_command

# Widget for AI chat
zle -N zsh_ai_assistant_chat

# Bind command transformation to Enter key when line starts with #
# Only set up zle bindings if zle is available (interactive shell)
if [[ -n "$ZSH_VERSION" ]] && command -v zle >/dev/null 2>&1; then
    zsh_ai_assistant_check_for_comment() {
        local line="$1"
        
        # Check if line starts with # (after trimming leading whitespace)
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

    # Define the accept-line wrapper function
    zsh_ai_assistant_accept_line_wrapper() {
        if zsh_ai_assistant_check_for_comment "$BUFFER"; then
            # Call the transform command function
            zsh_ai_assistant_transform_command "$BUFFER"
            # After transformation, we need to redraw the buffer to show the new command
            # but NOT execute it yet. The user will need to press Enter again.
            if [[ -n "${ZLE_STATE:-}" ]]; then
                # Use zle -R for buffer update only (not reset-prompt)
                zle -R
            fi
            # Don't execute, just show the transformed command
            return
        fi
        
        # Not a comment, execute normally
        # Always use zle .accept-line to execute the command
        if [[ -n "${ZLE_STATE:-}" ]]; then
            zle .accept-line
        fi
    }

    # Bind the check function to the accept-line widget
    # Store original accept-line widget name
    zsh_ai_assistant_original_accept_line_widget="${widgets[accept-line]}"
    
    # Load plugin
    autoload -Uz zsh_ai_assistant_check_for_comment
    zle -N zsh_ai_assistant_accept_line_wrapper
    
    # Bind the accept-line wrapper to the Enter key
    bindkey "^M" zsh_ai_assistant_accept_line_wrapper
else
    echo "zle is not available"
fi

# Add aiask command
aiask() {
    zsh_ai_assistant_chat
}

# Test helper function - transforms comment to command without zle
test_transform_comment() {
    local prompt="$1"
    
    local generated_command
    generated_command=$(zsh_ai_assistant_convert_comment_to_command "$prompt")
    
    if [[ -n "$generated_command" ]]; then
        echo "$generated_command"
        return 0
    else
        return 1
    fi
}
