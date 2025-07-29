"""
File Traversal Module

This module provides comprehensive file discovery functionality with support for:
- Directory traversal with depth tracking
- Extension-based filtering (include/exclude)
- Pattern-based filtering (include/exclude)
- Hidden file handling
- Binary file detection and filtering
- Specific file inclusion
- Directory ignoring

The module implements a clean pipeline for file discovery that handles all
filtering operations in a consistent and predictable order.
"""

from pathlib import Path
import logging
import os
import fnmatch
from typing import List, Dict, Any, Set, Optional, Tuple

from .utils import is_binary_file, validate_file_path


class FileFilter:
    """
    Handles all file filtering logic in a centralized, testable way.
    """
    
    def __init__(
        self,
        include_extensions: List[str] = None,
        exclude_extensions: List[str] = None,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        include_all: bool = False,
        include_hidden: bool = False,
        include_binary: bool = False,
        ignore_dirs: List[Path] = None
    ):
        """
        Initialize file filter with all filtering criteria.
        
        Args:
            include_extensions: List of extensions to include (with or without dots)
            exclude_extensions: List of extensions to exclude (with or without dots)
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude
            include_all: If True, include all files regardless of extension
            include_hidden: If True, include hidden files/directories
            include_binary: If True, include binary files
            ignore_dirs: List of directory paths to completely ignore
        """
        self.include_extensions = self._normalize_extensions(include_extensions or [])
        self.exclude_extensions = self._normalize_extensions(exclude_extensions or [])
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.include_all = include_all
        self.include_hidden = include_hidden
        self.include_binary = include_binary
        self.ignore_dirs = [Path(d).resolve() for d in (ignore_dirs or [])]
        
        logging.debug(f"FileFilter initialized with:")
        logging.debug(f"  Include extensions: {self.include_extensions}")
        logging.debug(f"  Exclude extensions: {self.exclude_extensions}")
        logging.debug(f"  Include patterns: {self.include_patterns}")
        logging.debug(f"  Exclude patterns: {self.exclude_patterns}")
        logging.debug(f"  Include all: {self.include_all}")
        logging.debug(f"  Include hidden: {self.include_hidden}")
        logging.debug(f"  Include binary: {self.include_binary}")
    
    def _normalize_extensions(self, extensions: List[str]) -> Set[str]:
        """Normalize extensions to always include the dot prefix."""
        normalized = set()
        for ext in extensions:
            ext = ext.strip()
            if ext and not ext.startswith('.'):
                ext = '.' + ext
            if ext:
                normalized.add(ext.lower())
        return normalized
    
    def should_ignore_directory(self, dir_path: Path) -> bool:
        """
        Check if a directory should be completely ignored.
        
        Args:
            dir_path: Directory path to check
            
        Returns:
            bool: True if directory should be ignored
        """
        try:
            resolved_path = dir_path.resolve()
            
            # Check against ignore list
            for ignore_dir in self.ignore_dirs:
                if resolved_path == ignore_dir or self._is_subdirectory(resolved_path, ignore_dir):
                    return True
                    
            # Check hidden directories
            if not self.include_hidden and dir_path.name.startswith('.'):
                return True
                
            return False
            
        except Exception as e:
            logging.debug(f"Error checking directory {dir_path}: {e}")
            return True
    
    def should_include_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Determine if a file should be included based on all filter criteria.
        
        Args:
            file_path: File path to check
            
        Returns:
            tuple: (should_include, reason) where reason explains the decision
        """
        try:
            # Check if file is hidden
            if not self.include_hidden and file_path.name.startswith('.'):
                return False, "hidden file"
            
            # Check if in ignored directory
            for ignore_dir in self.ignore_dirs:
                if self._is_subdirectory(file_path, ignore_dir):
                    return False, f"in ignored directory {ignore_dir}"
            
            # Check exclude patterns first (they take precedence)
            # Only check the filename, not the full path to avoid matching temp directories
            for pattern in self.exclude_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    return False, f"matches exclude pattern '{pattern}'"
            
            # Check exclude extensions
            if file_path.suffix.lower() in self.exclude_extensions:
                return False, f"has excluded extension '{file_path.suffix}'"
            
            # If include_all is True, include everything not excluded
            if self.include_all:
                # Still check binary files if not included
                if not self.include_binary and is_binary_file(file_path):
                    return False, "binary file (use --include-binary to include)"
                return True, "include_all enabled"
            
            # Check include patterns (only check filename, not full path)
            pattern_match = False
            for pattern in self.include_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    pattern_match = True
                    break
            
            # Check include extensions
            extension_match = file_path.suffix.lower() in self.include_extensions
            
            # Must match either pattern or extension (if any are specified)
            has_include_criteria = self.include_patterns or self.include_extensions
            
            if has_include_criteria:
                if not (pattern_match or extension_match):
                    return False, "does not match any include criteria"
            else:
                # If no include criteria specified and not include_all, don't include
                return False, "no include criteria specified"
            
            # Check binary files
            if not self.include_binary and is_binary_file(file_path):
                return False, "binary file (use --include-binary to include)"
            
            # Validate file accessibility
            is_valid, error_msg = validate_file_path(file_path)
            if not is_valid:
                return False, f"file validation failed: {error_msg}"
            
            return True, "passed all filters"
            
        except Exception as e:
            logging.error(f"Error filtering file {file_path}: {e}")
            return False, f"error during filtering: {str(e)}"
    
    def _is_subdirectory(self, child_path: Path, parent_path: Path) -> bool:
        """Check if child_path is a subdirectory of parent_path."""
        try:
            child_path.resolve().relative_to(parent_path.resolve())
            return True
        except ValueError:
            return False


def scan_directories(
    directories: List[str],
    file_filter: FileFilter,
    max_depth: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Scan directories and return all matching files and directories.
    
    Args:
        directories: List of directory paths to scan
        file_filter: FileFilter instance with all filtering criteria
        max_depth: Maximum depth to traverse (None for unlimited)
        
    Returns:
        List of dictionaries with file/directory information
    """
    if not directories:
        logging.error("No directories provided for scanning.")
        return []

    all_paths = []
    processed_paths = set()
    
    for base_directory in directories:
        base_path = Path(base_directory).resolve()
        
        if not base_path.exists():
            logging.error(f"Directory does not exist: {base_directory}")
            continue
            
        if not base_path.is_dir():
            logging.error(f"Path is not a directory: {base_directory}")
            continue
        
        if file_filter.should_ignore_directory(base_path):
            logging.info(f"Skipping ignored directory: {base_path}")
            continue

        logging.info(f"Scanning directory: {base_path}")
        
        # Calculate parent for relative paths
        parent_path = base_path.parent.resolve()
        
        # Scan the directory tree
        directory_paths = _scan_directory_recursive(
            base_path, 
            parent_path,
            file_filter,
            max_depth,
            current_depth=1,
            processed_paths=processed_paths
        )
        
        all_paths.extend(directory_paths)
    
    # Sort by relative path for consistent output
    all_paths.sort(key=lambda x: x["relative_path"])
    
    logging.info(f"Found {len([p for p in all_paths if p['type'] == 'file'])} files and "
                f"{len([p for p in all_paths if p['type'] == 'dir'])} directories")
    
    return all_paths


