#!/usr/bin/env python3
"""Debug why thinking tags aren't being removed."""

import sys
import re
sys.path.insert(0, 'lm_eval/models')
from code_extraction import extract_code

# Simulate the actual response
test_response = """<think>
Okay, I need to solve this problem where I have to check if any two numbers in the list are closer than the given threshold.
</think>
    sorted_numbers = sorted(numbers)
    for i in range(len(sorted_numbers) - 1):
        if sorted_numbers[i+1] - sorted_numbers[i] < threshold:
            return True
    return False"""

print("Original response:")
print(repr(test_response[:200]))
print("\nHas <think>:", "<think>" in test_response.lower())
print("Has </think>:", "</think>" in test_response.lower())

# Test the regex pattern directly
pattern = r'<think>.*?</think>'
match = re.search(pattern, test_response, flags=re.DOTALL | re.IGNORECASE)
if match:
    print("\nRegex match found:")
    print("Match span:", match.span())
    print("Matched text:", repr(match.group()[:100]))
else:
    print("\nNo regex match found!")

# Try different patterns
patterns = [
    (r'<think>.*?</think>', re.DOTALL | re.IGNORECASE),
    (r'<think>.*</think>', re.DOTALL | re.IGNORECASE),
    (r'(?i)<think>.*?</think>', re.DOTALL),
]

for i, (pat, flags) in enumerate(patterns):
    result = re.sub(pat, '', test_response, flags=flags)
    has_think = '<think>' in result.lower()
    print(f"\nPattern {i+1}: {pat}")
    print(f"Result has <think>: {has_think}")
    if not has_think:
        print("Success! Pattern removed thinking tags")
        break

# Now test extract_code
extracted = extract_code(test_response)
print("\n\nExtract_code result:")
print(repr(extracted[:200]))
print("Has <think>:", "<think>" in extracted.lower())