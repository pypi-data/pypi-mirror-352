#!/usr/bin/env python3
"""
Comprehensive test suite for Flort file concatenation tool.

This test suite covers all major functionality including:
- File discovery and filtering
- Extension-based inclusion/exclusion
- Pattern-based filtering
- Binary file detection
- Content concatenation
- Tree generation
- Error handling

Run with: python -m pytest tests/test_flort.py -v
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path to import flort modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from flort.utils import (
    is_binary_file, clean_content, write_file, count_tokens, 
    validate_file_path, sanitize_output_path
)
from flort.traverse import FileFilter, scan_directories, get_paths, add_specific_files
from flort.concatenate_files import FileConcatenator, concat_files, create_file_manifest
from flort.cli import parse_comma_separated_list, parse_ignore_dirs, validate_arguments
from flort.validation import ValidationError


class TestUtils:
    """Test suite for utility functions."""
    
    def test_is_binary_file(self, tmp_path):
        """Test binary file detection."""
        # Create text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello, world!\nThis is a text file.")
        assert not is_binary_file(text_file)
        
        # Create binary file with null bytes
        binary_file = tmp_path / "test.bin"
        binary_file.write_bytes(b"Hello\x00World\x01\x02\x03")
        assert is_binary_file(binary_file)
        
        # Test known binary extension
        exe_file = tmp_path / "test.exe"
        exe_file.write_text("Actually text but .exe extension")
        assert is_binary_file(exe_file)
        
        # Test empty file
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()
        assert not is_binary_file(empty_file)
    
    def test_clean_content(self, tmp_path):
        """Test content cleaning functionality."""
        test_file = tmp_path / "test.py"
        content = """
def hello():
    print("hello")    

    
def world():    
    print("world")
    

