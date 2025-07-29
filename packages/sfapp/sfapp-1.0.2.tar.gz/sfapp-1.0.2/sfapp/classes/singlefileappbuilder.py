"""SingleFileAppBuilder: Build a single-file version of a Python package.

This module provides the SingleFileAppBuilder class, which collects all modules
and dependencies of a Python package, sorts them topologically, and generates
a single-file output suitable for distribution or deployment.
"""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from sys import path as sys_path
from typing import Dict, List, Set, Tuple
from warnings import warn

from sfapp.classes.importdict import ImportDict
from sfapp.classes.module import Module
from sfapp.classes.sourcefile import SourceFile


@dataclass
class SingleFileAppBuilder:
    """Builds a single-file version of a Python package."""

    root: Path
    package: str
    silent: bool
    to_stdout: bool

    def log(self, message: str, level: int) -> None:
        """Log a message with indentation based on the level."""
        if not self.silent:
            print(f"{'  '*level}→ {message}")

    def collect_files(
        self,
    ) -> Tuple[Dict[Module, SourceFile], ImportDict]:
        """Collect all files and their imports for the package.

        Returns:
            Tuple containing a dictionary of files and their imports, and external imports.
        """
        self.log("Collecting files", 1)
        sys_path.append(str(self.root))
        try:
            main = Module.find(self.package, None)
            stack: List[Module] = [main]
            imported: Set[Module] = {main}
            files: Dict[Module, SourceFile] = {}
            external_imports = ImportDict()

            while stack:
                module = stack.pop(0)
                file = SourceFile.find(module)
                files[module] = file
                self.log(f"Analyzing module {module.name} at {module.origin}", 2)

                for dep, imports in file.imports.items():
                    origin = dep.origin
                    if origin and Path(origin).resolve().is_relative_to(
                        self.root
                    ):  # app dependency
                        if dep not in imported:
                            imported.add(dep)
                            stack.append(dep)
                            if imports.is_global:
                                warn(
                                    f"Module imports not supported for app dependency {dep.name} in {file.src.origin}"
                                )
                            self.log(f"Found new app dependency {dep.name}", 3)
                        else:
                            self.log(f"Found shared app dependency {dep.name}", 3)
                    else:
                        self.log(f"Found external dependency {dep.name}", 3)
                        external_imports[dep].update(imports)
            return files, external_imports
        finally:
            sys_path.remove(str(self.root))

    def topological_sort_files(
        self, files: Dict[Module, SourceFile]
    ) -> List[SourceFile]:
        """Sort files topologically based on their dependencies.

        Warns:
            A warning is issued if an import cycle is detected.

        Returns:
            List of files in topological order.
        """
        self.log(f"Building dependency graph for {len(files)} files", 1)
        file_to_dependants: Dict[SourceFile, Set[SourceFile]] = defaultdict(set)
        for file in files.values():
            file_to_dependants[file]  # ensure key exists
            for dependant in file.imports:
                if dependant in files:
                    file_to_dependants[files[dependant]].add(file)

        sorted_files: List[SourceFile] = []
        while True:
            independant_files = [
                file
                for file, dependant in file_to_dependants.items()
                if len(dependant) == 0
            ]
            if not independant_files:
                break
            processed_file = independant_files[0]
            del file_to_dependants[processed_file]
            sorted_files.insert(0, processed_file)
            self.log(f"Ordered {processed_file.src.name}", 2)
            for dependant in processed_file.imports:
                if dependant in files:
                    file_to_dependants[files[dependant]].remove(processed_file)

        if file_to_dependants:
            warn(
                f"Import cycle detected during topological sort, files may not be correctly sorted"
            )

            for file, dependants in file_to_dependants.items():

                self.log(
                    f"Dependants of {file.src.name}: {", ".join(i.src.name for i in dependants)}",
                    3,
                )
                sorted_files.insert(0, file)

        return sorted_files

    def generate(
        self,
        sorted_files: List[SourceFile],
        external_imports: ImportDict,
    ) -> str:
        """Generate the single-file output as a string.

        Args:
            sorted_files: List of files in dependency order.
            external_imports: Imports that are external to the app.

        Returns:
            The generated single-file app as a string.
        """
        self.log("Generating single-file output", 1)
        lines: List[str] = []

        for imps in external_imports.values():
            lines.append(str(imps))
        if lines:
            lines.append("")

        # Table of Contents
        lines.append("# Table of Contents")
        for idx, file in enumerate(sorted_files, 1):
            lines.append(f"# {idx}. {file.src.name}")
        lines.append("")

        # Module code with region markers
        for file in sorted_files:
            lines.append(f"# region {file.src.name}")
            lines.append(file.content)
            lines.append(f"# endregion {file.src.name}\n")

        return "\n".join(lines)

    def build(self, output: Path) -> None:
        """Build the single-file app and write to output or stdout.

        Args:
            output: The output file path or '-' for stdout.
        """
        self.log(
            f"Building Single File App for package {self.package} in {self.root}", 0
        )

        files, external_imports = self.collect_files()
        sorted_files = self.topological_sort_files(files)
        content = self.generate(sorted_files, external_imports)

        if self.to_stdout:
            self.log(f"Written output to stdout", 2)
            print(content)
        else:
            output.write_text(content, encoding="utf-8")
            self.log(f"Written output to {output}", 2)
