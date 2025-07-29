"""
Go GoDoc-style docstring formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample

from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class GoGoDocFormatter(BaseFormatter):
    """
    Formatter for Go GoDoc-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a GoDoc docstring.

        Args:
            schema: The docstring schema to format.

        Returns:
            The formatted docstring as a string.
        """
        lines = []

        # In Go, documentation comments are single-line comments prefixed with //
        # The first sentence should be a complete sentence that starts with the name of the element.
        if schema.name and schema.short_description:
            # Format name to be capitalized if it's not already (to follow Go convention)
            name = schema.name[0].upper() + schema.name[1:] if schema.name else ""
            lines.append(f"// {name} {schema.short_description}")
        elif schema.short_description:
            # If no name is available, just use the short description
            lines.append(f"// {schema.short_description}")

        # Add blank line if we have a long description
        if schema.long_description:
            lines.append("//")

        # Add long description (Go uses single comment lines, not blocks)
        if schema.long_description:
            for line in textwrap.wrap(schema.long_description, width=75):
                lines.append(f"// {line}")

        # Add a separator for parameter descriptions
        if schema.parameters or schema.returns or schema.raises:
            lines.append("//")

        # Add parameters - in Go, typically using indented parameter names with descriptions
        if schema.parameters:
            for param in schema.parameters:
                lines.append(f"// {param.name}:")
                if param.description:
                    wrapped_desc = textwrap.wrap(param.description, width=70)
                    for line in wrapped_desc:
                        lines.append(f"//     {line}")

        # Add returns - Go doesn't have explicit return annotations but we can document them
        if schema.returns and schema.returns.description:
            lines.append("// Returns:")
            wrapped_desc = textwrap.wrap(schema.returns.description, width=70)
            for line in wrapped_desc:
                lines.append(f"//     {line}")

        # Document errors - Go uses error returns rather than exceptions
        if schema.raises:
            lines.append("// Errors:")
            for exc in schema.raises:
                lines.append(f"//     {exc.exception}:")
                if exc.description:
                    wrapped_desc = textwrap.wrap(exc.description, width=65)
                    for line in wrapped_desc:
                        lines.append(f"//         {line}")

        # Add examples - Go has a special format for examples in tests
        # but we'll just document them inline
        if schema.examples:
            lines.append("//")
            lines.append("// Examples:")
            for i, example in enumerate(schema.examples):
                if example.description:
                    lines.append(f"//")
                    lines.append(f"// Example {i+1}: {example.description}")
                for code_line in example.code.split("\n"):
                    lines.append(f"//     {code_line}")

        # Add notes
        if schema.notes:
            lines.append("//")
            lines.append("// Notes:")
            for line in textwrap.wrap(schema.notes, width=75):
                lines.append(f"// {line}")

        # Add deprecated warning if applicable
        if schema.deprecated:
            lines.append("//")
            lines.append("// Deprecated: This feature is deprecated and will be removed in a future release.")

        return "\n".join(lines)


# Register the formatter
register_formatter("go", "godoc", GoGoDocFormatter)
