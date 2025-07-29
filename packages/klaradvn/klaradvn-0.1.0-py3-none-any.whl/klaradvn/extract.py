import os
import ast
import inspect
from pathlib import Path
import importlib.util
from dataclasses import is_dataclass, fields
from typing import Dict, List, Tuple, Any, Optional


def extract_function_code(folder_path: str, function_name: str) -> Optional[tuple[str, Path]]:
    """
    Find and return the code of a specified Python function within a folder.
    
    Args:
        function_name: The name of the function to search for
        folder_path: Path to the folder containing Python files to search
        
    Returns:
        The complete function code as a string if found, None otherwise
    """
    # Check if folder exists
    if not os.path.isdir(folder_path):
        raise ValueError(f"Folder '{folder_path}' does not exist")
    
    # Function to extract the function code from an AST node
    def get_function_code(node, source_code):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Get line numbers (subtract 1 as line numbers are 1-indexed)
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            
            # For older Python versions that don't have end_lineno
            if not hasattr(node, 'end_lineno'):
                lines = source_code.splitlines()
                indent = len(lines[start_line]) - len(lines[start_line].lstrip())
                
                # Find the end of the function by tracking indentation
                end_line = start_line
                for i in range(start_line + 1, len(lines)):
                    if i >= len(lines) or (lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) <= indent):
                        end_line = i - 1
                        break
                    end_line = i
            
            # Extract the function code
            lines = source_code.splitlines()[start_line:end_line+1]
            return '\n'.join(lines).rstrip()
        return None
    
    # Recursively walk the AST to find the function
    def find_function_in_ast(node, source_code):
        # Try to extract the function from the current node
        result = get_function_code(node, source_code)
        if result:
            return result
        
        # Recursively search in child nodes
        for child in ast.iter_child_nodes(node):
            result = find_function_in_ast(child, source_code)
            if result:
                return result
        return None
    
    # Search through all Python files in the folder
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    
                    # Parse the file into an AST
                    try:
                        tree = ast.parse(source_code)
                        result = find_function_in_ast(tree, source_code)
                        if result:
                            return result, Path(file_path)
                    except SyntaxError:
                        # Skip files with syntax errors
                        continue
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    return None, None