def _scan_directory_recursive(
    current_path: Path,
    parent_for_relative: Path,
    file_filter: FileFilter,
    max_depth: Optional[int],
    current_depth: int,
    processed_paths: Set[str]
) -> List[Dict[str, Any]]:
    """
    Recursively scan a directory and return matching files/directories.
    
    Args:
        current_path: Current directory being scanned
        parent_for_relative: Parent path for calculating relative paths
        file_filter: FileFilter instance
        max_depth: Maximum depth to traverse
        current_depth: Current traversal depth
        processed_paths: Set of already processed paths to avoid duplicates
        
    Returns:
        List of path dictionaries
    """
    paths = []
    
    # Check depth limit
    if max_depth is not None and current_depth > max_depth:
        return paths
    
    # Calculate relative path
    try:
        relative_path = str(current_path.relative_to(parent_for_relative))
    except ValueError:
        relative_path = str(current_path)
    
    # Skip if already processed
    path_key = str(current_path.resolve())
    if path_key in processed_paths:
        return paths
    processed_paths.add(path_key)
    
    # Add current directory
    paths.append({
        "path": current_path,
        "relative_path": relative_path,
        "depth": current_depth,
        "type": "dir"
    })
    
    try:
        # Get directory contents
        with os.scandir(current_path) as entries:
            # Sort entries for consistent output
            sorted_entries = sorted(entries, key=lambda e: (e.is_file(), e.name.lower()))
            
            for entry in sorted_entries:
                try:
                    entry_path = Path(entry.path).resolve()
                except Exception as e:
                    logging.warning(f"Could not resolve path {entry.path}: {e}")
                    continue
                
                # Skip if already processed
                entry_key = str(entry_path)
                if entry_key in processed_paths:
                    continue
                
                # Calculate relative path for entry
                try:
                    entry_relative = str(entry_path.relative_to(parent_for_relative))
                except ValueError:
                    entry_relative = str(entry_path)
                
                if entry.is_dir():
                    # Check if directory should be ignored
                    if not file_filter.should_ignore_directory(entry_path):
                        # Recursively scan subdirectory
                        subdir_paths = _scan_directory_recursive(
                            entry_path,
                            parent_for_relative,
                            file_filter,
                            max_depth,
                            current_depth + 1,
                            processed_paths
                        )
                        paths.extend(subdir_paths)
                    else:
                        logging.debug(f"Ignoring directory: {entry_path}")
                        
                elif entry.is_file():
                    # Check if file should be included
                    should_include, reason = file_filter.should_include_file(entry_path)
                    
                    if should_include:
                        processed_paths.add(entry_key)
                        paths.append({
                            "path": entry_path,
                            "relative_path": entry_relative,
                            "depth": current_depth + 1,
                            "type": "file"
                        })
                        logging.debug(f"Including file: {entry_path} ({reason})")
                    else:
                        logging.debug(f"Excluding file: {entry_path} ({reason})")
                        
    except PermissionError as e:
        logging.error(f"Permission denied accessing {current_path}: {e}")
    except Exception as e:
        logging.error(f"Error scanning {current_path}: {e}")
    
    return paths


