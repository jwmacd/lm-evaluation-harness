#!/usr/bin/env python3
"""
Simple test script for code extraction functionality
"""

import sys
import os

# Import from the correct path
from lm_eval.models.code_extraction import extract_code


def test_extract_code():
    """Test the extract_code function with various inputs"""
    print("Testing extract_code function...")
    
    test_cases = [
        # Basic markdown code block
        {
            "input": "```python\ndef add(a, b):\n    return a + b\n```",
            "expected": "def add(a, b):\n    return a + b",
            "description": "Basic markdown code block"
        },
        # Code with explanation
        {
            "input": "Here's the solution:\n\n```python\ndef multiply(x, y):\n    return x * y\n```\n\nThis multiplies two numbers.",
            "expected": "def multiply(x, y):\n    return x * y",
            "description": "Code with surrounding text"
        },
        # Special tokens
        {
            "input": "<|im_start|>assistant\n```python\ndef square(n):\n    return n ** 2\n```\n<|im_end|>",
            "expected": "def square(n):\n    return n ** 2",
            "description": "Code with special tokens"
        },
        # Direct function without markdown
        {
            "input": "def greet(name):\n    return f'Hello, {name}!'",
            "expected": "def greet(name):\n    return f'Hello, {name}!'",
            "description": "Direct function without markdown"
        },
        # Thinking tags
        {
            "input": "<think>I need to write a function</think>\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return None",
            "expected": "def divide(a, b):\n    if b != 0:\n        return a / b\n    return None",
            "description": "Code with thinking tags"
        },
        # Multiple functions
        {
            "input": "```python\ndef first():\n    return 1\n\ndef second():\n    return 2\n```",
            "expected": "def first():\n    return 1\n\ndef second():\n    return 2",
            "description": "Multiple functions in one block"
        },
        # Invalid code (should raise ValueError)
        {
            "input": "This is not valid Python code at all!",
            "expected": ValueError,
            "description": "Invalid code (should fail)"
        },
        # Empty input
        {
            "input": "",
            "expected": ValueError,
            "description": "Empty input (should fail)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test['description']}")
        print(f"Input preview: {repr(test['input'][:50])}...")
        
        try:
            result = extract_code(test['input'])
            if test['expected'] == ValueError:
                print(f"❌ FAILED: Expected ValueError but got: {repr(result[:50])}...")
                failed += 1
            elif result == test['expected']:
                print(f"✅ PASSED: Got expected output")
                passed += 1
            else:
                print(f"❌ FAILED: Expected {repr(test['expected'][:50])}, got {repr(result[:50])}")
                failed += 1
        except ValueError as e:
            if test['expected'] == ValueError:
                print(f"✅ PASSED: Got expected ValueError: {e}")
                passed += 1
            else:
                print(f"❌ FAILED: Unexpected ValueError: {e}")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: Unexpected exception: {type(e).__name__}: {e}")
            failed += 1
    
    return passed, failed


def test_real_world_examples():
    """Test with real-world LLM outputs"""
    print("\n\nTesting real-world examples...")
    
    examples = [
        {
            "input": """I'll solve this step by step.

<think>
The problem asks for a function that calculates the sum of a list.
</think>

Here's my solution:

```python
def sum_list(numbers):
    \"\"\"Calculate the sum of all numbers in a list.\"\"\"
    total = 0
    for num in numbers:
        total += num
    return total
```

This function iterates through the list and adds each number to a running total.""",
            "description": "Complex LLM output with thinking tags and explanation"
        },
        {
            "input": """<|im_start|>assistant
I'll write a function to check if a number is prime:

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
```
<|im_end|>""",
            "description": "Output with special tokens and markdown"
        }
    ]
    
    for i, example in enumerate(examples):
        print(f"\nExample {i+1}: {example['description']}")
        try:
            result = extract_code(example['input'])
            print(f"✅ Successfully extracted code:")
            print(f"   {result.split(chr(10))[0]}...")  # First line of extracted code
        except Exception as e:
            print(f"❌ Failed to extract: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Code Extraction Tests")
    print("=" * 60)
    
    passed, failed = test_extract_code()
    test_real_world_examples()
    
    print("\n" + "=" * 60)
    print(f"Testing complete! Passed: {passed}, Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! The code extraction module is working correctly.")
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the implementation.")
    
    print("\n📝 Integration Summary:")
    print("- Code extraction module: /code/github/lm-evaluation-harness/lm_eval/models/code_extraction.py")
    print("- Modified files: /code/github/lm-evaluation-harness/lm_eval/models/openai_completions.py")
    print("- Documentation: /code/github/lm-evaluation-harness/CODE_EXTRACTION_INTEGRATION.md")
    print("\nTo use: add 'extract_code=true' to model_args when running evaluations")


if __name__ == "__main__":
    main()