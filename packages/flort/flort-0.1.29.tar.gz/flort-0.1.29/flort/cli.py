#!/usr/bin/env python3
"""
Flort - File Concatenation and Project Overview Tool

This module provides functionality to create a consolidated view of a project's
source code by combining multiple files into a single output file. It can generate
directory trees, create Python module outlines, and concatenate source files while
respecting various filtering options.

The tool is particularly useful for:
- Creating project overviews for LLMs
- Generating documentation
- Sharing code in a single file
- Analyzing project structure

Usage:
    flort [DIRECTORY...] [--extension...] [options]

Example:
    flort . --extensions py,js --exclude-extensions pyc --output=project.txt
"""

import os
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .utils import (
    generate_tree, write_file, configure_logging, print_configuration, 
    count_file_tokens, archive_file, sanitize_output_path,
    parse_comma_separated_list, parse_ignore_dirs
)
from .traverse import get_paths, add_specific_files
from .concatenate_files import concat_files, create_file_manifest
from .python_outline import python_outline_files
from .validation import validate_arguments

def get_version() -> str:
    """Get the package version."""
    try:
        # Use importlib.metadata (Python 3.8+) or importlib_metadata for older versions
        try:
            from importlib.metadata import version
        except ImportError:
            from importlib_metadata import version
        return version('flort')
    except Exception:
        return "unknown"


def generate_config_output(
    directories: List[str],
    extensions: List[str],
    exclude_extensions: List[str],
    include_patterns: List[str],
    exclude_patterns: List[str],
    include_files: List[str],
    ignore_dirs: List[Path],
    include_all: bool,
    include_hidden: bool,
    include_binary: bool,
    max_depth: Optional[int],
    output_path: str,
    other_flags: dict
) -> str:
    """
    Generate configuration output showing all settings used.
    
    Args:
        directories: List of directories being processed
        extensions: List of included extensions
        exclude_extensions: List of excluded extensions  
        include_patterns: List of include glob patterns
        exclude_patterns: List of exclude glob patterns
        include_files: List of specifically included files
        ignore_dirs: List of ignored directories
        include_all: Whether all files are included
        include_hidden: Whether hidden files are included
        include_binary: Whether binary files are included
        max_depth: Maximum traversal depth
        output_path: Output file path
        other_flags: Dict of other boolean flags
        
    Returns:
        str: Formatted configuration string
    """
    config_lines = [
        "## Flort Configuration",
        f"Working Directory: {Path.cwd()}",
        f"Output File: {output_path}",
        f"Target Directories: {', '.join(directories)}",
        ""
    ]
    
    # File inclusion criteria
    inclusion_criteria = []
    if include_all:
        inclusion_criteria.append("All files (--all)")
    if extensions:
        inclusion_criteria.append(f"Extensions: {', '.join(extensions)}")
    if include_patterns:
        inclusion_criteria.append(f"Include patterns: {', '.join(include_patterns)}")
    if include_files:
        inclusion_criteria.append(f"Specific files: {', '.join(include_files)}")
    
    if inclusion_criteria:
        config_lines.append("### Inclusion Criteria:")
        for criteria in inclusion_criteria:
            config_lines.append(f"- {criteria}")
        config_lines.append("")
    
    # File exclusion criteria
    exclusion_criteria = []
    if exclude_extensions:
        exclusion_criteria.append(f"Extensions: {', '.join(exclude_extensions)}")
    if exclude_patterns:
        exclusion_criteria.append(f"Patterns: {', '.join(exclude_patterns)}")
    if ignore_dirs:
        exclusion_criteria.append(f"Directories: {', '.join(str(d) for d in ignore_dirs)}")
    if not include_binary:
        exclusion_criteria.append("Binary files (use --include-binary to include)")
    if not include_hidden:
        exclusion_criteria.append("Hidden files (use --hidden to include)")
    
    if exclusion_criteria:
        config_lines.append("### Exclusion Criteria:")
        for criteria in exclusion_criteria:
            config_lines.append(f"- {criteria}")
        config_lines.append("")
    
    # Processing options
    processing_options = []
    if max_depth is not None:
        processing_options.append(f"Maximum depth: {max_depth}")
    if other_flags.get('clean_content', True):
        processing_options.append("Content cleaning: enabled")
    else:
        processing_options.append("Content cleaning: disabled")
    
    # Output options
    output_options = []
    if other_flags.get('no_tree'):
        output_options.append("Directory tree: disabled")
    else:
        output_options.append("Directory tree: enabled")
        
    if other_flags.get('outline'):
        output_options.append("Python outline: enabled")
    else:
        output_options.append("Python outline: disabled")
        
    if other_flags.get('no_dump'):
        output_options.append("File concatenation: disabled")
    elif other_flags.get('manifest'):
        output_options.append("File manifest: enabled (no content)")
    else:
        output_options.append("File concatenation: enabled")
        
    if other_flags.get('archive'):
        output_options.append(f"Archive format: {other_flags['archive']}")
    
    all_options = processing_options + output_options
    if all_options:
        config_lines.append("### Processing Options:")
        for option in all_options:
            config_lines.append(f"- {option}")
        config_lines.append("")
    
    # Detection summary
    only_include_files = (
        include_files and 
        not extensions and 
        not include_all and 
        not include_patterns
    )
    
    if only_include_files:
        config_lines.append("### Mode: Specific Files Only")
        config_lines.append("Directory scanning disabled - only processing specified files")
    else:
        config_lines.append("### Mode: Directory Scanning")
        config_lines.append("Scanning directories with applied filters")
    
    config_lines.extend(["", "---", ""])
    
    return "\n".join(config_lines)




