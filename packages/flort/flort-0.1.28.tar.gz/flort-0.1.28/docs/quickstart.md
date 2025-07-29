# Quick Start Guide

Get up and running with Flort in just a few minutes! This guide will walk you through installation and your first successful file concatenation.

## 📦 Step 1: Installation

=== "Linux/macOS"

    ```bash
    # Install via pip
    pip install flort
    
    # Verify installation
    flort --version
    ```

=== "Windows"

    ```bash
    # Install with UI support
    pip install flort[ui]
    
    # Verify installation  
    flort --version
    ```

=== "Development"

    ```bash
    # Clone and install from source
    git clone https://github.com/watkinslabs/flort.git
    cd flort
    pip install -e .
    ```

!!! tip "Virtual Environment Recommended"
    ```bash
    python -m venv flort-env
    source flort-env/bin/activate  # Linux/macOS
    # or flort-env\Scripts\activate  # Windows
    pip install flort
    ```

## 🎯 Step 2: Your First Command

Let's start with a simple example. Navigate to any project directory and run:

```bash
# Process all Python files in current directory
flort . --extensions py --output my_project.txt
```

**What this does:**
- `.` - Process current directory
- `--extensions py` - Include only Python files
- `--output my_project.txt` - Save to specified file

You should see output like:
```
Processing 15 files from 3 directories -> my_project.txt
✅ Flort completed successfully!

Output Statistics:
Lines: 1,234
Tokens: 5,678
Characters: 45,123
```

## 📂 Step 3: Explore the Output

Open the generated file to see the structured output:

```
## Florted: 2025-06-02 10:30:15
## Directory Tree
my_project/
├── main.py
├── src/
│   ├── utils.py
│   └── config.py
└── tests/
    └── test_main.py

## File Data
--- File: main.py
--- Characters: 567
--- Token Count: 123
def main():
    print("Hello, World!")
...
```

## 🚀 Step 4: Try Common Patterns

### Multiple File Types
```bash
# Include Python, JavaScript, and Markdown files
flort . --extensions py,js,md --output codebase.txt
```

### Exclude Test Files
```bash
# Skip test files and cache directories
flort . --extensions py --exclude-patterns "*test*,*cache*" --output production_code.txt
```

### Interactive Selection
```bash
# Use the visual file selector
flort --ui
```

### Generate Code Outline
```bash
# Create Python API outline
flort . --extensions py --outline --output api_outline.txt
```

## 🎨 Step 5: Try the Interactive UI

Launch the interactive interface:

```bash
flort --ui
```

You'll see a file browser interface:

```
📁 /home/user/project
Filter: .py, .js, .md

📂 src/
  [✓] 📄 main.py
  [✓] 📄 utils.py  
  [ ] 📄 config.json
📂 tests/
  [✗] 📄 test_main.py
📄 README.md [✓]

Selected: 3 | Ignored: 1 | Types: 3
🎯 Navigation: ↑/↓ SPACE:Select TAB:Filter q:Done h:Help
```

**Quick UI Tips:**
- Use `↑/↓` to navigate
- `Space` to toggle selection  
- `Tab` to change file filters
- `q` to finish and process
- `h` for help

## ⚙️ Step 6: Common Workflows

### For LLM Context
```bash
# Prepare clean code context for AI
flort . \
  --extensions py,md \
  --exclude-patterns "*test*,*cache*,*__pycache__*" \
  --outline \
  --output llm_context.txt
```

### For Documentation
```bash
# Generate project overview
flort . \
  --extensions py,md,yml \
  --include-files "README.md,CHANGELOG.md" \
  --no-dump \
  --output project_overview.txt
```

### For Code Review
```bash
# Package specific files for review
flort . \
  --include-files "modified_file1.py,modified_file2.py,config.json" \
  --archive zip \
  --output code_review.txt
```

## 🔧 Step 7: Customization

### Output to Console
```bash
# Print to terminal instead of file
flort . --extensions py --output stdio
```

### Limit Directory Depth
```bash
# Only process top 2 levels
flort . --extensions py --max-depth 2
```

### Create Archive
```bash
# Generate ZIP archive
flort . --extensions py --archive zip --output project.txt
```

### Show Configuration
```bash
# Include settings in output
flort . --extensions py --show-config --output project.txt
```

## 🎯 Real-World Example

Let's process a typical Python project:

```bash
# Comprehensive project analysis
flort . \
  --extensions py,md,yml,json \
  --exclude-patterns "*test*,*cache*,*build*,*dist*" \
  --ignore-dirs "__pycache__,venv,.git,node_modules" \
  --include-files "setup.py,requirements.txt,pyproject.toml" \
  --outline \
  --show-config \
  --archive zip \
  --output full_analysis.txt
```

This command:
- ✅ Includes Python, Markdown, YAML, and JSON files
- ❌ Excludes test files, cache, and build artifacts  
- 🚫 Ignores common directories that shouldn't be processed
- 📄 Specifically includes important config files
- 🐍 Generates Python code outline
- ⚙️ Shows configuration used
- 🗜️ Creates a ZIP archive

## 🆘 Troubleshooting

### No Files Found?
```bash
# Check what would be processed
flort . --extensions py --manifest --output file_list.txt

# Use verbose mode for debugging
flort . --extensions py --verbose
```

### Permission Errors?
```bash
# Skip problematic directories
flort . --extensions py --ignore-dirs "restricted_folder"
```

### UI Not Working?
```bash
# On Windows, install curses support
pip install windows-curses

# Or use text-based fallback (automatic)
flort . --extensions py  # Skip --ui
```

### Large Output Files?
```bash
# Use manifest mode to see file list first
flort . --extensions py --manifest

# Limit depth to reduce file count
flort . --extensions py --max-depth 2
```

## 🎓 Next Steps

Now that you've got the basics down, explore more advanced features:

1. **[Master File Filtering](filtering.md)** - Advanced include/exclude patterns
2. **[Explore Output Formats](output-formats.md)** - Tree, outline, and manifest modes
3. **[Learn the Interactive UI](ui-guide.md)** - Full UI capabilities
4. **[See Real Examples](examples.md)** - Production use cases
5. **[API Integration](api/overview.md)** - Use Flort programmatically

## 💡 Pro Tips

!!! tip "Workflow Efficiency"
    - Start with `--manifest` to preview files before processing
    - Use `--ui` for unfamiliar codebases to explore interactively
    - Save commonly used patterns as shell aliases
    - Always exclude test and cache directories for cleaner output

!!! example "Shell Aliases"
    ```bash
    # Add to ~/.bashrc or ~/.zshrc
    alias flort-py="flort . --extensions py --exclude-patterns '*test*,*cache*'"
    alias flort-web="flort . --extensions js,ts,css,html,md"
    alias flort-llm="flort . --extensions py,md --outline --exclude-patterns '*test*'"
    ```

Ready to become a Flort power user? Check out the [complete usage guide](usage.md)!