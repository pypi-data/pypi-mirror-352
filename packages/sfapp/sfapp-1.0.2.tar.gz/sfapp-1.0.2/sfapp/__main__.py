"""Entry point for the command-line interface."""

import warnings
from argparse import ArgumentParser
from pathlib import Path
from sys import exit
from typing import TextIO

from sfapp.classes.singlefileappbuilder import SingleFileAppBuilder
from sfapp.showwarning import showwarning


def main():
    warnings_count = 0

    def register_warning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        file: TextIO | None = None,
        line: str | None = None,
    ):
        nonlocal warnings_count
        warnings_count += 1
        return showwarning(message, category, filename, lineno, file, line)

    warnings.showwarning = register_warning

    parser = ArgumentParser(
        description="Build a single-file app from a Python package."
    )
    parser.add_argument("root", type=Path, help="Root directory of the package.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("-"),
        help="Output file (default stdout). Use '-' for stdout.",
    )
    parser.add_argument(
        "-p",
        "--package",
        type=str,
        help="Root package name (defaults to directory name).",
    )
    parser.add_argument(
        "-s", "--silent", action="store_true", help="Disable verbose logging."
    )
    args = parser.parse_args()

    root = args.root.resolve()
    pkg = args.package or root.name
    to_stdout = args.output == Path("-")
    builder = SingleFileAppBuilder(
        root=root,
        package=pkg,
        silent=args.silent,
        to_stdout=to_stdout,
    )
    builder.build(args.output)

    if warnings_count:
        warnings.warn(
            f"Build completed with {warnings_count} warning{'s' if warnings_count>1 else ''}"
        )


if __name__ == "__main__":
    exit(main())
