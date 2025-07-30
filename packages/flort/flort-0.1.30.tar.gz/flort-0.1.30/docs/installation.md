# Installation Guide

This guide covers all installation methods and platform-specific requirements for Flort.

## 📦 Quick Installation

### From PyPI (Recommended)

=== "Standard Installation"

    ```bash
    # Install latest stable version
    pip install flort
    
    # Verify installation
    flort --version
    ```

=== "With UI Support"

    ```bash
    # Install with interactive UI support
    pip install flort[ui]
    
    # On Windows specifically
    pip install flort windows-curses
    ```

=== "Development Version"

    ```bash
    # Install latest from GitHub
    pip install git+https://github.com/watkinslabs/flort.git
    ```

## 🖥️ Platform-Specific Instructions

### Linux

=== "Ubuntu/Debian"

    ```bash
    # Update package list
    sudo apt update
    
    # Install Python and pip (if needed)
    sudo apt install python3 python3-pip
    
    # Install Flort
    pip3 install flort
    
    # For development (optional)
    sudo apt install python3-dev libncurses5-dev
    ```

=== "CentOS/RHEL/Fedora"

    ```bash
    # Fedora
    sudo dnf install python3 python3-pip
    
    # CentOS/RHEL
    sudo yum install python3 python3-pip
    
    # Install Flort
    pip3 install flort
    
    # Development headers (optional)
    sudo dnf install python3-devel ncurses-devel
    ```

=== "Arch Linux"

    ```bash
    # Install Python and pip
    sudo pacman -S python python-pip
    
    # Install Flort
    pip install flort
    ```

### macOS

=== "Homebrew"

    ```bash
    # Install Python via Homebrew
    brew install python3
    
    # Install Flort
    pip3 install flort
    ```

=== "MacPorts"

    ```bash
    # Install Python via MacPorts
    sudo port install python39 +universal
    
    # Install Flort
    pip3 install flort
    ```

=== "System Python"

    ```bash
    # Use system Python (not recommended)
    pip3 install --user flort
    
    # Add to PATH if needed
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    ```

### Windows

=== "Standard"

    ```bash
    # Using pip
    pip install flort
    
    # For interactive UI
    pip install windows-curses
    
    # Or install everything
    pip install flort[ui]
    ```

=== "PowerShell"

    ```powershell
    # Using PowerShell
    python -m pip install flort
    
    # With UI support
    python -m pip install flort[ui]
    ```

=== "Command Prompt"

    ```cmd
    # Using cmd
    py -m pip install flort
    
    # Verify installation
    flort --version
    ```

## 🐍 Python Version Requirements

!!! info "Python Compatibility"
    Flort supports Python 3.6+ on all platforms.

### Checking Python Version

```bash
# Check Python version
python --version
# or
python3 --version

# Check pip version
pip --version
```

### Python Installation

If you don't have Python installed:

=== "Linux"

    ```bash
    # Ubuntu/Debian
    sudo apt install python3 python3-pip
    
    # Fedora
    sudo dnf install python3 python3-pip
    ```

=== "macOS"

    ```bash
    # Download from python.org or use Homebrew
    brew install python3
    ```