def extract_class(folder: Path, class_name: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
    """
    Find a Python class in a folder and return the class object with all its methods, dataclass info, and complete source code.
    
    Args:
        folder_path (str | Path): Path to the folder to search in
        class_name (str): Name of the class to find
    
    Returns:
        Tuple containing:
        - Class object (if found)
        - Dictionary with comprehensive class information:
          - 'instance_methods': List of instance method names
          - 'class_methods': List of class method names  
          - 'static_methods': List of static method names
          - 'properties': List of property names
          - 'is_dataclass': Boolean indicating if it's a dataclass
          - 'dataclass_fields': List of dataclass field information (if applicable)
          - 'dataclass_methods': Auto-generated dataclass methods (if applicable)
          - 'source_code': Complete source code including ALL decorators
          - 'file_path': Path to the file containing the class
        Returns None if class not found.
    """
    
    # Recursively find all Python files
    for file_path in folder.rglob('*.py'):
        # Skip __init__.py and other dunder files
        if file_path.name.startswith('__'):
            continue
            
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if the class exists in this module
                if hasattr(module, class_name):
                    cls_ = getattr(module, class_name)
                    
                    # Verify it's actually a class
                    if inspect.isclass(cls_):
                        class_info = _extract_class_info(cls_, file_path)
                        return class_info
                        
        except Exception as e:
            # Skip files that can't be imported
            print(f"Warning: Could not import {file_path}: {e}")
            continue
    
    return None

def _extract_class_info(cls: type, file_path: Path) -> Dict[str, Any]:
    """Extract and categorize all methods and information from a class, including complete source code with decorators."""
    
    class_info = {
        'instance_methods': [],
        'class_methods': [],
        'static_methods': [],
        'properties': [],
        'is_dataclass': False,
        'dataclass_fields': [],
        'dataclass_methods': [],
        'source_code': '',
        'file_path': str(file_path)
    }
    
    # Extract source code with decorators
    class_info['source_code'] = _extract_complete_class_source(cls, file_path)
    
    # Check if it's a dataclass
    if is_dataclass(cls):
        class_info['is_dataclass'] = True
        class_info['dataclass_fields'] = _extract_dataclass_fields(cls)
        class_info['dataclass_methods'] = _extract_dataclass_methods(cls)
    
    # Get all members of the class
    for name, method in inspect.getmembers(cls):
        # Skip private methods and built-ins unless you want them
        if name.startswith('_'):
            continue
            
        if inspect.ismethod(method) or inspect.isfunction(method):
            # Check if it's a class method
            if hasattr(cls, name) and isinstance(inspect.getattr_static(cls, name), classmethod):
                class_info['class_methods'].append(name)
            # Check if it's a static method
            elif hasattr(cls, name) and isinstance(inspect.getattr_static(cls, name), staticmethod):
                class_info['static_methods'].append(name)
            # Otherwise it's an instance method
            else:
                class_info['instance_methods'].append(name)
        # Check if it's a property
        elif isinstance(inspect.getattr_static(cls, name), property):
            class_info['properties'].append(name)

    return class_info

def _extract_complete_class_source(cls: type, file_path: Path) -> str:
    """
    Extract complete class source code including ALL decorators using AST parsing.
    This ensures @dataclass and other decorators are included.
    """
    
    try:
        # First try inspect.getsource which usually includes decorators
        source = inspect.getsource(cls)
        
        # Verify that @dataclass is included if it's a dataclass
        if is_dataclass(cls) and '@dataclass' in source:
            return source
        elif not is_dataclass(cls):
            return source
        else:
            # Fall back to AST parsing if @dataclass is missing
            return _extract_class_with_ast(cls, file_path)
            
    except (OSError, TypeError):
        # If inspect fails, use AST parsing
        return _extract_class_with_ast(cls, file_path)

def _extract_class_with_ast(cls: type, file_path: Path) -> str:
    """
    Extract class source code using AST parsing to ensure all decorators are included.
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        # Parse the file with AST
        tree = ast.parse(file_content)
        
        # Find the class definition
        for node in ast.walk(tree):
            if (isinstance(node, ast.ClassDef) and 
                node.name == cls.__name__):
                
                # Get the complete source including decorators
                lines = file_content.split('\n')
                
                # Start from the first decorator if any, otherwise from class line
                start_line = node.lineno - 1  # AST lines are 1-indexed
                if node.decorator_list:
                    start_line = node.decorator_list[0].lineno - 1
                
                # Find end line by looking for the next class/function at same level
                end_line = len(lines)
                
                # Get the indentation of the class
                class_line = lines[node.lineno - 1]
                class_indent = len(class_line) - len(class_line.lstrip())
                
                # Look for the end of the class
                for i in range(node.lineno, len(lines)):
                    line = lines[i]
                    if line.strip() == '':
                        continue
                    
                    current_indent = len(line) - len(line.lstrip())
                    
                    # If we find something at the same or lower indentation level
                    if current_indent <= class_indent and line.strip():
                        # Check if it's a new class or function definition
                        stripped = line.strip()
                        if (stripped.startswith('class ') or 
                            stripped.startswith('def ') or 
                            stripped.startswith('async def ') or
                            (current_indent == 0 and not stripped.startswith(' '))):
                            end_line = i
                            break
                
                return '\n'.join(lines[start_line:end_line]).rstrip()
        
        # If class not found in AST, fall back to line-by-line parsing
        return _extract_class_source_from_file(cls, file_path)
        
    except Exception as e:
        return f"# Error extracting source code with AST: {e}\n# Falling back to basic extraction\n" + \
               _extract_class_source_from_file(cls, file_path)

def _extract_class_source_from_file(cls: type, file_path: Path) -> str:
    """
    Extract class source code by parsing the file directly with improved decorator detection.
    This is a fallback when other methods fail.
    """
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the class definition
        class_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith(f'class {cls.__name__}'):
                class_start = i
                break
        
        if class_start is None:
            return "# Source code could not be extracted - class definition not found"
        
        # Look backwards for decorators and imports
        actual_start = class_start
        for i in range(class_start - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith('@') or line == '':
                actual_start = i
            elif line and not line.startswith('#'):
                # Stop at non-empty, non-comment, non-decorator line
                break
        
        # Find the end of the class
        class_indent = len(lines[class_start]) - len(lines[class_start].lstrip())
        class_end = len(lines)
        
        for i in range(class_start + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            current_indent = len(line) - len(line.lstrip())
            
            # If we find a line at the same or lower indentation that starts a new definition
            if (current_indent <= class_indent and 
                (line.strip().startswith('class ') or 
                 line.strip().startswith('def ') or
                 line.strip().startswith('async def '))):
                class_end = i
                break
        
        extracted_source = ''.join(lines[actual_start:class_end])
        
        # Additional check: if it's a dataclass but @dataclass is not in the source,
        # try to find it in nearby lines
        if is_dataclass(cls) and '@dataclass' not in extracted_source:
            # Look further back for @dataclass
            for i in range(actual_start - 5, max(-1, actual_start - 20), -1):
                if i >= 0 and '@dataclass' in lines[i]:
                    extracted_source = ''.join(lines[i:class_end])
                    break
        
        return extracted_source
    
    except Exception as e:
        return f"# Error extracting source code: {e}"

def _extract_dataclass_fields(cls: type) -> List[Dict[str, Any]]:
    """Extract detailed information about dataclass fields."""
    
    if not is_dataclass(cls):
        return []
    
    field_info = []
    for field in fields(cls):
        field_data = {
            'name': field.name,
            'type': field.type,
            'default': field.default if field.default is not field.default_factory else None,
            'default_factory': field.default_factory if field.default_factory is not field.default_factory else None,
            'init': field.init,
            'repr': field.repr,
            'hash': field.hash,
            'compare': field.compare,
            'metadata': dict(field.metadata) if field.metadata else {}
        }
        field_info.append(field_data)
    
    return field_info

def _extract_dataclass_methods(cls: type) -> List[str]:
    """Extract auto-generated dataclass methods."""
    
    if not is_dataclass(cls):
        return []
    
    # Common dataclass auto-generated methods
    dataclass_methods = []
    auto_generated = ['__init__', '__repr__', '__eq__', '__hash__', '__lt__', '__le__', '__gt__', '__ge__']
    
    for method_name in auto_generated:
        if hasattr(cls, method_name):
            # Check if it's likely auto-generated by dataclass
            method = getattr(cls, method_name)
            if hasattr(method, '__qualname__') and cls.__name__ in method.__qualname__:
                dataclass_methods.append(method_name)
    
    return dataclass_methods