"""
File Utilities Module

This module provides utility functions for file operations including:
- Binary file detection
- Content cleaning
- File writing
- Directory tree generation
- Token counting
- Archive creation

These utilities support the core functionality of the file processing system
while handling errors gracefully and providing appropriate logging.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import zipfile
import tarfile
import logging


def is_binary_file(file_path: Path) -> bool:
    """
    Determine if a file is binary by examining its contents.

    Args:
        file_path (Path): Path to the file to check

    Returns:
        bool: True if the file appears to be binary, False otherwise

    The function uses multiple methods to detect binary files:
    1. Checks for null bytes in the first 8192 bytes
    2. Looks for non-text characters outside the ASCII printable range
    3. Checks file extensions for known binary types

    Note:
        - Returns True on any error, assuming binary to be safe
        - Only reads the first 8KB for efficiency
        - Uses both content and extension-based detection
    """
    try:
        # Check common binary extensions first
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o', '.a', '.lib',
            '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.wav',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pyc', '.pyo', '.pyd', '.class', '.jar'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return True
            
        # Check file content
        with open(file_path, 'rb') as file:
            # Read larger chunk for better detection
            chunk = file.read(8192)
            
            if not chunk:
                return False
                
            # Quick check for null bytes
            if b'\x00' in chunk:
                return True
                
            # Check for high percentage of non-text characters
            text_characters = bytes(range(32, 127)) + b'\n\r\t\f\b'
            non_text_count = len(chunk.translate(None, text_characters))
            
            # If more than 30% non-text characters, consider binary
            return (non_text_count / len(chunk)) > 0.3
            
    except Exception as e:
        logging.debug(f"Error determining if file is binary {file_path}: {e}")
        return True


def clean_content(file_path: Path) -> str:
    """
    Clean up file content by removing unnecessary whitespace while preserving structure.

    Args:
        file_path (Path): Path to the file to clean

    Returns:
        str: Cleaned content with normalized whitespace

    The function:
    1. Reads all lines from the file
    2. Preserves leading whitespace for indentation
    3. Strips trailing whitespace only
    4. Preserves empty lines that separate code blocks
    5. Removes excessive consecutive empty lines (max 2)

    Note:
        - Preserves code structure and indentation
        - Removes trailing whitespace
        - Limits consecutive empty lines to 2
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()
            
        cleaned_lines = []
        consecutive_empty = 0
        
        for line in lines:
            # Strip only trailing whitespace, preserve leading
            cleaned_line = line.rstrip()
            
            if not cleaned_line:
                consecutive_empty += 1
                # Allow max 2 consecutive empty lines
                if consecutive_empty <= 2:
                    cleaned_lines.append('')
            else:
                consecutive_empty = 0
                cleaned_lines.append(cleaned_line)
                
        # Remove trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
        
    except Exception as e:
        logging.error(f"Error cleaning content from {file_path}: {e}")
        return ""


def write_file(file_path: str, data: str, mode: str = 'a') -> bool:
    """
    Write data to a file or output to console.

    Args:
        file_path (str): Path to output file or "stdio" for console output
        data (str): Content to write
        mode (str, optional): File opening mode ('w' for write, 'a' for append).
            Defaults to 'a'.

    Returns:
        bool: True if write was successful, False otherwise

    The function handles two output modes:
    1. File output: Writes to the specified file path
    2. Console output: Prints to stdout if file_path is "stdio"

    Error handling:
    - IOError: Logged with specific error message
    - Other exceptions: Logged with generic error message

    Note:
        - Creates parent directories if they don't exist
        - Returns success status for error handling
        - Handles both creation and append operations
    """
    try:
        if file_path == "stdio":
            print(data, end='')
            return True
        else:
            # Create parent directories if they don't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as file:
                file.write(data)
            
            operation = 'create' if mode == 'w' else 'append'
            logging.debug(f"Output written to: {file_path}. Mode: {operation}.")
            return True
            
    except IOError as e:
        logging.error(f"Failed to write to {file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while writing to {file_path}: {e}")
        return False


def configure_logging(verbose: bool) -> None:
    """
    Configure the logging system based on the verbosity level.

    Args:
        verbose (bool): If True, sets logging level to INFO;
                       if False, sets it to WARNING.

    The logging format includes timestamp, level, and message:
        2024-01-02 12:34:56 - INFO - Sample message
    """
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True  # Override any existing configuration
    )


