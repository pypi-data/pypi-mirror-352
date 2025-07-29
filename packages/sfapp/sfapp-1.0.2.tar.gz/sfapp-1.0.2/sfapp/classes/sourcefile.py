"""SourceFile: Represents a Python source file and its imports.

This module provides the SourceFile class, which parses a Python file for its content
and import statements, and associates it with its corresponding Module.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List

from sfapp.classes.importdict import ImportDict
from sfapp.classes.module import Module


@dataclass(frozen=True)
class SourceFile:
    """Represents a source file, its content, and its imports."""

    src: Module
    content: str
    imports: ImportDict

    def __hash__(self) -> int:
        """Hash based on the source module."""
        return hash(self.src)

    @staticmethod
    def find(src: Module) -> "SourceFile":
        """Find and parse a file for its content and imports."""
        assert src.origin
        imports = ImportDict()
        final_lines: List[str] = []
        lines = Path(src.origin).read_text(encoding="utf-8").splitlines()

        for line in lines:
            if line.startswith(("import ", "from ")):
                tokens = line.split(None, 3)
                module = Module.find(tokens[1], src.name)
                if len(tokens) == 2:
                    imports[module].is_global = True
                elif len(tokens) == 4:
                    imports[module].imports.update(
                        imp.strip() for imp in tokens[3].split(",")
                    )
            else:
                final_lines.append(line)

        content = "\n".join(final_lines).strip()
        return SourceFile(src, content, imports)
