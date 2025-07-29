'''
Flort - File Concatenation and Project Overview Tool

A comprehensive tool for creating consolidated views of project source code
by combining multiple files into a single output file with intelligent filtering,
directory tree generation, and Python code outline capabilities.

Key Features:
- Comprehensive file discovery with include/exclude filtering
- Extension-based and pattern-based file filtering
- Binary file detection and exclusion
- Directory tree generation
- Python code outline generation
- File concatenation with metadata
- Archive creation support
- Interactive UI for file selection (requires curses)

This package provides both a command-line interface and a programmatic API
for processing project files.

Example CLI usage:
    flort . --extensions py,js --exclude-patterns '*test*' --output project.txt

Example programmatic usage:
    from flort import get_paths, concat_files
    
    file_list = get_paths(
        directories=['.'],
        extensions=['py', 'js'],
        exclude_patterns=['*test*']
    )
    concat_files(file_list, 'output.txt')

Interactive UI usage:
    flort --ui --extensions py,js
    
    Note: Interactive UI requires the curses module:
    - On Linux/macOS: included with Python
    - On Windows: pip install windows-curses
'''

from pathlib import Path
from .traverse import get_paths, FileFilter, scan_directories, add_specific_files
from .concatenate_files import concat_files, create_file_manifest, FileConcatenator
from .utils import (
    is_binary_file, clean_content, write_file, count_tokens,
    generate_tree, archive_file, configure_logging

)
from .validation import  ValidationError, ValidationResult
from .cli import main


def get_version():
    """Get version from VERSION file."""
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "2.0.0"

__version__ = get_version()
__author__ = 'Chris Watkins'
__email__ = 'chris@watkinslabs.com'
__description__ = 'A utility to flatten your source code directory into a single file for LLM usage'

# Public API exports
__all__ = [
    # Main entry points
    'main',
    'get_paths',
    'concat_files',
    
    # Core classes
    'FileFilter',
    'FileConcatenator',
    'ValidationError', 
    'ValidationResult',    
    
    # Utility functions
    'is_binary_file',
    'clean_content',
    'write_file',
    'count_tokens',
    'generate_tree',
    'archive_file',
    'configure_logging',
    
    # Advanced functions
    'scan_directories',
    'add_specific_files',
    'create_file_manifest',
    
    # Metadata
    '__version__',
    '__author__',
    '__email__',
    '__description__'
]