# File Filtering Guide

Master Flort's powerful filtering system to precisely control which files are processed. This guide covers all filtering methods from basic extension matching to complex pattern exclusions.

## 🎯 Filtering Overview

Flort uses a multi-stage filtering pipeline:

1. **🔍 Discovery** - Find all files in specified directories
2. **✅ Inclusion** - Apply positive filters (what to include)
3. **❌ Exclusion** - Apply negative filters (what to exclude)  
4. **🚫 Special** - Handle binary files, hidden files, etc.
5. **📄 Output** - Process the final file list

Understanding this pipeline helps you build effective filter combinations.

## 📁 Extension-Based Filtering

### Basic Extension Inclusion

```bash
# Single extension
flort . --extensions py

# Multiple extensions
flort . --extensions py,js,ts

# Common combinations
flort . --extensions py,md,yml,json    # Python project with docs
flort . --extensions js,ts,css,html   # Web project
flort . --extensions java,xml,properties  # Java project
```

!!! tip "Extension Format"
    Always omit the dot: use `py,js,md` not `.py,.js,.md`

### Extension Exclusion

```bash
# Exclude compiled files
flort . --all --exclude-extensions pyc,pyo,class

# Exclude minified files
flort . --extensions js,css --exclude-extensions min.js,min.css

# Exclude temporary files
flort . --all --exclude-extensions tmp,temp,bak,swp
```

### Extension Combinations

```bash
# Include Python, exclude compiled
flort . --extensions py,pyx --exclude-extensions pyc,pyo

# Include all, exclude binaries
flort . --all --exclude-extensions exe,dll,so,dylib,bin

# Web files, exclude minified
flort . --extensions js,css,html --exclude-extensions min.js,min.css
```

## 🌟 Pattern-Based Filtering

### Glob Pattern Syntax

Flort uses standard glob patterns:

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | Any characters | `*.py` matches all Python files |
| `?` | Single character | `test?.py` matches `test1.py`, `testa.py` |
| `**` | Recursive directories | `src/**/*.py` matches Python files in src/ and subdirs |
| `[abc]` | Character set | `test[123].py` matches `test1.py`, `test2.py`, `test3.py` |
| `[!abc]` | Negated set | `test[!0-9].py` matches `testa.py` but not `test1.py` |

### Include Patterns

```bash
# Specific files
flort . --glob "*.py"

# Multiple patterns
flort . --glob "*.py,*.js,*.md"

# Recursive patterns
flort . --glob "src/**/*.py,tests/**/*.py"

# Complex patterns
flort . --glob "**/*test*.py,**/*spec*.js"
```

### Exclude Patterns

```bash
# Exclude test files
flort . --extensions py --exclude-patterns "*test*,*spec*"

# Exclude cache and build
flort . --all --exclude-patterns "*cache*,*build*,*dist*"

# Exclude version control
flort . --all --exclude-patterns "*.git*,*.svn*,*.hg*"

# Exclude temporary files
flort . --all --exclude-patterns "*tmp*,*temp*,*.bak,*.swp"
```

## 📂 Directory Filtering

### Ignoring Directories

```bash
# Common ignore patterns
flort . --extensions py --ignore-dirs "__pycache__,venv,.git"

# Build and dependency directories
flort . --all --ignore-dirs "build,dist,node_modules,vendor"

# Multiple environment directories
flort . --extensions py --ignore-dirs "venv,env,.venv,.env,conda-env"
```

### How Directory Ignoring Works

When a directory is ignored:
- ✅ **Complete exclusion** - Directory and all contents are skipped
- ✅ **Performance benefit** - No time spent scanning ignored directories
- ✅ **Recursive** - Subdirectories are automatically ignored

```bash
# This ignores ALL files in node_modules, even if they match other filters
flort . --all --ignore-dirs "node_modules"
```

## 📄 Specific File Inclusion

### Including Exact Files

```bash
# Specific important files
flort . --include-files "setup.py,README.md,requirements.txt"

# Config files regardless of extension filters
flort . --extensions py --include-files "config.json,settings.yml"

# Mix relative and absolute paths
flort . --include-files "./local.py,/etc/config.conf"
```

