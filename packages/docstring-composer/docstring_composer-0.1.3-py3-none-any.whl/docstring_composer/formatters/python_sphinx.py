"""
Python Sphinx-style (reStructuredText) docstring formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class PythonSphinxFormatter(BaseFormatter):
    """
    Formatter for Python Sphinx-style (reStructuredText) docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a Sphinx-style Python docstring.

        :param schema: The docstring schema to format.
        :type schema: DocstringSchema
        :return: The formatted docstring as a string.
        :rtype: str
        """
        lines = []

        # Add short description
        if schema.short_description:
            lines.append(schema.short_description)

        # Add blank line if we have more content
        if (
            schema.long_description
            or schema.parameters
            or schema.returns
            or schema.raises
            or schema.examples
            or schema.notes
        ):
            lines.append("")

        # Add long description
        if schema.long_description:
            lines.extend(textwrap.wrap(schema.long_description, width=79))
            lines.append("")

        # Add parameters
        if schema.parameters:
            for param in schema.parameters:
                param_line = f":param {param.name}: "
                if param.description:
                    param_line += param.description
                lines.append(param_line)
                
                # Parameter type
                if param.type:
                    lines.append(f":type {param.name}: {param.type}")

        # Add returns
        if schema.returns:
            if schema.returns.description:
                lines.append(f":return: {schema.returns.description}")
            if schema.returns.type:
                lines.append(f":rtype: {schema.returns.type}")

        # Add raises
        if schema.raises:
            for exc in schema.raises:
                raise_line = f":raises {exc.exception}:"
                if exc.description:
                    raise_line += f" {exc.description}"
                lines.append(raise_line)

        # Add examples if available
        if schema.examples:
            lines.append("")
            lines.append("Examples:")
            lines.append("--------")
            for example in schema.examples:
                if example.description:
                    lines.append(f"{example.description}")
                
                lines.append(".. code-block:: python")
                lines.append("")
                # Indent the code by 4 spaces
                code_lines = example.code.split("\n")
                indented_code = indent_lines(code_lines, 4)
                lines.extend(indented_code)
                lines.append("")

        # Add notes
        if schema.notes:
            lines.append("")
            lines.append("Note:")
            lines.append("-----")
            note_lines = textwrap.wrap(schema.notes, width=75)
            lines.extend(note_lines)
            lines.append("")

        # Add version if available
        if schema.version:
            lines.append(f":version: {schema.version}")

        # Add author if available
        if schema.author:
            lines.append(f":author: {schema.author}")

        # Add deprecated warning if applicable
        if schema.deprecated:
            lines.append(".. deprecated:: ")
            lines.append("   This feature is deprecated and will be removed in a future release.")

        # Remove trailing blank lines
        while lines and not lines[-1]:
            lines.pop()

        # Format as a docstring
        docstring = "\"\"\"\n"
        if lines:
            docstring += "\n".join(lines) + "\n"
        docstring += "\"\"\""

        return docstring


# Register the formatter
register_formatter("python", "sphinx", PythonSphinxFormatter)
