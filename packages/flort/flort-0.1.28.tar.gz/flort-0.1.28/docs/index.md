# Welcome to Flort
<p align="center">
  <img src="https://raw.githubusercontent.com/watkinslabs/flort/main/assets/flort-logo.png" alt="Flort Logo" width="200">
</p>

<p align="center"><strong>File Concatenation and Project Overview Tool</strong></p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python Version"></a>
  <a href="https://pypi.org/project/flort/"><img src="https://img.shields.io/pypi/v/flort.svg" alt="PyPI Version"></a>
  <a href="https://github.com/watkinslabs/flort/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-BSD--3--Clause-green.svg" alt="License"></a>
    <a href="https://github.com/watkinslabs/flort/actions/workflows/test.yml"><img src="https://github.com/watkinslabs/flort/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
</p>

Flort is a powerful command-line tool designed to create consolidated views of your project's source code by combining multiple files into a single output file. It's perfect for preparing code context for Large Language Models (LLMs), generating documentation, and analyzing project structure.

## ✨ Key Features

!!! tip "Perfect for LLM Workflows"
    Flort was specifically designed to help developers prepare clean, organized code context for AI assistants and large language models.

<div class="grid cards" markdown>

-   :material-magnify: **Intelligent File Discovery**

    ---

    Comprehensive file scanning with advanced include/exclude filtering, pattern matching, and binary file detection.

    [:octicons-arrow-right-24: Learn about filtering](filtering.md)

-   :material-file-tree: **Directory Tree Generation**

    ---

    Visual project structure representation with customizable depth and formatting options.

    [:octicons-arrow-right-24: See output formats](output-formats.md)

-   :fontawesome-brands-python: **Python Code Outline**

    ---

    Extract class and function signatures, docstrings, and type annotations for API documentation.

    [:octicons-arrow-right-24: View examples](examples.md)

-   :material-filter: **Advanced Filtering**

    ---

    Extension-based, pattern-based, and directory-based filtering with support for complex exclusion rules.

    [:octicons-arrow-right-24: Master filtering](filtering.md)

-   :material-counter: **Token Counting**

    ---

    Built-in token analysis for LLM context planning and optimization.

    [:octicons-arrow-right-24: Understand tokens](usage.md#token-counting)

-   :material-archive: **Archive Support**

    ---

    Create ZIP or TAR.GZ archives of your processed output for easy sharing.

    [:octicons-arrow-right-24: Archive options](usage.md#archive-creation)

-   :material-mouse: **Interactive UI**

    ---

    Curses-based file selector with mouse support for visual project exploration.

    [:octicons-arrow-right-24: Try the UI](ui-guide.md)

-   :material-speedometer: **High Performance**

    ---

    Efficient processing of large codebases with memory optimization and progress tracking.

    [:octicons-arrow-right-24: Performance tips](usage.md#performance-optimization)

</div>

## 🚀 Quick Start

=== "Install"

    ```bash
    # Install from PyPI
    pip install flort
    
    # With UI support on Windows
    pip install flort[ui]
    ```

=== "Basic Usage"

    ```bash
    # Process Python files
    flort . --extensions py --output project.txt
    
    # Multiple file types
    flort . --extensions py,js,md --output codebase.txt
    
    # Interactive selection
    flort --ui
    ```

=== "Advanced"

    ```bash
    # Full project analysis
    flort . \
      --extensions py,js,ts,md \
      --exclude-patterns "*test*,*cache*" \
      --outline \
      --archive zip \
      --output analysis.txt
    ```

[Get Started :material-rocket:](quickstart.md){ .md-button .md-button--primary }
[View Examples :material-book-open:](examples.md){ .md-button }

## 🎯 Common Use Cases

### For LLM Context Preparation

Prepare clean, organized code context for AI assistants:

```bash
# Prepare Python project for LLM analysis
flort . --extensions py --exclude-patterns "*test*,*cache*" --outline --output llm_context.txt

# Include documentation and config files  
flort . --extensions py,md,yml,json --exclude-patterns "*test*" --output full_context.txt
```

### For Documentation

Generate comprehensive project overviews:

```bash
# Project structure overview
flort . --extensions py,md --no-dump --output structure.txt

# API documentation outline
flort . --extensions py --outline --no-dump --output api_docs.txt
```

### For Code Review

Package code changes for review:

```bash
# Review specific files
flort . --include-files "file1.py,file2.py,config.json" --archive zip

# Package component for review
flort src/ --extensions py,js --exclude-patterns "*min.js" --archive zip
```

## 🎨 Interactive Experience

Experience Flort's powerful interactive UI:

<div class="highlight">
<pre><code>$ flort --ui

🎯 FLORT FILE SELECTOR
📁 /home/user/project
Filter: .py, .js, .md

📂 src/
  [✓] 📄 main.py
  [✓] 📄 utils.py
  [ ] 📄 config.json
📂 tests/
  [✗] 📄 test_main.py
  [✗] 📄 test_utils.py
📄 README.md [✓]
📄 setup.py [✓]

Selected: 4 | Ignored: 2 | Types: 3
</code></pre>
</div>

**Features:**
- 🖱️ Mouse and keyboard navigation
- 📂 Real-time directory browsing  
- 🎯 File type filtering
- ✅ Visual selection management
- 🔍 Live preview of selections

## 📊 Output Format

Flort generates structured, readable output:

```
## Florted: 2025-06-02 10:30:15
## Directory Tree
project/
├── main.py
├── src/
│   ├── utils.py
│   └── config.py
└── README.md

## Python Code Outline
### File: main.py
FUNCTION: main() -> None
  DOCSTRING: Main entry point

CLASS: Application
  METHOD: __init__(self, config: str)
  METHOD: run(self) -> bool

## File Data
--- File: main.py
--- Characters: 1,234
--- Token Count: 256
[file content here]
```

## 🤝 Community & Support

<div class="grid cards" markdown>

-   :material-github: **GitHub Repository**

    ---

    Source code, issues, and contributions

    [:octicons-arrow-right-24: Visit repository](https://github.com/watkinslabs/flort)

-   :material-bug: **Report Issues**

    ---

    Found a bug? Have a feature request?

    [:octicons-arrow-right-24: Report issue](https://github.com/watkinslabs/flort/issues)

-   :material-chat: **Discussions**

    ---

    Ask questions and share ideas

    [:octicons-arrow-right-24: Join discussions](https://github.com/watkinslabs/flort/discussions)

-   :material-book: **Contributing**

    ---

    Help improve Flort

    [:octicons-arrow-right-24: Contribute](contributing.md)

</div>

## 🎯 Next Steps

Ready to dive deeper? Here's where to go next:

1. **[Installation Guide](installation.md)** - Detailed setup for your platform
2. **[Quick Start](quickstart.md)** - Get up and running in 5 minutes  
3. **[Usage Guide](usage.md)** - Master all command-line options
4. **[Examples](examples.md)** - Real-world use cases and workflows
5. **[API Reference](api/overview.md)** - Programmatic usage

---

<div align="center">
  <strong>Made with ❤️ by <a href="https://github.com/chris17453">Chris Watkins</a></strong>
  
  <em>Flort: Making code consolidation simple and powerful</em>
</div>