"""
Python Code Outline Generator

This module provides functionality to analyze Python source files and generate
comprehensive outlines showing classes, functions, methods, and their signatures.
The outlines include type annotations, docstrings, and decorators for complete
code structure understanding.

Key Features:
- Safe AST parsing with error handling
- Class and function signature extraction
- Type annotation preservation
- Docstring extraction
- Decorator information
- Nested class/function handling
- Error-tolerant processing

The generated outlines are particularly useful for:
- Code documentation
- Project structure analysis
- LLM context preparation
- Code review preparation
"""

import ast
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .utils import write_file


def safe_ast_parse(source: str) -> Optional[ast.AST]:
    """
    Safely parse Python source code with comprehensive error handling.
    
    Args:
        source: Python source code as string
        
    Returns:
        ast.AST: Parsed AST tree, or None if parsing failed
    """
    try:
        return ast.parse(source)
    except SyntaxError as e:
        logging.debug(f"Syntax error in Python code: {e}")
        return None
    except IndentationError as e:
        logging.debug(f"Indentation error in Python code: {e}")
        return None
    except TypeError as e:
        logging.debug(f"Type error parsing Python code: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error parsing Python code: {e}")
        return None


def safe_ast_unparse(node: Optional[ast.AST]) -> Optional[str]:
    """
    Safely unparse AST node to string with error handling.
    
    Args:
        node: AST node to unparse
        
    Returns:
        str: Unparsed string representation, or None if unparsing failed
    """
    if node is None:
        return None
    
    try:
        # Use ast.unparse if available (Python 3.9+)
        if hasattr(ast, 'unparse'):
            return ast.unparse(node)
        else:
            # Fallback for older Python versions
            return _manual_unparse(node)
    except Exception as e:
        logging.debug(f"Error unparsing AST node: {e}")
        return None


