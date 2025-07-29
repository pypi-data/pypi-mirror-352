# Command Reference

Complete guide to all Flort command-line options and usage patterns.

## 📋 Command Syntax

```bash
flort [DIRECTORIES...] [OPTIONS]
```

### Basic Examples

```bash
# Process current directory
flort .

# Process specific directories
flort src/ tests/ docs/

# Mix relative and absolute paths
flort ./src /home/user/project/lib
```

## 🎛️ Core Options

### File Selection

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--extensions` | `-e` | File extensions to include | `--extensions py,js,ts` |
| `--all` | `-a` | Include all files | `--all` |
| `--glob` | `-g` | Glob patterns to include | `--glob "*.py,src/**/*.js"` |
| `--include-files` | `-f` | Specific files to include | `--include-files "main.py,config.py"` |

!!! tip "Extension Format"
    Extensions should be specified without dots: `py,js,md` not `.py,.js,.md`

### File Exclusion

| Option | Description | Example |
|--------|-------------|---------|
| `--exclude-extensions` | Extensions to exclude | `--exclude-extensions pyc,pyo,min.js` |
| `--exclude-patterns` | Glob patterns to exclude | `--exclude-patterns "*test*,*cache*"` |
| `--ignore-dirs` | Directories to completely ignore | `--ignore-dirs "__pycache__,venv,.git"` |

### Special File Types

| Option | Short | Description |
|--------|-------|-------------|
| `--hidden` | `-H` | Include hidden files and directories |
| `--include-binary` | | Include binary files (normally excluded) |

## 📤 Output Options

### Output Destination

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file path | `--output project.txt` |
| | | Console output | `--output stdio` |

### Output Modes

| Option | Short | Description |
|--------|-------|-------------|
| `--outline` | `-O` | Generate Python code outline |
| `--no-dump` | `-n` | Skip file concatenation (tree/outline only) |
| `--no-tree` | `-t` | Skip directory tree generation |
| `--manifest` | | Generate file manifest (list) only |

### Content Processing

| Option | Description | Default |
|--------|-------------|---------|
| `--clean-content` | Clean whitespace from files | Enabled |
| `--no-clean` | Preserve original formatting | Disabled |
| `--show-config` | Include configuration in output | Disabled |

### Archive Creation

| Option | Short | Description | Formats |
|--------|-------|-------------|---------|
| `--archive` | `-z` | Create archive of output | `zip`, `tar.gz` |

## 🎮 Interface Options

### Interactive Mode

| Option | Short | Description |
|--------|-------|-------------|
| `--ui` | `-u` | Launch interactive file selector |

### Processing Control

| Option | Description | Example |
|--------|-------------|---------|
| `--max-depth` | Maximum directory traversal depth | `--max-depth 3` |

### Information & Debugging

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Enable detailed logging |
| `--version` | | Show version and exit |

## 📁 File Filtering

### Extension-Based Filtering

```bash
# Single extension
flort . --extensions py

# Multiple extensions
flort . --extensions py,js,ts,md,yml

# Exclude specific extensions
flort . --all --exclude-extensions pyc,pyo,min.js,map
```

### Pattern-Based Filtering

```bash
# Include patterns (glob syntax)
flort . --glob "*.py" --glob "src/**/*.js"

# Exclude patterns (more powerful than extensions)
flort . --extensions py --exclude-patterns "*test*,*spec*,*cache*"

# Complex exclusion patterns
flort . --all --exclude-patterns "*.min.*,*build*,*dist*,*node_modules*"
```

### Directory Filtering

```bash
# Ignore specific directories
flort . --extensions py --ignore-dirs "__pycache__,venv,.git"

# Ignore build and cache directories
flort . --all --ignore-dirs "build,dist,node_modules,.pytest_cache"

# Ignore environment directories
flort . --extensions py --ignore-dirs "venv,env,.venv,.env,conda-env"
```

### Specific File Inclusion

```bash
# Include important files regardless of filters
flort . --extensions py --include-files "setup.py,manage.py,wsgi.py"

