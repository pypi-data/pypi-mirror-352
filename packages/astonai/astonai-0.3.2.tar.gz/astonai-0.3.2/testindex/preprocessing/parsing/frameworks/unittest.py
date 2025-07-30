"""
unittest framework detection and parsing.
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from testindex.core.logging import get_logger

logger = get_logger("unittest-detector")

class UnittestDetector:
    """Detector for unittest framework."""
    
    def __init__(self):
        """Initialize the detector."""
        self.framework_name = "unittest"
    
    def detect(self, tree: ast.AST, file_path: Optional[Union[str, Path]] = None) -> bool:
        """Detect if this file uses unittest.
        
        Args:
            tree: The AST to analyze
            file_path: Optional path to the file (for context)
            
        Returns:
            bool: True if unittest is detected, False otherwise
        """
        # Check filename pattern
        if file_path:
            file_name = Path(file_path).name
            if file_name.startswith("test") or file_name.endswith("_test.py") or file_name.endswith("Tests.py"):
                # Filename suggests test file, check further
                visitor = UnittestVisitor()
                visitor.visit(tree)
                return visitor.is_unittest
        
        # Use visitor to check for unittest patterns
        visitor = UnittestVisitor()
        visitor.visit(tree)
        return visitor.is_unittest

class UnittestVisitor(ast.NodeVisitor):
    """AST visitor for detecting unittest patterns."""
    
    def __init__(self):
        """Initialize the visitor."""
        self.is_unittest = False
        self.imports_unittest = False
        self.has_test_case_subclass = False
        self.has_test_methods = False
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import nodes to detect unittest imports."""
        for name in node.names:
            if name.name == "unittest":
                self.imports_unittest = True
                self.is_unittest = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from nodes to detect unittest imports."""
        if node.module == "unittest" or node.module == "unittest.mock" or node.module == "unittest.case":
            self.imports_unittest = True
            self.is_unittest = True
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to detect TestCase subclasses."""
        # Check for unittest.TestCase inheritance
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "TestCase":
                self.has_test_case_subclass = True
                self.is_unittest = True
            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                if base.value.id == "unittest" and base.attr == "TestCase":
                    self.has_test_case_subclass = True
                    self.is_unittest = True
        
        # Check for test methods (test_*)
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and (item.name.startswith("test_") or item.name.startswith("test")):
                self.has_test_methods = True
                self.is_unittest = True
        
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to detect unittest API usage."""
        if isinstance(node.func, ast.Name):
            # Check for common unittest methods called standalone
            unittest_methods = [
                "assertEqual", "assertNotEqual", "assertTrue", "assertFalse",
                "assertIs", "assertIsNot", "assertIsNone", "assertIsNotNone",
                "assertIn", "assertNotIn", "assertAlmostEqual", "assertRaises"
            ]
            if node.func.id in unittest_methods:
                self.is_unittest = True
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # Check for self.assertX calls
            if node.func.value.id == "self":
                unittest_methods = [
                    "assertEqual", "assertNotEqual", "assertTrue", "assertFalse",
                    "assertIs", "assertIsNot", "assertIsNone", "assertIsNotNone",
                    "assertIn", "assertNotIn", "assertAlmostEqual", "assertRaises"
                ]
                if node.func.attr in unittest_methods:
                    self.is_unittest = True
            # Check for unittest.main() calls
            elif node.func.value.id == "unittest" and node.func.attr == "main":
                self.is_unittest = True
        
        self.generic_visit(node)

class UnittestTestCaseVisitor(ast.NodeVisitor):
    """AST visitor for extracting unittest test cases and methods."""
    
    def __init__(self, file_path: Optional[str] = None):
        """Initialize the visitor.
        
        Args:
            file_path: Optional path to the file being analyzed
        """
        self.file_path = file_path
        self.test_classes: List[Dict[str, Any]] = []
        self.test_methods: List[Dict[str, Any]] = []
        self.imports: Set[str] = set()
        self.current_class: Optional[Dict[str, Any]] = None
    
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
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract test classes."""
        # Check if this is a TestCase subclass
        is_test_case = False
        bases = []
        
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
                if base.id == "TestCase":
                    is_test_case = True
            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                base_name = f"{base.value.id}.{base.attr}"
                bases.append(base_name)
                if base.value.id == "unittest" and base.attr == "TestCase":
                    is_test_case = True
        
        # Only process TestCase subclasses
        if is_test_case:
            class_info = {
                "name": node.name,
                "file_path": self.file_path,
                "line_number": node.lineno,
                "col_offset": node.col_offset,
                "bases": bases,
                "is_test_case": is_test_case
            }
            
            self.test_classes.append(class_info)
            
            old_class = self.current_class
            self.current_class = class_info
            
            # Visit class body
            self.generic_visit(node)
            
            self.current_class = old_class
        else:
            # Still visit non-TestCase classes for nested TestCase classes
            self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract test methods."""
        # Only process methods in TestCase classes
        if self.current_class and self.current_class["is_test_case"]:
            # Check if this is a test method (starting with 'test')
            is_test = node.name.startswith("test")
            
            if is_test or node.name in ["setUp", "tearDown", "setUpClass", "tearDownClass"]:
                # Extract method arguments
                args = []
                for arg in node.args.args:
                    if hasattr(arg, 'arg'):
                        args.append(arg.arg)
                
                method_info = {
                    "name": node.name,
                    "file_path": self.file_path,
                    "line_number": node.lineno,
                    "col_offset": node.col_offset,
                    "class_name": self.current_class["name"],
                    "args": args,
                    "is_test": is_test,
                    "is_setup": node.name == "setUp" or node.name == "setUpClass",
                    "is_teardown": node.name == "tearDown" or node.name == "tearDownClass",
                    "is_class_method": node.name == "setUpClass" or node.name == "tearDownClass"
                }
                
                self.test_methods.append(method_info)
        
        # Visit method body
        self.generic_visit(node) 