def add_specific_files(
    path_list: List[Dict[str, Any]],
    include_files: List[str],
    base_dir: Path = None
) -> List[Dict[str, Any]]:
    """
    Add specific files to the path list, regardless of filtering rules.
    
    Args:
        path_list: Existing list of path dictionaries
        include_files: List of file paths to include
        base_dir: Base directory for resolving relative paths
        
    Returns:
        Updated path list with included files added
    """
    if not include_files:
        return path_list
    
    if base_dir is None:
        base_dir = Path.cwd()
    
    # Create set of existing paths for deduplication
    existing_paths = {str(item["path"].resolve()) for item in path_list}
    
    added_count = 0
    
    for file_str in include_files:
        file_str = file_str.strip()
        if not file_str:
            continue
            
        file_path = Path(file_str)
        
        # Handle relative paths
        if not file_path.is_absolute():
            file_path = base_dir / file_path
            
        try:
            file_path = file_path.resolve()
        except Exception as e:
            logging.warning(f"Could not resolve include file path {file_str}: {e}")
            continue
        
        # Check if file exists and is accessible
        is_valid, error_msg = validate_file_path(file_path)
        if not is_valid:
            logging.warning(f"Cannot include file {file_str}: {error_msg}")
            continue
        
        # Check for duplicates
        path_key = str(file_path)
        if path_key in existing_paths:
            logging.debug(f"File already included: {file_path}")
            continue
        
        # Calculate relative path
        try:
            relative_path = str(file_path.relative_to(base_dir))
        except ValueError:
            # If file is outside base_dir, use just the filename
            relative_path = file_path.name
        
        # Add to path list
        path_list.append({
            "path": file_path,
            "relative_path": relative_path,
            "depth": len(file_path.parts) - len(base_dir.parts),
            "type": "file"
        })
        
        existing_paths.add(path_key)
        added_count += 1
        logging.info(f"Added included file: {relative_path}")
    
    if added_count > 0:
        logging.info(f"Added {added_count} specifically included files")
    
    return path_list


