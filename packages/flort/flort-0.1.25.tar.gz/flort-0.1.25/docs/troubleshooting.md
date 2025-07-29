# Troubleshooting Guide

Common issues and solutions when using Flort. This guide helps you diagnose and fix problems quickly.

## 🚨 Common Error Messages

### "No files found matching criteria"

**Symptoms:**
```
No files found matching the specified criteria.
```

**Causes & Solutions:**

=== "Wrong Extensions"
    ```bash
    # ❌ Problem: Extensions with dots
    flort . --extensions .py,.js
    
    # ✅ Solution: No dots in extensions
    flort . --extensions py,js
    ```

=== "Too Restrictive Filters"
    ```bash
    # ❌ Problem: Conflicting filters
    flort . --extensions py --exclude-patterns "*.py"
    
    # ✅ Solution: Check filter logic
    flort . --extensions py --exclude-patterns "*test*.py"
    ```

=== "Wrong Directory"
    ```bash
    # ❌ Problem: Empty or wrong directory
    flort /nonexistent/path --extensions py
    
    # ✅ Solution: Verify directory exists and has files
    ls -la /path/to/project
    flort /correct/path --extensions py
    ```

### "Permission denied"

**Symptoms:**
```
❌ Directory is not readable: /protected/path
❌ Failed to read file: permission denied
```

**Solutions:**

```bash
# Check permissions
ls -la /path/to/check

# Fix directory permissions
chmod 755 /path/to/directory

# Fix file permissions
chmod 644 /path/to/file

# Run with appropriate user
sudo flort /protected/path --extensions py

# Skip problematic directories
flort . --extensions py --ignore-dirs "protected_folder"
```

### "Command not found: flort"

**Symptoms:**
```bash
$ flort --version
bash: flort: command not found
```

**Solutions:**

=== "Installation Issue"
    ```bash
    # Reinstall Flort
    pip install flort
    
    # Check installation
    python -m pip show flort
    ```

=== "PATH Issue"
    ```bash
    # Use Python module directly
    python -m flort . --extensions py
    
    # Add to PATH (Linux/macOS)
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    
    # Windows: Add Python Scripts to PATH
    ```

=== "Virtual Environment"
    ```bash
    # Activate virtual environment
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows
    
    # Then use flort
    flort . --extensions py
    ```

## 🖥️ Interactive UI Issues

### UI Won't Start

**Error:**
```
❌ UI failed to start: No module named '_curses'
```

**Solutions:**

=== "Windows"
    ```bash
    # Install curses support
    pip install windows-curses
    
    # Or reinstall with UI support
    pip install flort[ui]
    ```

=== "Linux"
    ```bash
    # Install development packages
    sudo apt install python3-dev libncurses5-dev  # Ubuntu/Debian
    sudo dnf install python3-devel ncurses-devel  # Fedora
    
    # Reinstall Python if needed
    sudo apt install python3-full
    ```

=== "macOS"
    ```bash
    # Usually works, but if not:
    brew install python3
    
    # Or use system Python
    python3 -m pip install flort
    ```

### UI Display Issues

**Problems:**
- Garbled text
- Missing colors
- Mouse not working

**Solutions:**

```bash
# Check terminal compatibility
echo $TERM

# Set terminal type
export TERM=xterm-256color

# Disable mouse if problematic
# (Use keyboard navigation only)

# Try different terminal
# - Linux: gnome-terminal, konsole, xterm
# - macOS: Terminal.app, iTerm2
# - Windows: Windows Terminal, PowerShell
```

### UI Performance Issues

**Symptoms:**
- Slow navigation
- UI freezes
- High memory usage

**Solutions:**

```bash
# Reduce scope
flort . --ui --max-depth 2 --ignore-dirs "large_folder"

# Use specific extensions
flort . --ui --extensions py,js

# Avoid very large directories
flort . --ui --ignore-dirs "node_modules,venv,.git"
```

## 📁 File Processing Issues

### Binary Files Included

**Problem:**
Output contains unreadable binary content.

**Solutions:**

```bash
# Exclude binary files (default behavior)
flort . --extensions py --output project.txt

# If needed, explicitly exclude binary extensions
flort . --all --exclude-extensions exe,dll,so,pyc,bin

# Check file types before processing
flort . --all --manifest --output file_list.txt
```

### Large Output Files

**Symptoms:**
- Very large output files
- Running out of disk space
- Slow processing

**Solutions:**

```bash
# Use manifest mode first
flort . --all --manifest --output preview.txt

# Limit file types
flort . --extensions py,md --output smaller.txt

# Exclude large directories
flort . --extensions py --ignore-dirs "data,logs,cache"

# Use max depth
flort . --extensions py --max-depth 3

# Skip file contents
flort . --extensions py --no-dump --output structure_only.txt
```

### Encoding Issues

**Symptoms:**
- Strange characters in output
- "UnicodeDecodeError"
- Corrupted text

**Solutions:**

```bash
# Check file encodings
file -i suspicious_file.py

# Use verbose mode to identify problematic files
flort . --extensions py --verbose

# Skip problematic files
flort . --extensions py --exclude-patterns "*problematic*"

# Force processing (Flort handles encoding automatically)
# Files are read with error replacement
```

