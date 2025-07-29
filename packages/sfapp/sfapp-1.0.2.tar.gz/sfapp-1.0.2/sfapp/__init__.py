"""Single File App Builder.

This module provides functionality to collect, analyze, and bundle a Python package
and its dependencies into a single file, preserving import order and handling
external dependencies.
"""

from pathlib import Path

from sfapp.classes.singlefileappbuilder import SingleFileAppBuilder


def build(root: Path, package: str, silent: bool, to_stdout: bool, output: Path):
    builder = SingleFileAppBuilder(
        root=root,
        package=package,
        silent=silent,
        to_stdout=to_stdout,
    )
    builder.build(output)
