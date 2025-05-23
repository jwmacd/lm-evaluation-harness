#!/usr/bin/env python3
"""
Test script for code extraction integration in lm-evaluation-harness
"""

import json
from typing import Dict, List, Union

from lm_eval.models.code_extraction import extract_code
from lm_eval.models.openai_completions import LocalCompletionsAPI, LocalChatCompletion


def test_extract_code_function():
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
        # Invalid code (should raise ValueError)
        {
            "input": "This is not valid Python code at all!",
            "expected": ValueError,
            "description": "Invalid code (should fail)"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test['description']}")
        print(f"Input: {repr(test['input'][:50])}...")
        
        try:
            result = extract_code(test['input'])
            if test['expected'] == ValueError:
                print(f"❌ FAILED: Expected ValueError but got: {repr(result)}")
            elif result == test['expected']:
                print(f"✅ PASSED: Got expected output")
            else:
                print(f"❌ FAILED: Expected {repr(test['expected'])}, got {repr(result)}")
        except ValueError as e:
            if test['expected'] == ValueError:
                print(f"✅ PASSED: Got expected ValueError: {e}")
            else:
                print(f"❌ FAILED: Unexpected ValueError: {e}")


def test_model_integration():
    """Test the integration with model classes"""
    print("\n\nTesting model integration...")
    
    # Mock outputs that models might return
    mock_completions_output = {
        "choices": [
            {
                "index": 0,
                "text": "Here's my solution:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```\n\nThis is a recursive implementation."
            }
        ]
    }
    
    mock_chat_output = {
        "choices": [
            {
                "index": 0,
                "message": {
                    "content": "<|im_start|>```python\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n```<|im_end|>"
                }
            }
        ]
    }
    
    # Test LocalCompletionsAPI with extract_code=True
    print("\n1. Testing LocalCompletionsAPI with extract_code=True")
    try:
        model = LocalCompletionsAPI(extract_code=True)
        result = model.parse_generations(mock_completions_output)
        expected = "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        if result[0] == expected:
            print("✅ PASSED: Code extraction worked correctly")
        else:
            print(f"❌ FAILED: Expected clean code, got: {repr(result[0])}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test LocalCompletionsAPI with extract_code=False
    print("\n2. Testing LocalCompletionsAPI with extract_code=False")
    try:
        model = LocalCompletionsAPI(extract_code=False)
        result = model.parse_generations(mock_completions_output)
        if "Here's my solution:" in result[0]:
            print("✅ PASSED: Code extraction disabled, original text preserved")
        else:
            print(f"❌ FAILED: Expected original text, got: {repr(result[0])}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test LocalChatCompletion with extract_code=True
    print("\n3. Testing LocalChatCompletion with extract_code=True")
    try:
        model = LocalChatCompletion(extract_code=True)
        result = model.parse_generations(mock_chat_output)
        expected = "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
        if result[0] == expected:
            print("✅ PASSED: Code extraction worked correctly for chat model")
        else:
            print(f"❌ FAILED: Expected clean code, got: {repr(result[0])}")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def test_error_handling():
    """Test error handling and fallback behavior"""
    print("\n\nTesting error handling...")
    
    # Output that will fail extraction
    mock_bad_output = {
        "choices": [
            {
                "index": 0,
                "text": "I cannot write code for this task."
            }
        ]
    }
    
    print("\n1. Testing fallback when extraction fails")
    try:
        model = LocalCompletionsAPI(extract_code=True)
        result = model.parse_generations(mock_bad_output)
        if result[0] == "I cannot write code for this task.":
            print("✅ PASSED: Correctly fell back to original text")
        else:
            print(f"❌ FAILED: Expected original text, got: {repr(result[0])}")
    except Exception as e:
        print(f"❌ ERROR: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Code Extraction Integration Tests")
    print("=" * 60)
    
    test_extract_code_function()
    test_model_integration()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
    
    print("\nUsage example for running evaluations:")
    print("lm_eval --model local-completions \\")
    print("    --model_args base_url=http://localhost:8000/v1/completions,model=your-model,extract_code=true \\")
    print("    --tasks humaneval \\")
    print("    --output_path results/")


if __name__ == "__main__":
    main()