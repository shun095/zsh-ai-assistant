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

# Flame animation characters
zsh_ai_assistant_flames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")

# Global variable to track animation process
zsh_ai_assistant_animation_pid=""

# Global variable to track foreground process
zsh_ai_assistant_foreground_pid=""

# Global variable to track animation control file
zsh_ai_assistant_animation_control_file=""

# Global variable to track animation start time for testing
zsh_ai_assistant_animation_start_time=""

# Global variable to track animation frame count for testing
zsh_ai_assistant_animation_frame_count=0

# Show flame animation in buffer
zsh_ai_assistant_show_loading() {
    # Only show loading message if ZLE is active
    if [[ -n "${ZLE_STATE:-}" ]]; then
        # Reset animation tracking variables
        zsh_ai_assistant_animation_start_time=""
        zsh_ai_assistant_animation_frame_count=0
        
        # Create a control file for inter-process communication
        zsh_ai_assistant_animation_control_file=$(mktemp -u)
        touch "$zsh_ai_assistant_animation_control_file"
        
        # Start flame animation in background
        (
            # Set options to suppress job control messages
            setopt local_options no_notify no_monitor
            
            # Flame characters as a string
            local flames="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            local flame_count=10
            
            # Animation loop
            local index=0
            local frame_count=0
            local start_time=$(date +%s%N)
            
            # Set animation start time for testing
            zsh_ai_assistant_animation_start_time="$start_time"
            
            # Run animation while control file exists
            while [[ -f "$zsh_ai_assistant_animation_control_file" ]]; do
                # Get current flame character
                local flame="${flames[$index]}"
                
                # Show flame animation
                # Write to stderr so pexpect can capture it (stdout is for command output)
                printf "$flame Generating command...\r" >&2
                
                # Increment index with wrap-around
                index=$(( (index + 1) % flame_count ))
                
                # Increment frame count for testing
                frame_count=$((frame_count + 1))
                zsh_ai_assistant_animation_frame_count=$frame_count
                
                # Ensure animation runs for at least 0.2 seconds to allow pexpect to capture it
                sleep 0.1
            done
            
            # Make sure we display at least one frame before exiting
            if [[ $frame_count -eq 0 ]]; then
                printf "⠋ Generating command...\r" >&2
            fi
        ) &
        
        # Capture the animation PID
        zsh_ai_assistant_animation_pid=$!
        
        # Start the foreground process in background
        # Use temporary files to capture output
        local stdout_file=$(mktemp)
        local stderr_file=$(mktemp)
        
        # Save current directory to restore later
        local original_dir=$(pwd)
        
        # Change to plugin directory to run uv commands
        cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
            echo "# Error: Could not change to plugin directory" >&2
            return 1
        }
        
        # Add --test flag if ZSH_AI_ASSISTANT_TEST_MODE is set
        local test_flag=""
        if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
            test_flag="--test"
        fi
        
        # Run uv command in background
        uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag command "$1" > "$stdout_file" 2> "$stderr_file" &
        zsh_ai_assistant_foreground_pid=$!
        
        # Restore original directory
        cd "$original_dir" >/dev/null 2>&1 || true
        
        # Wait for the foreground process to complete
        wait "$zsh_ai_assistant_foreground_pid"
        
        # Read the output after the process completes
        local generated_command=""
        local stderr_output=""
        
        if [[ -f "$stdout_file" ]]; then
            generated_command=$(cat "$stdout_file")
        fi
        if [[ -f "$stderr_file" ]]; then
            stderr_output=$(cat "$stderr_file")
        fi
        
        # Clean up temporary files
        rm -f "$stdout_file" "$stderr_file"
        
        # Give the animation a moment to display at least one frame
        sleep 0.2
        
        # Stop the animation by removing the control file
        rm -f "$zsh_ai_assistant_animation_control_file"
        
        # Wait for animation to finish
        wait "$zsh_ai_assistant_animation_pid" 2>/dev/null || true
        
        # If uv failed, return the captured stderr in the error message
        if [[ -z "$generated_command" ]] && [[ -n "$stderr_output" ]]; then
            echo "# Error: $stderr_output"
            return 1
        fi
        
        # Clean up
        zsh_ai_assistant_animation_pid=""
        zsh_ai_assistant_foreground_pid=""
        zsh_ai_assistant_animation_control_file=""
        
        # Return the generated command
        echo "$generated_command"
    fi
}

# Cleanup function for animation on SIGINT
zsh_ai_assistant_cleanup_animation() {
    # Kill the foreground process (uv command)
    if [[ -n "$zsh_ai_assistant_foreground_pid" ]]; then
        kill "$zsh_ai_assistant_foreground_pid" 2>/dev/null || true
    fi
    
    # Stop the animation by removing the control file
    if [[ -n "$zsh_ai_assistant_animation_control_file" ]] && [[ -f "$zsh_ai_assistant_animation_control_file" ]]; then
        rm -f "$zsh_ai_assistant_animation_control_file"
    fi
    
    # Kill the animation process
    if [[ -n "$zsh_ai_assistant_animation_pid" ]]; then
        kill "$zsh_ai_assistant_animation_pid" 2>/dev/null || true
    fi
    
    # Wait for both processes to finish
    wait "$zsh_ai_assistant_foreground_pid" 2>/dev/null || true
    wait "$zsh_ai_assistant_animation_pid" 2>/dev/null || true
    
    # Clean up
    zsh_ai_assistant_animation_pid=""
    zsh_ai_assistant_foreground_pid=""
    zsh_ai_assistant_animation_control_file=""
    
    # Remove the trap
    trap - INT
    
    # Exit the function to allow normal Ctrl+C behavior
    # The signal will be handled by the default handler
    return 1
}

