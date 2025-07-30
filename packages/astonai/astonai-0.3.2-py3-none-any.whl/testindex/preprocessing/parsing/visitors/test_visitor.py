"""
AST visitor for extracting test functions and related components.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Tuple

from testindex.core.logging import get_logger

logger = get_logger("test-visitor")

class TestVisitor(ast.NodeVisitor):
    """AST visitor for extracting test functions and test-related components."""
    
    def __init__(self, file_path: Optional[str] = None, framework: Optional[str] = "unknown"):
        """Initialize the visitor.
        
        Args:
            file_path: Optional path to the file being analyzed
            framework: Testing framework used (pytest, unittest, or unknown)
        """
        self.file_path = file_path
        self.framework = framework
        
        self.test_functions: List[Dict[str, Any]] = []
        self.test_classes: List[Dict[str, Any]] = []
        self.fixtures: List[Dict[str, Any]] = []
        self.imports: Set[str] = set()
        self.current_class: Optional[Dict[str, Any]] = None
        self.module_markers: List[Dict[str, Any]] = []  # For pytest marks like @pytest.mark.slow
        self.dependencies: Set[str] = set()  # Functions or fixtures called by tests
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import nodes to extract imports."""
        for name in node.names:
            self.imports.add(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from nodes to extract imports."""
        if node.module:
            for name in node.names:
                if name.name == '*':
                    continue
                self.imports.add(f"{node.module}.{name.name}")
        self.generic_visit(node)
    
    def visit_Module(self, node: ast.Module) -> None:
        """Visit module node to extract module-level markers."""
        # Check for module-level pytest markers
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "pytestmark":
                        if isinstance(item.value, ast.Name):
                            self.module_markers.append({
                                "type": "marker",
                                "name": item.value.id,
                                "args": []
                            })
                        elif isinstance(item.value, ast.Call) and isinstance(item.value.func, ast.Attribute):
                            if (isinstance(item.value.func.value, ast.Name) and 
                                item.value.func.value.id == "pytest" and 
                                item.value.func.attr == "mark"):
                                self.module_markers.append({
                                    "type": "marker",
                                    "name": f"pytest.mark.{item.value.args[0].s if item.value.args else ''}",
                                    "args": self._extract_call_args(item.value)
                                })
                        elif isinstance(item.value, ast.List):
                            for elt in item.value.elts:
                                if isinstance(elt, ast.Call) and isinstance(elt.func, ast.Attribute):
                                    if (isinstance(elt.func.value, ast.Name) and 
                                        elt.func.value.id == "pytest" and 
                                        elt.func.attr == "mark"):
                                        self.module_markers.append({
                                            "type": "marker",
                                            "name": f"pytest.mark.{elt.args[0].s if elt.args else ''}",
                                            "args": self._extract_call_args(elt)
                                        })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract test classes."""
        is_test_class = False
        
        # Check for naming conventions
        if self.framework == "unittest":
            # unittest: classes that inherit from TestCase
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == "TestCase":
                    is_test_class = True
                    break
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                    if base.value.id == "unittest" and base.attr == "TestCase":
                        is_test_class = True
                        break
        elif self.framework == "pytest":
            # pytest: classes that start with Test
            if node.name.startswith("Test"):
                is_test_class = True
        else:
            # General heuristics
            if (node.name.startswith("Test") or 
                node.name.endswith("Test") or 
                node.name.endswith("Tests") or
                "test" in node.name.lower()):
                is_test_class = True
                
                # Check if it has any test methods
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and (
                        item.name.startswith("test_") or
                        item.name.startswith("test")):
                        is_test_class = True
                        break
        
        # Extract class markers from decorators
        markers = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Attribute):
                if (isinstance(decorator.value.value, ast.Name) and 
                    decorator.value.value.id == "pytest" and 
                    decorator.value.attr == "mark"):
                    markers.append({
                        "type": "marker",
                        "name": f"pytest.mark.{decorator.attr}",
                        "args": []
                    })
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if (isinstance(decorator.func.value, ast.Attribute) and 
                    isinstance(decorator.func.value.value, ast.Name) and
                    decorator.func.value.value.id == "pytest" and
                    decorator.func.value.attr == "mark"):
                    markers.append({
                        "type": "marker",
                        "name": f"pytest.mark.{decorator.func.attr}",
                        "args": self._extract_call_args(decorator)
                    })
        
        if is_test_class:
            # Create class info
            class_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "doc": ast.get_docstring(node),
                "framework": self.framework,
                "markers": markers
            }
            
            # Add to test classes list
            self.test_classes.append(class_info)
            
            # Process class methods
            old_class = self.current_class
            self.current_class = class_info
            self.generic_visit(node)
            self.current_class = old_class
        else:
            # Still visit non-test classes for nested test classes
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract test functions and fixtures."""
        if self.framework == "pytest":
            self._process_pytest_function(node)
        elif self.framework == "unittest":
            self._process_unittest_function(node)
        else:
            # Use heuristics
            if node.name.startswith("test_") or node.name.startswith("test"):
                self._process_generic_test_function(node)
        
        # Visit function body
        self.generic_visit(node)
    
    def _process_pytest_function(self, node: ast.FunctionDef) -> None:
        """Process a function in a pytest context."""
        # Check if this is a fixture
        is_fixture = False
        fixture_params = {}
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "fixture" or decorator.func.id == "pytest.fixture":
                    is_fixture = True
                    fixture_params = self._extract_fixture_params(decorator)
            elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
                if decorator.value.id == "pytest" and decorator.attr == "fixture":
                    is_fixture = True
        
        # Extract markers from decorators
        markers = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Attribute):
                if (isinstance(decorator.value.value, ast.Name) and 
                    decorator.value.value.id == "pytest" and 
                    decorator.value.attr == "mark"):
                    markers.append({
                        "type": "marker",
                        "name": f"pytest.mark.{decorator.attr}",
                        "args": []
                    })
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if (isinstance(decorator.func.value, ast.Attribute) and 
                    isinstance(decorator.func.value.value, ast.Name) and
                    decorator.func.value.value.id == "pytest" and
                    decorator.func.value.attr == "mark"):
                    markers.append({
                        "type": "marker",
                        "name": f"pytest.mark.{decorator.func.attr}",
                        "args": self._extract_call_args(decorator)
                    })
        
        # Check if this is a test function
        is_test = node.name.startswith("test_")
        
        # Extract function args
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
                
                # If a test function has arguments, they're usually fixtures
                if is_test and arg.arg != "self":
                    self.dependencies.add(arg.arg)
        
        if is_fixture:
            # Store fixture info
            fixture_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "class_name": self.current_class["name"] if self.current_class else None,
                "args": args,
                "doc": ast.get_docstring(node),
                "markers": markers,
                "scope": fixture_params.get("scope", "function"),
                "autouse": fixture_params.get("autouse", False),
                "params": fixture_params.get("params", None)
            }
            
            self.fixtures.append(fixture_info)
            
        elif is_test:
            # Store test function info
            test_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "class_name": self.current_class["name"] if self.current_class else None,
                "args": args,
                "doc": ast.get_docstring(node),
                "markers": markers,
                "framework": "pytest"
            }
            
            self.test_functions.append(test_info)
    
    def _process_unittest_function(self, node: ast.FunctionDef) -> None:
        """Process a function in a unittest context."""
        # Only process if inside a test class
        if not self.current_class:
            return
        
        # Check if this is a test method (starts with test)
        is_test = node.name.startswith("test_") or node.name.startswith("test")
        
        # Extract function args
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
        
        if is_test:
            # Store test function info
            test_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "class_name": self.current_class["name"],
                "args": args,
                "doc": ast.get_docstring(node),
                "markers": [],
                "framework": "unittest"
            }
            
            self.test_functions.append(test_info)
        elif node.name in ["setUp", "tearDown", "setUpClass", "tearDownClass"]:
            # Store test lifecycle method
            method_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "class_name": self.current_class["name"],
                "args": args,
                "doc": ast.get_docstring(node),
                "is_setup": node.name in ["setUp", "setUpClass"],
                "is_teardown": node.name in ["tearDown", "tearDownClass"],
                "is_class_method": node.name in ["setUpClass", "tearDownClass"],
                "framework": "unittest"
            }
            
            # Add as a fixture (for consistency in data model)
            self.fixtures.append(method_info)
    
    def _process_generic_test_function(self, node: ast.FunctionDef) -> None:
        """Process a function using general heuristics to identify tests."""
        # Check if this is likely a test function
        is_test = node.name.startswith("test_") or node.name.startswith("test")
        
        if not is_test:
            return
        
        # Extract function args
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
        
        # Store test function info
        test_info = {
            "name": node.name,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "class_name": self.current_class["name"] if self.current_class else None,
            "args": args,
            "doc": ast.get_docstring(node),
            "markers": [],
            "framework": "unknown"
        }
        
        self.test_functions.append(test_info)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to track dependencies."""
        # Check for pytest fixture dependencies and assertion calls
        if isinstance(node.func, ast.Name):
            # Direct function calls like fixture()
            self.dependencies.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # Method calls like self.assertEqual()
            if node.func.value.id == "self":
                # Check for unittest assertions
                if node.func.attr.startswith("assert"):
                    pass  # Could track assertions here if needed
            else:
                # Other attribute calls - potential fixtures or dependencies
                self.dependencies.add(f"{node.func.value.id}.{node.func.attr}")
        
        self.generic_visit(node)
    
    def _extract_fixture_params(self, node: ast.Call) -> Dict[str, Any]:
        """Extract parameters from a fixture decorator."""
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
    
    def _extract_call_args(self, node: ast.Call) -> List[Any]:
        """Extract positional arguments from a function call."""
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Str):
                args.append(arg.s)
            elif isinstance(arg, ast.Num):
                args.append(arg.n)
            elif isinstance(arg, ast.NameConstant):
                args.append(arg.value)
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            else:
                args.append("...")
        return args 