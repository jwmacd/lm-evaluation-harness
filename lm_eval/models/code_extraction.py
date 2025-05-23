"""
Code extraction module for cleaning and extracting Python code from LLM outputs.
"""

import re
import ast
import textwrap
from typing import Optional


def extract_code(text: str) -> str:
    """
    Extract clean Python code from LLM output.
    
    This function:
    1. Removes special tokens (<|im_start|>, <|im_end|>, etc.)
    2. Strips thinking tags (<think>...</think>)
    3. Extracts code from markdown fences
    4. Finds and isolates Python function/class/import definitions
    5. Normalizes indentation with textwrap.dedent
    6. Validates syntax before returning
    7. Falls back to original output if extraction fails
    
    Args:
        text: Raw text output from LLM
        
    Returns:
        Cleaned Python code
        
    Raises:
        ValueError: If no valid Python code can be extracted
    """
    if not text:
        raise ValueError("Empty text provided")
    
    original_text = text
    
    # Step 1: Remove special tokens - any token wrapped in <| ... |>
    text = re.sub(r'<\|[^>]+?\|>', '', text)
    
    # Step 2: Remove thinking tags (case-insensitive)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Step 3: Try to extract from markdown code blocks
    code_blocks = []
    
    # Look for ```python, ```py, or generic ``` blocks
    fence_pattern = r'```(?:python|py|[^`\n]*)\n(.*?)```'
    fenced_blocks = re.findall(fence_pattern, text, re.DOTALL | re.IGNORECASE)
    code_blocks.extend(fenced_blocks)
    
    # Step 4: Try to find Python top-level statements if no code blocks found
    if not code_blocks:
        # Look for function, class, decorator, or import statements
        # These typically indicate the start of Python code
        top_level_pattern = r'^\s*(def\s|class\s|@\w|from\s+\w|import\s+\w)'
        match = re.search(top_level_pattern, text, re.MULTILINE)
        if match:
            # Extract from this point to the end of the text
            potential_code = text[match.start():]
            code_blocks.append(potential_code)
    
    # Step 5: Validate and return the best code block
    for code in code_blocks:
        # Normalize indentation and strip whitespace
        code = textwrap.dedent(code).strip()
        if code:
            try:
                # Try to parse as valid Python
                ast.parse(code)
                return code
            except SyntaxError:
                # If it's not valid Python, continue to next block
                continue
    
    # If no valid code blocks found, try to clean up the text directly
    text = text.strip()
    
    # Remove common prefixes/suffixes that might be added by the model
    prefixes_to_remove = [
        "Here's the solution:",
        "Here is the solution:",
        "The solution is:",
        "Solution:",
        "Answer:",
        "Output:",
        "Code:",
    ]
    
    for prefix in prefixes_to_remove:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
            break
    
    # Try to find a function definition in the cleaned text
    if 'def ' in text:
        # Find the start of the function
        def_start = text.find('def ')
        if def_start != -1:
            # Extract from def to the end or until we hit non-code text
            potential_code = text[def_start:]
            
            # Try to find where the function ends
            lines = potential_code.split('\n')
            code_lines = []
            in_function = False
            base_indent = None
            
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith('def '):
                    in_function = True
                    code_lines.append(line)
                    # Determine base indentation for the function body
                    base_indent = len(line) - len(stripped)
                elif in_function:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() == '':
                        code_lines.append(line)
                    elif current_indent > base_indent:
                        # This line is indented more than the def line, so it's part of the function
                        code_lines.append(line)
                    else:
                        # We've reached the end of the function
                        break
            
            if code_lines:
                potential_code = '\n'.join(code_lines)
                # Normalize indentation
                potential_code = textwrap.dedent(potential_code).strip()
                try:
                    ast.parse(potential_code)
                    return potential_code
                except SyntaxError:
                    pass
    
    # Step 6: Final validation - try to parse the entire cleaned text
    # First normalize indentation
    text = textwrap.dedent(text).strip()
    try:
        ast.parse(text)
        return text
    except SyntaxError:
        pass
    
    # If all else fails, raise an error
    raise ValueError("Could not extract valid Python code from the provided text")