### How File Inclusion Works

Specific files **override other filters**:
- ✅ **Always included** - Even if extension doesn't match
- ✅ **Ignore exclusion patterns** - Won't be filtered out
- ⚠️ **Must exist** - Flort will warn about non-existent files

## 🎛️ Special File Types

### Hidden Files

```bash
# Include hidden files and directories
flort . --extensions py --hidden

# Example: includes .env, .gitignore, .bashrc, etc.
flort . --all --hidden --exclude-patterns "*.git/*"
```

### Binary Files

```bash
# Include binary files (normally excluded)
flort . --all --include-binary

# Useful for documentation or analysis
flort . --extensions py --include-binary --include-files "icon.png,data.db"
```

!!! warning "Binary File Caution"
    Binary files can make output unreadable and very large. Use sparingly.

## 🔧 Advanced Filtering Strategies

### Project Type Patterns

=== "Python Project"

    ```bash
    flort . \
      --extensions py,pyx,pyi,md,yml,toml,cfg,ini \
      --exclude-patterns "*test*,*cache*,*__pycache__*" \
      --ignore-dirs "venv,env,.venv,build,dist,.pytest_cache" \
      --include-files "setup.py,pyproject.toml,requirements.txt"
    ```

=== "JavaScript/Node.js"

    ```bash
    flort . \
      --extensions js,ts,json,md,yml \
      --exclude-patterns "*.min.*,*bundle*,*build*,*dist*" \
      --ignore-dirs "node_modules,.npm,build,dist" \
      --include-files "package.json,package-lock.json,.env.example"
    ```

=== "Java Project"

    ```bash
    flort . \
      --extensions java,xml,properties,md \
      --exclude-patterns "*test*,*Test*" \
      --ignore-dirs "target,build,.gradle,out" \
      --include-files "pom.xml,build.gradle,gradle.properties"
    ```

=== "Web Development"

    ```bash
    flort . \
      --extensions html,css,js,ts,scss,less,md \
      --exclude-patterns "*.min.*,*bundle*,*vendor*" \
      --ignore-dirs "node_modules,dist,build,.cache" \
      --include-files "index.html,webpack.config.js,package.json"
    ```

### Documentation Projects

```bash
# Documentation files only
flort . \
  --extensions md,rst,txt,adoc \
  --include-files "README.md,CHANGELOG.md,LICENSE,CONTRIBUTING.md" \
  --ignore-dirs ".git,node_modules,venv"

# Include code examples in docs
flort docs/ examples/ \
  --extensions md,py,js,yml \
  --exclude-patterns "*build*,*cache*"
```

### LLM Context Preparation

```bash
# Clean code context for AI
flort . \
  --extensions py,md \
  --exclude-patterns "*test*,*spec*,*cache*,*__pycache__*,*.pyc" \
  --ignore-dirs "venv,.git,build,dist,.pytest_cache" \
  --max-depth 3 \
  --outline
```

## 🧪 Testing and Debugging Filters

### Preview Mode

```bash
# See what files would be processed
flort . --extensions py --manifest --output file_list.txt

# Quick preview to stdout
flort . --extensions py --manifest --output stdio
```

### Verbose Analysis

```bash
# See detailed filtering decisions
flort . --extensions py --verbose --output project.txt
```

Verbose output shows:
```
DEBUG - Including file: main.py (passed all filters)
DEBUG - Excluding file: test_main.py (matches exclude pattern '*test*')
DEBUG - Ignoring directory: __pycache__ (in ignore list)
```

### Incremental Testing

```bash
# Start simple
flort . --extensions py --max-depth 1 --manifest

# Add complexity gradually  
flort . --extensions py,md --max-depth 2 --manifest

# Add exclusions
flort . --extensions py,md --exclude-patterns "*test*" --manifest

# Final test
flort . --extensions py,md --exclude-patterns "*test*" --output final.txt
```

## ⚡ Performance Optimization

### Directory-Level Optimization

```bash
# Ignore large directories early (faster)
flort . --extensions py --ignore-dirs "venv,node_modules,.git"

# vs. pattern exclusion (slower)
flort . --extensions py --exclude-patterns "*venv*,*node_modules*"
```

