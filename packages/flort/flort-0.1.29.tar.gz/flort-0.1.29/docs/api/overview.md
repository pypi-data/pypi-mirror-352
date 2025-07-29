# API Overview

Flort can be used programmatically as a Python library. This guide covers the main API functions and classes for integrating Flort into your applications.

## 🚀 Quick Start

### Basic Usage

```python
from flort import get_paths, concat_files

# Discover files
file_list = get_paths(
    directories=['.'],
    extensions=['py', 'js'],
    exclude_patterns=['*test*']
)

# Concatenate files
success = concat_files(file_list, 'output.txt')
print(f"Processing {'succeeded' if success else 'failed'}")
```

### Import Structure

```python
# Core functions
from flort import get_paths, concat_files

# Advanced classes
from flort.traverse import FileFilter
from flort.concatenate_files import FileConcatenator

# Utilities
from flort.utils import is_binary_file, count_tokens, generate_tree
from flort.python_outline import process_python_file
```

## 📋 Core Functions

### `get_paths()`

The main file discovery function:

```python
from flort import get_paths

file_list = get_paths(
    directories=['src', 'tests'],           # Directories to scan
    extensions=['py', 'js'],                # File extensions
    exclude_extensions=['pyc', 'min.js'],   # Extensions to exclude
    include_patterns=['*.py'],              # Glob patterns to include
    exclude_patterns=['*test*', '*cache*'], # Glob patterns to exclude
    include_all=False,                      # Include all files
    include_hidden=False,                   # Include hidden files
    include_binary=False,                   # Include binary files
    ignore_dirs=[Path('venv'), Path('.git')], # Directories to ignore
    include_files=['setup.py', 'README.md'], # Specific files to include
    max_depth=None                          # Maximum traversal depth
)
```

**Returns:** List of dictionaries with file information:
```python
[
    {
        'path': Path('/project/main.py'),
        'relative_path': 'main.py',
        'depth': 1,
        'type': 'file'
    },
    # ... more files
]
```

### `concat_files()`

Concatenate discovered files:

```python
from flort import concat_files

success = concat_files(
    file_list,              # List from get_paths()
    output='output.txt',    # Output file path or 'stdio'
    clean_content=True      # Whether to clean whitespace
)
```

## 🔧 Advanced Classes

### `FileFilter`

Fine-grained control over file filtering:

```python
from flort.traverse import FileFilter
from pathlib import Path

# Create filter
file_filter = FileFilter(
    include_extensions=['py', 'js'],
    exclude_extensions=['pyc'],
    include_patterns=['*.py'],
    exclude_patterns=['*test*'],
    include_all=False,
    include_hidden=False,
    include_binary=False,
    ignore_dirs=[Path('venv')]
)

# Test if file should be included
should_include, reason = file_filter.should_include_file(Path('main.py'))
print(f"Include main.py: {should_include} ({reason})")

# Test if directory should be ignored
should_ignore = file_filter.should_ignore_directory(Path('venv'))
print(f"Ignore venv/: {should_ignore}")
```

### `FileConcatenator`

Advanced file concatenation with progress tracking:

```python
from flort.concatenate_files import FileConcatenator

# Create concatenator
concatenator = FileConcatenator(
    output_path='output.txt',
    clean_content_flag=True
)

# Concatenate files
success = concatenator.concatenate_files(file_list)

# Get statistics
stats = concatenator.get_statistics()
print(f"Processed: {stats['files_processed']}")
print(f"Skipped: {stats['files_skipped']}")
print(f"Total characters: {stats['total_characters']}")
print(f"Total tokens: {stats['total_tokens']}")
```

## 🛠️ Utility Functions

### File Operations

```python
from flort.utils import is_binary_file, clean_content, count_tokens

# Check if file is binary
if not is_binary_file(Path('data.png')):
    print("File is text-based")

# Clean file content
cleaned = clean_content(Path('messy_file.py'))

# Count tokens in text
token_count = count_tokens("def hello(): pass")
print(f"Tokens: {token_count}")
```

### Tree Generation

```python
from flort.utils import generate_tree

# Generate directory tree
success = generate_tree(file_list, 'tree_output.txt')
```

### Python Code Analysis

```python
from flort.python_outline import process_python_file

# Extract Python outline
outline = process_python_file(Path('my_module.py'))
print(outline)
```

## 📊 Complete Examples

### Custom File Processor

