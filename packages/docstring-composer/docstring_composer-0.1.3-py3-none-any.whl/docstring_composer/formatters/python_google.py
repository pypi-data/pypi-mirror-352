"""
Python Google-style docstring formatter.
"""

from typing import List, Optional
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class PythonGoogleFormatter(BaseFormatter):
    """
    Formatter for Python Google-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a Google-style Python docstring.

        Args:
            schema: The docstring schema to format.

        Returns:
            The formatted docstring as a string.
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
            lines.append("Args:")
            for param in schema.parameters:
                param_line = self._format_param(param)
                lines.append(param_line)
            lines.append("")

        # Add returns
        if schema.returns and schema.returns.description:
            lines.append("Returns:")
            return_line = "    "
            if schema.returns.type:
                return_line += f"{schema.returns.type}: "
            return_line += schema.returns.description
            lines.append(return_line)
            lines.append("")

        # Add raises
        if schema.raises:
            lines.append("Raises:")
            for exc in schema.raises:
                raise_line = f"    {exc.exception}: "
                if exc.description:
                    raise_line += exc.description
                lines.append(raise_line)
            lines.append("")

        # Add examples
        if schema.examples:
            lines.append("Examples:")
            for example in schema.examples:
                if example.description:
                    lines.append(f"    {example.description}")
                # Indent the code by 4 spaces
                code_lines = example.code.split("\n")
                indented_code = indent_lines(code_lines, 4)
                lines.extend(indented_code)
                lines.append("")

        # Add notes
        if schema.notes:
            lines.append("Notes:")
            note_lines = textwrap.wrap(schema.notes, width=75)
            indented_notes = indent_lines(note_lines, 4)
            lines.extend(indented_notes)
            lines.append("")

        # Remove trailing blank lines
        while lines and not lines[-1]:
            lines.pop()

        # Format as a docstring
        docstring = "\"\"\"\n"
        if len(lines) == 1:
            return "\"\"\"{}\"\"\"".format(lines[0])
        elif lines:
            docstring += "\n".join(lines) + "\n"
        docstring += "\"\"\""

        return docstring

    def _format_param(self, param: DocParam) -> str:
        """
        Format a parameter for a Google-style docstring.

        Args:
            param: The parameter to format.

        Returns:
            The formatted parameter line.
        """
        param_line = f"    {param.name}"
        
        # Add type if available
        if param.type:
            param_line += f" ({param.type})"
        
        # Add description if available
        if param.description:
            param_line += f": {param.description}"
            
        # Add default value if available
        if param.default is not None and not param.required:
            if isinstance(param.default, str):
                param_line += f" Defaults to '{param.default}'."
            else:
                param_line += f" Defaults to {param.default}."
                
        return param_line


# Register the formatter
register_formatter("python", "google", PythonGoogleFormatter)