def count_tokens(text: str) -> int:
    """
    Count tokens in text using a robust tokenization strategy.
    
    Args:
        text (str): Text to tokenize
        
    Returns:
        int: Number of tokens
        
    Uses a combination of regex patterns to identify:
    - Words (including contractions)
    - Numbers (including decimals and percentages)
    - Punctuation marks
    - Special symbols
    - Code-specific tokens (operators, brackets, etc.)
    """
    if not text:
        return 0
        
    # Enhanced pattern for better code tokenization
    patterns = [
        r'\b[A-Za-z_][A-Za-z0-9_]*\b',  # Identifiers/words
        r'\b\d+\.?\d*%?\b',             # Numbers and percentages
        r'[+\-*/=<>!&|^~]+=?',          # Operators
        r'[(){}\[\]]',                   # Brackets
        r'[.,;:]',                       # Punctuation
        r'[\'"`]',                       # Quotes
        r'[@#$%\\]',                     # Special symbols
        r'\s+',                          # Whitespace (will be filtered)
    ]
    
    combined_pattern = '|'.join(f'({pattern})' for pattern in patterns)
    tokens = re.findall(combined_pattern, text)
    
    # Filter out whitespace tokens and count non-empty matches
    non_whitespace_tokens = []
    for token_groups in tokens:
        for token in token_groups:
            if token and not token.isspace():
                non_whitespace_tokens.append(token)
                break
    
    return len(non_whitespace_tokens)


def count_file_tokens(filename: str) -> str:
    """
    Count tokens and characters in a file.
    
    Args:
        filename (str): Path to file to analyze
        
    Returns:
        str: Formatted string with token and character counts
    """
    try:
        if filename == "stdio":
            return "Token counting not available for stdio output"
            
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        token_count = count_tokens(text)
        char_count = len(text)
        line_count = text.count('\n') + (1 if text and not text.endswith('\n') else 0)
        
        return f"Lines: {line_count:,}\nTokens: {token_count:,}\nCharacters: {char_count:,}"
        
    except Exception as e:
        logging.error(f"Error counting tokens in {filename}: {e}")
        return f"Error counting tokens: {str(e)}"


def print_configuration(
    directories: list,
    extensions: list,
    exclude_extensions: list = None,
    exclude_patterns: list = None,
    include_all: bool = False,
    include_hidden: bool = False,
    ignore_dirs: list = None,
    include_files: list = None,
    glob_patterns: list = None
) -> None:
    """
    Log the current configuration settings for the file processing operation.

    Args:
        directories (list): List of directory paths to process
        extensions (list): List of file extensions to include
        exclude_extensions (list): List of file extensions to exclude
        exclude_patterns (list): List of glob patterns to exclude
        include_all (bool): Whether to include all file types
        include_hidden (bool): Whether to include hidden files
        ignore_dirs (list, optional): List of directories to ignore
        include_files (list, optional): List of specific files to include
        glob_patterns (list, optional): List of glob patterns to include

    This function provides visibility into the tool's configuration,
    which is particularly useful for debugging and verification.
    """
    logging.info("=== Flort Configuration ===")
    logging.info(f"Directories: {', '.join(directories)}")
    
    if extensions:
        logging.info(f"Include extensions: {', '.join(extensions)}")
    if exclude_extensions:
        logging.info(f"Exclude extensions: {', '.join(exclude_extensions)}")
    if glob_patterns:
        logging.info(f"Include patterns: {', '.join(glob_patterns)}")
    if exclude_patterns:
        logging.info(f"Exclude patterns: {', '.join(exclude_patterns)}")
    if include_files:
        logging.info(f"Include files: {', '.join(include_files)}")
    
    logging.info(f"Include all files: {include_all}")
    logging.info(f"Include hidden files: {include_hidden}")
    
    if ignore_dirs:
        logging.info(f"Ignore directories: {', '.join([str(d) for d in ignore_dirs])}")
    
    logging.info("=== End Configuration ===")


def archive_file(file_path: str, archive_format: str) -> str:
    """
    Archive a file using the specified format.
    
    Args:
        file_path (str): Path to the file to archive
        archive_format (str): 'zip' or 'tar.gz'
        
    Returns:
        str: Path to the created archive file, or None if failed
    """
    input_path = Path(file_path)
    
    if not input_path.exists():
        logging.error(f"File to archive does not exist: {file_path}")
        return None
    
    try:
        if archive_format == 'zip':
            archive_path = f"{file_path}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                zipf.write(file_path, arcname=input_path.name)
            
        elif archive_format == 'tar.gz':
            archive_path = f"{file_path}.tar.gz"
            with tarfile.open(archive_path, "w:gz", compresslevel=6) as tar:
                tar.add(file_path, arcname=input_path.name)
        else:
            logging.error(f"Unsupported archive format: {archive_format}. Must be 'zip' or 'tar.gz'")
            return None
        
        logging.info(f"Created archive: {archive_path}")
        return archive_path
        
    except Exception as e:
        logging.error(f"Error creating archive: {e}")
        return None


