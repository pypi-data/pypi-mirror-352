import ast
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .utils import write_file


def safe_ast_parse(source: str) -> Union[ast.AST, None]:
    """Try to parse Python source code, return None if invalid."""
    try:
        return ast.parse(source)
    except (SyntaxError, IndentationError, TypeError) as e:
        logging.error(f"Failed to parse Python code: {str(e)}")
        return None

def safe_ast_unparse(node: Optional[ast.AST]) -> Optional[str]:
    """Safely unparse AST node, return None if fails."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None

def get_function_info(node: ast.FunctionDef) -> Dict[str, Any]:
    try:
        args_info = []
        for arg in node.args.args:
            annotation = safe_ast_unparse(arg.annotation)
            args_info.append({
                "name": arg.arg,
                "annotation": annotation,
                "default": None
            })
        
        defaults = []
        try:
            defaults = [safe_ast_unparse(d) for d in node.args.defaults]
            defaults = ['None'] * (len(args_info) - len(defaults)) + defaults
            for arg, default in zip(args_info, defaults):
                arg["default"] = default if default != 'None' else None
        except Exception as e:
            logging.debug(f"Error processing defaults: {e}")

        return {
            "type": "function",
            "name": node.name,
            "args": args_info,
            "return_type": safe_ast_unparse(node.returns),
            "docstring": ast.get_docstring(node),
            "decorators": [safe_ast_unparse(d) for d in node.decorator_list if safe_ast_unparse(d)]
        }
    except Exception as e:
        logging.error(f"Error extracting function info for {getattr(node, 'name', 'unknown')}: {e}")
        return {"type": "function", "name": getattr(node, 'name', 'unknown'), "error": str(e)}

def map_classes_and_functions(filename: str) -> List[Dict[str, Any]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        logging.error(f"Failed to read file {filename}: {e}")
        return [{"type": "error", "message": f"Failed to read file: {str(e)}"}]

    tree = safe_ast_parse(source)
    if tree is None:
        return [{"type": "error", "message": "Failed to parse Python code"}]

    results = []
    for node in ast.walk(tree):
        try:
            if isinstance(node, ast.ClassDef):
                cls_info = {
                    "type": "class",
                    "name": node.name,
                    "decorators": [safe_ast_unparse(d) for d in node.decorator_list if safe_ast_unparse(d)],
                    "docstring": ast.get_docstring(node),
                    "functions": []
                }
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        func_info = get_function_info(child)
                        cls_info["functions"].append(func_info)
                results.append(cls_info)
            elif isinstance(node, ast.FunctionDef):
                results.append(get_function_info(node))
        except Exception as e:
            logging.error(f"Error processing node: {e}")
            continue
            
    return results

def format_symbol_map_for_ai(symbol_map: List[Dict[str, Any]]) -> str:
    output = []

    def format_args(args):
        try:
            formatted_args = []
            for arg in args:
                arg_str = arg["name"]
                if arg.get("annotation"):
                    arg_str += f": {arg['annotation']}"
                if arg.get("default"):
                    arg_str += f" = {arg['default']}"
                formatted_args.append(arg_str)
            return ", ".join(formatted_args)
        except Exception as e:
            logging.error(f"Error formatting arguments: {e}")
            return "<error formatting arguments>"

    for item in symbol_map:
        try:
            if item["type"] == "error":
                output.append(f"\nERROR: {item['message']}")
                continue

            if item["type"] == "class":
                output.append(f"\nCLASS: {item['name']}")
                if item.get("decorators"):
                    output.append(f"  DECORATORS: {', '.join(item['decorators'])}")
                if item.get("docstring"):
                    output.append(f"  DOCSTRING:\n    {item['docstring']}")
                
                for func in item.get("functions", []):
                    if "error" in func:
                        output.append(f"\n  FUNCTION: {func['name']} (Error: {func['error']})")
                        continue
                    output.append(f"\n  FUNCTION: {func['name']}({format_args(func['args'])})")
                    if func.get("return_type"):
                        output.append(f"    RETURNS: {func['return_type']}")
                    if func.get("decorators"):
                        output.append(f"    DECORATORS: {', '.join(func['decorators'])}")
                    if func.get("docstring"):
                        output.append(f"    DOCSTRING:\n      {func['docstring']}")
                        
            elif item["type"] == "function":
                if "error" in item:
                    output.append(f"\nFUNCTION: {item['name']} (Error: {item['error']})")
                    continue
                output.append(f"\nFUNCTION: {item['name']}({format_args(item['args'])})")
                if item.get("return_type"):
                    output.append(f"  RETURNS: {item['return_type']}")
                if item.get("decorators"):
                    output.append(f"  DECORATORS: {', '.join(item['decorators'])}")
                if item.get("docstring"):
                    output.append(f"  DOCSTRING:\n    {item['docstring']}")
        except Exception as e:
            logging.error(f"Error formatting item: {e}")
            output.append(f"\nERROR: Failed to format item: {str(e)}")

    return "\n".join(output)

def process_python_file(file_path: Path) -> str:
    try:
        symbol_map = map_classes_and_functions(str(file_path))
        return format_symbol_map_for_ai(symbol_map)
    except Exception as e:
        return f"ERROR: Failed to process file: {str(e)}"

def python_outline_files(file_list: List[Dict[str, Any]], output: str) -> None:
    write_file(output, "## Detailed Python Outline\n")
    
    for item in file_list:
        file_path = item["path"]
        if file_path.is_file() and file_path.suffix == '.py':
            write_file(output, f"\n### File: {item['relative_path']}\n")
            write_file(output, process_python_file(file_path) + "\n")