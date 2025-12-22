#!/bin/zsh

# Test with correct octal sequences
echo "=== Test: Correct octal sequences ==="

frames=($(printf '\342\240\213 \342\240\231 \342\240\271 \342\240\270 \342\240\274 \342\240\264'))
echo "Array length: ${#frames}"

for i in {1..6}; do
    if [[ -n "${frames[$i]}" ]]; then
        char="${frames[$i]}"
        code=$(printf '%d' "'$char'")
        echo "Frame $i: '$char' (code: $code)"
        
        # Check if it matches expected
        case $i in
            1) expected="⠋";;
            2) expected="⠙";;
            3) expected="⠹";;
            4) expected="⠸";;
            5) expected="⠼";;
            6) expected="⠴";;
        esac
        
        if [[ "$char" == "$expected" ]]; then
            echo "  ✓ Correct"
        else
            echo "  ✗ Expected '$expected' (code: $(printf '%d' "'$expected'"))"
        fi
    fi
done

echo ""
echo "=== Test: Animation ==="
frame_index=0

for i in {1..20}; do
    char="${frames[$frame_index]}"
    echo -n "$char Generating command..."
    echo -ne "\r"
    
    frame_index=$(( (frame_index + 1) % ${#frames} ))
    
    sleep 0.1
done

echo ""
echo "Done!"
