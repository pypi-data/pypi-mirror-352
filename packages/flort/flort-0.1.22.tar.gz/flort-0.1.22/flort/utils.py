"""
File Utilities Module

This module provides utility functions for file operations including:
- Binary file detection
- Content cleaning
- File writing
- Directory tree generation

These utilities support the core functionality of the file processing system
while handling errors gracefully and providing appropriate logging.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
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

    The function uses two methods to detect binary files:
    1. Checks for null bytes in the first 1024 bytes
    2. Looks for non-text characters outside the ASCII printable range

    Note:
        - Returns True on any error, assuming binary to be safe
        - Only reads the first 1024 bytes for efficiency
    """
    try:
        with open(file_path, 'rb') as file:
            # Read first chunk of file
            chunk = file.read(1024)
            
            # Quick check for null bytes
            if b'\x00' in chunk:
                return True
                
            # Check for non-text characters
            text_characters = bytes(range(32, 127)) + b'\n\r\t\f\b'
            return bool(chunk.translate(None, text_characters))
            
    except Exception as e:
        logging.error(f"Error determining if file is binary {file_path}: {e}")
        return True


def clean_content(file_path: Path) -> str:
    """
    Clean up file content by removing unnecessary whitespace.

    Args:
        file_path (Path): Path to the file to clean

    Returns:
        str: Cleaned content with empty lines removed and remaining lines stripped

    The function:
    1. Reads all lines from the file
    2. Strips whitespace from each line
    3. Filters out empty lines
    4. Joins remaining lines with newlines

    Note:
        - Preserves line breaks between non-empty lines
        - Removes leading/trailing whitespace from each line
        - Removes completely empty lines
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            return '\n'.join(cleaned_lines)
    except Exception as e:
        logging.error(f"Error cleaning content from {file_path}: {e}")
        return ""


def write_file(file_path: str, data: str, mode: str = 'a') -> None:
    """
    Write data to a file or output to console.

    Args:
        file_path (str): Path to output file or "stdio" for console output
        data (str): Content to write
        mode (str, optional): File opening mode ('w' for write, 'a' for append).
            Defaults to 'a'.

    The function handles two output modes:
    1. File output: Writes to the specified file path
    2. Console output: Prints to stdout if file_path is "stdio"

    Error handling:
    - IOError: Logged with specific error message
    - Other exceptions: Logged with generic error message

    Note:
        - Creates parent directories if they don't exist
        - Logs success with mode information
        - Handles both creation and append operations
    """
    try:
        if file_path == "stdio":
            print(data, end='')
        else:
            # Create parent directories if they don't exist
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, mode, encoding='utf-8') as file:
                file.write(data)
            
            operation = 'create' if mode == 'w' else 'append'
            logging.debug(f"Output written to: {file_path}. Mode: {operation}.")
            
    except IOError as e:
        logging.error(f"Failed to write to {file_path}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while writing to {file_path}: {e}")


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


def count_tokens(text):
    """
    Count tokens in text using a simple tokenization strategy.
    
    Args:
        text (str): Text to tokenize
        
    Returns:
        int: Number of tokens
    """
    if not text:
        return 0
        
    def split_words(word):
        if len(word) <= 4:
            return [word]
        return [word[i:i+4] for i in range(0, len(word), 4)]

    pattern = r'[A-Za-z]+(?:\'[A-Za-z]+)?|[0-9]+(?:\.[0-9]+)?%?|[.,!?;:]|[@#$&*]+'
    base_tokens = re.findall(pattern, text)
    
    tokens = []
    for token in base_tokens:
        tokens.extend(split_words(token))
        
    return len(tokens)


def count_file_tokens(filename):
    """
    Count tokens and characters in a file.
    
    Args:
        filename (str): Path to file to analyze
        
    Returns:
        str: Formatted string with token and character counts
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        token_count = count_tokens(text)
        char_count = len(text)
        
        return f"Tokens: {token_count:,}\nCharacters: {char_count:,}"
    except Exception as e:
        logging.error(f"Error counting tokens in {filename}: {e}")
        return "Error counting tokens"


