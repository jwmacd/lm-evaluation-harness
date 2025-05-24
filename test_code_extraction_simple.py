#!/usr/bin/env python3
"""Simple test of code extraction functionality."""

import sys
sys.path.insert(0, '.')

from lm_eval.models.code_extraction import extract_code

# Test cases
test_cases = [
    # Test 1: Code with thinking tags
    (
        "<think>I need to implement the function</think>\n\n```python\ndef add(a, b):\n    return a + b\n```",
        "def add(a, b):\n    return a + b"
    ),
    # Test 2: Raw code without any tags
    (
        "def add(a, b):\n    return a + b",
        "def add(a, b):\n    return a + b"
    ),
    # Test 3: Code with special tokens
    (
        "<|assistant|>Here's the solution:\n\ndef add(a, b):\n    return a + b",
        "Here's the solution:\n\ndef add(a, b):\n    return a + b"
    ),
    # Test 4: Code with preamble
    (
        "Here's my solution to the problem:\n\ndef add(a, b):\n    return a + b",
        "def add(a, b):\n    return a + b"
    ),
    # Test 5: Empty input
    (
        "",
        ""
    ),
    # Test 6: Code with multiple functions (should not stop at second def)
    (
        "def first():\n    pass\n\ndef second():\n    pass",
        "def first():\n    pass\n\ndef second():\n    pass"
    ),
]

print("Testing code extraction...")
all_pass = True

for i, (input_text, expected) in enumerate(test_cases, 1):
    result = extract_code(input_text)
    passed = result == expected
    all_pass = all_pass and passed
    
    print(f"\nTest {i}: {'PASS' if passed else 'FAIL'}")
    if not passed:
        print(f"Input: {repr(input_text)}")
        print(f"Expected: {repr(expected)}")
        print(f"Got: {repr(result)}")

print(f"\n{'All tests passed!' if all_pass else 'Some tests failed!'}")

# Now test the build_predictions function
print("\n" + "="*50)
print("Testing build_predictions with code extraction...")

from lm_eval.tasks.humaneval.utils import build_predictions

# Simulate model responses with various formatting issues
test_responses = [
    ["```python\ndef solution():\n    return 42\n```"],  # Markdown fence
    ["<think>Let me think...</think>\n\ndef solution():\n    return 42"],  # Thinking tags
    ["def solution():\n    return 42"],  # Clean response
]

test_docs = [
    {"prompt": "def test1():\n    "},
    {"prompt": "def test2():\n    "},
    {"prompt": "def test3():\n    "},
]

predictions = build_predictions(test_responses, test_docs)

print("Build predictions results:")
for i, (doc, pred_list) in enumerate(zip(test_docs, predictions)):
    print(f"\nDoc {i+1} prompt: {repr(doc['prompt'])}")
    for j, pred in enumerate(pred_list):
        print(f"  Prediction {j+1}: {repr(pred)}")
        # Check that the prediction starts with the prompt and has clean code appended
        if pred.startswith(doc['prompt']):
            appended = pred[len(doc['prompt']):]
            print(f"  Appended code: {repr(appended)}")
        else:
            print("  ERROR: Prediction doesn't start with prompt!")