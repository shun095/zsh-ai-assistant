#!/bin/zsh

# Test printf with array assignment
echo "=== Test: printf in array assignment ==="

frames=()
frames+=($(printf '\342\240\213'))  # ⠋
echo "After adding first frame:"
echo "Array length: ${#frames}"
for i in {0..${#frames}}; do
    if [[ -n "${frames[$i]}" ]]; then
        echo "  Frame $i: '${frames[$i]}' (code: $(printf '%d' "'${frames[$i]}'"))"
    fi
done

frames+=($(printf '\342\240\211'))  # ⠙
echo "After adding second frame:"
echo "Array length: ${#frames}"
for i in {0..${#frames}}; do
    if [[ -n "${frames[$i]}" ]]; then
        echo "  Frame $i: '${frames[$i]}' (code: $(printf '%d' "'${frames[$i]}'"))"
    fi
done

echo ""
echo "=== Test: Alternative approach - single printf ==="

# Try using a single printf call
frames2=()
frames2=($(printf '\342\240\213 \342\240\211 \342\240\211 \342\240\210 \342\240\214 \342\240\204'))
echo "Array length: ${#frames2}"
for i in {0..${#frames2}}; do
    if [[ -n "${frames2[$i]}" ]]; then
        echo "  Frame $i: '${frames2[$i]}' (code: $(printf '%d' "'${frames2[$i]}'"))"
    fi
done

echo ""
echo "=== Test: Using eval with printf ==="

# Try using eval
frames3=()
eval "frames3=($(printf '\342\240\213 \342\240\211 \342\240\211 \342\240\210 \342\240\214 \342\240\204'))"
echo "Array length: ${#frames3}"
for i in {0..${#frames3}}; do
    if [[ -n "${frames3[$i]}" ]]; then
        echo "  Frame $i: '${frames3[$i]}' (code: $(printf '%d' "'${frames3[$i]}'"))"
    fi
done