# Mix with other filtering
flort src/ --extensions py --include-files "README.md,requirements.txt,Dockerfile"

# Include config files
flort . --extensions py,md --include-files "pyproject.toml,.env.example,docker-compose.yml"
```

## 📊 Output Formats

### Standard Concatenation

```bash
# Default: tree + file contents
flort . --extensions py --output project.txt
```

Output structure:
```
## Florted: 2025-06-02 10:30:15
## Directory Tree
[tree structure]

## File Data
[concatenated files with metadata]
```

### Directory Tree Only

```bash
# Structure without file contents
flort . --extensions py --no-dump --output structure.txt
```

### Python Code Outline

```bash
# Extract class/function signatures
flort . --extensions py --outline --output api.txt

# Outline without file contents
flort . --extensions py --outline --no-dump --output signatures.txt
```

Output format:
```
## Python Code Outline

### File: main.py

CLASS: MyClass(BaseClass)
  DECORATORS: @dataclass
  METHOD: __init__(self, name: str)
  METHOD: process(self) -> bool
    DECORATORS: @property

FUNCTION: main() -> None
  DOCSTRING: Main entry point
```

### File Manifest

```bash
# List files with metadata only
flort . --extensions py --manifest --output file_list.txt
```

Output:
```
## File Manifest
  1. main.py (1,234 bytes)
  2. src/utils.py (2,345 bytes)
  3. tests/test_main.py (567 bytes) [BINARY]

Total: 3 files, 4,146 bytes
```

## 🗜️ Archive Creation

### ZIP Archives

```bash
# Create ZIP with output
flort . --extensions py --archive zip --output project.txt
# Creates: project.txt.zip

# Archive with filtering
flort . --extensions py,md --exclude-patterns "*test*" --archive zip
```

### TAR.GZ Archives

```bash
# Create compressed TAR archive
flort . --extensions py --archive tar.gz --output project.txt
# Creates: project.txt.tar.gz
```

!!! note "Archive Limitations"
    Archives cannot be created when using `--output stdio`

## ⚙️ Advanced Usage

### Configuration Display

```bash
# Show settings used in output
flort . --extensions py --show-config --output project.txt
```

Adds configuration section:
```
## Flort Configuration
Working Directory: /home/user/project
Output File: project.txt
Target Directories: .

### Inclusion Criteria:
- Extensions: py

### Processing Options:
- Content cleaning: enabled
- Directory tree: enabled
```

### Depth Limiting

```bash
# Limit traversal depth
flort . --extensions py --max-depth 2

# Only top-level files
flort . --extensions py --max-depth 1
```

### Content Cleaning Control

```bash
# Clean whitespace (default)
flort . --extensions py --clean-content --output clean.txt

# Preserve original formatting
flort . --extensions py --no-clean --output raw.txt
```

## 🔄 Complex Workflows

### Full Project Analysis

```bash
flort . \
  --extensions py,js,ts,md,yml,json \
  --exclude-patterns "*test*,*spec*,*cache*,*.min.*,*build*" \
  --ignore-dirs "node_modules,venv,.git,build,dist,__pycache__" \
  --include-files "README.md,package.json,setup.py,requirements.txt" \
  --outline \
  --show-config \
  --archive zip \
  --output comprehensive_analysis.txt
```

### Documentation Extraction

```bash
flort . \
  --extensions md,rst,txt \
  --include-files "README.md,CHANGELOG.md,LICENSE,CONTRIBUTING.md" \
  --ignore-dirs ".git,venv,node_modules" \
  --no-dump \
  --output documentation_structure.txt
```

### Code Review Package

```bash
flort . \
  --include-files "changed_file1.py,changed_file2.py,new_config.json" \
  --outline \
  --archive zip \
  --output code_review_$(date +%Y%m%d).txt
