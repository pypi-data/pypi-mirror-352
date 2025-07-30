"""
C# XML Documentation Comments formatter.
"""

from typing import List
import textwrap
import html

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class CSharpXmlDocFormatter(BaseFormatter):
    """
    Formatter for C# XML Documentation Comments.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as C# XML Documentation Comments.

        Args:
            schema: The docstring schema to format.

        Returns:
            The formatted docstring as a string.
        """
        lines = ["/// <summary>"]

        # Add short description
        if schema.short_description:
            lines.append(f"/// {html.escape(schema.short_description)}")

        # Close summary tag
        lines.append("/// </summary>")

        # Add long description if available
        if schema.long_description:
            lines.append("///")
            lines.append("/// <remarks>")
            for line in textwrap.wrap(schema.long_description, width=75):
                lines.append(f"/// {html.escape(line)}")
            lines.append("/// </remarks>")

        # Add parameters
        if schema.parameters:
            for param in schema.parameters:
                param_line = f"/// <param name=\"{param.name}\">"
                if param.description:
                    param_line += html.escape(param.description)
                param_line += "</param>"
                lines.append(param_line)

        # Add returns
        if schema.returns and schema.returns.description:
            return_line = "/// <returns>"
            return_line += html.escape(schema.returns.description)
            return_line += "</returns>"
            lines.append(return_line)

        # Add exceptions
        if schema.raises:
            for exc in schema.raises:
                exception_line = f"/// <exception cref=\"{exc.exception}\">"
                if exc.description:
                    exception_line += html.escape(exc.description)
                exception_line += "</exception>"
                lines.append(exception_line)

        # Add examples
        if schema.examples:
            lines.append("///")
            lines.append("/// <example>")
            for example in schema.examples:
                if example.description:
                    lines.append(f"/// {html.escape(example.description)}")
                lines.append("/// <code>")
                for code_line in example.code.split("\n"):
                    lines.append(f"/// {html.escape(code_line)}")
                lines.append("/// </code>")
            lines.append("/// </example>")

        # Add remarks for notes if available
        if schema.notes:
            lines.append("///")
            lines.append("/// <remarks>")
            lines.append("/// <para>Notes:</para>")
            for line in textwrap.wrap(schema.notes, width=75):
                lines.append(f"/// {html.escape(line)}")
            lines.append("/// </remarks>")

        return "\n".join(lines)


# Register the formatter
register_formatter("csharp", "xmldoc", CSharpXmlDocFormatter)