def print_configuration(
    directories: list,
    extensions: list,
    include_all: bool,
    include_hidden: bool,
    ignore_dirs: list = None
) -> None:
    """
    Log the current configuration settings for the file processing operation.

    Args:
        directories (list): List of directory paths to process
        extensions (list): List of file extensions to include
        include_all (bool): Whether to include all file types
        include_hidden (bool): Whether to include hidden files
        ignore_dirs (list, optional): List of directories to ignore

    This function provides visibility into the tool's configuration,
    which is particularly useful for debugging and verification.
    """
    logging.info(f"Processing directories: {', '.join(directories)}")
    if extensions:
        logging.info(f"File types: {', '.join(extensions)}")
    logging.info(f"All files: {include_all}")
    logging.info(f"Hidden files: {include_hidden}")
    if ignore_dirs:
        logging.info(f"Ignoring directories: {', '.join([str(d) for d in ignore_dirs])}")


def archive_file(file_path, archive_format):
    """
    Archive a file using the specified format.
    
    Args:
        file_path (str): Path to the file to archive
        archive_format (str): 'zip' or 'tar.gz'
        
    Returns:
        str: Path to the created archive file
    """
    input_path = Path(file_path)
    
    if not input_path.exists():
        logging.error(f"File to archive does not exist: {file_path}")
        return None
    
    try:
        if archive_format == 'zip':
            archive_path = f"{file_path}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, arcname=input_path.name)
            
        elif archive_format == 'tar.gz':
            archive_path = f"{file_path}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(file_path, arcname=input_path.name)
        else:
            logging.error(f"Unsupported archive format: {archive_format}")
            return None
        
        logging.info(f"Created archive: {archive_path}")
        return archive_path
        
    except Exception as e:
        logging.error(f"Error creating archive: {e}")
        return None


def generate_tree(path_list: list, output: str) -> None:
    """
    Generate a hierarchical tree structure from a list of paths.
    
    Args:
        path_list (list): List of path dictionaries
        output (str): Output file path or "stdio"
    """
    if not path_list:
        write_file(output, "## Directory Tree\n(No files found)\n\n")
        return
        
    # Get current working directory for normalization
    cwd = Path.cwd()
    
    # Normalize paths and add to a new list
    normalized_paths = []
    root_name = os.path.basename(cwd)
    
    for item in path_list:
        # Skip the current directory entry itself
        if str(item["path"]) == str(cwd) or item["relative_path"] == '.':
            continue
            
        # Create a copy of the item to modify
        new_item = item.copy()
        
        # Normalize relative path
        rel_path = new_item["relative_path"]
        if rel_path.startswith('./'):
            rel_path = rel_path[2:]
        
        # For paths relative to cwd, prefix with root directory name
        if not rel_path or rel_path == '.':
            rel_path = root_name
        elif not rel_path.startswith(root_name + '/'):
            rel_path = f"{root_name}/{rel_path}"
            
        new_item["normalized_path"] = rel_path
        
        # Calculate depth based on path parts
        path_parts = rel_path.split('/')
        new_item["display_depth"] = len(path_parts) - 1
        
        normalized_paths.append(new_item)
    
    # Add root directory as first item if there are any paths
    if normalized_paths:
        normalized_paths.insert(0, {
            "path": cwd,
            "relative_path": ".",
            "normalized_path": root_name,
            "display_depth": 0,
            "type": "dir"
        })
    
    # Sort by normalized path for consistent output
    sorted_paths = sorted(normalized_paths, key=lambda x: x["normalized_path"])
    
    # Write header
    write_file(output, "## Directory Tree\n")
    structure = []
    
    # Track processed paths to avoid duplicates
    processed = set()
    
    for item in sorted_paths:
        norm_path = item["normalized_path"]
        
        # Skip duplicates
        if norm_path in processed:
            continue
            
        processed.add(norm_path)
        
        # Get the path components for display
        path_parts = norm_path.split('/')
        name = path_parts[-1]
        depth = item["display_depth"]
        
        # Calculate indent
        indent = '|   ' * depth + '|-- ' if depth > 0 else ''
        
        # Add to structure
        if item["type"] == 'dir':
            structure.append(f"{indent}{name}/")
        else:
            structure.append(f"{indent}{name}")
    
    # Write to output
    write_file(output, '\n'.join(structure) + "\n\n\n")