#!/bin/zsh

# Test different ways to represent Unicode characters in zsh

echo "=== Test 1: Direct Unicode characters ==="
spinner1=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴')
echo "Array element 0: '${spinner1[0]}'"
echo "Length: ${#spinner1}"

# Try to print it
for i in {1..3}; do
    echo "Frame $i: ${spinner1[$((i-1))]} Generating command..."
    sleep 0.5
done

echo ""
echo "=== Test 2: Hex escape sequences ==="
spinner2=('\xE2\xA0\x8B' '\xE2\xA0\x89' '\xE2\xA0\x89' '\xE2\xA0\x88' '\xE2\xA0\x8C' '\xE2\xA0\x84')
echo "Array element 0: '${spinner2[0]}'"
echo "Length: ${#spinner2}"

# Try to print it
for i in {1..3}; do
    echo "Frame $i: ${spinner2[$((i-1))]} Generating command..."
    sleep 0.5
done

echo ""
echo "=== Test 3: printf with format specifiers ==="
# Using printf to generate the characters
spinner3=($(printf '\xE2\xA0\x8B'))
spinner3+=($(printf '\xE2\xA0\x89'))
spinner3+=($(printf '\xE2\xA0\x89'))
spinner3+=($(printf '\xE2\xA0\x88'))
spinner3+=($(printf '\xE2\xA0\x8C'))
spinner3+=($(printf '\xE2\xA0\x84'))
echo "Array element 0: '${spinner3[0]}'"
echo "Length: ${#spinner3}"

# Try to print it
for i in {1..3}; do
    echo "Frame $i: ${spinner3[$((i-1))]} Generating command..."
    sleep 0.5
done

echo ""
echo "=== Test 4: Octal escape sequences ==="
spinner4=('\342\240\213' '\342\240\211' '\342\240\211' '\342\240\210' '\342\240\214' '\342\240\204')
echo "Array element 0: '${spinner4[0]}'"
echo "Length: ${#spinner4}"

# Try to print it
for i in {1..3}; do
    echo "Frame $i: ${spinner4[$((i-1))]} Generating command..."
    sleep 0.5
done

echo ""
echo "=== Test 5: Using BUFFER variable (simulating zle) ==="
# Simulate what happens in the plugin
BUFFER="${spinner1[0]} Generating command..."
echo "BUFFER content: '$BUFFER'"
echo "BUFFER length: ${#BUFFER}"

# Check if the character is actually in the buffer
if [[ "$BUFFER" == *"⠋"* ]]; then
    echo "✓ Unicode character found in BUFFER"
else
    echo "✗ Unicode character NOT found in BUFFER"
fi

echo ""
echo "=== Test 6: Check file encoding ==="
file test_unicode.sh
