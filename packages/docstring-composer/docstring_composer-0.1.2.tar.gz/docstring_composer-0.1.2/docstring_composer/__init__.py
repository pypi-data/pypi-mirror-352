"""
Docstring Composer: Convert schema-based docstrings to different language formats.

This package provides tools to convert schema-based docstrings (defined using Pydantic models)
to various language-specific formats such as Google-style for Python, Javadoc for Java,
JSDoc for JavaScript/TypeScript, and more.

Example usage:
    
    ```python
    from docstring_composer import DocstringComposer
    
    composer = DocstringComposer()
    docstring = composer.convert(
        schema={
            "name": "my_function",
            "short_description": "A brief summary of what the function does.",
            "parameters": [
                {"name": "param1", "type": "str", "description": "Description of param1"}
            ],
            "returns": {"type": "bool", "description": "Whether the operation succeeded"}
        },
        language="python",
        style="google"
    )
    print(docstring)
    ```

For more examples, see the examples directory in the package.
"""

__version__ = "0.1.0"

from docstring_composer.composer import DocstringComposer
from docstring_composer.schema import load_schema
from docstring_composer.formatters import list_supported_formats

__all__ = ["DocstringComposer", "load_schema", "list_supported_formats"]
