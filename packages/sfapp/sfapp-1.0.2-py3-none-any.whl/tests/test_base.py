from pathlib import Path

from sfapp.classes.importdict import ImportDict
from sfapp.classes.module import Module
from sfapp.classes.moduleimport import ModuleImport
from sfapp.classes.singlefileappbuilder import SingleFileAppBuilder
from sfapp.classes.sourcefile import SourceFile


def test_moduleimport_str_and_update():
    mi = ModuleImport("os")
    assert str(mi) == ""
    mi.is_global = True
    mi.imports.update({"path", "walk"})
    s = str(mi)
    assert "import os" in s
    assert "from os import" in s
    mi2 = ModuleImport("os", imports={"listdir"})
    mi.update(mi2)
    assert "listdir" in mi.imports


def test_importdict_missing():
    from sfapp.classes.module import Module

    d = ImportDict()
    m = Module("os", None)
    imp = d[m]
    assert isinstance(imp, ModuleImport)
    assert imp.module == "os"


def test_sourcefile_find(tmp_path: Path):
    # Write a file with imports and code
    file = tmp_path / "bar.py"
    file.write_text("import os\nfrom sys import path, argv\nprint('hi')\n")
    m = Module("bar", str(file))
    sf = SourceFile.find(m)
    assert "print('hi')" in sf.content
    assert any(imp.module == "os" for imp in sf.imports.values())
    assert any(imp.module == "sys" for imp in sf.imports.values())


def test_singlefileappbuilder_toposort(tmp_path: Path):
    # Create two modules, one importing the other
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    a.write_text("from b import foo\nx=1\n")
    b.write_text("foo=42\n")
    sys_path = __import__("sys").path
    sys_path.insert(0, str(tmp_path))
    try:
        # Import both so importlib can find them
        import importlib.util

        for name, path in [("a", a), ("b", b)]:
            spec = importlib.util.spec_from_file_location(name, path)
            assert spec
            assert spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        builder = SingleFileAppBuilder(
            root=tmp_path,
            package="a",
            silent=True,
            to_stdout=True,
        )
        files, _external = builder.collect_files()
        sorted_files = builder.topological_sort_files(files)
        # b should come before a
        assert sorted_files[-1].src.name == "a"
        assert sorted_files[0].src.name == "b"
    finally:
        sys_path.remove(str(tmp_path))
