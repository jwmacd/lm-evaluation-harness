#!/usr/bin/env python3
"""Diagnose what's happening with HumanEval evaluation."""

import sys
sys.path.insert(0, 'lm_eval/models')
sys.path.insert(0, 'lm_eval/tasks/humaneval')

from code_extraction import extract_code

# Test the extract_code function
test_response = '''Here's the solution:

```python
def add(a, b):
    return a + b
```'''

extracted = extract_code(test_response)
print("Test extraction:")
print(f"Input: {repr(test_response)}")
print(f"Output: {repr(extracted)}")
print()

# Now test build_predictions
from utils import build_predictions

test_resps = [[test_response]]  # List of list of responses
test_docs = [{"prompt": "def test_func():\n    "}]

predictions = build_predictions(test_resps, test_docs)
print("Build predictions test:")
print(f"Input responses: {test_resps}")
print(f"Input docs: {test_docs}")
print(f"Output predictions: {predictions}")
print()

# The prediction should be: prompt + extracted code
expected = test_docs[0]["prompt"] + extracted
print(f"Expected: {repr(expected)}")
print(f"Actual: {repr(predictions[0][0])}")
print(f"Match: {predictions[0][0] == expected}")

# Now let's test what happens with the actual HumanEval evaluation
print("\n" + "="*50)
print("Testing HumanEval evaluation pipeline...")

# Simulate what happens in the actual evaluation
from utils import pass_at_k

# Example HumanEval problem
humaneval_prompt = '''def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
'''

# Model response (without prompt)
model_response = '''    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if abs(numbers[i] - numbers[j]) < threshold:
                return True
    return False'''

# Test reference (what the code needs to pass)
test_reference = '''def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False

check(has_close_elements)'''

# What build_predictions would do
doc = {"prompt": humaneval_prompt}
resp = [[model_response]]
prediction = build_predictions(resp, [doc])

print(f"Prompt: {repr(humaneval_prompt[:50])}...")
print(f"Model response: {repr(model_response[:50])}...")
print(f"Build predictions output: {repr(prediction[0][0][:100])}...")

# Now test if this would pass
try:
    result = pass_at_k([test_reference], prediction, k=[1])
    print(f"\npass@1 result: {result}")
except Exception as e:
    print(f"\nError during evaluation: {e}")
    import traceback
    traceback.print_exc()