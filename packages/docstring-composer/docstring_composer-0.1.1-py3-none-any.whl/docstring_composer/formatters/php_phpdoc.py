"""
PHP PHPDoc-style docstring formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample

from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class PhpPhpDocFormatter(BaseFormatter):
    """
    Formatter for PHP PHPDoc-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a PHPDoc docstring.

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

        # Add blank line before tags
        if (
            schema.parameters
            or schema.returns
            or schema.raises
            or schema.examples
            or schema.notes
        ):
            lines.append(" *")

        # Add parameters
        if schema.parameters:
            for param in schema.parameters:
                param_line = f" * @param"
                if param.type:
                    param_line += f" {param.type}"
                param_line += f" ${param.name}" # PHP variables start with $
                if param.description:
                    param_line += f" {param.description}"
                lines.append(param_line)

        # Add returns
        if schema.returns:
            return_line = " * @return"
            if schema.returns.type:
                return_line += f" {schema.returns.type}"
            if schema.returns.description:
                return_line += f" {schema.returns.description}"
            lines.append(return_line)

        # Add throws
        if schema.raises:
            for exc in schema.raises:
                throws_line = f" * @throws {exc.exception}"
                if exc.description:
                    throws_line += f" {exc.description}"
                lines.append(throws_line)

        # Add examples
        if schema.examples:
            lines.append(" *")
            lines.append(" * @example")
            for example in schema.examples:
                if example.description:
                    lines.append(f" * {example.description}")
                for code_line in example.code.split("\n"):
                    lines.append(f" * {code_line}")

        # Add notes
        if schema.notes:
            lines.append(" *")
            lines.append(" * @note")
            for line in textwrap.wrap(schema.notes, width=75):
                lines.append(f" * {line}")

        # Add author if available
        if schema.author:
            lines.append(f" * @author {schema.author}")

        # Add version if available
        if schema.version:
            lines.append(f" * @version {schema.version}")

        # Add deprecated tag if applicable
        if schema.deprecated:
            lines.append(" * @deprecated This feature is deprecated and will be removed in a future release.")

        # Close the PHPDoc block
        lines.append(" */")

        return "\n".join(lines)


# Register the formatter
register_formatter("php", "phpdoc", PhpPhpDocFormatter)