def _manual_unparse(node: ast.AST) -> str:
    """
    Manual unparsing for older Python versions that don't have ast.unparse.
    
    Args:
        node: AST node to unparse
        
    Returns:
        str: String representation of the node
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    elif isinstance(node, ast.Attribute):
        return f"{_manual_unparse(node.value)}.{node.attr}"
    elif isinstance(node, ast.Subscript):
        return f"{_manual_unparse(node.value)}[{_manual_unparse(node.slice)}]"
    elif isinstance(node, ast.List):
        elements = [_manual_unparse(el) for el in node.elts]
        return f"[{', '.join(elements)}]"
    elif isinstance(node, ast.Tuple):
        elements = [_manual_unparse(el) for el in node.elts]
        return f"({', '.join(elements)})"
    else:
        return "<complex_expression>"


def extract_function_info(node: ast.FunctionDef) -> Dict[str, Any]:
    """
    Extract comprehensive information from a function definition.
    
    Args:
        node: AST FunctionDef node
        
    Returns:
        dict: Function information including signature, docstring, decorators
    """
    try:
        # Extract arguments
        args_info = []
        
        # Regular arguments
        for i, arg in enumerate(node.args.args):
            arg_info = {
                "name": arg.arg,
                "annotation": safe_ast_unparse(arg.annotation),
                "default": None,
                "kind": "positional"
            }
            
            # Handle defaults (they align with the end of the args list)
            defaults_offset = len(node.args.args) - len(node.args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                if default_idx < len(node.args.defaults):
                    arg_info["default"] = safe_ast_unparse(node.args.defaults[default_idx])
            
            args_info.append(arg_info)
        
        # *args
        if node.args.vararg:
            args_info.append({
                "name": f"*{node.args.vararg.arg}",
                "annotation": safe_ast_unparse(node.args.vararg.annotation),
                "default": None,
                "kind": "vararg"
            })
        
        # Keyword-only arguments
        for i, arg in enumerate(node.args.kwonlyargs):
            arg_info = {
                "name": arg.arg,
                "annotation": safe_ast_unparse(arg.annotation),
                "default": None,
                "kind": "keyword_only"
            }
            
            if i < len(node.args.kw_defaults) and node.args.kw_defaults[i]:
                arg_info["default"] = safe_ast_unparse(node.args.kw_defaults[i])
            
            args_info.append(arg_info)
        
        # **kwargs
        if node.args.kwarg:
            args_info.append({
                "name": f"**{node.args.kwarg.arg}",
                "annotation": safe_ast_unparse(node.args.kwarg.annotation),
                "default": None,
                "kind": "kwarg"
            })
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorator_str = safe_ast_unparse(decorator)
            if decorator_str:
                decorators.append(decorator_str)
        
        return {
            "type": "function",
            "name": node.name,
            "args": args_info,
            "return_type": safe_ast_unparse(node.returns),
            "docstring": ast.get_docstring(node),
            "decorators": decorators,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "lineno": node.lineno
        }
        
    except Exception as e:
        logging.warning(f"Error extracting function info for {getattr(node, 'name', 'unknown')}: {e}")
        return {
            "type": "function",
            "name": getattr(node, 'name', 'unknown'),
            "error": str(e),
            "lineno": getattr(node, 'lineno', 0)
        }


def extract_class_info(node: ast.ClassDef) -> Dict[str, Any]:
    """
    Extract comprehensive information from a class definition.
    
    Args:
        node: AST ClassDef node
        
    Returns:
        dict: Class information including methods, inheritance, decorators
    """
    try:
        # Extract base classes
        bases = []
        for base in node.bases:
            base_str = safe_ast_unparse(base)
            if base_str:
                bases.append(base_str)
        
        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            decorator_str = safe_ast_unparse(decorator)
            if decorator_str:
                decorators.append(decorator_str)
        
        # Extract methods and nested classes
        methods = []
        nested_classes = []
        
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = extract_function_info(child)
                method_info["is_method"] = True
                methods.append(method_info)
            elif isinstance(child, ast.ClassDef):
                nested_class_info = extract_class_info(child)
                nested_class_info["is_nested"] = True
                nested_classes.append(nested_class_info)
        
        return {
            "type": "class",
            "name": node.name,
            "bases": bases,
            "decorators": decorators,
            "docstring": ast.get_docstring(node),
            "methods": methods,
            "nested_classes": nested_classes,
            "lineno": node.lineno
        }
        
    except Exception as e:
        logging.warning(f"Error extracting class info for {getattr(node, 'name', 'unknown')}: {e}")
        return {
            "type": "class",
            "name": getattr(node, 'name', 'unknown'),
            "error": str(e),
            "lineno": getattr(node, 'lineno', 0)
        }


def analyze_python_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Analyze a Python file and extract all classes and functions.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        list: List of dictionaries containing class/function information
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            source = f.read()
    except Exception as e:
        logging.error(f"Failed to read file {file_path}: {e}")
        return [{"type": "error", "message": f"Failed to read file: {str(e)}"}]

    tree = safe_ast_parse(source)
    if tree is None:
        return [{"type": "error", "message": "Failed to parse Python code"}]

    results = []
    
    # Walk the AST and extract top-level classes and functions
    for node in ast.walk(tree):
        try:
            # Only process top-level nodes (not nested)
            if hasattr(node, 'parent') and node.parent is not None:
                continue
                
            if isinstance(node, ast.ClassDef):
                class_info = extract_class_info(node)
                results.append(class_info)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if this function is at module level
                parent_found = False
                for parent in ast.walk(tree):
                    if isinstance(parent, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(parent, 'body') and node in parent.body and parent != node:
                            parent_found = True
                            break
                
                if not parent_found:
                    func_info = extract_function_info(node)
                    func_info["is_method"] = False
                    results.append(func_info)
                    
        except Exception as e:
            logging.debug(f"Error processing AST node: {e}")
            continue
    
    # Sort by line number for consistent output
    results.sort(key=lambda x: x.get('lineno', 0))
    
    return results


def format_function_signature(func_info: Dict[str, Any]) -> str:
    """
    Format a function signature from function information.
    
    Args:
        func_info: Function information dictionary
        
    Returns:
        str: Formatted function signature
    """
    if "error" in func_info:
        return f"{func_info['name']} (Error: {func_info['error']})"
    
    try:
        args = func_info.get("args", [])
        arg_strings = []
        
        for arg in args:
            arg_str = arg["name"]
            if arg.get("annotation"):
                arg_str += f": {arg['annotation']}"
            if arg.get("default"):
                arg_str += f" = {arg['default']}"
            arg_strings.append(arg_str)
        
        signature = f"{func_info['name']}({', '.join(arg_strings)})"
        
        if func_info.get("return_type"):
            signature += f" -> {func_info['return_type']}"
        
        return signature
        
    except Exception as e:
        logging.debug(f"Error formatting function signature: {e}")
        return f"{func_info.get('name', 'unknown')} (formatting error)"


def format_outline_for_display(symbol_map: List[Dict[str, Any]]) -> str:
    """
    Format the symbol map into a readable outline format.
    
    Args:
        symbol_map: List of extracted symbol information
        
    Returns:
        str: Formatted outline string
    """
    if not symbol_map:
        return "No Python symbols found."
    
    output = []

    for item in symbol_map:
        try:
            if item.get("type") == "error":
                output.append(f"\nERROR: {item['message']}")
                continue

            if item.get("type") == "class":
                # Format class header
                class_line = f"\nCLASS: {item['name']}"
                if item.get("bases"):
                    class_line += f"({', '.join(item['bases'])})"
                output.append(class_line)
                
                # Add decorators
                if item.get("decorators"):
                    output.append(f"  DECORATORS: {', '.join(item['decorators'])}")
                
                # Add docstring
                if item.get("docstring"):
                    docstring_lines = item['docstring'].strip().split('\n')
                    output.append(f"  DOCSTRING:")
                    for line in docstring_lines[:3]:  # Limit to first 3 lines
                        output.append(f"    {line.strip()}")
                    if len(docstring_lines) > 3:
                        output.append(f"    ... ({len(docstring_lines) - 3} more lines)")
                
                # Add methods
                for method in item.get("methods", []):
                    method_sig = format_function_signature(method)
                    method_prefix = "ASYNC METHOD" if method.get("is_async") else "METHOD"
                    output.append(f"\n  {method_prefix}: {method_sig}")
                    
                    if method.get("decorators"):
                        output.append(f"    DECORATORS: {', '.join(method['decorators'])}")
                    
                    if method.get("docstring"):
                        method_doc_lines = method['docstring'].strip().split('\n')
                        output.append(f"    DOCSTRING:")
                        for line in method_doc_lines[:2]:  # Limit to first 2 lines for methods
                            output.append(f"      {line.strip()}")
                        if len(method_doc_lines) > 2:
                            output.append(f"      ... ({len(method_doc_lines) - 2} more lines)")
                
                # Add nested classes
                for nested_class in item.get("nested_classes", []):
                    output.append(f"\n  NESTED CLASS: {nested_class['name']}")
                    if nested_class.get("docstring"):
                        output.append(f"    DOCSTRING: {nested_class['docstring'][:100]}...")
                        
            elif item.get("type") == "function":
                # Format function
                func_sig = format_function_signature(item)
                func_prefix = "ASYNC FUNCTION" if item.get("is_async") else "FUNCTION"
                output.append(f"\n{func_prefix}: {func_sig}")
                
                if item.get("decorators"):
                    output.append(f"  DECORATORS: {', '.join(item['decorators'])}")
                
                if item.get("docstring"):
                    func_doc_lines = item['docstring'].strip().split('\n')
                    output.append(f"  DOCSTRING:")
                    for line in func_doc_lines[:3]:  # Limit to first 3 lines
                        output.append(f"    {line.strip()}")
                    if len(func_doc_lines) > 3:
                        output.append(f"    ... ({len(func_doc_lines) - 3} more lines)")
                        
        except Exception as e:
            logging.error(f"Error formatting outline item: {e}")
            output.append(f"\nERROR: Failed to format item: {str(e)}")

    return "\n".join(output)


def process_python_file(file_path: Path) -> str:
    """
    Process a single Python file and return its formatted outline.
    
    Args:
        file_path: Path to the Python file to process
        
    Returns:
        str: Formatted outline of the file
    """
    try:
        symbol_map = analyze_python_file(file_path)
        return format_outline_for_display(symbol_map)
    except Exception as e:
        error_msg = f"ERROR: Failed to process file: {str(e)}"
        logging.error(f"Error processing Python file {file_path}: {e}")
        return error_msg


def python_outline_files(file_list: List[Dict[str, Any]], output: str) -> bool:
    """
    Generate Python outlines for all Python files in the file list.
    
    Args:
        file_list: List of file dictionaries with path and metadata
        output: Output file path or "stdio"
        
    Returns:
        bool: True if outline generation was successful
    """
    if not write_file(output, "## Python Code Outline\n"):
        return False
    
    python_files = [
        item for item in file_list 
        if item.get("type") == "file" and item["path"].suffix.lower() == '.py'
    ]
    
    if not python_files:
        return write_file(output, "\nNo Python files found for outline generation.\n\n")
    
    logging.info(f"Generating outlines for {len(python_files)} Python files")
    
    for item in python_files:
        file_path = item["path"]
        relative_path = item["relative_path"]
        
        if not write_file(output, f"\n### File: {relative_path}\n"):
            return False
        
        try:
            outline = process_python_file(file_path)
            if not write_file(output, outline + "\n"):
                return False
        except Exception as e:
            error_msg = f"Error processing {relative_path}: {str(e)}\n"
            logging.error(error_msg.strip())
            if not write_file(output, error_msg):
                return False
    
    return write_file(output, "\n")