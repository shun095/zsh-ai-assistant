#!/bin/zsh

# Test to see what printf actually generates
echo "=== Test: What does printf generate? ==="

# Test each octal sequence individually
echo "Testing octal sequences:"
char1=$(printf '\342\240\213')
echo "\\342\\240\\213 -> '$char1' (code: $(printf '%d' "'$char1'"))"

char2=$(printf '\342\240\211')
echo "\\342\\240\\211 -> '$char2' (code: $(printf '%d' "'$char2'"))"

char3=$(printf '\342\240\210')
echo "\\342\\240\\210 -> '$char3' (code: $(printf '%d' "'$char3'"))"

char4=$(printf '\342\240\214')
echo "\\342\\240\\214 -> '$char4' (code: $(printf '%d' "'$char4'"))"

char5=$(printf '\342\240\204')
echo "\\342\\240\\204 -> '$char5' (code: $(printf '%d' "'$char5'"))"

echo ""
echo "Expected characters (Unicode braille patterns):"
echo "⠋ (U+280B) - code: $(printf '%d' "'⠋'")"
echo "⠙ (U+2819) - code: $(printf '%d' "'⠙'")"
echo "⠹ (U+2819) - code: $(printf '%d' "'⠹'")"
echo "⠸ (U+2818) - code: $(printf '%d' "'⠸'")"
echo "⠼ (U+281C) - code: $(printf '%d' "'⠼'")"
echo "⠴ (U+2814) - code: $(printf '%d' "'⠴'")"

echo ""
echo "=== Test: Using direct Unicode in function ==="

# Try using direct Unicode characters in a function
zsh_ai_assistant_init_spinner_direct() {
    # Use direct Unicode characters
    zsh_ai_assistant_spinner_frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴')
}

zsh_ai_assistant_init_spinner_direct

echo "Array length: ${#zsh_ai_assistant_spinner_frames}"

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
echo "=== Test: BUFFER with direct Unicode ==="
BUFFER="${zsh_ai_assistant_spinner_frames[0]} Generating command..."
echo "BUFFER: '$BUFFER'"

if [[ "$BUFFER" == *"⠋"* ]]; then
    echo "✓ Unicode character found in BUFFER"
else
    echo "✗ Unicode character NOT found in BUFFER"
fi
