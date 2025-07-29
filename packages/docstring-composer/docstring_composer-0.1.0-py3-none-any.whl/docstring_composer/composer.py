"""
Main composer module for docstring-composer.

This module provides the DocstringComposer class, which is the main entry point
for converting docstring schemas to different language formats.
"""

from typing import Dict, Any, Optional, Union

from docstring_composer.formatters import (
    get_formatter,
    SUPPORTED_LANGUAGES,
    SUPPORTED_STYLES,
)
from docstring_composer.schema import load_schema
from docstring_composer.ds_schema.docstring_schema import DocstringSchema

class DocstringComposer:
    """
    Main class for converting docstring schemas to different language formats.
    """

    def convert(
        self,
        schema: Union[Dict[str, Any], str, DocstringSchema],
        language: str,
        style: Optional[str] = None,
    ) -> str:
        """
        Convert a docstring schema to a specific language format.

        Args:
            schema: The docstring schema as a dictionary, JSON string, or DocstringSchema instance.
            language: The target language (e.g., "python", "java", "javascript").
            style: The docstring style (e.g., "google", "javadoc", "jsdoc").
                  If None, the default style for the language will be used.

        Returns:
            The formatted docstring as a string.

        Raises:
            ValueError: If the language or style is not supported.
        """
        # Check if the language is supported
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages are: {', '.join(SUPPORTED_LANGUAGES)}"
            )

        # If style is not specified, use the default style for the language
        if style is None:
            style = SUPPORTED_LANGUAGES[language]["default_style"]
        else:
            # Check if the style is supported for the language
            if style not in SUPPORTED_LANGUAGES[language]["styles"]:
                raise ValueError(
                    f"Unsupported style '{style}' for language '{language}'. "
                    f"Supported styles are: {', '.join(SUPPORTED_LANGUAGES[language]['styles'])}"
                )

        # Load and validate the schema
        if not isinstance(schema, DocstringSchema):
            schema = load_schema(schema)

        # Get the appropriate formatter for the language and style
        formatter = get_formatter(language, style)

        # Format the docstring
        return formatter.format(schema)
