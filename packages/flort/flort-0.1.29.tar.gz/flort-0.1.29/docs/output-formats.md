# Output Formats Guide

Flort provides multiple output formats to suit different use cases. This guide covers all available formats and when to use each one.

## 📊 Output Format Overview

| Format | Description | Best For |
|--------|-------------|----------|
| **Standard** | Tree + File Contents | LLM context, full analysis |
| **Tree Only** | Directory structure only | Project overview, documentation |
| **Outline** | Python API signatures | API documentation, code review |
| **Manifest** | File listing with metadata | Inventory, file analysis |
| **Archive** | Compressed output | Sharing, storage |

## 🌳 Standard Format (Default)

The default output includes directory tree and full file contents:

```bash
flort . --extensions py --output project.txt
```

### Output Structure

```
## Florted: 2025-06-02 10:30:15
## Directory Tree
project/
├── main.py
├── src/
│   ├── utils.py
│   └── config.py
└── tests/
    └── test_main.py

## File Data
--- File: main.py
--- Characters: 1,234
--- Token Count: 256
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()

--- File: src/utils.py
--- Characters: 567
--- Token Count: 123
def helper_function():
    return "helper"
```

### Use Cases

- **LLM context preparation** - Complete code understanding
- **Code sharing** - Full project in single file
- **Documentation** - Comprehensive project view
- **Backup** - Readable project snapshot

## 🌲 Tree-Only Format

Generate directory structure without file contents:

```bash
flort . --extensions py --no-dump --output structure.txt
```

### Output

```
## Florted: 2025-06-02 10:30:15
## Directory Tree
project/
├── main.py
├── src/
│   ├── utils.py
│   ├── config.py
│   └── models/
│       ├── user.py
│       └── product.py
├── tests/
│   ├── test_main.py
│   └── test_utils.py
└── docs/
    └── README.md
```

### Use Cases

- **Project structure documentation**
- **Architecture overview**
- **Directory planning**
- **Quick project scan**

## 🐍 Python Outline Format

Extract class and function signatures from Python files:

```bash
flort . --extensions py --outline --output api.txt
```

### Output Structure

```
## Florted: 2025-06-02 10:30:15
## Directory Tree
[tree structure]

## Python Code Outline

### File: main.py

FUNCTION: main() -> None
  DOCSTRING:
    Main entry point for the application.
    
    Initializes the system and starts processing.

CLASS: Application
  DECORATORS: @dataclass
  DOCSTRING:
    Main application class handling core functionality.

  METHOD: __init__(self, config: Config)
    DOCSTRING:
      Initialize application with configuration.

  METHOD: run(self) -> bool
    DECORATORS: @retry(max_attempts=3)
    DOCSTRING:
      Run the main application loop.
      
      Returns:
        bool: True if successful, False otherwise.

### File: src/utils.py

FUNCTION: helper_function(data: str) -> dict
  DOCSTRING:
    Process input data and return structured result.

CLASS: DataProcessor
  METHOD: process(self, input_data: Any) -> ProcessedData
```

### Use Cases

- **API documentation generation**
- **Code review preparation**
- **Architecture analysis**
- **Interface documentation**

### Outline with File Contents

```bash
# Outline + full file contents
flort . --extensions py --outline --output complete_api.txt
```

### Outline Only (No File Contents)

```bash
# Just the outline, no file contents
flort . --extensions py --outline --no-dump --output signatures_only.txt
```

## 📋 Manifest Format

Generate a file listing with metadata:

```bash
flort . --extensions py --manifest --output inventory.txt
```

### Output Structure

```
## Florted: 2025-06-02 10:30:15
## File Manifest

  1. main.py (1,234 bytes)
  2. src/utils.py (2,345 bytes)
  3. src/config.py (567 bytes)
  4. src/models/user.py (3,456 bytes)
  5. tests/test_main.py (890 bytes)
  6. tests/test_utils.py (1,234 bytes) [BINARY]
  7. docs/README.md (2,345 bytes)

Total: 7 files, 12,071 bytes
```

### Use Cases

- **File inventory**
- **Size analysis**
- **Preview before processing**
- **Project statistics**

## 🗜️ Archive Formats

Create compressed archives of your output:

### ZIP Archive

