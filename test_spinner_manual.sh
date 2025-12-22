#!/bin/zsh

# Manual test script to verify spinner functionality

# Initialize spinner
zsh_ai_assistant_spinner_frames=(⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏)
zsh_ai_assistant_spinner_frame_index=0
zsh_ai_assistant_spinner_pid=""
zsh_ai_assistant_spinner_control_file=""

echo "Testing spinner animation..."
echo "This should show an animated spinner for 3 seconds"
echo ""

# Show first frame
frame="${zsh_ai_assistant_spinner_frames[1]}"
echo -ne "$frame Testing spinner...\r"

# Start spinner in background
(
    while true; do
        zsh_ai_assistant_spinner_frame_index=$(( (zsh_ai_assistant_spinner_frame_index + 1) % ${#zsh_ai_assistant_spinner_frames} ))
        if [[ $zsh_ai_assistant_spinner_frame_index -eq 0 ]]; then
            zsh_ai_assistant_spinner_frame_index=${#zsh_ai_assistant_spinner_frames}
        fi
        frame="${zsh_ai_assistant_spinner_frames[zsh_ai_assistant_spinner_frame_index]}"
        echo -ne "$frame Testing spinner...\r"
        sleep 0.1
    done
) &

spinner_pid=$!
sleep 3

# Stop spinner
echo -ne "\r                              \r"
kill -TERM "$spinner_pid" 2>/dev/null || true

echo ""
echo "Spinner test completed successfully!"
