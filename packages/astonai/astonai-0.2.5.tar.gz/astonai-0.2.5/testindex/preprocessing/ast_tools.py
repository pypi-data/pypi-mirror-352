"""
AST-based tools for extracting Python code elements.

This module provides utilities for extracting imports and function calls
from Python code using the AST (Abstract Syntax Tree).
"""
import ast
import logging
from typing import Dict, List, Optional, Set, Tuple, Union

from testindex.core.logging import get_logger

# Set up logger
logger = get_logger(__name__)


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract module imports."""
    
    def __init__(self):
        """Initialize the import visitor."""
        self.imports = []
        self.import_from = []  # Track 'from X import Y' style imports separately
        
    def visit_Import(self, node):
        """Process 'import X' statement."""
        for name in node.names:
            # Handle 'import X as Y' - we only care about X
            module_name = name.name
            self.imports.append(module_name)
        self.generic_visit(node)
            
    def visit_ImportFrom(self, node):
        """Process 'from X import Y' statement."""
        if node.module:
            # Record the module being imported from
            module_name = node.module
            
            # Record the full module path including imports
            # We only track the base module for IMPORTS edges
            if module_name not in self.imports:
                self.imports.append(module_name)
            
            # Also track what's being imported (for completeness)
            for name in node.names:
                self.import_from.append((module_name, name.name))
                
        self.generic_visit(node)


class CallVisitor(ast.NodeVisitor):
    """AST visitor to extract function calls."""
    
    def __init__(self):
        """Initialize the call visitor."""
        self.calls = []
        self.local_names = {}  # Track local variable assignments for resolving
        self.imported_names = {}  # Track imported functions for resolving
        
    def visit_Assign(self, node):
        """Process variable assignment to track function aliases."""
        if isinstance(node.value, ast.Name):
            # Handle simple assignment: x = y
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.local_names[target.id] = node.value.id
        elif isinstance(node.value, ast.Attribute):
            # Handle attribute assignment: x = module.function
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attr_name = self._extract_name(node.value)
                    if attr_name:
                        self.local_names[target.id] = attr_name
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        """Track imported functions for name resolution."""
        if node.module:
            for name in node.names:
                imported_as = name.asname or name.name
                self.imported_names[imported_as] = f"{node.module}.{name.name}"
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """Track imported modules for name resolution."""
        for name in node.names:
            if name.asname:
                # For "import X as Y", we need to track Y -> X mapping
                self.imported_names[name.asname] = name.name
        self.generic_visit(node)
        
    def visit_Call(self, node):
        """Process function calls."""
        # Extract the function name/path
        func_name = self._extract_name(node.func)
        if func_name:
            # Resolve aliased names
            resolved_name = self._resolve_name(func_name)
            
            # Add to the list of calls
            if resolved_name not in self.calls:
                self.calls.append(resolved_name)
            
            # Process arguments (to catch nested calls)
            for arg in node.args:
                if isinstance(arg, ast.Call):
                    self.visit(arg)
                elif isinstance(arg, ast.Name):
                    # Check if this is a function passed as an argument (e.g., map(int, ...))
                    arg_name = arg.id
                    if arg_name not in self.calls:
                        self.calls.append(self._resolve_name(arg_name))
        self.generic_visit(node)
    
    def _extract_name(self, node):
        """Extract the fully qualified name from an expression."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Attribute):
                base = self._extract_name(node.value)
                if base:
                    return f"{base}.{node.attr}"
            elif isinstance(node, ast.List) or isinstance(node, ast.Tuple) or isinstance(node, ast.Set):
                # Handle list/tuple/set literals with method calls
                return str(node)
            elif isinstance(node, ast.Subscript):
                # Handle subscript expressions: array[index].method()
                base = self._extract_name(node.value)
                return f"{base}[..]" if base else None
        except Exception as e:
            logger.warning(f"Error extracting name: {e}")
        return None
    
    def _resolve_name(self, name):
        """Resolve a name through aliases and imports."""
        # First check if it's a local variable alias
        if name in self.local_names:
            resolved = self.local_names[name]
            # Re-resolve if it points to another name
            if resolved in self.local_names or resolved in self.imported_names:
                return self._resolve_name(resolved)
            return resolved
        
        # Then check if it's an imported name
        parts = name.split('.')
        if parts[0] in self.imported_names:
            base = self.imported_names[parts[0]]
            if len(parts) > 1:
                return f"{base}.{'.'.join(parts[1:])}"
            return base
            
        return name


def extract_imports(tree: ast.AST) -> List[str]:
    """Extract module imports from an AST.
    
    Args:
        tree: Python AST to analyze
        
    Returns:
        List of imported module names
    """
    visitor = ImportVisitor()
    try:
        visitor.visit(tree)
        return visitor.imports
    except Exception as e:
        logger.warning(f"Error extracting imports: {e}")
        return []


def extract_calls(tree: ast.AST) -> List[str]:
    """Extract function calls from an AST.
    
    Args:
        tree: Python AST to analyze
        
    Returns:
        List of called function names (including qualified names)
    """
    visitor = CallVisitor()
    try:
        visitor.visit(tree)
        return visitor.calls
    except Exception as e:
        logger.warning(f"Error extracting function calls: {e}")
        return [] 