def generate_tree(path_list: list, output: str) -> bool:
    """
    Generate a hierarchical tree structure from a list of paths.
    
    Args:
        path_list (list): List of path dictionaries with 'path', 'relative_path', 'type' keys
        output (str): Output file path or "stdio"
        
    Returns:
        bool: True if tree generation was successful
    """
    if not path_list:
        return write_file(output, "## Directory Tree\n(No files found)\n\n")
    
    # Write header
    if not write_file(output, "## Directory Tree\n"):
        return False
    
    # Build a simple tree structure using a dict
    tree = {}
    
    # Add all paths to the tree
    for item in path_list:
        rel_path = item["relative_path"]
        item_type = item["type"]
        
        # Normalize the path - remove leading ./ 
        if rel_path.startswith('./'):
            rel_path = rel_path[2:]
        
        # Skip empty paths or current directory
        if not rel_path or rel_path == '.':
            continue
            
        # Split path into parts
        parts = rel_path.split('/')
        
        # Navigate/create the tree structure
        current = tree
        for i, part in enumerate(parts):
            if part not in current:
                current[part] = {}
            
            # If this is the last part, mark if it's a file
            if i == len(parts) - 1 and item_type == "file":
                current[part]["__is_file__"] = True
            else:
                current = current[part]
    
    # Function to recursively print the tree
    def print_tree_recursive(node, prefix="", is_last=True):
        items = [(k, v) for k, v in node.items() if k != "__is_file__"]
        items.sort(key=lambda x: (x[1].get("__is_file__", False), x[0].lower()))
        
        for i, (name, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            
            # Determine the connector
            if prefix == "":  # Root level
                connector = "├── " if not is_last_item else "└── "
            else:
                connector = "├── " if not is_last_item else "└── "
            
            # Determine if this is a file or directory
            is_file = subtree.get("__is_file__", False)
            display_name = name if is_file else name + "/"
            
            # Write the line
            line = f"{prefix}{connector}{display_name}\n"
            if not write_file(output, line):
                return False
            
            # Recurse for directories
            if not is_file and subtree:
                # Determine the new prefix
                if prefix == "":  # Root level
                    new_prefix = "│   " if not is_last_item else "    "
                else:
                    new_prefix = prefix + ("│   " if not is_last_item else "    ")
                
                if not print_tree_recursive(subtree, new_prefix, is_last_item):
                    return False
        
        return True
    
    # Get the current directory name for the root
    cwd = Path.cwd()
    root_name = cwd.name
    
    # Print root directory name
    if not write_file(output, f"{root_name}/\n"):
        return False
    
    # Print the tree
    if not print_tree_recursive(tree):
        return False
    
    return write_file(output, "\n")


def validate_file_path(file_path: Path) -> tuple[bool, str]:
    """
    Validate if a file path is accessible and readable.
    
    Args:
        file_path (Path): Path to validate
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    try:
        if not file_path.exists():
            return False, "File does not exist"
            
        if not file_path.is_file():
            return False, "Path is not a file"
            
        # Test readability
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            f.read(1)  # Try to read one character
            
        return True, ""
        
    except PermissionError:
        return False, "Permission denied"
    except Exception as e:
        return False, f"Error accessing file: {str(e)}"


def sanitize_output_path(output_path: str, base_dir: Path = None) -> Path:
    """
    Sanitize and validate output path.
    
    Args:
        output_path (str): Raw output path
        base_dir (Path): Base directory for relative paths
        
    Returns:
        Path: Sanitized absolute path
    """
    if output_path == "stdio":
        return Path("stdio")
        
    path = Path(output_path)
    
    # Make absolute if relative
    if not path.is_absolute():
        if base_dir:
            path = base_dir / path
        else:
            path = Path.cwd() / path
            
    return path.resolve()

def parse_comma_separated_list(value: Optional[str]) -> List[str]:
    """
    Parse a comma-separated string into a list of stripped values.
    
    Args:
        value: Comma-separated string or None
        
    Returns:
        list: List of stripped values, empty if input was None
    """
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def parse_ignore_dirs(ignore_dirs_str: Optional[str], base_dirs: List[str]) -> List[Path]:
    """
    Parse ignore directories string and convert to resolved Path objects.
    
    Args:
        ignore_dirs_str: Comma-separated string of directories to ignore
        base_dirs: List of base directories for resolving relative paths
        
    Returns:
        list: List of resolved Path objects
    """
    if not ignore_dirs_str:
        return []
    
    ignore_dirs = []
    base_path = Path(base_dirs[0]).resolve() if base_dirs else Path.cwd()
    
    for ignore_dir_str in parse_comma_separated_list(ignore_dirs_str):
        ignore_path = Path(ignore_dir_str)
        
        # Handle both absolute and relative paths
        if ignore_path.is_absolute():
            ignore_dirs.append(ignore_path.resolve())
        else:
            # Resolve relative to first base directory or cwd
            ignore_dirs.append((base_path / ignore_path).resolve())
    
    if ignore_dirs:
        logging.info(f"Will ignore directories: {[str(d) for d in ignore_dirs]}")
    
    return ignore_dirs
