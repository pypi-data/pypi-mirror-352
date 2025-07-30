"""
Text utility functions for docstring-composer.
"""

from typing import List


def indent_lines(lines: List[str], indent: int) -> List[str]:
    """
    Indent a list of lines by a specified number of spaces.

    Args:
        lines: The lines to indent.
        indent: The number of spaces to indent by.

    Returns:
        The indented lines.
    """
    indent_str = " " * indent
    return [indent_str + line for line in lines]
