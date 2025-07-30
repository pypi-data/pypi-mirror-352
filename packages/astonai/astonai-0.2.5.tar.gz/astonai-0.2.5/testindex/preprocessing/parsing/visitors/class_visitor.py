"""
AST visitor for extracting class definitions.
"""
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from testindex.core.logging import get_logger

logger = get_logger("class-visitor")

class ClassVisitor(ast.NodeVisitor):
    """AST visitor for extracting class definitions."""
    
    def __init__(self, file_path: Optional[str] = None, module_name: Optional[str] = None):
        """Initialize the visitor.
        
        Args:
            file_path: Optional path to the file being analyzed
            module_name: Optional module name (package.module)
        """
        self.file_path = file_path
        self.module_name = module_name
        
        self.classes: List[Dict[str, Any]] = []
        self.imports: Dict[str, str] = {}  # alias -> real_name
        self.methods: Dict[str, List[Dict[str, Any]]] = {}  # class_name -> [methods]
        self.current_class: Optional[Dict[str, Any]] = None
        self.inheritance_graph: Dict[str, List[str]] = {}  # class -> [base_classes]
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import nodes to extract imports."""
        for name in node.names:
            self.imports[name.asname or name.name] = name.name
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from nodes to extract imports."""
        if node.module:
            for name in node.names:
                if name.name == '*':
                    continue  # Skip wildcard imports
                import_name = f"{node.module}.{name.name}"
                self.imports[name.asname or name.name] = import_name
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        # Resolve base classes
        bases = self._extract_bases(node.bases)
        
        # Create qualified name
        qualname = node.name
        if self.module_name:
            qualname = f"{self.module_name}.{node.name}"
        
        # Extract class methods
        methods = []
        class_attrs = {}
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_method(item, qualname)
                if method_info:
                    methods.append(method_info)
            elif isinstance(item, ast.AsyncFunctionDef):
                method_info = self._extract_async_method(item, qualname)
                if method_info:
                    methods.append(method_info)
            elif isinstance(item, ast.Assign):
                # Extract class attributes
                attr_names = self._extract_assign_targets(item.targets)
                for attr_name in attr_names:
                    class_attrs[attr_name] = self._extract_assign_value(item.value)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Extract annotated class attributes
                class_attrs[item.target.id] = {
                    "annotation": self._extract_annotation(item.annotation),
                    "value": self._extract_assign_value(item.value) if item.value else None
                }
        
        # Store class info
        class_info = {
            "name": node.name,
            "qualname": qualname,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "doc": ast.get_docstring(node),
            "bases": bases,
            "decorators": self._extract_decorators(node.decorator_list),
            "methods": [method["name"] for method in methods],
            "attributes": class_attrs
        }
        
        # Add to classes list
        self.classes.append(class_info)
        
        # Store methods
        self.methods[qualname] = methods
        
        # Update inheritance graph
        self.inheritance_graph[qualname] = bases
        
        # Process nested classes (change context)
        old_class = self.current_class
        self.current_class = class_info
        self.generic_visit(node)
        self.current_class = old_class
    
    def _extract_method(self, node: ast.FunctionDef, class_qualname: str) -> Optional[Dict[str, Any]]:
        """Extract method information."""
        # Skip private methods (except special methods)
        if node.name.startswith('_') and not (node.name.startswith('__') and node.name.endswith('__')):
            return None
        
        # Extract arguments
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
        
        # Check if this is a staticmethod, classmethod, or property
        is_static = False
        is_class = False
        is_property = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'staticmethod':
                    is_static = True
                elif decorator.id == 'classmethod':
                    is_class = True
                elif decorator.id == 'property':
                    is_property = True
        
        # Determine if this is a test method
        is_test = False
        if node.name.startswith('test_') or node.name.startswith('test'):
            is_test = True
        
        method_info = {
            "name": node.name,
            "qualname": f"{class_qualname}.{node.name}",
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "args": args,
            "decorators": self._extract_decorators(node.decorator_list),
            "doc": ast.get_docstring(node),
            "is_static": is_static,
            "is_class": is_class,
            "is_property": is_property,
            "is_test": is_test,
            "is_async": False,
            "return_annotation": self._extract_annotation(node.returns)
        }
        
        return method_info
    
    def _extract_async_method(self, node: ast.AsyncFunctionDef, class_qualname: str) -> Optional[Dict[str, Any]]:
        """Extract async method information."""
        # Skip private methods (except special methods)
        if node.name.startswith('_') and not (node.name.startswith('__') and node.name.endswith('__')):
            return None
        
        # Extract arguments
        args = []
        for arg in node.args.args:
            if hasattr(arg, 'arg'):
                args.append(arg.arg)
        
        # Check if this is a staticmethod, classmethod, or property
        is_static = False
        is_class = False
        is_property = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'staticmethod':
                    is_static = True
                elif decorator.id == 'classmethod':
                    is_class = True
                elif decorator.id == 'property':
                    is_property = True
        
        # Determine if this is a test method
        is_test = False
        if node.name.startswith('test_') or node.name.startswith('test'):
            is_test = True
        
        method_info = {
            "name": node.name,
            "qualname": f"{class_qualname}.{node.name}",
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "args": args,
            "decorators": self._extract_decorators(node.decorator_list),
            "doc": ast.get_docstring(node),
            "is_static": is_static,
            "is_class": is_class,
            "is_property": is_property,
            "is_test": is_test,
            "is_async": True,
            "return_annotation": self._extract_annotation(node.returns)
        }
        
        return method_info
    
    def _extract_bases(self, bases: List[ast.expr]) -> List[str]:
        """Extract base classes."""
        base_list = []
        for base in bases:
            if isinstance(base, ast.Name):
                base_list.append(base.id)
            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                # Handle module.Class
                if base.value.id in self.imports:
                    module_name = self.imports[base.value.id]
                    base_list.append(f"{module_name}.{base.attr}")
                else:
                    base_list.append(f"{base.value.id}.{base.attr}")
            elif isinstance(base, ast.Call):
                # Handle things like Generic[T]
                if isinstance(base.func, ast.Name):
                    base_list.append(f"{base.func.id}[...]")
                elif isinstance(base.func, ast.Attribute):
                    parts = []
                    node = base.func
                    while isinstance(node, ast.Attribute):
                        parts.insert(0, node.attr)
                        node = node.value
                    if isinstance(node, ast.Name):
                        parts.insert(0, node.id)
                        base_list.append(f"{'.'.join(parts)}[...]")
        return base_list
    
    def _extract_decorators(self, decorators: List[ast.expr]) -> List[str]:
        """Extract decorator names."""
        decorator_list = []
        for decorator in decorators:
            if isinstance(decorator, ast.Name):
                decorator_list.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                decorator_list.append(f"{decorator.func.id}(...)")
            elif isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
                decorator_list.append(f"{decorator.value.id}.{decorator.attr}")
        return decorator_list
    
    def _extract_annotation(self, annotation: Optional[ast.AST]) -> Optional[str]:
        """Extract a type annotation."""
        if annotation is None:
            return None
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Str):
            return annotation.s
        elif isinstance(annotation, ast.Subscript):
            # Handle generics like List[int]
            if isinstance(annotation.value, ast.Name):
                container = annotation.value.id
                # This is a simplification, a full implementation would recursively handle annotations
                return f"{container}[...]"
        
        # For complex annotations, return a placeholder
        return "..."
    
    def _extract_assign_targets(self, targets: List[ast.expr]) -> List[str]:
        """Extract assignment targets (attribute names)."""
        names = []
        for target in targets:
            if isinstance(target, ast.Name):
                names.append(target.id)
            elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                # Handle multiple assignment (a, b = 1, 2)
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        names.append(elt.id)
        return names
    
    def _extract_assign_value(self, value: ast.expr) -> Any:
        """Extract the value from an assignment."""
        if isinstance(value, ast.Num):
            return value.n
        elif isinstance(value, ast.Str):
            return value.s
        elif isinstance(value, ast.NameConstant):
            return value.value
        elif isinstance(value, ast.List):
            return [self._extract_assign_value(elt) for elt in value.elts]
        elif isinstance(value, ast.Tuple):
            return tuple(self._extract_assign_value(elt) for elt in value.elts)
        elif isinstance(value, ast.Dict):
            return {self._extract_assign_value(k): self._extract_assign_value(v) 
                   for k, v in zip(value.keys, value.values)}
        elif isinstance(value, ast.Name):
            return value.id
        
        # For complex values, return a placeholder
        return "..." 