## ⚡ Performance Issues

### Slow Processing

**Symptoms:**
- Takes very long to complete
- High CPU usage
- System becomes unresponsive

**Diagnosis:**

```bash
# Use verbose mode to see what's happening
flort . --extensions py --verbose

# Test with limited scope
flort . --extensions py --max-depth 1

# Check directory sizes
du -sh */ | sort -hr
```

**Solutions:**

```bash
# Ignore large directories early
flort . --extensions py --ignore-dirs "venv,node_modules,.git,data"

# Use specific directories
flort src/ tests/ --extensions py

# Limit depth
flort . --extensions py --max-depth 3

# Use manifest mode for preview
flort . --extensions py --manifest
```

### Memory Issues

**Symptoms:**
- "Out of memory" errors
- System swap usage high
- Process killed

**Solutions:**

```bash
# Process directories separately
flort src/ --extensions py --output src.txt
flort tests/ --extensions py --output tests.txt

# Skip content concatenation
flort . --extensions py --no-dump

# Use manifest mode
flort . --extensions py --manifest

# Limit file count
flort . --extensions py --max-depth 2
```

## 🔧 Configuration Issues

### Invalid Command Line Options

**Error:**
```
❌ Invalid glob pattern 'test[unclosed': missing ]
```

**Solutions:**

```bash
# Check pattern syntax
flort . --glob "test*.py"  # ✅ Valid
flort . --glob "test[123].py"  # ✅ Valid
flort . --glob "test[unclosed"  # ❌ Invalid

# Use exclude-patterns instead
flort . --extensions py --exclude-patterns "*test*"

# Quote complex patterns
flort . --glob "**/*.{py,js}"
```

### Conflicting Options

**Error:**
```
❌ Cannot use both --no-dump and --manifest
```

**Solutions:**

```bash
# Choose one output mode
flort . --extensions py --no-dump      # Tree only
flort . --extensions py --manifest     # File list only
flort . --extensions py                # Full content (default)
```

## 📊 Output Issues

### No Output Generated

**Symptoms:**
- Command completes but no output file
- Empty output file

**Diagnosis:**

```bash
# Check if files were found
flort . --extensions py --manifest --output stdio

# Use verbose mode
flort . --extensions py --verbose

# Check current directory
pwd
ls -la
```

**Solutions:**

```bash
# Verify file extensions exist
find . -name "*.py" | head -5

# Check permissions in output directory
ls -la $(dirname output.txt)

# Use absolute path for output
flort . --extensions py --output /full/path/to/output.txt
```

### Corrupted Output

**Symptoms:**
- Unreadable output file
- Mixed binary and text content

**Solutions:**

```bash
# Exclude binary files
flort . --extensions py,md,txt --output clean.txt

# Check what's being included
flort . --all --manifest --output preview.txt

# Use specific extensions only
flort . --extensions py --output python_only.txt
```

## 🔍 Debugging Techniques

### Enable Verbose Logging

```bash
# See detailed processing information
flort . --extensions py --verbose --output project.txt
```

**What verbose shows:**
- Files being processed
- Files being skipped and why
- Directory scanning progress
- Error details

### Preview Before Processing

```bash
# See what files would be processed
flort . --extensions py --manifest --output preview.txt

# Quick count
flort . --extensions py --manifest --output stdio | wc -l
```

### Incremental Testing

```bash
# Start small
flort . --extensions py --max-depth 1 --output test1.txt

# Add complexity gradually
flort . --extensions py,md --max-depth 2 --output test2.txt

# Add exclusions
flort . --extensions py,md --exclude-patterns "*test*" --output test3.txt
```

### Check System Resources

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Monitor during processing
top -p $(pgrep -f flort)
```

## 🐛 Bug Reporting

### Gather Information

Before reporting a bug, collect:

```bash
# System information
uname -a
python --version
pip show flort

# Reproduction case
flort . --extensions py --verbose 2>&1 | tee flort_debug.log

# File structure
find . -type f -name "*.py" | head -20
```

### Minimal Reproduction

Create the smallest possible example:

```bash
# Create test directory
mkdir flort_bug_test
cd flort_bug_test

# Create minimal files
echo "print('hello')" > test.py
echo "# Test" > README.md

# Test with minimal command
flort . --extensions py --output test.txt

# Report the exact command and error
```

## 📞 Getting Help

### Self-Help Resources

1. **Check this troubleshooting guide**
2. **Try verbose mode**: `--verbose`
3. **Search existing issues**: [GitHub Issues](https://github.com/watkinslabs/flort/issues)
4. **Check documentation**: [Full docs](https://watkinslabs.github.io/flort/)

### Community Support

1. **GitHub Discussions**: Ask questions and share experiences
2. **GitHub Issues**: Report bugs with detailed information
3. **Stack Overflow**: Tag questions with `flort`

### Bug Reports

Use the [bug report template](https://github.com/watkinslabs/flort/issues/new?template=bug_report.yml) and include:

- Flort version (`flort --version`)
- Operating system and Python version
- Exact command used
- Expected vs. actual behavior
- Error messages (with `--verbose`)
- Minimal reproduction case

---

**Most issues can be resolved with proper filtering and configuration. When in doubt, start simple and add complexity gradually! 🔧**

---
