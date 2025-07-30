"""
pytest framework detection and parsing.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from testindex.core.logging import get_logger

logger = get_logger("pytest-detector")

class PyTestDetector:
    """Detector for pytest framework."""
    
    def __init__(self):
        """Initialize the detector."""
        self.framework_name = "pytest"
    
    def detect(self, tree: ast.AST, file_path: Optional[Union[str, Path]] = None) -> bool:
        """Detect if this file uses pytest.
        
        Args:
            tree: The AST to analyze
            file_path: Optional path to the file (for context)
            
        Returns:
            bool: True if pytest is detected, False otherwise
        """
        # Check filename pattern
        if file_path:
            file_name = Path(file_path).name
            if file_name.startswith("test_") or file_name.endswith("_test.py"):
                # Filename suggests pytest
                visitor = PyTestVisitor()
                visitor.visit(tree)
                return visitor.is_pytest
        
        # Use visitor to check for pytest patterns
        visitor = PyTestVisitor()
        visitor.visit(tree)
        return visitor.is_pytest

class PyTestVisitor(ast.NodeVisitor):
    """AST visitor for detecting pytest patterns."""
    
    def __init__(self):
        """Initialize the visitor."""
        self.is_pytest = False
        self.imports_pytest = False
        self.has_test_functions = False
        self.has_fixtures = False
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import nodes to detect pytest imports."""
        for name in node.names:
            if name.name == "pytest":
                self.imports_pytest = True
                self.is_pytest = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from nodes to detect pytest imports."""
        if node.module == "pytest":
            self.imports_pytest = True
            self.is_pytest = True
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to detect test functions and fixtures."""
        # Check for test functions (starting with 'test_')
        if node.name.startswith("test_"):
            self.has_test_functions = True
            self.is_pytest = True
        
        # Check for pytest fixtures
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "fixture" or decorator.func.id == "pytest.fixture":
                    self.has_fixtures = True
                    self.is_pytest = True
            elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
                if decorator.value.id == "pytest" and decorator.attr == "fixture":
                    self.has_fixtures = True
                    self.is_pytest = True
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to detect pytest API usage."""
        if isinstance(node.func, ast.Name):
            # Check for common pytest functions
            if node.func.id in ["parametrize", "mark", "raises", "approx", "skip", "xfail"]:
                self.is_pytest = True
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # Check for pytest.X calls
            if node.func.value.id == "pytest":
                self.is_pytest = True
            # Check for pytest.mark.X calls
            elif (node.func.value.id == "mark" and 
                  hasattr(node.func.value, 'value') and 
                  isinstance(node.func.value.value, ast.Name) and 
                  node.func.value.value.id == "pytest"):
                self.is_pytest = True
        
        self.generic_visit(node)

class PyTestFunctionVisitor(ast.NodeVisitor):
    """AST visitor for extracting pytest test functions and fixtures."""
    
    def __init__(self, file_path: Optional[str] = None):
        """Initialize the visitor.
        
        Args:
            file_path: Optional path to the file being analyzed
        """
        self.file_path = file_path
        self.test_functions: List[Dict[str, Any]] = []
        self.fixtures: List[Dict[str, Any]] = []
        self.imports: Set[str] = set()
        self.current_class: Optional[str] = None
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract test classes."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Store the class information
        class_info = {
            "name": node.name,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "parent_class": old_class
        }
        
        # Check if this is a test class
        is_test_class = False
        if node.name.startswith("Test"):
            is_test_class = True
        
        # Extract base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
        
        class_info["bases"] = bases
        class_info["is_test_class"] = is_test_class
        
        # Visit class body
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract test functions and fixtures."""
        # Check if this is a test function
        is_test = node.name.startswith("test_")
        is_fixture = False
        
        # Check for pytest fixtures
        fixture_params = {}
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "fixture" or decorator.func.id == "pytest.fixture":
                    is_fixture = True
                    # Extract fixture parameters
                    fixture_params = self._extract_fixture_params(decorator)
            elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
                if decorator.value.id == "pytest" and decorator.attr == "fixture":
                    is_fixture = True
        
        # Extract function args
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
        
        # Create function info
        func_info = {
            "name": node.name,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "class_name": self.current_class,
            "args": args,
            "is_test": is_test,
            "is_fixture": is_fixture
        }
        
        if is_fixture:
            func_info.update(fixture_params)
            self.fixtures.append(func_info)
        elif is_test:
            self.test_functions.append(func_info)
        
        # Visit function body
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import nodes to extract imports."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from nodes to extract imports."""
        if node.module:
            for name in node.names:
                self.imports.add(f"{node.module}.{name.name}")
        self.generic_visit(node)
    
    def _extract_fixture_params(self, node: ast.Call) -> Dict[str, Any]:
        """Extract parameters from a fixture decorator.
        
        Args:
            node: The fixture decorator AST node
            
        Returns:
            Dict: Dictionary of fixture parameters
        """
        params = {
            "scope": "function",  # Default scope
            "autouse": False,     # Default autouse
            "params": None        # Default params
        }
        
        for keyword in node.keywords:
            if keyword.arg == "scope" and isinstance(keyword.value, ast.Str):
                params["scope"] = keyword.value.s
            elif keyword.arg == "autouse" and isinstance(keyword.value, ast.NameConstant):
                params["autouse"] = keyword.value.value
            elif keyword.arg == "params":
                # Just note that params exist, the actual values are complex to extract
                params["params"] = True
        
        return params 