```python
#!/usr/bin/env python3
"""
Custom Flort integration example
"""

from pathlib import Path
from flort import get_paths, concat_files
from flort.traverse import FileFilter
from flort.utils import count_tokens, is_binary_file

class ProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.file_stats = {}
    
    def analyze_python_project(self):
        """Analyze a Python project and generate reports."""
        
        # Discover Python files
        file_list = get_paths(
            directories=[str(self.project_path)],
            extensions=['py'],
            exclude_patterns=['*test*', '*__pycache__*'],
            ignore_dirs=[self.project_path / 'venv', self.project_path / '.git']
        )
        
        # Generate statistics
        self._calculate_stats(file_list)
        
        # Create outputs
        self._generate_outline(file_list)
        self._generate_full_code(file_list)
        
        return self.file_stats
    
    def _calculate_stats(self, file_list):
        """Calculate project statistics."""
        total_files = 0
        total_lines = 0
        total_tokens = 0
        
        for item in file_list:
            if item['type'] == 'file':
                try:
                    content = item['path'].read_text(encoding='utf-8')
                    lines = len(content.splitlines())
                    tokens = count_tokens(content)
                    
                    total_files += 1
                    total_lines += lines
                    total_tokens += tokens
                    
                except Exception as e:
                    print(f"Error processing {item['path']}: {e}")
        
        self.file_stats = {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_tokens': total_tokens
        }
    
    def _generate_outline(self, file_list):
        """Generate Python code outline."""
        from flort.python_outline import python_outline_files
        
        success = python_outline_files(file_list, 'api_outline.txt')
        print(f"Outline generation: {'success' if success else 'failed'}")
    
    def _generate_full_code(self, file_list):
        """Generate full code concatenation."""
        success = concat_files(file_list, 'full_code.txt', clean_content=True)
        print(f"Code concatenation: {'success' if success else 'failed'}")

# Usage
if __name__ == '__main__':
    analyzer = ProjectAnalyzer('.')
    stats = analyzer.analyze_python_project()
    
    print(f"Project Analysis Results:")
    print(f"  Files: {stats['total_files']}")
    print(f"  Lines: {stats['total_lines']:,}")
    print(f"  Tokens: {stats['total_tokens']:,}")
```

### Flask Integration

```python
from flask import Flask, request, jsonify, send_file
from flort import get_paths, concat_files
import tempfile
import os

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    """API endpoint to analyze uploaded project."""
    
    data = request.json
    project_path = data.get('project_path', '.')
    extensions = data.get('extensions', ['py'])
    exclude_patterns = data.get('exclude_patterns', ['*test*'])
    
    try:
        # Discover files
        file_list = get_paths(
            directories=[project_path],
            extensions=extensions,
            exclude_patterns=exclude_patterns
        )
        
        # Create temporary output
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            success = concat_files(file_list, tmp.name)
            
            if success:
                # Read and return content
                with open(tmp.name, 'r') as f:
                    content = f.read()
                
                os.unlink(tmp.name)
                
                return jsonify({
                    'success': True,
                    'content': content,
                    'file_count': len([f for f in file_list if f['type'] == 'file'])
                })
            else:
                os.unlink(tmp.name)
                return jsonify({'success': False, 'error': 'Concatenation failed'})
                
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
```

### Jupyter Notebook Integration

```python
# Cell 1: Setup
import sys
sys.path.append('.')  # Add current directory to path

from flort import get_paths, concat_files
from flort.utils import count_tokens
import pandas as pd

# Cell 2: Project Analysis
def analyze_project_files(project_path='.', extensions=['py']):
    """Analyze project and return DataFrame of file statistics."""
    
    file_list = get_paths(
        directories=[project_path],
        extensions=extensions,
        exclude_patterns=['*test*', '*cache*']
    )
    
    data = []
    for item in file_list:
        if item['type'] == 'file':
            try:
                content = item['path'].read_text(encoding='utf-8')
                data.append({
                    'file': item['relative_path'],
                    'lines': len(content.splitlines()),
                    'characters': len(content),
                    'tokens': count_tokens(content),
                    'size_kb': item['path'].stat().st_size / 1024
                })
            except Exception as e:
                print(f"Error processing {item['path']}: {e}")
    
    return pd.DataFrame(data)

# Cell 3: Visualization
df = analyze_project_files()
print(f"Project Statistics:")
print(f"Total files: {len(df)}")
print(f"Total lines: {df['lines'].sum():,}")
print(f"Total tokens: {df['tokens'].sum():,}")
print(f"Average file size: {df['size_kb'].mean():.1f} KB")

# Plot file sizes
df.plot(x='file', y='tokens', kind='bar', figsize=(12, 6), title='Token Count by File')
```

## 🔒 Error Handling

```python
from flort import get_paths, concat_files
from flort.validation import ValidationError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def safe_process_project(project_path, output_path):
    """Safely process a project with comprehensive error handling."""
    
    try:
        # Discover files
        file_list = get_paths(
            directories=[project_path],
            extensions=['py', 'js', 'md']
        )
        
        if not file_list:
            logging.warning("No files found matching criteria")
            return False
        
        # Filter to only files (not directories)
        files_only = [f for f in file_list if f['type'] == 'file']
        
        if not files_only:
            logging.warning("No files found, only directories")
            return False
        
        # Concatenate files
        success = concat_files(files_only, output_path)
        
        if success:
            logging.info(f"Successfully processed {len(files_only)} files")
            return True
        else:
            logging.error("File concatenation failed")
            return False
            
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        return False
    except PermissionError as e:
        logging.error(f"Permission error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False

# Usage
result = safe_process_project('.', 'safe_output.txt')
print(f"Processing {'succeeded' if result else 'failed'}")
```

## 📚 API Reference

For detailed API documentation of each function and class, see:

- [Core Functions](core.md) - `get_paths()`, `concat_files()`
- [File Operations](files.md) - File handling and processing
- [Utilities](utils.md) - Helper functions and tools

---

**The Flort API provides powerful programmatic access to all file processing capabilities. Build custom tools and integrations with ease! 🔧**

---