# Hide loading message and refresh prompt
zsh_ai_assistant_hide_loading() {
    # Clear the animation line
    printf "\r\033[K"
    
    # Use zle to refresh the prompt properly
    if [[ -n "${ZLE_STATE:-}" ]]; then
        zle -R
    fi
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
    local stderr_output=""
    # Use temporary files to capture stdout and stderr separately
    local stdout_file=$(mktemp)
    local stderr_file=$(mktemp)
    
    # Save current directory to restore later
    local original_dir=$(pwd)
    
    # Change to plugin directory to run uv commands, then restore original directory
    # This ensures uv can find the virtual environment and dependencies
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag command "$comment" > "$stdout_file" 2> "$stderr_file"
    
    # Restore original directory
    cd "$original_dir" >/dev/null 2>&1 || true
    
    # Check the exit code of the uv command
    local uv_exit_code=$?
    
    # Read the captured output
    if [[ -f "$stdout_file" ]]; then
        generated_command=$(cat "$stdout_file")
    fi
    if [[ -f "$stderr_file" ]]; then
        stderr_output=$(cat "$stderr_file")
    fi
    
    # Clean up temporary files
    rm -f "$stdout_file" "$stderr_file"
    
    if [[ $uv_exit_code -eq 0 ]] && [[ -n "$generated_command" ]]; then
        echo "$generated_command"
        return 0
    else
        # If uv failed, return the captured stderr in the error message
        if [[ -n "$stderr_output" ]]; then
            echo "# Error: $stderr_output"
        else
            echo "# Error: Failed to generate command"
        fi
        return 1
    fi
}

# SIGTERM handler to interrupt animation and foreground process
zsh_ai_assistant_sigterm_handler() {
    # Stop the animation by removing the control file
    if [[ -n "$zsh_ai_assistant_animation_control_file" ]] && [[ -f "$zsh_ai_assistant_animation_control_file" ]]; then
        rm -f "$zsh_ai_assistant_animation_control_file"
    fi
    
    # Kill processes
    if [[ -n "$zsh_ai_assistant_animation_pid" ]]; then
        kill "$zsh_ai_assistant_animation_pid" 2>/dev/null || true
    fi
    if [[ -n "$zsh_ai_assistant_foreground_pid" ]]; then
        kill "$zsh_ai_assistant_foreground_pid" 2>/dev/null || true
    fi
    
    # Clear animation line
    printf "\r\033[K" 2>/dev/null || true
    
    # Restore prompt
    if [[ -n "${ZLE_STATE:-}" ]]; then
        zle -R 2>/dev/null || true
    fi
    
    # Exit with error code
    exit 1
}

# Command transformation function (zle-dependent wrapper)
zsh_ai_assistant_transform_command() {
    local prompt="$1"
    
    # Set up SIGTERM handler
    trap zsh_ai_assistant_sigterm_handler SIGTERM
    
    # Set up SIGINT handler for Ctrl+C
    trap zsh_ai_assistant_cleanup_animation INT
    
    # Show loading animation and get generated command
    local generated_command=""
    generated_command=$(zsh_ai_assistant_show_loading "$prompt")
    
    # Remove signal handlers
    trap - SIGTERM
    trap - INT
    
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

# AI chat function - minimal wrapper that delegates to Python
zsh_ai_assistant_chat() {
    # Add --test flag if ZSH_AI_ASSISTANT_TEST_MODE is set
    local test_flag=""
    if [[ -n "${ZSH_AI_ASSISTANT_TEST_MODE:-}" ]]; then
        test_flag="--test"
    fi
    
    # Save current directory to restore later
    local original_dir=$(pwd)
    
    # Change to plugin directory to run uv commands, then restore original directory
    cd "${ZSH_AI_ASSISTANT_DIR}" >/dev/null 2>&1 || {
        echo "# Error: Could not change to plugin directory" >&2
        return 1
    }
    
    # Run interactive chat using Python backend
    uv run python "${ZSH_AI_ASSISTANT_DIR}/src/zsh_ai_assistant/cli.py" $test_flag interactive
    
    # Restore original directory
    cd "$original_dir" >/dev/null 2>&1 || true
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

# Test helper function - gets animation frame count
test_get_animation_frame_count() {
    echo "$zsh_ai_assistant_animation_frame_count"
}

# Test helper function - gets animation start time
test_get_animation_start_time() {
    echo "$zsh_ai_assistant_animation_start_time"
}
