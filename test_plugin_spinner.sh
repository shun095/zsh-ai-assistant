#!/bin/zsh

# Test the spinner initialization from the plugin

# Simulate the plugin's spinner initialization
zsh_ai_assistant_spinner_frames=()
zsh_ai_assistant_spinner_frame_index=0

# Initialize spinner frames with Unicode braille patterns
zsh_ai_assistant_init_spinner() {
    # Use direct Unicode characters for spinner animation
    zsh_ai_assistant_spinner_frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠇' '⠏' '⠋')
}

# Initialize spinner when plugin loads
zsh_ai_assistant_init_spinner

echo "Array length: ${#zsh_ai_assistant_spinner_frames}"

for i in {0..9}; do
    frame="${zsh_ai_assistant_spinner_frames[$i]}"
    echo "Frame $i: '$frame' (length: ${#frame})"
done

echo ""
echo "=== Test: Animation loop ==="
zsh_ai_assistant_spinner_frame_index=0

for i in {1..20}; do
    frame="${zsh_ai_assistant_spinner_frames[zsh_ai_assistant_spinner_frame_index]}"
    echo -n "$frame Generating command..."
    echo -ne "\r"
    
    # Increment frame index
    zsh_ai_assistant_spinner_frame_index=$(( (zsh_ai_assistant_spinner_frame_index + 1) % ${#zsh_ai_assistant_spinner_frames} ))
    
    sleep 0.1
done

echo ""
echo "Done!"
