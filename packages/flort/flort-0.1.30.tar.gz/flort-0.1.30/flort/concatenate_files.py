"""
File Concatenation Module

This module handles the concatenation of multiple source files into a single output,
with proper formatting, error handling, and metadata tracking.

Features:
- Safe file reading with encoding detection
- Content cleaning and formatting
- Token and character counting
- Progress tracking for large operations
- Robust error handling with detailed logging
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .utils import write_file, count_tokens, clean_content, is_binary_file


class FileConcatenator:
    """
    Handles the concatenation of multiple files with comprehensive error handling
    and progress tracking.
    """
    
    def __init__(self, output_path: str, clean_content_flag: bool = True):
        """
        Initialize the file concatenator.
        
        Args:
            output_path: Path to write concatenated output
            clean_content_flag: Whether to clean whitespace from content
        """
        self.output_path = output_path
        self.clean_content_flag = clean_content_flag
        self.stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "total_characters": 0,
            "total_tokens": 0,
            "errors": []
        }
    
    def concatenate_files(self, file_list: List[Dict[str, Any]]) -> bool:
        """
        Concatenate all files in the file list to the output.
        
        Args:
            file_list: List of file dictionaries with path and metadata
            
        Returns:
            bool: True if concatenation was successful
        """
        if not file_list:
            logging.warning("No files provided for concatenation")
            return write_file(self.output_path, "## File Data\n(No files to concatenate)\n\n")
        
        # Filter to only files (not directories)
        files_to_process = [item for item in file_list if item.get("type") == "file"]
        
        if not files_to_process:
            logging.warning("No files found in file list")
            return write_file(self.output_path, "## File Data\n(No files found)\n\n")
        
        logging.info(f"Starting concatenation of {len(files_to_process)} files")
        
        # Write header
        if not write_file(self.output_path, "## File Data\n"):
            return False
        
        # Process each file
        for i, item in enumerate(files_to_process, 1):
            file_path = item["path"]
            relative_path = item["relative_path"]
            
            logging.debug(f"Processing file {i}/{len(files_to_process)}: {relative_path}")
            
            success = self._process_single_file(file_path, relative_path)
            
            if success:
                self.stats["files_processed"] += 1
            else:
                self.stats["files_skipped"] += 1
            
            # Log progress for large operations
            if i % 10 == 0 or i == len(files_to_process):
                logging.info(f"Progress: {i}/{len(files_to_process)} files processed")
        
        # Write summary
        self._write_summary()
        
        logging.info(f"Concatenation complete. Processed: {self.stats['files_processed']}, "
                    f"Skipped: {self.stats['files_skipped']}")
        
        return True
    
    def _process_single_file(self, file_path: Path, relative_path: str) -> bool:
        """
        Process a single file for concatenation.
        
        Args:
            file_path: Path to the file to process
            relative_path: Relative path for display
            
        Returns:
            bool: True if file was processed successfully
        """
        try:
            # Double-check that it's not a binary file
            if is_binary_file(file_path):
                logging.warning(f"Skipping binary file: {relative_path}")
                error_msg = f"Binary file skipped: {relative_path}"
                self.stats["errors"].append(error_msg)
                return self._write_file_error(relative_path, "Binary file")
            
            # Read file content
            content = self._read_file_safely(file_path)
            if content is None:
                return False
            
            # Clean content if requested
            if self.clean_content_flag:
                content = self._clean_file_content(file_path, content)
            
            # Calculate metrics
            char_count = len(content)
            token_count = count_tokens(content)
            
            # Update statistics
            self.stats["total_characters"] += char_count
            self.stats["total_tokens"] += token_count
            
            # Write file header
            if not self._write_file_header(relative_path, char_count, token_count):
                return False
            
            # Write file content
            if not write_file(self.output_path, content):
                return False
            
            # Add separator
            if not write_file(self.output_path, "\n\n"):
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"Error processing {relative_path}: {str(e)}"
            logging.error(error_msg)
            self.stats["errors"].append(error_msg)
            return self._write_file_error(relative_path, str(e))
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """
        Safely read a file with multiple encoding attempts.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            str: File content, or None if reading failed
        """
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    content = f.read()
                    
                # Validate that we got reasonable content
                if content or file_path.stat().st_size == 0:  # Allow empty files
                    logging.debug(f"Successfully read {file_path} with encoding {encoding}")
                    return content
                    
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logging.error(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        # If all encodings failed, try binary read with replacement
        try:
            with open(file_path, 'rb') as f:
                raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
                logging.warning(f"Used binary read with replacement for {file_path}")
                return content
        except Exception as e:
            error_msg = f"Failed to read {file_path} with any encoding: {e}"
            logging.error(error_msg)
            self.stats["errors"].append(error_msg)
            return None
    
    def _clean_file_content(self, file_path: Path, content: str) -> str:
        """
        Clean file content while preserving structure.
        
        Args:
            file_path: Path to the file (for context)
            content: Raw file content
            
        Returns:
            str: Cleaned content
        """
        try:
            return clean_content(file_path)
        except Exception as e:
            logging.warning(f"Content cleaning failed for {file_path}: {e}, using raw content")
            return content
    
    def _write_file_header(self, relative_path: str, char_count: int, token_count: int) -> bool:
        """
        Write the header information for a file.
        
        Args:
            relative_path: Relative path of the file
            char_count: Number of characters in the file
            token_count: Number of tokens in the file
            
        Returns:
            bool: True if header was written successfully
        """
        header = f"--- File: {relative_path}\n"
        header += f"--- Characters: {char_count:,}\n"
        header += f"--- Token Count: {token_count:,}\n"
        
        return write_file(self.output_path, header)
    
    def _write_file_error(self, relative_path: str, error_message: str) -> bool:
        """
        Write an error entry for a file that couldn't be processed.
        
        Args:
            relative_path: Relative path of the file
            error_message: Error description
            
        Returns:
            bool: True if error entry was written successfully
        """
        error_content = f"--- File: {relative_path}\n"
        error_content += f"--- Error: {error_message}\n"
        error_content += "--- Content: <Unable to read file>\n\n"
        
        return write_file(self.output_path, error_content)
    
    def _write_summary(self) -> bool:
        """
        Write a summary of the concatenation operation.
        
        Returns:
            bool: True if summary was written successfully
        """
        summary = "\n## Concatenation Summary\n"
        summary += f"Files processed: {self.stats['files_processed']}\n"
        summary += f"Files skipped: {self.stats['files_skipped']}\n"
        summary += f"Total characters: {self.stats['total_characters']:,}\n"
        summary += f"Total tokens: {self.stats['total_tokens']:,}\n"
        
        if self.stats["errors"]:
            summary += f"\n### Errors ({len(self.stats['errors'])}):\n"
            for error in self.stats["errors"][:10]:  # Limit to first 10 errors
                summary += f"- {error}\n"
            if len(self.stats["errors"]) > 10:
                summary += f"... and {len(self.stats['errors']) - 10} more errors\n"
        
        summary += f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        return write_file(self.output_path, summary)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get concatenation statistics.
        
        Returns:
            dict: Statistics about the concatenation operation
        """
        return self.stats.copy()


