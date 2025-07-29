"""
Simple Text-Based File Selector

A fallback file selector for when curses is not available.
Provides basic interactive functionality through text prompts.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set


def simple_select_files(
    start_path: str = ".",
    preselected_filters: List[str] = None,
    included_files: List[str] = None,
    ignored_dirs: List[str] = None,
    included_dirs: List[str] = None
) -> Optional[Dict[str, List[str]]]:
    """
    Simple text-based file selector as fallback for curses UI.
    
    Args:
        start_path: Starting directory path
        preselected_filters: Pre-selected file extensions
        included_files: Pre-included specific files
        ignored_dirs: Pre-ignored directories
        included_dirs: Pre-included directories
        
    Returns:
        dict: Selection results or None if cancelled
    """
    print("\n🔧 Flort Simple File Selector")
    print("=" * 50)
    print("Interactive file selection (text-based fallback)")
    
    # Discover file types in the directory
    print(f"\n🔍 Discovering file types in {start_path}...")
    discovered_types = discover_file_types_simple(start_path)
    
    if discovered_types:
        print(f"📋 Found {len(discovered_types)} file types:")
        for i, ext in enumerate(discovered_types[:20], 1):  # Show first 20
            print(f"  {i:2d}. {ext}")
        if len(discovered_types) > 20:
            print(f"  ... and {len(discovered_types) - 20} more")
    else:
        print("❌ No file types discovered")
    
    # Initialize with discovery or preselected
    if preselected_filters:
        file_types = set(preselected_filters)
        print(f"\n🎯 Using preselected filters: {', '.join(file_types)}")
    else:
        # Auto-select common code types
        common_code_types = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.css', '.html', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.md', '.txt', '.yml', '.yaml', '.json', '.xml'}
        auto_selected = [ext for ext in discovered_types if ext in common_code_types]
        
        if auto_selected:
            file_types = set(auto_selected)
            print(f"\n🎯 Auto-selected common code types: {', '.join(sorted(file_types))}")
        else:
            # Offer to select from discovered types
            file_types = set()
            print(f"\n🤔 No common code types found. Select from discovered types:")
            if discovered_types:
                print("Enter numbers (comma-separated) or 'all' for all types:")
                try:
                    choice = input("❓ Your choice: ").strip().lower()
                    if choice == 'all':
                        file_types = set(discovered_types)
                    elif choice:
                        numbers = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
                        file_types = {discovered_types[i-1] for i in numbers if 1 <= i <= len(discovered_types)}
                except (ValueError, IndexError, KeyboardInterrupt):
                    file_types = set(discovered_types[:5])  # Default to first 5
            
            if not file_types:
                file_types = set(discovered_types[:5])  # Fallback
                print(f"🎯 Using default selection: {', '.join(sorted(file_types))}")
    
    selected_files = set(included_files or [])
    ignored_directories = set(ignored_dirs or [])
    selected_dirs = set(included_dirs or [start_path])
    
    while True:
        print("\n📋 Current Configuration:")
        print(f"  Start Path: {start_path}")
        print(f"  File Types: {', '.join(sorted(file_types)) if file_types else 'All files'}")
        print(f"  Selected Files: {len(selected_files)} files")
        print(f"  Ignored Dirs: {len(ignored_directories)} directories")
        print(f"  Selected Dirs: {', '.join(selected_dirs)}")
        
        print("\n📝 Options:")
        print("  1. Add file extensions")
        print("  2. Remove file extensions") 
        print("  3. Quick-select common types (py,js,md,txt)")
        print("  4. Select from discovered types")
        print("  5. Add specific files")
        print("  6. Remove specific files")
        print("  7. Add ignored directories")
        print("  8. Remove ignored directories")
        print("  9. Preview selected files")
        print("  0. Use current selection")
        print("  q. Cancel")
        
        try:
            choice = input("\n❓ Choose option: ").strip().lower()
            
            if choice == '1':
                extensions = input("📝 Enter file extensions (comma-separated, no dots): ").strip()
                if extensions:
                    new_exts = [f".{ext.strip().lstrip('.')}" for ext in extensions.split(',') if ext.strip()]
                    file_types.update(new_exts)
                    print(f"✅ Added extensions: {', '.join(new_exts)}")
            
            elif choice == '2':
                if file_types:
                    print("Current extensions:", ', '.join(sorted(file_types)))
                    ext_to_remove = input("📝 Enter extension to remove: ").strip()
                    if ext_to_remove:
                        if not ext_to_remove.startswith('.'):
                            ext_to_remove = '.' + ext_to_remove
                        if ext_to_remove in file_types:
                            file_types.remove(ext_to_remove)
                            print(f"✅ Removed extension: {ext_to_remove}")
                        else:
                            print(f"❌ Extension not found: {ext_to_remove}")
                else:
                    print("❌ No extensions to remove")
            
            elif choice == '3':
                common_types = {'.py', '.js', '.ts', '.md', '.txt', '.json', '.yml', '.css', '.html'}
                available_common = [ext for ext in common_types if ext in discovered_types]
                if available_common:
                    file_types.update(available_common)
                    print(f"✅ Added common types: {', '.join(sorted(available_common))}")
                else:
                    print("❌ No common code types found in directory")
            
            elif choice == '4':
                if discovered_types:
                    print("\n📋 Discovered file types:")
                    for i, ext in enumerate(discovered_types, 1):
                        indicator = "✓" if ext in file_types else " "
                        print(f"  {indicator} {i:2d}. {ext}")
                    
                    print("\nEnter numbers to toggle (comma-separated):")
                    try:
                        numbers_input = input("❓ Numbers: ").strip()
                        if numbers_input:
                            numbers = [int(x.strip()) for x in numbers_input.split(',') if x.strip().isdigit()]
                            for num in numbers:
                                if 1 <= num <= len(discovered_types):
                                    ext = discovered_types[num-1]
                                    if ext in file_types:
                                        file_types.remove(ext)
                                        print(f"➖ Removed: {ext}")
                                    else:
                                        file_types.add(ext)
                                        print(f"➕ Added: {ext}")
                    except ValueError:
                        print("❌ Please enter valid numbers")
                else:
                    print("❌ No file types discovered")
            
            elif choice == '5':
                files = input("📝 Enter file paths (comma-separated): ").strip()
                if files:
                    new_files = [f.strip() for f in files.split(',') if f.strip()]
                    # Validate files exist
                    valid_files = []
                    for file_path in new_files:
                        if Path(file_path).exists():
                            valid_files.append(file_path)
                        else:
                            print(f"⚠️  File not found: {file_path}")
                    
                    if valid_files:
                        selected_files.update(valid_files)
                        print(f"✅ Added files: {', '.join(valid_files)}")
            
            elif choice == '6':
                if selected_files:
                    print("Current files:")
                    for i, file_path in enumerate(selected_files, 1):
                        print(f"  {i}. {file_path}")
                    
                    try:
                        file_num = int(input("📝 Enter file number to remove: ").strip())
                        file_list = list(selected_files)
                        if 1 <= file_num <= len(file_list):
                            removed_file = file_list[file_num - 1]
                            selected_files.remove(removed_file)
                            print(f"✅ Removed file: {removed_file}")
                        else:
                            print("❌ Invalid file number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("❌ No files to remove")
            
            elif choice == '7':
                dirs = input("📝 Enter directories to ignore (comma-separated): ").strip()
                if dirs:
                    new_dirs = [d.strip() for d in dirs.split(',') if d.strip()]
                    ignored_directories.update(new_dirs)
                    print(f"✅ Added ignored directories: {', '.join(new_dirs)}")
            
            elif choice == '8':
                if ignored_directories:
                    print("Current ignored directories:")
                    for i, dir_path in enumerate(ignored_directories, 1):
                        print(f"  {i}. {dir_path}")
                    
                    try:
                        dir_num = int(input("📝 Enter directory number to remove: ").strip())
                        dir_list = list(ignored_directories)
                        if 1 <= dir_num <= len(dir_list):
                            removed_dir = dir_list[dir_num - 1]
                            ignored_directories.remove(removed_dir)
                            print(f"✅ Removed ignored directory: {removed_dir}")
                        else:
                            print("❌ Invalid directory number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("❌ No ignored directories to remove")
            
            elif choice == '9':
                print("\n🔍 Preview of Selected Files:")
                preview_files(start_path, file_types, selected_files, ignored_directories)
            
            elif choice == '0':
                print("✅ Using current selection")
                break
            
            elif choice == 'q':
                print("❌ Selection cancelled")
                return None
            
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled")
            return None
        except EOFError:
            print("\n❌ Selection cancelled")
            return None
    
    # Return results in the same format as curses selector
    return {
        "selected": list(selected_dirs),
        "ignored": list(ignored_directories),
        "file_types": list(file_types)
    }


def discover_file_types_simple(path: str) -> List[str]:
    """Discover all file types in the given path."""
    extensions = set()
    try:
        for file_path in Path(path).rglob("*"):
            if file_path.is_file():
                try:
                    file_path.stat()  # Check accessibility
                    ext = file_path.suffix.lower()
                    if ext:
                        extensions.add(ext)
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        pass
    return sorted(extensions)
    
    while True:
        print("\n📋 Current Configuration:")
        print(f"  Start Path: {start_path}")
        print(f"  File Types: {', '.join(file_types) if file_types else 'None'}")
        print(f"  Selected Files: {len(selected_files)} files")
        print(f"  Ignored Dirs: {len(ignored_directories)} directories")
        print(f"  Selected Dirs: {', '.join(selected_dirs)}")
        
        print("\n📝 Options:")
        print("  1. Add file extensions (e.g., py,js,md)")
        print("  2. Remove file extensions")
        print("  3. Add specific files")
        print("  4. Remove specific files")
        print("  5. Add ignored directories")
        print("  6. Remove ignored directories")
        print("  7. Preview selected files")
        print("  8. Use current selection")
        print("  9. Cancel")
        
        try:
            choice = input("\n❓ Choose option (1-9): ").strip()
            
            if choice == '1':
                extensions = input("📝 Enter file extensions (comma-separated, no dots): ").strip()
                if extensions:
                    new_exts = [f".{ext.strip().lstrip('.')}" for ext in extensions.split(',') if ext.strip()]
                    file_types.update(new_exts)
                    print(f"✅ Added extensions: {', '.join(new_exts)}")
            
            elif choice == '2':
                if file_types:
                    print("Current extensions:", ', '.join(file_types))
                    ext_to_remove = input("📝 Enter extension to remove: ").strip()
                    if ext_to_remove:
                        if not ext_to_remove.startswith('.'):
                            ext_to_remove = '.' + ext_to_remove
                        if ext_to_remove in file_types:
                            file_types.remove(ext_to_remove)
                            print(f"✅ Removed extension: {ext_to_remove}")
                        else:
                            print(f"❌ Extension not found: {ext_to_remove}")
                else:
                    print("❌ No extensions to remove")
            
            elif choice == '3':
                files = input("📝 Enter file paths (comma-separated): ").strip()
                if files:
                    new_files = [f.strip() for f in files.split(',') if f.strip()]
                    # Validate files exist
                    valid_files = []
                    for file_path in new_files:
                        if Path(file_path).exists():
                            valid_files.append(file_path)
                        else:
                            print(f"⚠️  File not found: {file_path}")
                    
                    if valid_files:
                        selected_files.update(valid_files)
                        print(f"✅ Added files: {', '.join(valid_files)}")
            
            elif choice == '4':
                if selected_files:
                    print("Current files:")
                    for i, file_path in enumerate(selected_files, 1):
                        print(f"  {i}. {file_path}")
                    
                    try:
                        file_num = int(input("📝 Enter file number to remove: ").strip())
                        file_list = list(selected_files)
                        if 1 <= file_num <= len(file_list):
                            removed_file = file_list[file_num - 1]
                            selected_files.remove(removed_file)
                            print(f"✅ Removed file: {removed_file}")
                        else:
                            print("❌ Invalid file number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("❌ No files to remove")
            
            elif choice == '5':
                dirs = input("📝 Enter directories to ignore (comma-separated): ").strip()
                if dirs:
                    new_dirs = [d.strip() for d in dirs.split(',') if d.strip()]
                    ignored_directories.update(new_dirs)
                    print(f"✅ Added ignored directories: {', '.join(new_dirs)}")
            
            elif choice == '6':
                if ignored_directories:
                    print("Current ignored directories:")
                    for i, dir_path in enumerate(ignored_directories, 1):
                        print(f"  {i}. {dir_path}")
                    
                    try:
                        dir_num = int(input("📝 Enter directory number to remove: ").strip())
                        dir_list = list(ignored_directories)
                        if 1 <= dir_num <= len(dir_list):
                            removed_dir = dir_list[dir_num - 1]
                            ignored_directories.remove(removed_dir)
                            print(f"✅ Removed ignored directory: {removed_dir}")
                        else:
                            print("❌ Invalid directory number")
                    except ValueError:
                        print("❌ Please enter a valid number")
                else:
                    print("❌ No ignored directories to remove")
            
            elif choice == '7':
                print("\n🔍 Preview of Selected Files:")
                preview_files(start_path, file_types, selected_files, ignored_directories)
            
            elif choice == '8':
                print("✅ Using current selection")
                break
            
            elif choice == '9':
                print("❌ Selection cancelled")
                return None
            
            else:
                print("❌ Invalid choice. Please enter 1-9.")
                
        except KeyboardInterrupt:
            print("\n❌ Selection cancelled")
            return None
        except EOFError:
            print("\n❌ Selection cancelled")
            return None
    
    # Return results in the same format as curses selector
    return {
        "selected": list(selected_dirs),
        "ignored": list(ignored_directories),
        "file_types": list(file_types)
    }


def preview_files(
    start_path: str, 
    file_types: Set[str], 
    selected_files: Set[str], 
    ignored_dirs: Set[str]
) -> None:
    """
    Preview files that would be selected with current settings.
    
    Args:
        start_path: Base directory path
        file_types: Set of file extensions to include
        selected_files: Set of specifically selected files
        ignored_dirs: Set of directories to ignore
    """
    base_path = Path(start_path)
    
    print(f"\n📁 Scanning from: {base_path}")
    print(f"🎯 File types: {', '.join(file_types) if file_types else 'All'}")
    print(f"🚫 Ignored dirs: {', '.join(ignored_dirs) if ignored_dirs else 'None'}")
    
    matching_files = []
    
    try:
        # Scan for matching files
        for file_path in base_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Check if in ignored directory
            skip = False
            for ignore_dir in ignored_dirs:
                if str(file_path).startswith(str(Path(ignore_dir).resolve())):
                    skip = True
                    break
            
            if skip:
                continue
            
            # Check if matches file types or is specifically selected
            if (file_path.suffix.lower() in file_types or 
                str(file_path) in selected_files or
                not file_types):  # Include all if no types specified
                matching_files.append(file_path)
        
        # Add specifically selected files
        for file_str in selected_files:
            file_path = Path(file_str)
            if file_path.exists() and file_path not in matching_files:
                matching_files.append(file_path)
        
        # Display results
        if matching_files:
            print(f"\n📋 Found {len(matching_files)} matching files:")
            
            # Group by directory for better display
            by_dir = {}
            for file_path in sorted(matching_files):
                dir_name = str(file_path.parent)
                if dir_name not in by_dir:
                    by_dir[dir_name] = []
                by_dir[dir_name].append(file_path.name)
            
            for dir_name, files in by_dir.items():
                print(f"\n  📂 {dir_name}/")
                for file_name in files[:10]:  # Limit to first 10 per directory
                    print(f"    📄 {file_name}")
                if len(files) > 10:
                    print(f"    ... and {len(files) - 10} more files")
        else:
            print("\n❌ No files match current criteria")
            
    except Exception as e:
        print(f"❌ Error scanning files: {e}")
    
    input("\n⏎ Press Enter to continue...")


def test_simple_selector():
    """Test the simple selector functionality."""
    print("🧪 Testing Simple Selector")
    
    result = simple_select_files(
        start_path=".",
        preselected_filters=[".py"],
        included_files=["README.md"]
    )
    
    if result:
        print("\n✅ Test completed successfully")
        print(f"Results: {result}")
    else:
        print("\n❌ Test cancelled")


if __name__ == "__main__":
    test_simple_selector()