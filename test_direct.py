#!/usr/bin/env python3
import sys
sys.path.insert(0, 'lm_eval/models')
from code_extraction import extract_code

# Test a simple case
test_input = '```python\ndef add(a, b):\n    return a + b\n```'
result = extract_code(test_input)
print(f'Input: {repr(test_input)}')
print(f'Output: {repr(result)}')
print(f'Expected: def add(a, b):\\n    return a + b')
print(f'Success: {result == "def add(a, b):\\n    return a + b"}')