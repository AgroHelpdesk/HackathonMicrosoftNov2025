"""JSON parsing utilities.

This module provides helper functions for parsing JSON from LLM responses,
handling common formatting issues like markdown code blocks.
"""

import json
import re
from typing import Any


def clean_json_response(content: str) -> str:
    """Clean JSON response by removing markdown code blocks and extra whitespace.
    
    Args:
        content: Raw response content that may contain JSON with markdown
        
    Returns:
        Cleaned JSON string ready for parsing
        
    Example:
        >>> clean_json_response('```json\\n{"key": "value"}\\n```')
        '{"key": "value"}'
    """
    content = content.strip()
    
    # Remove markdown code blocks with language specifier
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    
    if content.endswith("```"):
        content = content[:-3]
    
    content = content.strip()
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(lines)
    
    return content


def parse_json_response(content: str) -> dict[str, Any]:
    """Parse JSON from LLM response with automatic cleaning.
    
    Args:
        content: Raw response content that may contain JSON
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        json.JSONDecodeError: If content is not valid JSON after cleaning
    """
    cleaned = clean_json_response(content)
    return json.loads(cleaned)


def extract_json_from_text(text: str) -> dict[str, Any] | None:
    """Extract and parse the first JSON object found in text.
    
    This function is useful when the LLM response contains JSON mixed with
    other text (e.g., explanations before or after the JSON).
    
    Args:
        text: Text that may contain JSON object
        
    Returns:
        Parsed JSON dictionary if found, None otherwise
    """
    # Try to find JSON object pattern
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    return None


def parse_and_validate_json(content: str, model: type) -> Any:
    """Parse JSON from LLM response and validate with Pydantic model.
    
    Combines JSON cleaning and Pydantic validation in a single step.
    
    Args:
        content: Raw response content that may contain JSON
        model: Pydantic model class to validate against
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        json.JSONDecodeError: If content is not valid JSON after cleaning
        pydantic.ValidationError: If JSON doesn't match model schema
    """
    cleaned = clean_json_response(content)
    return model.model_validate_json(cleaned)
