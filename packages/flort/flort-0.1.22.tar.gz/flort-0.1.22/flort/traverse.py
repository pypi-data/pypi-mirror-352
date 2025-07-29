from pathlib import Path
import logging
import os

def get_paths(
    directories=None, 
    extensions=None, 
    include_all=False, 
    include_hidden=False, 
    ignore_dirs=None
):
    """
    Traverses directories and collects paths with depth information.

    Args:
        directories (list): List of directories to traverse.
        extensions (list): List of file extensions to include.
        include_all (bool): Whether to include all files regardless of extension.
        include_hidden (bool): Whether to include hidden files.
        ignore_dirs (list): List of Path objects representing directories to ignore.

    Returns:
        list: A list of dictionaries containing path and depth information.
    """
    if directories is None or not directories:
        logging.error("No directories provided for traversal.")
        return []

    path_list = []
    ignore_dirs = ignore_dirs or []
    
    # Resolve all ignore directories to absolute paths for consistent comparison
    resolved_ignore_dirs = [ignore_dir.resolve() for ignore_dir in ignore_dirs]

    for base_directory in directories:
        base_path = Path(base_directory).resolve()
        
        if not base_path.is_dir():
            logging.error(f"The path {base_directory} is not a valid directory.")
            continue

        logging.info(f"Processing directory: {base_path}")

        # Check if base directory should be ignored
        if any(base_path == ignore_dir or _is_subdirectory(base_path, ignore_dir) 
               for ignore_dir in resolved_ignore_dirs):
            logging.info(f"Skipping ignored directory: {base_path}")
            continue

        # Calculate parent for relative paths
        try:
            parent_path = base_path.parent.resolve()
        except Exception:
            parent_path = Path.cwd()

        # Add base directory to the list
        try:
            rel_path = str(base_path.relative_to(parent_path))
        except ValueError:
            rel_path = str(base_path)
            
        path_list.append({
            "path": base_path, 
            "relative_path": rel_path, 
            "depth": 1, 
            'type': 'dir'
        })

        def scan_directory(current_path, current_depth, parent_for_relative):
            """Recursively scan directory for files and subdirectories."""
            try:
                with os.scandir(current_path) as entries:
                    for entry in sorted(entries, key=lambda e: e.name):
                        try:
                            entry_path = Path(entry.path).resolve()
                        except Exception as e:
                            logging.warning(f"Could not resolve path {entry.path}: {e}")
                            continue

                        # Skip hidden files/directories if not included
                        if not include_hidden and entry.name.startswith('.'):
                            continue

                        # Check if path should be ignored
                        if any(entry_path == ignore_dir or _is_subdirectory(entry_path, ignore_dir) 
                               for ignore_dir in resolved_ignore_dirs):
                            logging.debug(f"Skipping ignored path: {entry_path}")
                            continue

                        # Calculate relative path
                        try:
                            relative_path = str(entry_path.relative_to(parent_for_relative))
                        except ValueError:
                            relative_path = str(entry_path)

                        if entry.is_dir():
                            path_list.append({
                                "path": entry_path,
                                "relative_path": relative_path,
                                "depth": current_depth,
                                'type': 'dir'
                            })
                            # Recursively scan subdirectories
                            scan_directory(entry_path, current_depth + 1, parent_for_relative)
                            
                        elif entry.is_file():
                            # Check if file should be included based on criteria
                            should_include = False
                            
                            if include_all:
                                should_include = True
                            elif extensions:
                                file_ext = entry_path.suffix.lower()
                                should_include = file_ext in extensions
                            
                            if should_include:
                                path_list.append({
                                    "path": entry_path,
                                    "relative_path": relative_path,
                                    "depth": current_depth,
                                    'type': 'file'
                                })
                                
            except PermissionError as e:
                logging.error(f"Permission denied accessing {current_path}: {e}")
            except Exception as e:
                logging.error(f"Error processing {current_path}: {e}")

        # Start recursive scan from base directory
        scan_directory(base_path, 2, parent_path)  # Start depth at 2 since base dir is depth 1

    return path_list


def _is_subdirectory(child_path, parent_path):
    """Check if child_path is a subdirectory of parent_path."""
    try:
        child_path.relative_to(parent_path)
        return True
    except ValueError:
        return False


def get_files_from_glob_patterns(directories, glob_patterns, ignore_dirs=None, re_glob=True):
    """
    Find files matching glob patterns within specified directories.
    
    Args:
        directories (list): List of directory paths to search in
        glob_patterns (list): List of glob patterns to match
        ignore_dirs (list): List of directory paths to ignore
        re_glob (bool): Whether to apply globbing (if False, assumes patterns are already file paths)
        
    Returns:
        list: List of Path objects for files matching the patterns
    """
    if ignore_dirs is None:
        ignore_dirs = []
    
    # Resolve all paths to absolute for consistent comparison
    ignore_dirs = [Path(d).resolve() for d in ignore_dirs]
    matching_files = []
    
    # For each specified directory
    for directory in directories:
        base_path = Path(directory).resolve()
        logging.debug(f"Searching in: {base_path}")
        
        if not base_path.exists() or not base_path.is_dir():
            logging.warning(f"Directory {base_path} does not exist or is not a directory")
            continue
            
        # For each glob pattern
        for pattern in glob_patterns:
            logging.debug(f"Using pattern: {pattern}")
            
            # If re_glob is True, apply globbing
            if re_glob:
                try:
                    if '**' in pattern:
                        # Pattern already includes recursive search
                        file_paths = list(base_path.glob(pattern))
                    else:
                        # Add recursive search
                        file_paths = list(base_path.glob('**/' + pattern))
                    logging.debug(f"Found {len(file_paths)} matches for pattern {pattern}")
                except Exception as e:
                    logging.error(f"Error with glob pattern '{pattern}': {e}")
                    continue
            else:
                # If re_glob is False, treat patterns as file paths
                file_path = Path(pattern)
                if file_path.is_absolute():
                    file_paths = [file_path] if file_path.exists() else []
                else:
                    file_paths = [base_path / pattern] if (base_path / pattern).exists() else []
            
            for file_path in file_paths:
                try:
                    file_path = file_path.resolve()
                except Exception as e:
                    logging.warning(f"Could not resolve path {file_path}: {e}")
                    continue
                    
                # Skip directories
                if not file_path.is_file():
                    continue
                    
                # Check if file is in an ignored directory
                should_ignore = False
                for ignore_dir in ignore_dirs:
                    if _is_subdirectory(file_path, ignore_dir):
                        should_ignore = True
                        logging.debug(f"Ignoring {file_path} (in ignored dir {ignore_dir})")
                        break
                
                if not should_ignore and file_path not in matching_files:
                    matching_files.append(file_path)
                    logging.debug(f"Added {file_path}")
    
    return matching_files