def concat_files(file_list: List[Dict[str, Any]], output: str, clean_content: bool = True) -> bool:
    """
    Concatenate files from a file list into a single output.
    
    This is the main entry point for file concatenation. It creates a FileConcatenator
    instance and processes all files in the provided list.
    
    Args:
        file_list: List of file dictionaries with path and metadata information
        output: Output file path or "stdio" for console output
        clean_content: Whether to clean whitespace from file content
        
    Returns:
        bool: True if concatenation was successful, False otherwise
        
    Example:
        file_list = [
            {"path": Path("main.py"), "relative_path": "main.py", "type": "file"},
            {"path": Path("utils.py"), "relative_path": "utils.py", "type": "file"}
        ]
        success = concat_files(file_list, "output.txt")
    """
    if not file_list:
        logging.warning("No files provided to concat_files")
        return False
    
    try:
        concatenator = FileConcatenator(output, clean_content)
        success = concatenator.concatenate_files(file_list)
        
        # Log final statistics
        stats = concatenator.get_statistics()
        if stats["files_processed"] > 0:
            logging.info(f"Concatenation statistics: {stats}")
        
        return success
        
    except Exception as e:
        logging.error(f"Error in concat_files: {e}")
        return False


def create_file_manifest(file_list: List[Dict[str, Any]], output: str) -> bool:
    """
    Create a manifest of all files without their content.
    
    This function creates a summary listing of all files that would be processed,
    including their sizes and types, without actually concatenating the content.
    Useful for previewing what will be included.
    
    Args:
        file_list: List of file dictionaries
        output: Output file path or "stdio"
        
    Returns:
        bool: True if manifest was created successfully
    """
    try:
        if not write_file(output, "## File Manifest\n"):
            return False
        
        files_only = [item for item in file_list if item.get("type") == "file"]
        
        if not files_only:
            return write_file(output, "(No files found)\n\n")
        
        total_size = 0
        total_files = len(files_only)
        
        for i, item in enumerate(files_only, 1):
            file_path = item["path"]
            relative_path = item["relative_path"]
            
            try:
                size = file_path.stat().st_size
                total_size += size
                
                # Determine if binary
                is_binary = is_binary_file(file_path)
                binary_indicator = " [BINARY]" if is_binary else ""
                
                manifest_line = f"{i:3d}. {relative_path} ({size:,} bytes){binary_indicator}\n"
                
                if not write_file(output, manifest_line):
                    return False
                    
            except Exception as e:
                error_line = f"{i:3d}. {relative_path} (ERROR: {e})\n"
                if not write_file(output, error_line):
                    return False
        
        # Write summary
        summary = f"\nTotal: {total_files} files, {total_size:,} bytes\n\n"
        return write_file(output, summary)
        
    except Exception as e:
        logging.error(f"Error creating file manifest: {e}")
        return False