"""ModuleImport: Represents and manages import statements for modules.

This module defines the ModuleImport class, which encapsulates information about import
statements, including whether they are global and which symbols are imported.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ModuleImport:
    """Represents an import statement for a module."""

    module: str
    is_global: bool = False
    imports: set[str] = field(default_factory=set[str])

    def __str__(self) -> str:
        """Return the string representation of the import statement(s)."""
        lines: List[str] = []
        if self.is_global:
            lines.append(f"import {self.module}\n")
        if self.imports:
            lines.append(f"from {self.module} import {', '.join(self.imports)}\n")
        return "".join(lines)

    def update(self, other: "ModuleImport"):
        """Update this import with another Import's properties."""
        if other.is_global:
            self.is_global = True
        self.imports.update(other.imports)