def apply_glob_patterns(
    directories: List[str],
    glob_patterns: List[str],
    file_filter: FileFilter
) -> List[Dict[str, Any]]:
    """
    Find files matching glob patterns within specified directories.
    
    Args:
        directories: List of directory paths to search in
        glob_patterns: List of glob patterns to match
        file_filter: FileFilter instance for additional filtering
        
    Returns:
        List of path dictionaries for matching files
    """
    if not glob_patterns:
        return []
    
    matching_files = []
    processed_paths = set()
    
    for directory in directories:
        base_path = Path(directory).resolve()
        
        if not base_path.exists() or not base_path.is_dir():
            logging.warning(f"Invalid directory for glob search: {directory}")
            continue
            
        if file_filter.should_ignore_directory(base_path):
            logging.debug(f"Skipping ignored directory for glob: {base_path}")
            continue
            
        logging.debug(f"Applying glob patterns in: {base_path}")
        
        for pattern in glob_patterns:
            logging.debug(f"Processing glob pattern: {pattern}")
            
            try:
                # Handle recursive patterns
                if '**' in pattern:
                    matches = list(base_path.glob(pattern))
                else:
                    matches = list(base_path.glob('**/' + pattern))
                
                logging.debug(f"Found {len(matches)} matches for pattern '{pattern}'")
                
                for file_path in matches:
                    if not file_path.is_file():
                        continue
                    
                    # Resolve path
                    try:
                        file_path = file_path.resolve()
                    except Exception as e:
                        logging.warning(f"Could not resolve glob match {file_path}: {e}")
                        continue
                    
                    # Check for duplicates
                    path_key = str(file_path)
                    if path_key in processed_paths:
                        continue
                    
                    # Apply file filter
                    should_include, reason = file_filter.should_include_file(file_path)
                    if not should_include:
                        logging.debug(f"Glob match excluded: {file_path} ({reason})")
                        continue
                    
                    # Calculate relative path
                    try:
                        relative_path = str(file_path.relative_to(base_path.parent))
                    except ValueError:
                        relative_path = str(file_path)
                    
                    matching_files.append({
                        "path": file_path,
                        "relative_path": relative_path,
                        "depth": len(file_path.parts) - len(base_path.parent.parts),
                        "type": "file"
                    })
                    
                    processed_paths.add(path_key)
                    logging.debug(f"Added glob match: {file_path}")
                    
            except Exception as e:
                logging.error(f"Error processing glob pattern '{pattern}' in {base_path}: {e}")
    
    logging.info(f"Found {len(matching_files)} files matching glob patterns")
    return matching_files


def get_paths(
    directories: List[str] = None,
    extensions: List[str] = None,
    exclude_extensions: List[str] = None,
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
    include_all: bool = False,
    include_hidden: bool = False,
    include_binary: bool = False,
    ignore_dirs: List[Path] = None,
    include_files: List[str] = None,
    glob_patterns: List[str] = None,
    max_depth: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Main entry point for file path discovery with comprehensive filtering.
    
    This function orchestrates the entire file discovery pipeline:
    1. Directory scanning with basic filters
    2. Glob pattern matching
    3. Specific file inclusion
    4. Deduplication
    5. Final sorting
    
    Args:
        directories: List of directories to traverse
        extensions: List of file extensions to include
        exclude_extensions: List of file extensions to exclude
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        include_all: Include all files regardless of extension
        include_hidden: Include hidden files
        include_binary: Include binary files
        ignore_dirs: List of directories to ignore
        include_files: List of specific files to include
        glob_patterns: List of glob patterns to search for
        max_depth: Maximum traversal depth
        
    Returns:
        List of path dictionaries sorted by relative path
    """
    if not directories:
        directories = ["."]
    
    # Create file filter
    file_filter = FileFilter(
        include_extensions=extensions,
        exclude_extensions=exclude_extensions,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        include_all=include_all,
        include_hidden=include_hidden,
        include_binary=include_binary,
        ignore_dirs=ignore_dirs
    )
    
    # Step 1: Scan directories
    all_paths = scan_directories(directories, file_filter, max_depth)
    
    # Step 2: Add glob pattern matches
    if glob_patterns:
        glob_matches = apply_glob_patterns(directories, glob_patterns, file_filter)
        all_paths.extend(glob_matches)
    
    # Step 3: Add specifically included files
    if include_files:
        base_dir = Path(directories[0]).resolve() if directories else Path.cwd()
        all_paths = add_specific_files(all_paths, include_files, base_dir)
    
    # Step 4: Remove duplicates while preserving order
    seen_paths = set()
    deduplicated_paths = []
    
    for item in all_paths:
        path_key = str(item["path"].resolve())
        if path_key not in seen_paths:
            seen_paths.add(path_key)
            deduplicated_paths.append(item)
    
    # Step 5: Final sort by relative path
    deduplicated_paths.sort(key=lambda x: (x["type"] == "file", x["relative_path"]))
    
    file_count = len([p for p in deduplicated_paths if p["type"] == "file"])
    dir_count = len([p for p in deduplicated_paths if p["type"] == "dir"])
    
    logging.info(f"Final result: {file_count} files, {dir_count} directories")
    
    return deduplicated_paths