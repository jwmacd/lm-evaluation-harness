"""
Code extraction module for cleaning LLM outputs of formatting noise.

This is a minimal, non-validating extraction that only removes:
- Special tokens like <|im_start|>, <|im_end|>
- Thinking tags like <think>...</think>
- Markdown code fences
- Common preambles

It does NOT validate Python syntax to avoid "cheating" on evaluations.
"""

import re


def extract_code(text: str) -> str:
    """
    Remove formatting noise from LLM output while preserving the actual code.
    
    This function is intentionally minimal and does NOT validate syntax.
    It only removes common formatting artifacts that aren't part of the
    actual code response.
    
    Args:
        text: Raw text output from LLM
        
    Returns:
        Cleaned text with formatting artifacts removed
    """
    if not text:
        return text
    
    # Step 1: Remove special tokens - any token wrapped in <| ... |>
    text = re.sub(r'<\|[^>]+?\|>', '', text)
    
    # Step 2: Remove thinking tags (case-insensitive)
    # First try to match complete think tags
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # If there's still an opening <think> tag without closing, remove everything from <think> to the end
    # This handles truncated responses
    if '<think>' in text.lower():
        think_start = text.lower().find('<think>')
        if think_start != -1:
            # Check if there's a closing tag after this position
            remaining_text = text[think_start:].lower()
            if '</think>' not in remaining_text:
                # No closing tag, so remove from <think> to the end
                text = text[:think_start]
    
    # If there's a closing </think> tag, take everything after it
    # This handles cases where we want the code that comes after thinking
    think_close = text.lower().find('</think>')
    if think_close != -1:
        text = text[think_close + len('</think>'):]
    
    # Clean up any leading newlines that might be left after removing tags
    text = text.lstrip('\n')
    
    # Step 3: Extract from markdown code fences if present
    # Look for ```python, ```py, or generic ``` blocks
    # Use negative lookahead to avoid matching ``` inside strings
    fence_pattern = r'```(?:python|py|[^`\n]*)\n(.*?)(?:\n)?```'
    fence_match = re.search(fence_pattern, text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).rstrip()
    
    # Step 4: Remove common preambles if at the very start
    preambles = [
        "Here's the solution:",
        "Here is the solution:",
        "Here's the code:",
        "Here is the code:",
        "Solution:",
        "Answer:",
        "Output:",
        "Code:",
    ]
    
    for preamble in preambles:
        if text.lower().startswith(preamble.lower()):
            text = text[len(preamble):].lstrip()
            break
    
    # Return the cleaned text, only stripping trailing whitespace
    return text.rstrip()