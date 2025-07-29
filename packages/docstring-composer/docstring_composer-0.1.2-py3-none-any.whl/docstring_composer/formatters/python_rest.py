"""
Python reStructuredText (reST)-style docstring formatter.
"""

from typing import List
import textwrap

from docstring_composer.ds_schema.docstring_schema import DocstringSchema, DocParam, DocRaise, DocExample
from docstring_composer.formatters import BaseFormatter, register_formatter
from docstring_composer.utils.text import indent_lines


class PythonReSTFormatter(BaseFormatter):
    """
    Formatter for Python reStructuredText (reST)-style docstrings.
    """

    def format(self, schema: DocstringSchema) -> str:
        """
        Format a docstring schema as a reST-style Python docstring.

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

        # Add parameters section if we have parameters
        if schema.parameters:
            lines.append(":Parameters:")
            lines.append("")
            for param in schema.parameters:
                # Parameter name and type
                if param.type:
                    lines.append(f"   **{param.name}** : {param.type}")
                else:
                    lines.append(f"   **{param.name}**")
                
                # Parameter description
                if param.description:
                    desc_lines = textwrap.wrap(param.description, width=75)
                    indented_desc = indent_lines(desc_lines, 7)
                    lines.extend(indented_desc)
                    
                # Parameter default value
                if param.default is not None and not param.required:
                    if isinstance(param.default, str):
                        lines.append(f"       Default: '{param.default}'")
                    else:
                        lines.append(f"       Default: {param.default}")
                
                # Add a blank line between parameters
                lines.append("")

        # Add returns
        if schema.returns:
            lines.append(":Returns:")
            lines.append("")
            if schema.returns.type:
                lines.append(f"   **{schema.returns.type}**")
            if schema.returns.description:
                desc_lines = textwrap.wrap(schema.returns.description, width=75)
                indented_desc = indent_lines(desc_lines, 7)
                lines.extend(indented_desc)
            lines.append("")

        # Add raises
        if schema.raises:
            lines.append(":Raises:")
            lines.append("")
            for exc in schema.raises:
                lines.append(f"   **{exc.exception}**")
                if exc.description:
                    desc_lines = textwrap.wrap(exc.description, width=75)
                    indented_desc = indent_lines(desc_lines, 7)
                    lines.extend(indented_desc)
                lines.append("")

        # Add examples
        if schema.examples:
            lines.append(":Examples:")
            lines.append("")
            for i, example in enumerate(schema.examples):
                if example.description:
                    lines.append(f"   {example.description}")
                    lines.append("")
                lines.append("   .. code-block:: python")
                lines.append("")
                for code_line in example.code.split("\n"):
                    lines.append(f"      {code_line}")
                lines.append("")

        # Add notes
        if schema.notes:
            lines.append(":Notes:")
            lines.append("")
            note_lines = textwrap.wrap(schema.notes, width=75)
            indented_notes = indent_lines(note_lines, 3)
            lines.extend(indented_notes)
            lines.append("")

        # Add version if available
        if schema.version:
            lines.append(f":Version: {schema.version}")
            lines.append("")

        # Add author if available
        if schema.author:
            lines.append(f":Author: {schema.author}")
            lines.append("")

        # Add deprecated warning if applicable
        if schema.deprecated:
            lines.append(".. deprecated:: current")
            lines.append("   This feature is deprecated and will be removed in a future release.")
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
register_formatter("python", "rest", PythonReSTFormatter)