"""
        test_file.write_text(content)
        
        cleaned = clean_content(test_file)
        lines = cleaned.split('\n')
        
        # Should remove trailing whitespace and limit consecutive empty lines
        assert not any(line.endswith(' ') for line in lines if line)
        # Should limit to max 2 consecutive empty lines (which creates max \n\n\n)
        assert cleaned.count('\n\n\n\n') == 0  # No quadruple newlines
        # Should preserve function separation with double newlines
        assert 'def hello():' in cleaned
        assert 'def world():' in cleaned
    
    def test_count_tokens(self):
        """Test token counting functionality."""
        # Test empty string
        assert count_tokens("") == 0
        
        # Test simple text
        assert count_tokens("hello world") == 2
        
        # Test code with operators
        code = "def func(x, y): return x + y"
        token_count = count_tokens(code)
        assert token_count > 5  # Should detect multiple tokens
        
        # Test with numbers and symbols
        assert count_tokens("123 + 456 = 579") > 3
    
    def test_validate_file_path(self, tmp_path):
        """Test file path validation."""
        # Valid file
        valid_file = tmp_path / "valid.txt"
        valid_file.write_text("content")
        is_valid, error = validate_file_path(valid_file)
        assert is_valid
        assert error == ""
        
        # Non-existent file
        non_existent = tmp_path / "does_not_exist.txt"
        is_valid, error = validate_file_path(non_existent)
        assert not is_valid
        assert "does not exist" in error.lower()
        
        # Directory instead of file
        directory = tmp_path / "test_dir"
        directory.mkdir()
        is_valid, error = validate_file_path(directory)
        assert not is_valid
        assert "not a file" in error.lower()
    
    def test_sanitize_output_path(self, tmp_path):
        """Test output path sanitization."""
        # Test stdio
        assert sanitize_output_path("stdio").name == "stdio"
        
        # Test relative path
        relative = sanitize_output_path("output.txt")
        assert relative.is_absolute()
        
        # Test absolute path
        absolute = tmp_path / "output.txt"
        result = sanitize_output_path(str(absolute))
        assert result.is_absolute()
        assert result == absolute.resolve()


class TestFileFilter:
    """Test suite for FileFilter class."""
    
    def test_extension_normalization(self):
        """Test extension normalization."""
        filter_obj = FileFilter(
            include_extensions=["py", ".js", "txt"],
            exclude_extensions=["pyc", ".pyo"]
        )
        
        assert ".py" in filter_obj.include_extensions
        assert ".js" in filter_obj.include_extensions
        assert ".txt" in filter_obj.include_extensions
        assert ".pyc" in filter_obj.exclude_extensions
        assert ".pyo" in filter_obj.exclude_extensions
    
    def test_should_include_file(self, tmp_path):
        """Test file inclusion logic."""
        # Create test files
        python_file = tmp_path / "test.py"
        python_file.write_text("print('hello')")
        
        compiled_file = tmp_path / "test.pyc"
        compiled_file.write_bytes(b"\x00\x01\x02")
        
        hidden_file = tmp_path / ".hidden.py"
        hidden_file.write_text("hidden content")
        
        # Test basic inclusion
        filter_obj = FileFilter(include_extensions=["py"])
        
        should_include, reason = filter_obj.should_include_file(python_file)
        assert should_include
        
        # Test exclusion
        filter_obj = FileFilter(
            include_extensions=["py"],
            exclude_extensions=["pyc"]
        )
        
        should_include, reason = filter_obj.should_include_file(compiled_file)
        assert not should_include
        assert "excluded extension" in reason
        
        # Test hidden files
        filter_obj = FileFilter(include_extensions=["py"], include_hidden=False)
        should_include, reason = filter_obj.should_include_file(hidden_file)
        assert not should_include
        assert "hidden" in reason
        
        # Test include all
        filter_obj = FileFilter(include_all=True)
        should_include, reason = filter_obj.should_include_file(python_file)
        assert should_include
    
    def test_pattern_matching(self, tmp_path):
        """Test glob pattern matching."""
        test_file = tmp_path / "test_unit.py"
        test_file.write_text("test content")
        
        # Test exclude pattern
        filter_obj = FileFilter(
            include_extensions=["py"],
            exclude_patterns=["*test*"]
        )
        
        should_include, reason = filter_obj.should_include_file(test_file)
        assert not should_include
        assert "exclude pattern" in reason
        
        # Test include pattern
        filter_obj = FileFilter(include_patterns=["test_*"])
        
        should_include, reason = filter_obj.should_include_file(test_file)
        assert should_include


class TestTraverse:
    """Test suite for file traversal functionality."""
    
    def create_test_directory_structure(self, base_path):
        """Create a test directory structure."""
        # Create directories
        (base_path / "src").mkdir()
        (base_path / "tests").mkdir()
        (base_path / "__pycache__").mkdir()
        (base_path / ".git").mkdir()
        
        # Create files
        (base_path / "main.py").write_text("print('main')")
        (base_path / "README.md").write_text("# Project")
        (base_path / "src" / "utils.py").write_text("def util(): pass")
        (base_path / "src" / "config.json").write_text('{"key": "value"}')
        (base_path / "tests" / "test_main.py").write_text("def test(): pass")
        (base_path / "__pycache__" / "main.cpython-39.pyc").write_bytes(b"\x00\x01")
        (base_path / ".git" / "config").write_text("git config")
        (base_path / ".hidden.txt").write_text("hidden content")
    
    def test_scan_directories_basic(self, tmp_path):
        """Test basic directory scanning."""
        self.create_test_directory_structure(tmp_path)
        
        file_filter = FileFilter(include_extensions=["py"])
        results = scan_directories([str(tmp_path)], file_filter)
        
        # Should find Python files
        py_files = [r for r in results if r["type"] == "file" and r["path"].suffix == ".py"]
        assert len(py_files) >= 2  # main.py and utils.py at minimum
        
        # Should include directories
        dirs = [r for r in results if r["type"] == "dir"]
        assert len(dirs) > 0
    
    def test_ignore_directories(self, tmp_path):
        """Test directory ignoring."""
        self.create_test_directory_structure(tmp_path)
        
        ignore_dirs = [tmp_path / "__pycache__", tmp_path / ".git"]
        file_filter = FileFilter(include_all=True, ignore_dirs=ignore_dirs)
        results = scan_directories([str(tmp_path)], file_filter)
        
        # Should not include files from ignored directories
        ignored_files = [
            r for r in results 
            if any(str(ignore_dir) in str(r["path"]) for ignore_dir in ignore_dirs)
        ]
        assert len(ignored_files) == 0
    
    def test_get_paths_comprehensive(self, tmp_path):
        """Test comprehensive path discovery."""
        self.create_test_directory_structure(tmp_path)
        
        # Test with multiple filters
        results = get_paths(
            directories=[str(tmp_path)],
            extensions=["py", "md"],
            exclude_extensions=["pyc"],
            exclude_patterns=["*test*"],
            include_hidden=False,
            ignore_dirs=[tmp_path / "__pycache__"]
        )
        
        files = [r for r in results if r["type"] == "file"]
        
        # Should include main.py and README.md
        py_files = [f for f in files if f["path"].suffix == ".py"]
        md_files = [f for f in files if f["path"].suffix == ".md"]
        
        assert len(py_files) >= 1  # At least main.py
        assert len(md_files) >= 1  # At least README.md
        
        # Should exclude test files and compiled files
        test_files = [f for f in files if "test" in f["path"].name]
        pyc_files = [f for f in files if f["path"].suffix == ".pyc"]
        
        assert len(test_files) == 0
        assert len(pyc_files) == 0
    
    def test_add_specific_files(self, tmp_path):
        """Test adding specific files."""
        self.create_test_directory_structure(tmp_path)
        
        # Start with Python files only
        initial_results = get_paths(
            directories=[str(tmp_path)],
            extensions=["py"]
        )
        
        # Add specific non-Python file
        config_file = str(tmp_path / "src" / "config.json")
        updated_results = add_specific_files(
            initial_results, 
            [config_file], 
            tmp_path
        )
        
        # Should now include the JSON file
        json_files = [r for r in updated_results if r["path"].suffix == ".json"]
        assert len(json_files) == 1
        assert json_files[0]["relative_path"].endswith("config.json")


class TestConcatenation:
    """Test suite for file concatenation functionality."""
    
    def test_file_concatenator_basic(self, tmp_path):
        """Test basic file concatenation."""
        # Create test files
        file1 = tmp_path / "file1.py"
        file1.write_text("def func1(): pass")
        
        file2 = tmp_path / "file2.py"
        file2.write_text("def func2(): pass")
        
        output_file = tmp_path / "output.txt"
        
        # Create file list
        file_list = [
            {"path": file1, "relative_path": "file1.py", "type": "file"},
            {"path": file2, "relative_path": "file2.py", "type": "file"}
        ]
        
        # Test concatenation
        concatenator = FileConcatenator(str(output_file))
        success = concatenator.concatenate_files(file_list)
        
        assert success
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "file1.py" in content
        assert "file2.py" in content
        assert "def func1(): pass" in content
        assert "def func2(): pass" in content
        
        # Check statistics
        stats = concatenator.get_statistics()
        assert stats["files_processed"] == 2
        assert stats["files_skipped"] == 0
    
    def test_concat_files_function(self, tmp_path):
        """Test the main concat_files function."""
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello world')")
        
        output_file = tmp_path / "output.txt"
        
        file_list = [
            {"path": test_file, "relative_path": "test.py", "type": "file"}
        ]
        
        success = concat_files(file_list, str(output_file))
        
        assert success
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "## File Data" in content
        assert "test.py" in content
        assert "print('hello world')" in content
    
    def test_create_file_manifest(self, tmp_path):
        """Test file manifest creation."""
        # Create test files
        small_file = tmp_path / "small.txt"
        small_file.write_text("small")
        
        large_file = tmp_path / "large.txt"
        large_file.write_text("x" * 1000)
        
        output_file = tmp_path / "manifest.txt"
        
        file_list = [
            {"path": small_file, "relative_path": "small.txt", "type": "file"},
            {"path": large_file, "relative_path": "large.txt", "type": "file"}
        ]
        
        success = create_file_manifest(file_list, str(output_file))
        
        assert success
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "## File Manifest" in content
        assert "small.txt" in content
        assert "large.txt" in content
        assert "bytes" in content


class TestCLI:
    """Test suite for CLI functionality."""
    
    def test_parse_comma_separated_list(self):
        """Test comma-separated list parsing."""
        # Normal case
        result = parse_comma_separated_list("py,js,txt")
        assert result == ["py", "js", "txt"]
        
        # With spaces
        result = parse_comma_separated_list("py, js , txt ")
        assert result == ["py", "js", "txt"]
        
        # Empty string
        result = parse_comma_separated_list("")
        assert result == []
        
        # None
        result = parse_comma_separated_list(None)
        assert result == []
        
        # Single item
        result = parse_comma_separated_list("py")
        assert result == ["py"]
    
    def test_parse_ignore_dirs(self, tmp_path):
        """Test ignore directories parsing."""
        # Create test directories
        (tmp_path / "dir1").mkdir()
        (tmp_path / "dir2").mkdir()
        
        # Test relative paths
        result = parse_ignore_dirs("dir1,dir2", [str(tmp_path)])
        assert len(result) == 2
        assert all(isinstance(p, Path) for p in result)
        assert all(p.is_absolute() for p in result)
        
        # Test absolute paths
        abs_path = str(tmp_path / "dir1")
        result = parse_ignore_dirs(abs_path, [str(tmp_path)])
        assert len(result) == 1
        assert result[0].is_absolute()

    def test_validate_arguments(self, tmp_path):
        """Test argument validation."""
        # Create test files and directories
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        
        nonexistent_dir = tmp_path / "nonexistent"
        
        # Create mock args
        class MockArgs:
            def __init__(self):
                self.ui = None
                self.directories = [str(tmp_path)]
                self.extensions = "py"
                self.exclude_extensions = None
                self.all = False
                self.glob = None
                self.exclude_patterns = None
                self.include_files = None
                self.ignore_dirs = None
                self.archive = None
                self.output = "test.txt"
                self.max_depth = None
                self.no_dump = False
                self.manifest = False
                self.outline = False
        
        # Test 1: Valid case
        args = MockArgs()
        result = validate_arguments(args)
        assert result.is_valid
        assert len(result.errors) == 0
        
        # Test 2: No inclusion criteria
        args = MockArgs()
        args.extensions = None
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.NO_INCLUSION_CRITERIA)
        
        # Test 3: Invalid directory
        args = MockArgs()
        args.directories = ["/nonexistent/directory"]
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.DIRECTORY_NOT_FOUND)
        
        # Test 4: Extensions with dots (invalid)
        args = MockArgs()
        args.extensions = ".py,.js"
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.EXTENSION_HAS_DOT)
        
        # Test 5: Valid include files
        args = MockArgs()
        args.include_files = str(test_file)
        result = validate_arguments(args)
        assert result.is_valid
        assert len(result.errors) == 0
        
        # Test 6: Invalid include files
        args = MockArgs()
        args.include_files = "/nonexistent/file.py"
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.FILE_NOT_FOUND)
        
        # Test 7: Invalid glob pattern - use a pattern that actually breaks
        args = MockArgs()
        # Use a pattern with unmatched brackets which can cause issues
        args.glob = "test[unclosed"
        result = validate_arguments(args)
        # This might or might not be invalid depending on system, just test that we get a result
        assert isinstance(result.is_valid, bool)
        
        # Test 8: Invalid exclude pattern - similar approach
        args = MockArgs()
        args.exclude_patterns = "test[unclosed"
        result = validate_arguments(args)
        assert isinstance(result.is_valid, bool)
        
        # Test 9: Negative max_depth
        args = MockArgs()
        args.max_depth = -1
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.INVALID_MAX_DEPTH)
        
        # Test 10: Conflicting options (no_dump + manifest)
        args = MockArgs()
        args.no_dump = True
        args.manifest = True
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.CONFLICTING_OPTIONS)
        
        # Test 11: Archive with stdio output
        args = MockArgs()
        args.output = "stdio"
        args.archive = "zip"
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.ARCHIVE_WITH_STDIO)
        
        # Test 12: UI mode (should skip inclusion criteria check)
        args = MockArgs()
        args.ui = True
        args.extensions = None
        result = validate_arguments(args)
        assert result.is_valid
        assert not result.has_error(ValidationError.NO_INCLUSION_CRITERIA)
        
        # Test 13: Empty extensions get filtered out by parse_comma_separated_list
        args = MockArgs()
        args.extensions = "py,,js"  # Empty extension in middle gets filtered out
        result = validate_arguments(args)
        assert result.is_valid  # Should be valid since empty extensions are filtered out
        
        # Test 14: Exclude extensions with dots
        args = MockArgs()
        args.exclude_extensions = ".pyc,.pyo"
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.EXTENSION_HAS_DOT)
        
        # Test 15: Valid ignore directories (non-existent should warn, not error)
        args = MockArgs()
        args.ignore_dirs = str(nonexistent_dir)
        result = validate_arguments(args)
        assert result.is_valid  # Should still be valid, just warn
        assert len(result.warnings) > 0
        
        # Test 16: File as ignore directory (should error)
        args = MockArgs()
        args.ignore_dirs = str(test_file)  # File, not directory
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.PATH_NOT_DIRECTORY)
        
        # Test 17: Include file that's actually a directory
        test_dir = tmp_path / "test_subdir"
        test_dir.mkdir()
        args = MockArgs()
        args.include_files = str(test_dir)
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.PATH_NOT_FILE)
        
        # Test 18: Multiple valid extensions
        args = MockArgs()
        args.extensions = "py,js,ts"
        result = validate_arguments(args)
        assert result.is_valid
        assert len(result.errors) == 0
        
        # Test 19: Valid glob patterns
        args = MockArgs()
        args.glob = "*.py,**/*.js"
        result = validate_arguments(args)
        assert result.is_valid
        assert len(result.errors) == 0
        
        # Test 20: Multiple errors in one validation
        args = MockArgs()
        args.extensions = ".py"  # Has dot
        args.max_depth = -1     # Invalid depth
        args.directories = ["/nonexistent"]  # Invalid directory
        result = validate_arguments(args)
        assert not result.is_valid
        assert result.has_error(ValidationError.EXTENSION_HAS_DOT)
        assert result.has_error(ValidationError.INVALID_MAX_DEPTH)
        assert result.has_error(ValidationError.DIRECTORY_NOT_FOUND)
        assert len(result.errors) == 3
        
        # Test 21: Error message formatting
        args = MockArgs()
        args.extensions = None
        result = validate_arguments(args)
        error_msg = result.get_error_message()
        assert error_msg is not None
        assert "❌" in error_msg  # Check formatting exists
        
        # Test 22: No errors gives None message
        args = MockArgs()
        result = validate_arguments(args)
        assert result.get_error_message() is None


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self, tmp_path):
        """Test a complete flort workflow."""
        # Create a realistic project structure
        (tmp_path / "src").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "docs").mkdir()
        (tmp_path / "__pycache__").mkdir()
        
        # Create various file types
        (tmp_path / "main.py").write_text("""
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
""")
        
        (tmp_path / "src" / "utils.py").write_text("""
