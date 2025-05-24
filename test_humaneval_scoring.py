#!/usr/bin/env python3
"""Test script to verify HumanEval scoring is working correctly."""

import json
import sys
from lm_eval.tasks.humaneval.utils import pass_at_k

# Test data: A simple function that should pass
test_references = [
    "assert add(2, 3) == 5\nassert add(1, 2) == 3\nassert add(-1, 1) == 0"
]

# Test predictions: 
# - First one is correct
# - Second one is wrong (multiplies instead of adds)
test_predictions = [
    ["def add(a, b):\n    return a + b"],
    ["def add(a, b):\n    return a * b"]
]

print("Testing pass_at_k function...")
print(f"References: {test_references}")
print(f"Predictions for test 1 (correct): {test_predictions[0]}")
print(f"Predictions for test 2 (wrong): {test_predictions[1]}")

# Test individual cases
try:
    result1 = pass_at_k([test_references[0]], [test_predictions[0]], k=[1])
    print(f"\nTest 1 (correct implementation) pass@1: {result1}")
    
    result2 = pass_at_k([test_references[0]], [test_predictions[1]], k=[1])
    print(f"Test 2 (wrong implementation) pass@1: {result2}")
    
    # Test both together (50% pass rate expected)
    result_combined = pass_at_k(
        test_references + test_references,  # Same test twice
        [test_predictions[0], test_predictions[1]],  # One correct, one wrong
        k=[1]
    )
    print(f"\nCombined (1 pass, 1 fail) pass@1: {result_combined} (should be ~0.5)")
    
except Exception as e:
    print(f"\nError during testing: {e}")
    import traceback
    traceback.print_exc()

# Now test with actual HumanEval-style data
print("\n" + "="*50)
print("Testing with HumanEval-style data...")

# Example from HumanEval dataset
humaneval_prompt = '''def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
'''

humaneval_test = '''def check(candidate):
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True
    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True
    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False
    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0], 2.0) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 1.0) == True
    assert candidate([1.1, 2.2, 3.1, 4.1, 5.1], 0.5) == False

check(has_close_elements)'''

# A correct solution
correct_solution = '''    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                distance = abs(elem - elem2)
                if distance < threshold:
                    return True
    return False'''

# Build the full code as HumanEval would
full_code_correct = humaneval_prompt + correct_solution

print(f"Testing correct HumanEval solution...")
try:
    result = pass_at_k([humaneval_test], [[full_code_correct]], k=[1])
    print(f"Correct solution pass@1: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()