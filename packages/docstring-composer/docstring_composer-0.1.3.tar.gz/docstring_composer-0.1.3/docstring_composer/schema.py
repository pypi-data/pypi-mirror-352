"""
Schema handling module for docstring-composer.

This module provides functionality for loading and validating docstring schemas.
"""

import json
import sys
from typing import Dict, Any, Union, TextIO

from pydantic import ValidationError


from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample, HighComplexityDocstringSchema, LowComplexityDocstringSchema, MediumComplexityDocstringSchema, VeryHighComplexityDocstringSchema

def load_schema(
    schema_data: Union[Dict[str, Any], str, TextIO]
) -> DocstringSchema:
    """
    Load and validate a docstring schema from a dictionary, JSON string, or file-like object.

    Args:
        schema_data: The schema data as a dictionary, JSON string, or file-like object.

    Returns:
        A validated DocstringSchema instance.

    Raises:
        ValueError: If the schema data is invalid or cannot be parsed.
        ValidationError: If the schema fails validation.
    """
    if isinstance(schema_data, dict):
        # Already a dictionary
        schema_dict = schema_data
    elif isinstance(schema_data, str):
        # Parse JSON string
        try:
            schema_dict = json.loads(schema_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}")
    elif hasattr(schema_data, 'read'):
        # File-like object
        try:
            schema_dict = json.load(schema_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file: {e}")
    else:
        raise ValueError(
            "schema_data must be a dictionary, JSON string, or file-like object"
        )

    # Determine the complexity level based on the fields present
    if "examples" in schema_dict or "notes" in schema_dict:
        try:
            return VeryHighComplexityDocstringSchema(**schema_dict)
        except ValidationError:
            pass  # Try the next level

    if "parameters" in schema_dict or "returns" in schema_dict or "raises" in schema_dict:
        try:
            return HighComplexityDocstringSchema(**schema_dict)
        except ValidationError:
            pass  # Try the next level

    if "long_description" in schema_dict:
        try:
            return MediumComplexityDocstringSchema(**schema_dict)
        except ValidationError:
            pass  # Try the next level

    if "short_description" in schema_dict:
        try:
            return LowComplexityDocstringSchema(**schema_dict)
        except ValidationError:
            pass  # Try the base schema

    # Default to the base schema
    try:
        return DocstringSchema(**schema_dict)
    except ValidationError as e:
        raise ValueError(f"Schema validation error: {e}")
