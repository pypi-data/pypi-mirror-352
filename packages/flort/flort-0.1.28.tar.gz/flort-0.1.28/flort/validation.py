import os
import argparse
import logging
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .utils import parse_comma_separated_list, parse_ignore_dirs

class ValidationError(Enum):
    NO_INCLUSION_CRITERIA = "no_inclusion_criteria"
    DIRECTORY_NOT_FOUND = "directory_not_found"
    DIRECTORY_NOT_READABLE = "directory_not_readable"
    FILE_NOT_FOUND = "file_not_found"
    FILE_NOT_READABLE = "file_not_readable"
    INVALID_GLOB_PATTERN = "invalid_glob_pattern"
    INVALID_EXCLUDE_PATTERN = "invalid_exclude_pattern"
    EXTENSION_HAS_DOT = "extension_has_dot"
    EMPTY_EXTENSION = "empty_extension"
    INVALID_MAX_DEPTH = "invalid_max_depth"
    OUTPUT_NOT_WRITABLE = "output_not_writable"
    CONFLICTING_OPTIONS = "conflicting_options"
    ARCHIVE_WITH_STDIO = "archive_with_stdio"
    PATH_NOT_DIRECTORY = "path_not_directory"
    PATH_NOT_FILE = "path_not_file"

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationError]
    error_details: List[str]  # Human-readable details for each error
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
    
    def has_error(self, error_type: ValidationError) -> bool:
        """Check if a specific error type is present."""
        return error_type in self.errors
    
    def get_error_message(self) -> Optional[str]:
        """Get formatted error message for display."""
        if not self.error_details:
            return None
        return "\n".join(f"❌ {detail}" for detail in self.error_details)