```bash
flort . --extensions py --archive zip --output project.txt
# Creates: project.txt.zip
```

### TAR.GZ Archive

```bash
flort . --extensions py --archive tar.gz --output project.txt
# Creates: project.txt.tar.gz
```

### Use Cases

- **Sharing projects**
- **Backup storage**
- **Email attachments**
- **Version snapshots**

## ⚙️ Configuration Display

Show the exact settings used:

```bash
flort . --extensions py --show-config --output project.txt
```

### Added Section

```
## Flort Configuration
Working Directory: /home/user/project
Output File: project.txt
Target Directories: .

### Inclusion Criteria:
- Extensions: py

### Exclusion Criteria:
- Patterns: *test*, *cache*
- Directories: __pycache__, venv

### Processing Options:
- Content cleaning: enabled
- Directory tree: enabled
- Python outline: disabled
- Maximum depth: unlimited

### Mode: Directory Scanning
Scanning directories with applied filters

---
```

## 📤 Output Destinations

### File Output

```bash
# Specific file
flort . --extensions py --output my_project.txt

# Auto-generated name
flort . --extensions py
# Creates: {directory_name}.flort.txt
```

### Console Output

```bash
# Print to stdout
flort . --extensions py --output stdio

# Pipe to other commands
flort . --extensions py --output stdio | grep "def "
```

### Multiple Outputs

```bash
# Generate different formats
flort . --extensions py --outline --output api_docs.txt
flort . --extensions py --manifest --output file_list.txt
flort . --extensions py --no-tree --output code_only.txt
```

## 🎨 Customization Options

### Content Processing

```bash
# Clean whitespace (default)
flort . --extensions py --clean-content

# Preserve original formatting
flort . --extensions py --no-clean

# Skip directory tree
flort . --extensions py --no-tree
```

### Depth Control

```bash
# Limit directory depth in tree
flort . --extensions py --max-depth 2
```

### Token Information

All formats include token counting:

```
## Concatenation Summary
Files processed: 15
Files skipped: 2
Total characters: 50,432
Total tokens: 12,108

Completed at: 2025-06-02 10:30:15
```

## 🔄 Format Combinations

### Multiple Features

```bash
# Tree + Outline + Config
flort . --extensions py --outline --show-config --output complete.txt

# Manifest + Archive
flort . --all --manifest --archive zip --output inventory.txt

# Outline only + Archive
flort . --extensions py --outline --no-dump --archive tar.gz --output api.txt
```

### Conditional Processing

```bash
# Large projects: manifest first
flort . --all --manifest --output preview.txt
# Review, then:
flort . --extensions py,md --outline --output final.txt

# Documentation: tree + specific files
flort . --extensions md --no-dump --include-files "README.md,CHANGELOG.md"
```

## 📊 Format Comparison

| Feature | Standard | Tree Only | Outline | Manifest |
|---------|----------|-----------|---------|----------|
| **File contents** | ✅ | ❌ | ✅ | ❌ |
| **Directory tree** | ✅ | ✅ | ✅ | ❌ |
| **Python signatures** | ❌ | ❌ | ✅ | ❌ |
| **File metadata** | ✅ | ❌ | ✅ | ✅ |
| **Size** | Large | Small | Medium | Small |
| **Processing time** | Slow | Fast | Medium | Fast |

## 🎯 Best Practices

### Choose the Right Format

- **Exploring new codebase**: Start with tree-only or manifest
- **LLM context**: Use standard format with outline for Python projects
- **Documentation**: Use outline-only for API docs, tree-only for structure
- **Sharing**: Use archive format for easy distribution

### Optimize for Use Case

```bash
# Quick project scan
flort . --all --manifest --max-depth 2

# LLM-ready Python context
flort . --extensions py,md --outline --exclude-patterns "*test*"

# Complete project backup
flort . --all --archive zip --exclude-patterns "*cache*,*build*"

# API documentation
flort . --extensions py --outline --no-dump --exclude-patterns "*test*"
```

### Performance Considerations

- **Manifest format**: Fastest, good for previews
- **Tree-only format**: Fast, good for structure analysis
- **Standard format**: Slowest, most complete
- **Archive creation**: Adds processing time but saves space

---

**Choose the right output format for your specific needs and optimize your Flort workflow! 📊**

-