### Depth Limiting

```bash
# Limit traversal depth for faster scanning
flort . --extensions py --max-depth 3

# Combine with ignore-dirs for best performance
flort . --extensions py --max-depth 3 --ignore-dirs "venv,build"
```

### Extension vs. Pattern Performance

```bash
# Faster: specific extensions
flort . --extensions py,js,md

# Slower: broad patterns
flort . --glob "**/*.py,**/*.js,**/*.md"

# Slowest: include-all with exclusions
flort . --all --exclude-patterns "*exe,*dll,*so"
```

## 🎨 Filter Combinations

### Layered Filtering

```bash
# Layer 1: Basic inclusion
flort . --extensions py,js,md \
# Layer 2: Pattern exclusion
  --exclude-patterns "*test*,*spec*,*cache*" \
# Layer 3: Directory exclusion  
  --ignore-dirs "venv,node_modules,.git" \
# Layer 4: Specific additions
  --include-files "important_config.json"
```

### Complex Real-World Example

```bash
# Comprehensive Django project filtering
flort . \
  --extensions py,html,css,js,md,yml,json \
  --exclude-patterns "*test*,*migration*,*cache*,*.min.*" \
  --ignore-dirs "venv,env,node_modules,staticfiles,media,.git" \
  --include-files "manage.py,requirements.txt,docker-compose.yml,.env.example" \
  --max-depth 4 \
  --outline
```

## 🔍 Common Filtering Scenarios

### Code Review

```bash
# Only changed files
flort . --include-files "$(git diff --name-only HEAD~1)"

# Specific component
flort src/auth/ --extensions py,html,js --exclude-patterns "*test*"
```

### Documentation Generation

```bash
# API documentation
flort . --extensions py --outline --exclude-patterns "*test*,*migration*"

# Full project docs
flort . --extensions py,md,rst --include-files "README.md,CHANGELOG.md"
```

### Security Audit

```bash
# Configuration and code files
flort . \
  --extensions py,js,json,yml,env,conf,cfg \
  --include-files ".env.example,docker-compose.yml" \
  --exclude-patterns "*test*,*cache*"
```

### Package Distribution

```bash
# Source distribution
flort . \
  --extensions py,md,txt,cfg,ini,toml \
  --include-files "setup.py,MANIFEST.in,LICENSE" \
  --ignore-dirs "build,dist,*.egg-info,.git"
```

## 📊 Filter Decision Matrix

| Need | Use | Example |
|------|-----|---------|
| **Specific file types** | `--extensions` | `--extensions py,js` |
| **Exclude file types** | `--exclude-extensions` | `--exclude-extensions pyc,min.js` |
| **Complex patterns** | `--glob` / `--exclude-patterns` | `--exclude-patterns "*test*"` |
| **Skip directories** | `--ignore-dirs` | `--ignore-dirs "venv,.git"` |
| **Important files** | `--include-files` | `--include-files "setup.py"` |
| **Hidden files** | `--hidden` | `--hidden` |
| **All files** | `--all` | `--all --exclude-extensions exe` |
| **Limit scope** | `--max-depth` | `--max-depth 2` |

## 🎯 Best Practices

### ✅ Do's

- **Start specific, then broaden** - Begin with exact extensions, add as needed
- **Use `--ignore-dirs` for performance** - Skip large directories early
- **Test with `--manifest` first** - Preview before processing
- **Combine multiple methods** - Use extensions + patterns + ignore-dirs
- **Use `--verbose` for debugging** - Understand why files are included/excluded

### ❌ Don'ts

- **Don't use overly broad patterns** - `--all` with many exclusions is slow
- **Don't ignore performance** - Use directory ignoring vs. pattern matching
- **Don't forget hidden files** - Add `--hidden` if you need config files
- **Don't mix up inclusion/exclusion** - Remember: include-files overrides other filters

---

**Master these filtering techniques and you'll have precise control over what Flort processes! 🎯**

Next: [Output Formats Guide](output-formats.md) to learn how to customize your results.