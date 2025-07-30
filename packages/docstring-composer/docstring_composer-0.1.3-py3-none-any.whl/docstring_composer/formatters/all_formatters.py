"""
Import all formatters to make sure they are registered.

This module simply imports all the formatter modules to ensure that all formatters
are registered with the registry when the package is imported.
"""

from docstring_composer.formatters import python_google
from docstring_composer.formatters import python_numpy
from docstring_composer.formatters import python_sphinx
from docstring_composer.formatters import python_epydoc
from docstring_composer.formatters import python_rest
from docstring_composer.formatters import java_javadoc
from docstring_composer.formatters import js_jsdoc
from docstring_composer.formatters import csharp_xmldoc
from docstring_composer.formatters import ruby_yard
from docstring_composer.formatters import kotlin_kdoc
from docstring_composer.formatters import c_doxygen
from docstring_composer.formatters import cpp_doxygen
from docstring_composer.formatters import php_phpdoc
from docstring_composer.formatters import go_godoc

__all__ = [
    "python_google",
    "python_numpy",
    "python_sphinx",
    "python_epydoc",
    "python_rest",
    "java_javadoc",
    "js_jsdoc",
    "csharp_xmldoc", 
    "ruby_yard",
    "kotlin_kdoc",
    "c_doxygen",
    "cpp_doxygen",
    "php_phpdoc",
    "go_godoc",
]