=== "Windows"

    Download from [python.org](https://python.org) and ensure "Add to PATH" is checked during installation.

## 🔧 Virtual Environment Setup

!!! tip "Recommended Approach"
    Always use virtual environments to avoid dependency conflicts.

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv flort-env

# Activate (Linux/macOS)
source flort-env/bin/activate

# Activate (Windows)
flort-env\Scripts\activate

# Install Flort
pip install flort

# Deactivate when done
deactivate
```

### Using conda

```bash
# Create conda environment
conda create -n flort python=3.9

# Activate environment
conda activate flort

# Install Flort
pip install flort

# Deactivate
conda deactivate
```

### Using pipenv

```bash
# Install pipenv (if needed)
pip install pipenv

# Create environment and install
pipenv install flort

# Activate shell
pipenv shell

# Run Flort
flort --help
```

## 🛠️ Development Installation

### Clone and Install

```bash
# Clone repository
git clone https://github.com/watkinslabs/flort.git
cd flort

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

### Development Dependencies

```bash
# Testing tools
pip install pytest pytest-cov

# Code quality
pip install black flake8 isort mypy

# Documentation
pip install -r docs/requirements.txt

# All development tools
pip install -e .[dev,docs]
```

## 📱 Interactive UI Support

### Linux/macOS

Usually included with Python:

```bash
# Test curses availability
python -c "import curses; print('✅ Curses available')"

# If missing, install development packages
# Ubuntu/Debian
sudo apt install python3-dev libncurses5-dev

# Fedora
sudo dnf install python3-devel ncurses-devel
```

### Windows

Requires additional package:

```bash
# Install curses support for Windows
pip install windows-curses

# Test installation
python -c "import curses; print('✅ Curses available')"

# Or install Flort with UI support
pip install flort[ui]
```

## ✅ Verification

### Basic Installation Check

```bash
# Check version
flort --version

# Display help
flort --help

# Test basic functionality
flort . --extensions txt --manifest --max-depth 1
```

### Interactive UI Check

```bash
# Test curses support
python -c "
try:
    import curses
    print('✅ Interactive UI supported')
except ImportError:
    print('❌ Interactive UI not available')
"

# Test Flort UI (exit with 'q')
flort --ui
```

### Full Feature Test

```bash
# Create test directory
mkdir flort-test
cd flort-test

# Create test files
echo "print('hello')" > test.py
echo "# Test Project" > README.md

# Test all major features
flort . --extensions py,md --outline --output test.txt

# Check output
cat test.txt

# Cleanup
cd ..
rm -rf flort-test
```

## 🚨 Troubleshooting

### Common Issues

#### Permission Errors

```bash
# Use --user flag
pip install --user flort

# Or create virtual environment
python -m venv venv
source venv/bin/activate
pip install flort
```

#### Command Not Found

```bash
# Check if pip installed to user directory
python -m pip show flort

# Add to PATH (Linux/macOS)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Windows: Add Python Scripts folder to PATH
```

#### Import Errors

```bash
# Reinstall in clean environment
pip uninstall flort
pip install flort

# Check Python path
python -c "import sys; print(sys.path)"
```

#### UI Not Working

```bash
# Windows: Install curses support
pip install windows-curses

# Linux: Install development packages
sudo apt install python3-dev libncurses5-dev

# Test fallback mode
flort . --extensions py  # Skip --ui flag
```

### Platform-Specific Issues

#### macOS

```bash
# If using system Python and getting SSL errors
/Applications/Python\ 3.x/Install\ Certificates.command

# If pip is outdated
python -m pip install --upgrade pip
```

#### Windows

```bash
# If getting "Microsoft Visual C++ required" error
# Download and install Microsoft C++ Build Tools

# If Python is not in PATH
py -m pip install flort
```

#### Linux

```bash
# If getting "No module named _curses"
sudo apt install python3-dev libncurses5-dev

# If pip install fails with permissions
pip install --user flort
```

## 🔄 Updating

### Update to Latest Version

```bash
# Update from PyPI
pip install --upgrade flort

# Update development installation
cd flort
git pull
pip install -e .
```

### Check for Updates

```bash
# Check current version
flort --version

# Check available versions
pip index versions flort
```

## 🗑️ Uninstallation

### Remove Flort

```bash
# Uninstall Flort
pip uninstall flort

# Remove configuration (if any)
rm -rf ~/.flort

# Remove virtual environment
rm -rf flort-env
```

### Clean Installation

```bash
# Completely clean install
pip uninstall flort
pip cache purge
pip install flort
```

## 📞 Getting Help

If you encounter issues:

1. **Check the logs**: Run with `--verbose` flag
2. **Search issues**: [GitHub Issues](https://github.com/watkinslabs/flort/issues)
3. **Ask questions**: [GitHub Discussions](https://github.com/watkinslabs/flort/discussions)
4. **Report bugs**: Use our [bug report template](https://github.com/watkinslabs/flort/issues/new?template=bug_report.yml)

## 🎯 Next Steps

After successful installation:

1. **[Quick Start Guide](quickstart.md)** - Get running in 5 minutes
2. **[Usage Guide](usage.md)** - Learn all command options
3. **[Examples](examples.md)** - See real-world use cases
4. **[Interactive UI Guide](ui-guide.md)** - Master the visual interface

---

**Installation complete! Ready to start using Flort? 🚀**