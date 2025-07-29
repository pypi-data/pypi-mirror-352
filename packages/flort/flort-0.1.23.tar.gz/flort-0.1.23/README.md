# Flort: File Concatenation and Project Overview Tool

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/flort.svg)](https://pypi.org/project/flort/)

Flort is a powerful command-line tool that helps developers generate consolidated views of their project source code. It combines directory trees, Python module outlines, and source file concatenation into a single, shareable output.

---

## Features 

- **Interactive File Selection UI**
- **Directory Tree Generation**
- **Source File Concatenation**
- **Python Module Outline**
  - Function signatures with type hints
  - Class hierarchies
  - Docstrings
  - Decorators
- **Flexible File Filtering**
- **Configurable Output**

---

## Installation

Install from [PyPI](https://pypi.org/project/flort/):

```bash
pip install flort
````

---

## Quick Start 

```bash
# Basic usage with Python files
flort -e py

# Using interactive UI
flort -u -e py
```

---

## Usage Examples

### Standard Command Line

```bash
flort -e py
flort -d src tests -e py,js,css
flort -e py -f setup.py,README.md -i venv,build
flort -a -H -o stdio
flort -e py -O -n
flort -d src tests \
    -e py,js \
    -i venv,build \
    -f setup.py \
    -H \
    -o project.txt
```

### Interactive UI

```bash
flort -u
flort -u -e py
flort -u -f setup.py,requirements.txt -o stdio
flort -u -e py,js,css -d src tests
flort -u -a -H
flort -u -O -n -e py
flort -u \
    -e py,js \
    -i venv,build \
    -f setup.py \
    -H \
    -o project.txt \
    -d src tests
```

### Glob Patterns

```bash
flort -g "*.py"
flort -g "*.py,*.js"
flort -d src -g "*.py"
flort -g "*.py" -i venv,build -H
```

---

## Command Line Options

| Option            | Short | Description                                           |
| ----------------- | ----- | ----------------------------------------------------- |
| `--dir DIRECTORY` | `-d`  | Directories to analyze (default: current directory)   |
| `--extensions`    | `-e`  | File extensions to include (comma-separated, no dots) |
| `--output`        | `-o`  | Output file path (default: `{cwd}.flort.txt`)         |
| `--outline`       | `-O`  | Generate Python module outline                        |
| `--no-dump`       | `-n`  | Skip source file concatenation                        |
| `--no-tree`       | `-t`  | Skip directory tree generation                        |
| `--all`           | `-a`  | Include all file types                                |
| `--hidden`        | `-H`  | Include hidden files                                  |
| `--ignore-dirs`   | `-i`  | Comma-separated directories to ignore                 |
| `--include-files` | `-f`  | Comma-separated files to include                      |
| `--glob`          | `-g`  | Glob patterns (quoted, comma-separated)               |
| `--ui`            | `-u`  | Launch interactive file selector UI                   |
| `--verbose`       | `-v`  | Enable verbose logging                                |
| `--archive`       | `-z`  | Archive output (zip, tar.gz)                          |
| `--help`          | `-h`  | Show help                                             |

---

## Interactive UI Controls

| Key   | Action                 |
| ----- | ---------------------- |
| ↑/↓   | Navigate files         |
| ←/→   | Navigate directories   |
| SPACE | Toggle selection       |
| i     | Toggle ignore          |
| f     | Edit file type filters |
| v     | View selections        |
| q     | Save and exit          |
| ESC   | Exit without saving    |

---

## Output Format

```
## Florted: 2025-01-02 05:54:57

## Directory Tree
|-- project/
|   |-- src/
|   |   |-- main.py
|   |-- tests/
|       |-- test_main.py

## Detailed Python Outline
### File: src/main.py
CLASS: MyClass
  DOCSTRING:
    Class description
  FUNCTION: my_method(arg1: str, arg2: int = 0) -> bool
    DOCSTRING:
      Method description

## File data
--- File: src/main.py
[source code here]
```

---

## Development

```bash
git clone https://github.com/chris17453/flort.git
cd flort
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
```

### Running Tests

```bash
python -m pytest
python -m pytest --cov=flort tests/
```

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Commit and push
4. Open a PR

Please include:

* Type hints
* Docstrings
* Tests for new features

---

## License

BSD 3-Clause License. See the [LICENSE](LICENSE) file.

---

## Acknowledgments

* Inspired by code exploration and documentation tools
* Thanks to all contributors

---

## Support 💬

Open an issue: [GitHub Issues](https://github.com/chris17453/flort/issues)
