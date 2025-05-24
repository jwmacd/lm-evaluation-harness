#!/usr/bin/env python3
"""Test extraction of thinking tags."""

import sys
sys.path.insert(0, 'lm_eval/models')
from code_extraction import extract_code

# Test with actual response from the failure file
test_response = """<think>
Okay, I need to solve this problem where I have to check if any two numbers in the list are closer than the given threshold. Hmm. Let's think about how to approach this.

First, the input is a list of numbers and a threshold. The output should be True if there exists at least two distinct elements in the list such that their absolute difference is less than the threshold. Otherwise, False.
</think>

Here's the solution:

```python
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    sorted_numbers = sorted(numbers)
    for i in range(len(sorted_numbers) - 1):
        if sorted_numbers[i+1] - sorted_numbers[i] < threshold:
            return True
    return False
```"""

extracted = extract_code(test_response)
print("Test response length:", len(test_response))
print("Extracted length:", len(extracted))
print("\nExtracted code:")
print(extracted)
print("\nHas <think>:", "<think>" in extracted.lower())
print("Has </think>:", "</think>" in extracted.lower())

# Test with the pattern from the failure
test_response2 = "<think>\nSome thinking\n</think>\n    return True"
extracted2 = extract_code(test_response2)
print("\n\nTest 2:")
print("Input:", repr(test_response2))
print("Extracted:", repr(extracted2))