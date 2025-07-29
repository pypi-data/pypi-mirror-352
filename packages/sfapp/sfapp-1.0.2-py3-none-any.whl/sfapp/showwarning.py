"""Custom warning display for visually enhanced warnings.

This module provides a replacement for `warnings.showwarning` that
renders warnings with color and context for better visibility.
"""

from sys import stderr, stdout
from typing import List, TextIO

# ANSI color codes for terminal output
if stdout.isatty():
    yellow = "\x1b[33m"
    gray = "\x1b[2m"
    reset = "\x1b[0m"
else:
    yellow = gray = reset = ""


def showwarning(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
) -> None:
    """Display a warning message in a visually enhanced format.

    Args:
        message: The warning message or exception.
        category: The warning category (class).
        filename: The file in which the warning occurred.
        lineno: The line number where the warning occurred.
        file: Optional file-like object to write the warning to (defaults to stderr).
        line: The line of source code to be displayed (unused).
    """
    parts: List[str] = [
        yellow,
        "Warn" if category is UserWarning else category.__name__,
        ":",
        reset,
        " ",
        str(message),
        reset,
        " ",
        gray,
        f"({filename}:{lineno})",
        reset,
    ]

    output: TextIO = file if file is not None else stderr
    print("".join(parts), file=output)
