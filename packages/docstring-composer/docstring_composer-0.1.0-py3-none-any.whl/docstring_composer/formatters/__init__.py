"""
Formatters module for docstring-composer.

This module provides the base formatter class and registry for language-specific formatters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Optional, List

from docstring_composer.ds_schema.docstring_schema import DocstringSchema


class BaseFormatter(ABC):
    """
    Base class for docstring formatters.
    
    All language-specific formatters should inherit from this class.
    """

    @abstractmethod
    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema according to the specific language and style.

        Args:
            schema: The docstring schema to format.

        Returns:
            The formatted docstring as a string.
        """
        pass


# Registry of supported languages and styles
SUPPORTED_LANGUAGES = {
    "python": {
        "default_style": "google",
        "styles": ["google", "numpy", "sphinx", "epydoc", "rest"],
    },
    "java": {
        "default_style": "javadoc",
        "styles": ["javadoc"],
    },
    "javascript": {
        "default_style": "jsdoc",
        "styles": ["jsdoc"],
    },
    "typescript": {
        "default_style": "jsdoc",
        "styles": ["jsdoc", "typedoc"],
    },
    "csharp": {
        "default_style": "xmldoc",
        "styles": ["xmldoc"],
    },
    "ruby": {
        "default_style": "yard",
        "styles": ["yard"],
    },
    "kotlin": {
        "default_style": "kdoc",
        "styles": ["kdoc"],
    },
    "c": {
        "default_style": "doxygen",
        "styles": ["doxygen"],
    },
    "cpp": {
        "default_style": "doxygen",
        "styles": ["doxygen"],
    },
    "php": {
        "default_style": "phpdoc",
        "styles": ["phpdoc"],
    },
    "go": {
        "default_style": "godoc",
        "styles": ["godoc"],
    },
}

# Registry of formatter classes
SUPPORTED_STYLES = {}


def register_formatter(language: str, style: str, formatter_cls: Type[BaseFormatter]):
    """
    Register a formatter class for a specific language and style.

    Args:
        language: The language to register the formatter for.
        style: The style to register the formatter for.
        formatter_cls: The formatter class to register.
    """
    if language not in SUPPORTED_STYLES:
        SUPPORTED_STYLES[language] = {}
    SUPPORTED_STYLES[language][style] = formatter_cls


def get_formatter(language: str, style: str) -> BaseFormatter:
    """
    Get a formatter for a specific language and style.

    Args:
        language: The language to get the formatter for.
        style: The style to get the formatter for.

    Returns:
        A formatter instance.

    Raises:
        ValueError: If no formatter is registered for the language and style.
    """
    if (
        language not in SUPPORTED_STYLES
        or style not in SUPPORTED_STYLES[language]
    ):
        raise ValueError(
            f"No formatter registered for language '{language}' and style '{style}'"
        )
    return SUPPORTED_STYLES[language][style]()


def list_supported_formats() -> Dict[str, Dict[str, List[str]]]:
    """
    Get a dictionary of supported languages and styles.

    Returns:
        A dictionary where keys are language names and values are dictionaries with
        "default_style" and "styles" keys.
    """
    return SUPPORTED_LANGUAGES


# Import all formatters to ensure they are registered
from docstring_composer.formatters import all_formatters
