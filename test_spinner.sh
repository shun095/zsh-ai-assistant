#!/bin/zsh

# Test script to verify spinner functionality

# Initialize spinner
zsh_ai_assistant_spinner_frames=()
zsh_ai_assistant_spinner_frame_index=0

zsh_ai_assistant_init_spinner() {
    # Generate spinner frames using printf with UTF-8 byte sequences
    zsh_ai_assistant_spinner_frames=($(printf '\342\240\213 \342\240\231 \342\240\271 \342\240\270 \342\240\274 \342\240\264'))
}

zsh_ai_assistant_init_spinner

echo "Spinner frames initialized:"
echo "Number of frames: ${#zsh_ai_assistant_spinner_frames}"

for i in {1..${#zsh_ai_assistant_spinner_frames}}; do
    frame="${zsh_ai_assistant_spinner_frames[$i]}"
    echo "Frame $i: '$frame' (length: ${#frame})"
done

echo ""
echo "Testing spinner animation:"
for i in {1..12}; do
    frame="${zsh_ai_assistant_spinner_frames[$i]}"
    echo -n "$frame Generating command...\r"
    sleep 0.2
done
echo ""
