"""
JavaScript/TypeScript JSDoc-style formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class JsJsdocFormatter(BaseFormatter):
    """
    Formatter for JavaScript/TypeScript JSDoc-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a JSDoc docstring.

        Args:
            schema: The docstring schema to format.

        Returns:
            The formatted docstring as a string.
        """
        lines = ["/**"]

        # Add short description
        if schema.short_description:
            lines.append(f" * {schema.short_description}")

        # Add blank line if we have a long description
        if schema.long_description:
            lines.append(" *")

        # Add long description
        if schema.long_description:
            for line in textwrap.wrap(schema.long_description, width=75):
                lines.append(f" * {line}")

        # Add blank line before tags if we have any
        if (
            schema.parameters
            or schema.returns
            or schema.raises
            or schema.examples
            or schema.deprecated
            or schema.version
            or schema.author
        ):
            lines.append(" *")

        # Add parameters
        if schema.parameters:
            for param in schema.parameters:
                param_line = f" * @param"
                if param.type:
                    param_line += f" {{{'*' if not param.required else ''}{param.type}}}"
                param_line += f" {param.name}"
                if param.description:
                    param_line += f" {param.description}"
                if param.default is not None and not param.required:
                    if isinstance(param.default, str):
                        param_line += f" Default: '{param.default}'"
                    else:
                        param_line += f" Default: {param.default}"
                lines.append(param_line)

        # Add returns
        if schema.returns:
            return_line = " * @returns"
            if schema.returns.type:
                return_line += f" {{{schema.returns.type}}}"
            if schema.returns.description:
                return_line += f" {schema.returns.description}"
            lines.append(return_line)

        # Add throws
        if schema.raises:
            for exc in schema.raises:
                throws_line = f" * @throws {{{exc.exception}}}"
                if exc.description:
                    throws_line += f" {exc.description}"
                lines.append(throws_line)

        # Add examples
        if schema.examples:
            for example in schema.examples:
                lines.append(" *")
                lines.append(" * @example")
                if example.description:
                    lines.append(f" * {example.description}")
                for code_line in example.code.split("\n"):
                    lines.append(f" * {code_line}")

        # Add deprecated tag if applicable
        if schema.deprecated:
            lines.append(" * @deprecated This feature is deprecated and will be removed in a future release.")

        # Add version if available
        if schema.version:
            lines.append(f" * @version {schema.version}")

        # Add author if available
        if schema.author:
            lines.append(f" * @author {schema.author}")

        # Add notes
        if schema.notes:
            lines.append(" *")
            lines.append(" * @note")
            for line in textwrap.wrap(schema.notes, width=75):
                lines.append(f" * {line}")

        # Close the JSDoc block
        lines.append(" */")

        return "\n".join(lines)


# Register the formatters for JavaScript and TypeScript
register_formatter("javascript", "jsdoc", JsJsdocFormatter)
register_formatter("typescript", "jsdoc", JsJsdocFormatter)
