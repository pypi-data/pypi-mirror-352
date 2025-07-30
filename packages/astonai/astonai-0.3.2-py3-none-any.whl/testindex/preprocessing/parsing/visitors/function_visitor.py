"""
AST visitor for extracting function definitions.
"""
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Tuple

from testindex.core.logging import get_logger

logger = get_logger("function-visitor")

class FunctionVisitor(ast.NodeVisitor):
    """AST visitor for extracting function definitions."""
    
    def __init__(self, file_path: Optional[str] = None, module_name: Optional[str] = None):
        """Initialize the visitor.
        
        Args:
            file_path: Optional path to the file being analyzed
            module_name: Optional module name (package.module)
        """
        self.file_path = file_path
        self.module_name = module_name
        
        self.functions: List[Dict[str, Any]] = []
        self.imports: Dict[str, str] = {}  # alias -> real_name
        self.current_class: Optional[Dict[str, Any]] = None
        self.current_function: Optional[Dict[str, Any]] = None
        self.current_scope: List[Dict[str, Any]] = []
        self.call_graph: Dict[str, List[str]] = {}  # function -> [called_functions]
        
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
    
    def _enter_scope(self, node_info: Dict[str, Any]) -> None:
        """Enter a new scope (class or function)."""
        self.current_scope.append(node_info)
    
    def _exit_scope(self) -> None:
        """Exit the current scope."""
        if self.current_scope:
            self.current_scope.pop()
    
    def _get_qualname(self, name: str) -> str:
        """Get the qualified name for a name in the current scope."""
        parts = []
        for scope in self.current_scope:
            if scope["type"] == "class":
                parts.append(scope["name"])
        parts.append(name)
        
        qualname = ".".join(parts)
        
        if self.module_name:
            return f"{self.module_name}:{qualname}"
        return qualname
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        # Store class info
        class_info = {
            "type": "class",
            "name": node.name,
            "qualname": self._get_qualname(node.name),
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "doc": ast.get_docstring(node),
            "bases": self._extract_bases(node.bases),
            "decorators": self._extract_decorators(node.decorator_list)
        }
        
        # Enter class scope
        old_class = self.current_class
        self.current_class = class_info
        self._enter_scope(class_info)
        
        # Visit class body
        self.generic_visit(node)
        
        # Exit class scope
        self._exit_scope()
        self.current_class = old_class
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        # Ignore special methods if part of a class
        if self.current_class and node.name.startswith("__") and node.name.endswith("__"):
            if node.name not in ["__init__", "__call__"]:
                self.generic_visit(node)
                return
        
        # Extract arguments
        args, defaults, kwarg, vararg = self._extract_args(node.args)
        
        # Store function info
        qualname = self._get_qualname(node.name)
        func_info = {
            "type": "function",
            "name": node.name,
            "qualname": qualname,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "args": args,
            "defaults": defaults,
            "kwarg": kwarg,
            "vararg": vararg,
            "decorators": self._extract_decorators(node.decorator_list),
            "is_method": self.current_class is not None,
            "class_name": self.current_class["name"] if self.current_class else None,
            "doc": ast.get_docstring(node),
            "return_annotation": self._extract_annotation(node.returns),
            "calls": []
        }
        
        # Add to functions list
        self.functions.append(func_info)
        
        # Enter function scope
        old_function = self.current_function
        self.current_function = func_info
        self._enter_scope(func_info)
        
        # Initialize call graph entry
        self.call_graph[qualname] = []
        
        # Visit function body
        self.generic_visit(node)
        
        # Exit function scope
        self._exit_scope()
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        # Same as regular function but mark as async
        # Ignore special methods if part of a class
        if self.current_class and node.name.startswith("__") and node.name.endswith("__"):
            if node.name not in ["__init__", "__call__"]:
                self.generic_visit(node)
                return
        
        # Extract arguments
        args, defaults, kwarg, vararg = self._extract_args(node.args)
        
        # Store function info
        qualname = self._get_qualname(node.name)
        func_info = {
            "type": "function",
            "name": node.name,
            "qualname": qualname,
            "file_path": self.file_path,
            "line_number": node.lineno,
            "col_offset": node.col_offset,
            "args": args,
            "defaults": defaults,
            "kwarg": kwarg,
            "vararg": vararg,
            "decorators": self._extract_decorators(node.decorator_list),
            "is_method": self.current_class is not None,
            "class_name": self.current_class["name"] if self.current_class else None,
            "doc": ast.get_docstring(node),
            "is_async": True,
            "return_annotation": self._extract_annotation(node.returns),
            "calls": []
        }
        
        # Add to functions list
        self.functions.append(func_info)
        
        # Enter function scope
        old_function = self.current_function
        self.current_function = func_info
        self._enter_scope(func_info)
        
        # Initialize call graph entry
        self.call_graph[qualname] = []
        
        # Visit function body
        self.generic_visit(node)
        
        # Exit function scope
        self._exit_scope()
        self.current_function = old_function
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to build call graph."""
        if self.current_function:
            callee_name = self._extract_call_name(node)
            if callee_name:
                # Add to current function's calls
                if callee_name not in self.current_function["calls"]:
                    self.current_function["calls"].append(callee_name)
                
                # Add to call graph
                qualname = self.current_function["qualname"]
                if callee_name not in self.call_graph[qualname]:
                    self.call_graph[qualname].append(callee_name)
        
        self.generic_visit(node)
    
    def _extract_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract the name of a called function."""
        if isinstance(node.func, ast.Name):
            # Simple name like func()
            return node.func.id
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # Attribute like obj.method() or module.func()
            # Check if it's an import
            if node.func.value.id in self.imports:
                module_name = self.imports[node.func.value.id]
                return f"{module_name}.{node.func.attr}"
            return f"{node.func.value.id}.{node.func.attr}"
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Attribute):
            # Nested attribute like module.submodule.func()
            parts = self._extract_nested_attribute(node.func)
            if parts:
                return ".".join(parts)
        return None
    
    def _extract_nested_attribute(self, node: ast.Attribute) -> List[str]:
        """Extract a nested attribute chain like module.submodule.func."""
        parts = []
        
        while isinstance(node, ast.Attribute):
            parts.insert(0, node.attr)
            node = node.value
        
        if isinstance(node, ast.Name):
            parts.insert(0, node.id)
            return parts
        
        return []
    
    def _extract_args(self, args: ast.arguments) -> Tuple[List[Dict[str, Any]], List[Any], Optional[str], Optional[str]]:
        """Extract function arguments."""
        arg_list = []
        defaults_list = []
        kwarg_name = None
        vararg_name = None
        
        # Handle positional args
        for arg in args.args:
            arg_info = {
                "name": arg.arg,
                "annotation": self._extract_annotation(arg.annotation)
            }
            arg_list.append(arg_info)
        
        # Handle keyword-only args
        for arg in getattr(args, 'kwonlyargs', []):
            arg_info = {
                "name": arg.arg,
                "annotation": self._extract_annotation(arg.annotation),
                "is_kwonly": True
            }
            arg_list.append(arg_info)
        
        # Handle vararg (like *args)
        if args.vararg:
            vararg_name = args.vararg.arg
        
        # Handle kwarg (like **kwargs)
        if args.kwarg:
            kwarg_name = args.kwarg.arg
        
        # Handle defaults for positional args
        for default in getattr(args, 'defaults', []):
            default_value = self._extract_value(default)
            defaults_list.append(default_value)
        
        # Handle defaults for keyword-only args
        for default in getattr(args, 'kw_defaults', []):
            if default is not None:
                default_value = self._extract_value(default)
                defaults_list.append(default_value)
            else:
                defaults_list.append(None)
        
        return arg_list, defaults_list, kwarg_name, vararg_name
    
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
    
    def _extract_bases(self, bases: List[ast.expr]) -> List[str]:
        """Extract base classes."""
        base_list = []
        for base in bases:
            if isinstance(base, ast.Name):
                base_list.append(base.id)
            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                base_list.append(f"{base.value.id}.{base.attr}")
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
    
    def _extract_value(self, node: ast.AST) -> Any:
        """Extract a literal value from an AST node."""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.NameConstant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._extract_value(elt) for elt in node.elts)
        elif isinstance(node, ast.Dict):
            return {self._extract_value(k): self._extract_value(v) 
                   for k, v in zip(node.keys, node.values)}
        # For complex values, return a placeholder
        return "..." 