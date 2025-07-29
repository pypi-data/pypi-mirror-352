# sfapp

**sfapp** is a Python tool for building single-file Python applications from a package or directory. It analyzes source files, resolves imports, and generates a standalone Python script containing all necessary code.

## Features

- Collects and analyzes Python source files in a package.
- Resolves and inlines internal imports.
- Outputs a single Python file for easy distribution.
- Supports custom package roots and output locations.
- Optionally suppresses log output.

## Usage

You can use `sfapp` as a command-line tool:

```sh
python -m sfapp <root> [-o <output_file.py>] [-p <package_name>] [-s]
```

### Arguments

- `root`: Path to the root directory of your package (positional argument).

### Options

- `-o`, `--output`: Output file path for the generated single-file app (default: stdout, use `-` for stdout).
- `-p`, `--package`: Name of the package to build (defaults to the root directory name).
- `-s`, `--silent`: Suppress log output (optional).

## Example

```sh
python -m sfapp ./myproject -p myproject -o myproject_single.py
```

## License

MIT License.
