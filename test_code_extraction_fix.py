#!/usr/bin/env python3
"""Test that code extraction is properly applied in HumanEval and MBPP utils."""

from lm_eval.tasks.humaneval.utils import build_predictions, build_predictions_instruct
from lm_eval.tasks.mbpp.utils import pass_at_1


def test_humaneval_build_predictions():
    """Test that build_predictions applies code extraction."""
    # Test case with markdown formatting
    resps = [[
        """<|im_start|>assistant
Here's the solution:

```python
def add(a, b):
    return a + b
```
<|im_end|>"""
    ]]
    
    docs = [{"prompt": "def add(a, b):\n    "}]
    
    result = build_predictions(resps, docs)
    
    # The result should have the prompt + cleaned code
    expected = [["def add(a, b):\n    def add(a, b):\n    return a + b"]]
    
    print("HumanEval build_predictions test:")
    print(f"Input response: {resps[0][0]!r}")
    print(f"Result: {result[0][0]!r}")
    print(f"Expected to contain only code without markdown/tokens: {'def add(a, b):' in result[0][0] and 'return a + b' in result[0][0]}")
    print(f"Should not contain markdown: {'```' not in result[0][0]}")
    print(f"Should not contain tokens: {'<|im_' not in result[0][0]}")
    print()


def test_humaneval_build_predictions_instruct():
    """Test that build_predictions_instruct applies code extraction."""
    resps = [[
        """```python
def multiply(x, y):
    return x * y
```"""
    ]]
    
    docs = [{"prompt": "def multiply(x, y):\n    "}]
    
    result = build_predictions_instruct(resps, docs)
    
    print("HumanEval build_predictions_instruct test:")
    print(f"Input response: {resps[0][0]!r}")
    print(f"Result: {result[0][0]!r}")
    print(f"Should not contain markdown: {'```' not in result[0][0]}")
    print()


def test_mbpp_pass_at_1():
    """Test that pass_at_1 applies code extraction."""
    
    # Mock the pass_at_k compute function
    import lm_eval.tasks.mbpp.utils as mbpp_utils
    
    # Store the original function
    original_compute = mbpp_utils.pass_at_k.compute
    
    # Track what gets passed to compute
    captured_predictions = []
    
    def mock_compute(references, predictions, k):
        captured_predictions.extend(predictions)
        return [{"pass@1": 1.0}]  # Mock success
    
    mbpp_utils.pass_at_k.compute = mock_compute
    
    try:
        # Test with response containing formatting
        response = """<think>
Let me solve this step by step.
</think>

Here's the solution:

```python
def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return res
```"""
        
        references = [
            "assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)"
        ]
        
        result = pass_at_1(references, response)
        
        print("MBPP pass_at_1 test:")
        print(f"Input response: {response!r}")
        print(f"Captured predictions: {captured_predictions}")
        print(f"Should contain only code: {len(captured_predictions) > 0 and 'def similar_elements' in captured_predictions[0]}")
        print(f"Should not contain markdown: {len(captured_predictions) > 0 and '```' not in captured_predictions[0]}")
        print(f"Should not contain thinking tags: {len(captured_predictions) > 0 and '<think>' not in captured_predictions[0]}")
        
    finally:
        # Restore original function
        mbpp_utils.pass_at_k.compute = original_compute


if __name__ == "__main__":
    test_humaneval_build_predictions()
    test_humaneval_build_predictions_instruct()
    test_mbpp_pass_at_1()