def validate_arguments(args: argparse.Namespace) -> ValidationResult:
    """
    Validate command line arguments for consistency and correctness.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        ValidationResult: Structured validation result
    """
    errors = []
    error_details = []
    warnings = []
    
    # Validate we have something to process - BUT skip this check if using UI
    if not args.ui and not args.extensions and not args.all and not args.glob:
        errors.append(ValidationError.NO_INCLUSION_CRITERIA)
        error_details.append("No extensions or glob provided and --all flag not set. No files to process. "
                           "Use --extensions, --glob, --include-files, --all, or --ui to specify what to include.")
    
    # Validate directories exist
    for directory in args.directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            errors.append(ValidationError.DIRECTORY_NOT_FOUND)
            error_details.append(f"Directory does not exist: {directory}")
        elif not dir_path.is_dir():
            errors.append(ValidationError.PATH_NOT_DIRECTORY)
            error_details.append(f"Path is not a directory: {directory}")
        elif not os.access(directory, os.R_OK):
            errors.append(ValidationError.DIRECTORY_NOT_READABLE)
            error_details.append(f"Directory is not readable: {directory}")
    
    # Validate specific include files exist
    if args.include_files:
        include_files = parse_comma_separated_list(args.include_files)
        for file_path in include_files:
            if not file_path.strip():
                continue
                
            # Handle both absolute and relative paths
            if Path(file_path).is_absolute():
                full_path = Path(file_path)
            else:
                # Resolve relative to first directory or cwd
                base_dir = Path(args.directories[0]) if args.directories else Path.cwd()
                full_path = base_dir / file_path
            
            if not full_path.exists():
                errors.append(ValidationError.FILE_NOT_FOUND)
                error_details.append(f"Include file does not exist: {file_path} (resolved to: {full_path})")
            elif not full_path.is_file():
                errors.append(ValidationError.PATH_NOT_FILE)
                error_details.append(f"Include path is not a file: {file_path}")
            elif not os.access(str(full_path), os.R_OK):
                errors.append(ValidationError.FILE_NOT_READABLE)
                error_details.append(f"Include file is not readable: {file_path}")
    
    # Validate ignore directories exist (warn if they don't)
    if args.ignore_dirs:
        ignore_dirs_list = parse_comma_separated_list(args.ignore_dirs)
        base_dir = Path(args.directories[0]) if args.directories else Path.cwd()
        
        for ignore_dir in ignore_dirs_list:
            if not ignore_dir.strip():
                continue
                
            if Path(ignore_dir).is_absolute():
                ignore_path = Path(ignore_dir)
            else:
                ignore_path = base_dir / ignore_dir
            
            if not ignore_path.exists():
                warnings.append(f"Ignore directory does not exist (will be skipped): {ignore_dir}")
            elif not ignore_path.is_dir():
                errors.append(ValidationError.PATH_NOT_DIRECTORY)
                error_details.append(f"Ignore path is not a directory: {ignore_dir}")
    
    # Validate glob patterns are syntactically correct
    if args.glob:
        import glob as glob_module
        glob_patterns = parse_comma_separated_list(args.glob)
        for pattern in glob_patterns:
            if not pattern.strip():
                continue
            try:
                # Test the pattern by attempting to compile it
                # This catches basic syntax errors
                glob_module.glob(pattern, recursive=True)
            except Exception as e:
                errors.append(ValidationError.INVALID_GLOB_PATTERN)
                error_details.append(f"Invalid glob pattern '{pattern}': {e}")
    
    # Validate exclude patterns are syntactically correct
    if args.exclude_patterns:
        import glob as glob_module
        exclude_patterns = parse_comma_separated_list(args.exclude_patterns)
        for pattern in exclude_patterns:
            if not pattern.strip():
                continue
            try:
                glob_module.glob(pattern, recursive=True)
            except Exception as e:
                errors.append(ValidationError.INVALID_EXCLUDE_PATTERN)
                error_details.append(f"Invalid exclude pattern '{pattern}': {e}")
    
    # Validate extensions don't have dots
    if args.extensions:
        extensions = parse_comma_separated_list(args.extensions)
        for ext in extensions:
            if ext.startswith('.'):
                errors.append(ValidationError.EXTENSION_HAS_DOT)
                error_details.append(f"Extension should not include dot: '{ext}' (use '{ext[1:]}' instead)")
            if not ext.strip():
                errors.append(ValidationError.EMPTY_EXTENSION)
                error_details.append("Empty extension found in extensions list")
    
    # Validate exclude extensions don't have dots
    if args.exclude_extensions:
        exclude_extensions = parse_comma_separated_list(args.exclude_extensions)
        for ext in exclude_extensions:
            if ext.startswith('.'):
                errors.append(ValidationError.EXTENSION_HAS_DOT)
                error_details.append(f"Exclude extension should not include dot: '{ext}' (use '{ext[1:]}' instead)")
            if not ext.strip():
                errors.append(ValidationError.EMPTY_EXTENSION)
                error_details.append("Empty extension found in exclude-extensions list")
    
    # Validate max_depth is positive
    if args.max_depth is not None and args.max_depth < 1:
        errors.append(ValidationError.INVALID_MAX_DEPTH)
        error_details.append(f"Max depth must be positive: {args.max_depth}")
    
    # Validate output path is writable (if not stdio)
    if args.output and args.output != "stdio":
        try:
            from .utils import sanitize_output_path
            output_path = sanitize_output_path(args.output)
            output_dir = output_path.parent
            
            # Check if directory exists or can be created
            if not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError) as e:
                    errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
                    error_details.append(f"Cannot create output directory {output_dir}: {e}")
            elif not os.access(str(output_dir), os.W_OK):
                errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
                error_details.append(f"Output directory is not writable: {output_dir}")
            
            # Check if we can write to the output file
            if output_path.exists() and not os.access(str(output_path), os.W_OK):
                errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
                error_details.append(f"Output file exists but is not writable: {output_path}")
                
        except Exception as e:
            errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
            error_details.append(f"Invalid output path '{args.output}': {e}")
    
    # Validate archive format dependencies
    if args.archive:
        if args.output == "stdio":
            errors.append(ValidationError.ARCHIVE_WITH_STDIO)
            error_details.append("Cannot create archive when output is stdio")
        
        if args.archive == "tar.gz":
            try:
                import tarfile
            except ImportError:
                errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
                error_details.append("tar.gz archive format requires tarfile module")
        elif args.archive == "zip":
            try:
                import zipfile
            except ImportError:
                errors.append(ValidationError.OUTPUT_NOT_WRITABLE)
                error_details.append("zip archive format requires zipfile module")
    
    # Validate conflicting options
    if args.no_dump and args.manifest:
        errors.append(ValidationError.CONFLICTING_OPTIONS)
        error_details.append("Cannot use both --no-dump and --manifest (both disable content output)")
    
    if args.outline and not any([
        args.extensions and any(ext in ['py', 'python'] for ext in parse_comma_separated_list(args.extensions)),
        args.all,
        args.include_files and any(f.endswith('.py') for f in parse_comma_separated_list(args.include_files or ""))
    ]):
        warnings.append("--outline specified but no Python files will be processed")
    
    # Return structured result
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        error_details=error_details,
        warnings=warnings
    )
    """
    Validate command line arguments for consistency and correctness.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        tuple: (is_valids, error_message)
    """
    errors = []
    
    # Validate we have something to process - BUT skip this check if using UI
    if not args.ui and not args.extensions and not args.all and not args.glob:
        errors.append("No extensions or glob provided and --all flag not set. No files to process. "
                     "Use --extensions, --glob, --include-files, --all, or --ui to specify what to include.")
    
    # Validate directories exist
    for directory in args.directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            errors.append(f"Directory does not exist: {directory}")
        elif not dir_path.is_dir():
            errors.append(f"Path is not a directory: {directory}")
        elif not os.access(directory, os.R_OK):
            errors.append(f"Directory is not readable: {directory}")
    
    # Validate specific include files exist
    if args.include_files:
        include_files = parse_comma_separated_list(args.include_files)
        for file_path in include_files:
            if not file_path.strip():
                continue
                
            # Handle both absolute and relative paths
            if Path(file_path).is_absolute():
                full_path = Path(file_path)
            else:
                # Resolve relative to first directory or cwd
                base_dir = Path(args.directories[0]) if args.directories else Path.cwd()
                full_path = base_dir / file_path
            
            if not full_path.exists():
                errors.append(f"Include file does not exist: {file_path} (resolved to: {full_path})")
            elif not full_path.is_file():
                errors.append(f"Include path is not a file: {file_path}")
            elif not os.access(str(full_path), os.R_OK):
                errors.append(f"Include file is not readable: {file_path}")
    
    # Validate ignore directories exist (warn if they don't)
    if args.ignore_dirs:
        ignore_dirs_list = parse_comma_separated_list(args.ignore_dirs)
        base_dir = Path(args.directories[0]) if args.directories else Path.cwd()
        
        for ignore_dir in ignore_dirs_list:
            if not ignore_dir.strip():
                continue
                
            if Path(ignore_dir).is_absolute():
                ignore_path = Path(ignore_dir)
            else:
                ignore_path = base_dir / ignore_dir
            
            if not ignore_path.exists():
                logging.warning(f"Ignore directory does not exist (will be skipped): {ignore_dir}")
            elif not ignore_path.is_dir():
                errors.append(f"Ignore path is not a directory: {ignore_dir}")
    
    # Validate glob patterns are syntactically correct
    if args.glob:
        import glob as glob_module
        glob_patterns = parse_comma_separated_list(args.glob)
        for pattern in glob_patterns:
            if not pattern.strip():
                continue
            try:
                # Test the pattern by attempting to compile it
                # This catches basic syntax errors
                glob_module.glob(pattern, recursive=True)
            except Exception as e:
                errors.append(f"Invalid glob pattern '{pattern}': {e}")
    
    # Validate exclude patterns are syntactically correct
    if args.exclude_patterns:
        import glob as glob_module
        exclude_patterns = parse_comma_separated_list(args.exclude_patterns)
        for pattern in exclude_patterns:
            if not pattern.strip():
                continue
            try:
                glob_module.glob(pattern, recursive=True)
            except Exception as e:
                errors.append(f"Invalid exclude pattern '{pattern}': {e}")
    
    # Validate extensions don't have dots
    if args.extensions:
        extensions = parse_comma_separated_list(args.extensions)
        for ext in extensions:
            if ext.startswith('.'):
                errors.append(f"Extension should not include dot: '{ext}' (use '{ext[1:]}' instead)")
            if not ext.strip():
                errors.append("Empty extension found in extensions list")
    
    # Validate exclude extensions don't have dots
    if args.exclude_extensions:
        exclude_extensions = parse_comma_separated_list(args.exclude_extensions)
        for ext in exclude_extensions:
            if ext.startswith('.'):
                errors.append(f"Exclude extension should not include dot: '{ext}' (use '{ext[1:]}' instead)")
            if not ext.strip():
                errors.append("Empty extension found in exclude-extensions list")
    
    # Validate max_depth is positive
    if args.max_depth is not None and args.max_depth < 1:
        errors.append(f"Max depth must be positive: {args.max_depth}")
    
    # Validate output path is writable (if not stdio)
    if args.output and args.output != "stdio":
        try:
            output_path = sanitize_output_path(args.output)
            output_dir = output_path.parent
            
            # Check if directory exists or can be created
            if not output_dir.exists():
                try:
                    output_dir.mkdir(parents=True, exist_ok=True)
                except (OSError, PermissionError) as e:
                    errors.append(f"Cannot create output directory {output_dir}: {e}")
            elif not os.access(str(output_dir), os.W_OK):
                errors.append(f"Output directory is not writable: {output_dir}")
            
            # Check if we can write to the output file
            if output_path.exists() and not os.access(str(output_path), os.W_OK):
                errors.append(f"Output file exists but is not writable: {output_path}")
                
        except Exception as e:
            errors.append(f"Invalid output path '{args.output}': {e}")
    
    # Validate archive format dependencies
    if args.archive:
        if args.output == "stdio":
            errors.append("Cannot create archive when output is stdio")
        
        if args.archive == "tar.gz":
            try:
                import tarfile
            except ImportError:
                errors.append("tar.gz archive format requires tarfile module")
        elif args.archive == "zip":
            try:
                import zipfile
            except ImportError:
                errors.append("zip archive format requires zipfile module")
    
    # Validate conflicting options
    if args.no_dump and args.manifest:
        errors.append("Cannot use both --no-dump and --manifest (both disable content output)")
    
    if args.outline and not any([
        args.extensions and any(ext in ['py', 'python'] for ext in parse_comma_separated_list(args.extensions)),
        args.all,
        args.include_files and any(f.endswith('.py') for f in parse_comma_separated_list(args.include_files or ""))
    ]):
        logging.warning("--outline specified but no Python files will be processed")
    
    # Return structured result
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        error_details=error_details,
        warnings=warnings
    )