```

### LLM Context Preparation

```bash
flort . \
  --extensions py,md \
  --exclude-patterns "*test*,*cache*,*__pycache__*,*.pyc" \
  --ignore-dirs "venv,.git,build,dist" \
  --outline \
  --max-depth 3 \
  --output llm_context.txt
```

## 🎯 Token Counting

Flort automatically counts tokens in processed files:

```bash
flort . --extensions py --output project.txt
```

Output statistics:
```
Output Statistics:
Lines: 1,234
Tokens: 5,678
Characters: 45,123
```

!!! info "Token Estimation"
    Token counts are estimates using a regex-based tokenizer. Actual LLM token usage may vary.

## 🔍 Debugging and Troubleshooting

### Verbose Output

```bash
# Enable detailed logging
flort . --extensions py --verbose --output project.txt
```

### Preview Files

```bash
# See what files would be processed
flort . --extensions py --manifest --output file_preview.txt

# Check with specific filters
flort . --extensions py --exclude-patterns "*test*" --manifest
```

### Test with Limited Scope

```bash
# Test with small subset
flort . --extensions py --max-depth 1 --output test.txt

# Single directory test
flort src/ --extensions py --output src_only.txt
```

## 📈 Performance Optimization

### For Large Projects

```bash
# Limit depth to reduce file count
flort . --extensions py --max-depth 3

# Exclude large directories early
flort . --extensions py --ignore-dirs "venv,node_modules,.git,build"

# Use specific directories instead of root
flort src/ lib/ --extensions py
```

### Memory Optimization

```bash
# Process specific subdirectories separately
flort src/ --extensions py --output src.txt
flort tests/ --extensions py --output tests.txt

# Skip content cleaning for speed
flort . --extensions py --no-clean
```

### Speed Optimization

```bash
# Skip tree generation
flort . --extensions py --no-tree

# Use manifest for quick file listing
flort . --extensions py --manifest

# Specific extensions instead of --all
flort . --extensions py,js,md  # Instead of --all
```

## 🚨 Error Handling

### Common Error Messages

```bash
# No inclusion criteria
❌ No extensions or glob provided and --all flag not set

# Fix: Specify what to include
flort . --extensions py

# Directory not found
❌ Directory does not exist: /nonexistent/path

# Fix: Check path spelling and existence
ls -la /path/to/check

# Permission denied
❌ Directory is not readable: /protected/path

# Fix: Check permissions or run with appropriate user
sudo flort /protected/path --extensions py

# Invalid glob pattern
❌ Invalid glob pattern 'test[unclosed': missing ]

# Fix: Check pattern syntax
flort . --glob "test*.py"
```

### Recovery Strategies

```bash
# Start with simple command
flort . --extensions py --max-depth 1

# Add complexity gradually
flort . --extensions py,md --max-depth 2

# Use verbose mode for debugging
flort . --extensions py --verbose
```

## 🔗 Integration Examples

### Shell Scripts

```bash
#!/bin/bash
# generate_docs.sh

PROJECT_NAME=$(basename $(pwd))
OUTPUT_FILE="docs/${PROJECT_NAME}_$(date +%Y%m%d).txt"

flort . \
  --extensions py,md,yml \
  --exclude-patterns "*test*,*cache*" \
  --outline \
  --archive zip \
  --output "$OUTPUT_FILE"

echo "Documentation generated: $OUTPUT_FILE"
```

### Makefile Integration

```makefile
# Project documentation
docs:
	flort . \
		--extensions py,md \
		--exclude-patterns "*test*,*cache*" \
		--outline \
		--output docs/project_overview.txt

# Code review package
review:
	flort . \
		--include-files $(FILES) \
		--archive zip \
		--output review_$(shell date +%Y%m%d).txt

.PHONY: docs review
```

### Git Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Generate project overview before commit
flort . \
  --extensions py \
  --exclude-patterns "*test*" \
  --outline \
  --output .git/hooks/current_state.txt
```

---

**Master these commands and you'll be a Flort power user! 🚀**

For more examples and real-world usage patterns, see the [Examples Guide](examples.md).