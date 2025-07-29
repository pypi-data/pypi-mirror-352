import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

from flort.traverse import get_paths
from flort.utils import is_binary_file, clean_content, write_file, generate_tree
from flort.concatinate_files import concat_files
from flort.python_outline import process_python_file, map_classes_and_functions

class TestFlortTraverse(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))
        
        # Create test file structure
        self.setup_test_files()
        
    def setup_test_files(self):
        """Create a test directory structure with various file types"""
        # Create directories
        os.makedirs(os.path.join(self.test_dir, "subdir"))
        os.makedirs(os.path.join(self.test_dir, ".hidden_dir"))
        
        # Create regular files
        with open(os.path.join(self.test_dir, "test.py"), "w") as f:
            f.write("print('test')")
        with open(os.path.join(self.test_dir, "test.txt"), "w") as f:
            f.write("test content")
        with open(os.path.join(self.test_dir, ".hidden_file"), "w") as f:
            f.write("hidden content")
            
        # Create files in subdirectory
        with open(os.path.join(self.test_dir, "subdir", "sub.py"), "w") as f:
            f.write("def test(): pass")

    def test_get_paths_basic(self):
        """Test basic path traversal with default settings"""
        paths = get_paths(
            directories=[self.test_dir],
            extensions=[".py"],
            include_all=False,
            include_hidden=False
        )
        
        # Should find the main directory, subdirectory, and .py files
        self.assertEqual(len([p for p in paths if p['type'] == 'file']), 2)
        self.assertEqual(len([p for p in paths if p['type'] == 'dir']), 2)

    def test_get_paths_with_hidden(self):
        """Test path traversal including hidden files"""
        paths = get_paths(
            directories=[self.test_dir],
            extensions=[".py"],
            include_all=False,
            include_hidden=True
        )
        
        # Should include hidden directories and files
        hidden_items = [p for p in paths if p['path'].name.startswith('.')]
        self.assertGreater(len(hidden_items), 0)

    def test_get_paths_all_files(self):
        """Test path traversal including all file types"""
        paths = get_paths(
            directories=[self.test_dir],
            extensions=None,
            include_all=True,
            include_hidden=False
        )
        
        # Should find all non-hidden files regardless of extension
        files = [p for p in paths if p['type'] == 'file']
        self.assertGreater(len(files), 2)  # Should find both .py and .txt files

class TestFlortUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))

    def test_is_binary_file(self):
        """Test binary file detection"""
        # Create test files
        text_file = Path(os.path.join(self.test_dir, "text.txt"))
        binary_file = Path(os.path.join(self.test_dir, "binary.bin"))
        
        with open(text_file, 'w') as f:
            f.write("Hello, world!")
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03')
            
        self.assertFalse(is_binary_file(text_file))
        self.assertTrue(is_binary_file(binary_file))

    def test_clean_content(self):
        """Test content cleaning functionality"""
        test_file = Path(os.path.join(self.test_dir, "test.txt"))
        content = "  Line 1  \n\n  Line 2  \n\n\n  Line 3  "
        
        with open(test_file, 'w') as f:
            f.write(content)
            
        cleaned = clean_content(test_file)
        self.assertEqual(cleaned, "Line 1\nLine 2\nLine 3")

    def test_write_file(self):
        """Test file writing functionality"""
        test_file = os.path.join(self.test_dir, "output.txt")
        test_content = "Test content"
        
        # Test writing new file
        write_file(test_file, test_content, 'w')
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), test_content)
            
        # Test appending to file
        write_file(test_file, "\nMore content", 'a')
        with open(test_file, 'r') as f:
            self.assertEqual(f.read(), test_content + "\nMore content")

class TestPythonOutline(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.test_dir))

    def test_process_python_file(self):
        """Test Python file processing for outline generation"""
        test_file = Path(os.path.join(self.test_dir, "test.py"))
        with open(test_file, 'w') as f:
            f.write('''
def test_function(arg1: str, arg2: int = 0) -> bool:
    """Test docstring"""
    return True

class TestClass:
    """Class docstring"""
    def method(self):
        pass
''')
        
        result = process_python_file(test_file)
        self.assertIn("FUNCTION: test_function", result)
        self.assertIn("CLASS: TestClass", result)
        self.assertIn("Test docstring", result)
        self.assertIn("Class docstring", result)

    def test_map_classes_and_functions(self):
        """Test mapping of Python classes and functions"""
        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('''
@decorator
def func(x: int) -> str:
    """Function doc"""
    return str(x)

class MyClass:
    def method(self):
        pass
''')
        
        result = map_classes_and_functions(test_file)
        
        # Check function mapping
        func_info = next(item for item in result if item["type"] == "function")
        self.assertEqual(func_info["name"], "func")
        self.assertEqual(func_info["return_type"], "str")
        
        # Check class mapping
        class_info = next(item for item in result if item["type"] == "class")
        self.assertEqual(class_info["name"], "MyClass")
        self.assertTrue(any(f["name"] == "method" for f in class_info["functions"]))

if __name__ == '__main__':
    unittest.main()
