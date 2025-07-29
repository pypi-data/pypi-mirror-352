"""ImportDict: A specialized dictionary for module imports.

This module defines ImportDict, a dictionary mapping Module objects to their corresponding
ModuleImport objects, with automatic creation of missing entries.
"""

from sfapp.classes.module import Module
from sfapp.classes.moduleimport import ModuleImport


class ImportDict(dict[Module, ModuleImport]):
    """A dictionary mapping Modules to their Import objects."""

    def __missing__(self, key: Module) -> ModuleImport:
        """Create a new Import entry if the key is missing."""
        self[key] = ModuleImport(key.name)
        return self[key]