def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Set up and configure the command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description="flort: Create a single file containing all source code from specified "
                   "directories, with comprehensive filtering and organization options.",
        prog='flort',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flort . --extensions py,js,ts                    # Include Python, JavaScript, TypeScript
  flort . --all --exclude-extensions pyc,pyo       # All files except compiled Python
  flort . --extensions py --exclude-patterns "*test*,*cache*"  # Python excluding tests
  flort . --glob "*.py" --include-files config.ini # Glob patterns + specific files
  flort . --extensions py --ignore-dirs __pycache__,venv      # Ignore specific directories
  flort src tests --output project.txt --archive zip         # Multiple dirs with archive
        """
    )

    # Positional arguments
    parser.add_argument(
        'directories', 
        metavar='DIRECTORY',
        nargs='*',
        default=["."],
        help='Directories to process (default: current directory)'
    )

    # Core functionality
    parser.add_argument(
        '-e', '--extensions', 
        type=str,
        help='File extensions to include (comma-separated, no dots: py,js,txt)'
    )
    
    parser.add_argument(
        '--exclude-extensions',
        type=str,
        help='File extensions to exclude (comma-separated, no dots: pyc,pyo,min.js)'
    )
    
    parser.add_argument(
        '-g', '--glob', 
        type=str,
        help='Glob patterns to include (comma-separated: "*.py,src/**/*.js")'
    )
    
    parser.add_argument(
        '--exclude-patterns',
        type=str,
        help='Glob patterns to exclude (comma-separated: "*test*,*cache*,*.min.*")'
    )
    
    parser.add_argument(
        '-f', '--include-files', 
        type=str,
        help='Specific files to include regardless of other filters (comma-separated)'
    )
    
    parser.add_argument(
        '-i', '--ignore-dirs', 
        type=str,
        help='Directories to ignore completely (comma-separated)'
    )

    # Output options
    parser.add_argument(
        '-o', '--output', 
        type=str,
        default=f"{os.path.basename(os.getcwd())}.flort.txt",
        help='Output file path (default: <current_dir>.flort.txt, "stdio" for console)'
    )
    
    parser.add_argument(
        '-z', '--archive', 
        type=str,
        choices=['zip', 'tar.gz'],
        help='Create archive of output file (zip or tar.gz)'
    )

    # Content control flags
    parser.add_argument(
        '-a', '--all', 
        action='store_true',
        help='Include all files regardless of extension (respects exclude filters)'
    )
    
    parser.add_argument(
        '-H', '--hidden', 
        action='store_true',
        help='Include hidden files and directories'
    )
    
    parser.add_argument(
        '--include-binary', 
        action='store_true',
        help='Include binary files (normally excluded for safety)'
    )
    
    parser.add_argument(
        '--max-depth', 
        type=int,
        help='Maximum directory depth to traverse'
    )

    # Output format options
    parser.add_argument(
        '-O', '--outline', 
        action='store_true',
        help='Generate Python class/function outline instead of full source'
    )
    
    parser.add_argument(
        '-n', '--no-dump', 
        action='store_true',
        help='Do not concatenate file contents (directory tree and outline only)'
    )
    
    parser.add_argument(
        '-t', '--no-tree', 
        action='store_true',
        help='Do not generate directory tree'
    )
    
    parser.add_argument(
        '--manifest', 
        action='store_true',
        help='Generate file manifest instead of concatenating content'
    )
    
    parser.add_argument(
        '--clean-content', 
        action='store_true',
        default=True,
        help='Clean whitespace from file content (default: enabled)'
    )
    
    parser.add_argument(
        '--no-clean', 
        dest='clean_content',
        action='store_false',
        help='Do not clean whitespace from file content'
    )
    
    parser.add_argument(
        '--show-config',
        action='store_true',
        help='Show configuration settings at the beginning of the output'
    )

    # Interface options
    parser.add_argument(
        '-u', '--ui', 
        action='store_true',
        help='Launch interactive file selector (discovers and selects files visually)'
    )

    # Utility options
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Enable verbose logging (INFO level)'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'flort {get_version()}',
        help='Show program version and exit'
    )

    return parser


def process_ui_integration(args: argparse.Namespace) -> argparse.Namespace:
    """
    Integrate UI selections with command-line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        argparse.Namespace: Updated arguments with UI selections
    """
    if not args.ui:
        return args
    
    # Try curses-based UI first
    try:
        import curses
        
        try:
            from .curses_selector import select_files
            use_curses = True
        except ImportError:
            use_curses = False
        
        if use_curses:
            print("🎨 Starting interactive file selector (curses-based)...")
        else:
            print("📝 Curses not available, using simple text-based selector...")
            
    except ImportError:
        use_curses = False
        print("📝 Using simple text-based file selector...")
    
    try:
        # Prepare current settings for UI
        current_extensions = parse_comma_separated_list(args.extensions)
        current_include_files = parse_comma_separated_list(args.include_files)
        current_ignore_dirs = parse_ignore_dirs(args.ignore_dirs, args.directories)
        
        # Launch appropriate UI
        if use_curses:
            from .curses_selector import select_files
            result = select_files(
                start_path=args.directories[0] if args.directories else ".",
                preselected_filters=[f".{ext}" for ext in current_extensions],
                included_files=current_include_files,
                ignored_dirs=[str(d) for d in current_ignore_dirs],
                included_dirs=args.directories if args.directories != ["."] else None
            )
        else:
            from .simple_selector import simple_select_files
            result = simple_select_files(
                start_path=args.directories[0] if args.directories else ".",
                preselected_filters=[f".{ext}" for ext in current_extensions],
                included_files=current_include_files,
                ignored_dirs=[str(d) for d in current_ignore_dirs],
                included_dirs=args.directories if args.directories != ["."] else None
            )
        
        if result is None:
            logging.info("UI selection cancelled")
            sys.exit(0)
        
        # Merge UI results with CLI arguments (UI selections are additive)
        ui_extensions = [ext.lstrip('.') for ext in result.get("file_types", []) if ext and ext != "*"]
        if ui_extensions:
            existing_extensions = current_extensions
            combined_extensions = list(set(existing_extensions + ui_extensions))
            args.extensions = ','.join(combined_extensions) if combined_extensions else None
        
        # Add UI ignored directories
        ui_ignored = [Path(p) for p in result.get("ignored", []) if p]
        if ui_ignored:
            existing_ignored = current_ignore_dirs
            combined_ignored = existing_ignored + ui_ignored
            unique_ignored = []
            seen = set()
            for d in combined_ignored:
                d_str = str(d)
                if d_str not in seen:
                    seen.add(d_str)
                    unique_ignored.append(d)
            
            if unique_ignored:
                args.ignore_dirs = ','.join(str(d) for d in unique_ignored)
        
        # Update directories if UI made selections
        ui_selected = [p for p in result.get("selected", []) if Path(p).is_dir()]
        if ui_selected:
            args.directories = ui_selected
        
        logging.info("UI selections integrated with command-line arguments")
        
    except KeyboardInterrupt:
        print("\n❌ UI cancelled by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error in UI integration: {e}")
        print(f"❌ UI failed to start: {e}")
        print("📝 Continuing without interactive mode...")
        args.ui = False  # Disable UI and continue
    
    return args


def exclude_output_file(path_list: List[dict], output_path: str) -> List[dict]:
    """
    Remove the output file from the path list to prevent self-inclusion.
    
    Args:
        path_list: List of path dictionaries
        output_path: Output file path
        
    Returns:
        list: Updated path list with output file excluded
    """
    if output_path == "stdio":
        return path_list
    
    try:
        output_resolved = sanitize_output_path(output_path)
        original_count = len(path_list)
        
        filtered_list = []
        for item in path_list:
            try:
                item_resolved = item["path"].resolve()
                if item_resolved != output_resolved:
                    filtered_list.append(item)
            except Exception as e:
                logging.debug(f"Error resolving path {item['path']}: {e}")
                filtered_list.append(item)  # Include if we can't resolve
        
        excluded_count = original_count - len(filtered_list)
        if excluded_count > 0:
            logging.info(f"Excluded {excluded_count} output file(s) from processing")
        
        return filtered_list
        
    except Exception as e:
        logging.error(f"Error excluding output file: {e}")
        return path_list


def main() -> None:
    """
    Main entry point for the Flort tool.

    This function orchestrates the entire file processing pipeline:
    1. Parse and validate command line arguments
    2. Configure logging and validate inputs
    3. Integrate UI selections if requested
    4. Discover files using the comprehensive filtering system
    5. Generate outputs (tree, outline, concatenation) as requested
    6. Create archives if specified
    7. Report final statistics

    Returns:
        None

    Raises:
        SystemExit: If arguments are invalid or critical errors occur
    """
    # Parse arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Configure logging early
    configure_logging(args.verbose)

    # Parse and prepare arguments
    directories = args.directories
    extensions = parse_comma_separated_list(args.extensions)
    exclude_extensions = parse_comma_separated_list(args.exclude_extensions)
    include_patterns = parse_comma_separated_list(args.glob)
    exclude_patterns = parse_comma_separated_list(args.exclude_patterns)
    include_files = parse_comma_separated_list(args.include_files)
    ignore_dirs = parse_ignore_dirs(args.ignore_dirs, directories)
    


    # Validate arguments
    validation_result = validate_arguments(args)
    if not validation_result.is_valid:
        error_message = validation_result.get_error_message()
        logging.error(error_message)
        parser.print_help()
        sys.exit(1)

    # Process UI integration
    if args.ui:
        args = process_ui_integration(args)
        # Re-validate after UI changes
        validation_result = validate_arguments(args)
        if not validation_result.is_valid:
            error_message = validation_result.get_error_message()
            logging.error(f"Invalid configuration after UI integration: {error_message}")
            sys.exit(1)
    # Sanitize output path
    output_path = sanitize_output_path(args.output)
    output_str = str(output_path) if output_path.name != "stdio" else "stdio"
    
    # Log configuration
    print_configuration(
        directories=directories,
        extensions=extensions,
        exclude_extensions=exclude_extensions,
        exclude_patterns=exclude_patterns,
        include_all=args.all,
        include_hidden=args.hidden,
        ignore_dirs=ignore_dirs,
        include_files=include_files,
        glob_patterns=include_patterns
    )
    
    # Initialize output file with timestamp
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if not write_file(output_str, f"## Florted: {current_datetime}\n", 'w'):
        logging.error(f"Failed to initialize output file: {output_str}")
        sys.exit(1)
    
    # Add configuration output if requested
    if args.show_config:
        config_output = generate_config_output(
            directories=directories,
            extensions=extensions,
            exclude_extensions=exclude_extensions,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            include_files=include_files,
            ignore_dirs=ignore_dirs,
            include_all=args.all,
            include_hidden=args.hidden,
            include_binary=args.include_binary,
            max_depth=args.max_depth,
            output_path=output_str,
            other_flags={
                'clean_content': args.clean_content,
                'no_tree': args.no_tree,
                'outline': args.outline,
                'no_dump': args.no_dump,
                'manifest': args.manifest,
                'archive': args.archive
            }
        )
        if not write_file(output_str, config_output):
            logging.error("Failed to write configuration output")
            sys.exit(1)
    
    # Get file paths using the comprehensive discovery system
    logging.info("Starting file discovery...")
    
    try:
        # If only include_files is specified (no extensions, no --all, no glob), 
        # then ONLY process those files
        only_include_files = (
            include_files and 
            not extensions and 
            not args.all and 
            not include_patterns and
            not args.glob
        )
        
        if only_include_files:
            logging.info("Only processing specifically included files (no directory scanning)")
            path_list = []
            path_list = add_specific_files(path_list, include_files, Path(directories[0]))
        else:
            path_list = get_paths(
                directories=directories,
                extensions=extensions,
                exclude_extensions=exclude_extensions,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                include_all=args.all,
                include_hidden=args.hidden,
                include_binary=args.include_binary,
                ignore_dirs=ignore_dirs,
                include_files=include_files,
                glob_patterns=include_patterns,  # Same as include_patterns for compatibility
                max_depth=args.max_depth
            )
    except Exception as e:
        logging.error(f"Error during file discovery: {e}")
        sys.exit(1)
    
    # Exclude output file from processing
    path_list = exclude_output_file(path_list, output_str)
    
    # Count results
    file_count = len([item for item in path_list if item['type'] == 'file'])
    dir_count = len([item for item in path_list if item['type'] == 'dir'])
    
    if file_count == 0:
        logging.warning("No files found matching criteria")
        if not write_file(output_str, "## No files found matching criteria\n"):
            sys.exit(1)
        print("No files found matching the specified criteria.")
        return
    
    print(f"Processing {file_count} files from {dir_count} directories -> {output_str}")
    
    try:
        # Generate directory tree if not disabled
        if not args.no_tree:
            logging.info("Generating directory tree...")
            if not generate_tree(path_list, output_str):
                logging.error("Failed to generate directory tree")
                sys.exit(1)
        
        # Generate Python outline if requested
        if args.outline:
            logging.info("Generating Python outline...")
            if not python_outline_files(path_list, output_str):
                logging.error("Failed to generate Python outline")
                sys.exit(1)
        
        # Generate file manifest or concatenate files
        if args.manifest:
            logging.info("Generating file manifest...")
            if not create_file_manifest(path_list, output_str):
                logging.error("Failed to create file manifest")
                sys.exit(1)
        elif not args.no_dump:
            logging.info("Concatenating files...")
            if not concat_files(path_list, output_str, args.clean_content):
                logging.error("Failed to concatenate files")
                sys.exit(1)
        
        # Show token count and statistics
        if output_str != "stdio":
            token_info = count_file_tokens(output_str)
            print(f"\nOutput Statistics:\n{token_info}")
        
        # Archive the output file if requested
        if args.archive and output_str != "stdio":
            logging.info(f"Creating {args.archive} archive...")
            archive_path = archive_file(output_str, args.archive)
            if archive_path:
                print(f"Archive created: {archive_path}")
            else:
                logging.warning("Failed to create archive")
        
        print("Flort completed successfully!")
        
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()