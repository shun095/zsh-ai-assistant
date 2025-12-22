#!/bin/zsh

# Test using printf to generate Unicode characters at runtime
echo "=== Test: Using printf to generate spinner frames ==="

# Define spinner frames using printf
zsh_ai_assistant_spinner_frames=()
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\213'))  # ⠋
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\211'))  # ⠙
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\211'))  # ⠹
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\210'))  # ⠸
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\214'))  # ⠼
zsh_ai_assistant_spinner_frames+=($(printf '\342\240\204'))  # ⠴

echo "Array length: ${#zsh_ai_assistant_spinner_frames}"

# Test each frame
for i in {0..5}; do
    frame="${zsh_ai_assistant_spinner_frames[$i]}"
    echo "Frame $i: '$frame' (length: ${#frame})"
    
    # Check if it's the expected character
    if [[ "$frame" == "⠋" ]]; then
        echo "  ✓ Frame 0 is correct"
    elif [[ "$frame" == "⠙" ]]; then
        echo "  ✓ Frame 1 is correct"
    elif [[ "$frame" == "⠹" ]]; then
        echo "  ✓ Frame 2 is correct"
    elif [[ "$frame" == "⠸" ]]; then
        echo "  ✓ Frame 3 is correct"
    elif [[ "$frame" == "⠼" ]]; then
        echo "  ✓ Frame 4 is correct"
    elif [[ "$frame" == "⠴" ]]; then
        echo "  ✓ Frame 5 is correct"
    else
        echo "  ✗ Frame $i is NOT correct"
    fi
done

echo ""
echo "=== Test: Animation loop ==="
zsh_ai_assistant_spinner_frame_index=0

for i in {1..10}; do
    frame="${zsh_ai_assistant_spinner_frames[zsh_ai_assistant_spinner_frame_index]}"
    echo -n "$frame Generating command..."
    echo -ne "\r"
    
    # Increment frame index
    zsh_ai_assistant_spinner_frame_index=$(( (zsh_ai_assistant_spinner_frame_index + 1) % ${#zsh_ai_assistant_spinner_frames} ))
    
    sleep 0.2
done

echo ""
echo "=== Test: BUFFER simulation ==="
BUFFER="${zsh_ai_assistant_spinner_frames[0]} Generating command..."
echo "BUFFER: '$BUFFER'"

if [[ "$BUFFER" == *"⠋"* ]]; then
    echo "✓ Unicode character found in BUFFER"
else
    echo "✗ Unicode character NOT found in BUFFER"
fi
