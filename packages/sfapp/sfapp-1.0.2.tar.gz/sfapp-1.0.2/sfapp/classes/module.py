"""Module: Represents a Python module and its origin.

This module defines the Module class, which encapsulates the name and origin of a Python
module and provides utilities for locating modules.
"""

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Optional


@dataclass(frozen=True)
class Module:
    """Represents a Python module with its name and origin."""

    name: str
    origin: Optional[str]

    def __hash__(self) -> int:
        """Hash based on the module name."""
        return hash(self.name)

    @staticmethod
    def find(name: str, package: Optional[str]) -> "Module":
        """Find and return a Module object for the given name and package.

        Raises:
            ModuleNotFoundError: If the module cannot be found.
        """
        try:
            spec = find_spec(name, package)
        except ModuleNotFoundError:
            spec = None
        if spec is None or spec.origin is None:
            raise ModuleNotFoundError(
                f"No module named {name!r}, imported from {package}"
            )
        origin = spec.origin if spec.has_location else None
        return Module(spec.name, origin)