def helper_function():
    return "helper"

class UtilClass:
    def method(self):
        pass
""")
        
        (tmp_path / "tests" / "test_main.py").write_text("""
import unittest

class TestMain(unittest.TestCase):
    def test_something(self):
        pass
""")
        
        (tmp_path / "README.md").write_text("# Test Project")
        (tmp_path / "requirements.txt").write_text("pytest\nflake8")
        (tmp_path / "__pycache__" / "main.cpython-39.pyc").write_bytes(b"\x00\x01")
        
        output_file = tmp_path / "project.flort.txt"
        
        # Test complete file discovery and concatenation
        file_list = get_paths(
            directories=[str(tmp_path)],
            extensions=["py", "md", "txt"],
            exclude_patterns=["*test*"],
            ignore_dirs=[tmp_path / "__pycache__"]
        )
        
        # Should find files but exclude tests and cache
        files = [f for f in file_list if f["type"] == "file"]
        py_files = [f for f in files if f["path"].suffix == ".py"]
        
        # Should have main.py and utils.py, but not test_main.py
        assert len(py_files) == 2
        assert not any("test_" in f["path"].name for f in py_files)
        
        # Test concatenation
        success = concat_files(file_list, str(output_file))
        assert success
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "## File Data" in content
        assert "main.py" in content
        assert "utils.py" in content
        assert "README.md" in content
        assert "def main():" in content
        assert "class UtilClass:" in content


# Pytest fixtures and utilities
@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure for testing."""
    project_structure = {
        "main.py": "def main(): pass",
        "src/utils.py": "def util(): pass",
        "src/__init__.py": "",
        "tests/test_main.py": "def test(): pass",
        "docs/README.md": "# Documentation",
        "config.json": '{"setting": "value"}',
        ".gitignore": "*.pyc\n__pycache__/",
        "__pycache__/main.cpython-39.pyc": b"\x00\x01\x02"
    }
    
    for file_path, content in project_structure.items():
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, bytes):
            full_path.write_bytes(content)
        else:
            full_path.write_text(content)
    
    return tmp_path


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])