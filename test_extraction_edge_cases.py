#!/usr/bin/env python3
"""Test edge cases in code extraction that might cause evaluation failures."""

import sys
sys.path.insert(0, 'lm_eval/models')
from code_extraction import extract_code

# Test various edge cases that might cause issues
test_cases = [
    # Empty or whitespace
    ("", ""),
    ("   ", ""),
    ("\n\n\n", ""),
    
    # Code that starts with whitespace (indentation issues)
    ("    def add(a, b):\n        return a + b", "def add(a, b):\n        return a + b"),
    
    # Code with leading newlines
    ("\n\ndef add(a, b):\n    return a + b", "def add(a, b):\n    return a + b"),
    
    # Code that's just indented content (no function definition)
    ("    return a + b", "return a + b"),
    
    # Multiple code blocks
    ("```python\nfirst_block\n```\n\nSome text\n\n```python\nsecond_block\n```", "first_block"),
    
    # Code with triple backticks but no language
    ("```\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
    
    # Nested backticks (edge case)
    ("```python\ndef code():\n    return '```'\n```", "def code():\n    return '```'"),
]

print("Testing edge cases that might cause evaluation failures...\n")

for i, (input_text, expected) in enumerate(test_cases, 1):
    result = extract_code(input_text)
    passed = result == expected
    
    print(f"Test {i}: {'PASS' if passed else 'FAIL'}")
    if not passed or True:  # Always show details
        print(f"  Input: {repr(input_text)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got: {repr(result)}")
        print()

# Special test: What happens with indented code (common in completions)
print("\nSpecial case: Indented completion (common pattern)")
indented_completion = "    for i in range(len(numbers)):\n        for j in range(i + 1, len(numbers)):\n            if abs(numbers[i] - numbers[j]) < threshold:\n                return True\n    return False"
extracted = extract_code(indented_completion)
print(f"Input (indented completion):\n{indented_completion}")
print(f"\nExtracted:\n{extracted}")
print(f"\nStarts with spaces: {extracted.startswith('    ')}")

# Test what happens when we concatenate with a prompt
prompt = "def has_close_elements(numbers: List[float], threshold: float) -> bool:\n"
full_code = prompt + extracted
print(f"\nFull code after concatenation:")
print(full_code)

# Check if indentation is preserved correctly
lines = full_code.split('\n')
print(f"\nLine analysis:")
for i, line in enumerate(lines[:5]):  # First 5 lines
    print(f"  Line {i}: {repr(line)}")