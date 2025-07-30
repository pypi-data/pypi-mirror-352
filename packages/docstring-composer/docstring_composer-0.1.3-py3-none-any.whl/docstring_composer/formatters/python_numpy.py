"""
Python NumPy-style docstring formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class PythonNumpyFormatter(BaseFormatter):
    """
    Formatter for Python NumPy-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a NumPy-style Python docstring.

        Parameters
        ----------
        schema : DocstringSchema
            The docstring schema to format.

        Returns
        -------
        str
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
            lines.append("Parameters")
            lines.append("----------")
            for param in schema.parameters:
                # Parameter name and type
                param_line = param.name
                if param.type:
                    param_line += f" : {param.type}"
                lines.append(param_line)
                
                # Parameter description
                if param.description:
                    wrapped_desc = textwrap.wrap(param.description, width=75)
                    indented_desc = indent_lines(wrapped_desc, 4)
                    lines.extend(indented_desc)
                    
                # Parameter default value
                if param.default is not None and not param.required:
                    default_line = "    Default: "
                    if isinstance(param.default, str):
                        default_line += f"'{param.default}'"
                    else:
                        default_line += f"{param.default}"
                    lines.append(default_line)
            lines.append("")

        # Add returns
        if schema.returns:
            lines.append("Returns")
            lines.append("-------")
            if schema.returns.type:
                lines.append(f"{schema.returns.type}")
            if schema.returns.description:
                wrapped_desc = textwrap.wrap(schema.returns.description, width=75)
                indented_desc = indent_lines(wrapped_desc, 4)
                lines.extend(indented_desc)
            lines.append("")

        # Add raises
        if schema.raises:
            lines.append("Raises")
            lines.append("------")
            for exc in schema.raises:
                lines.append(f"{exc.exception}")
                if exc.description:
                    wrapped_desc = textwrap.wrap(exc.description, width=75)
                    indented_desc = indent_lines(wrapped_desc, 4)
                    lines.extend(indented_desc)
            lines.append("")

        # Add examples
        if schema.examples:
            lines.append("Examples")
            lines.append("--------")
            for example in schema.examples:
                if example.description:
                    lines.append(example.description)
                # Indent the code
                code_lines = example.code.split("\n")
                indented_code = indent_lines(code_lines, 4)
                lines.extend(indented_code)
                lines.append("")

        # Add notes
        if schema.notes:
            lines.append("Notes")
            lines.append("-----")
            note_lines = textwrap.wrap(schema.notes, width=75)
            lines.extend(note_lines)
            lines.append("")

        # Add version if available
        if schema.version:
            lines.append(f"Version: {schema.version}")
            lines.append("")

        # Add author if available
        if schema.author:
            lines.append(f"Author: {schema.author}")
            lines.append("")

        # Add deprecated warning if applicable
        if schema.deprecated:
            lines.append(".. deprecated:: ")
            lines.append("    This feature is deprecated and will be removed in a future release.")
            lines.append("")

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
register_formatter("python", "numpy", PythonNumpyFormatter)
