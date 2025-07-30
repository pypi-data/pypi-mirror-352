"""
Code chunking module for segmenting Python code into logical units.

This module provides strategies for breaking down Python code into
meaningful chunks that can be processed independently while preserving
context and relationships between chunks.
"""

import ast
import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Tuple, Generator
from abc import ABC, abstractmethod

from testindex.core.logging import get_logger
from testindex.core.config import ConfigModel
from testindex.core.exceptions import AstonError
from testindex.preprocessing.parsing.ast_parser import ASTParser


class ChunkingError(AstonError):
    """Custom exception for errors during code chunking."""
    error_code = "CHUNK001"
    default_message = "An error occurred during code chunking."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        final_message = message or self.default_message
        if file_path:
            final_message = f"{final_message} in file {file_path}"

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=context or details
        )
        self.file_path = file_path


class ChunkType(enum.Enum):
    """Enum representing different types of code chunks."""
    
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    MODULE = "module"
    NESTED_FUNCTION = "nested_function"
    NESTED_CLASS = "nested_class"
    STANDALONE_CODE = "standalone_code"


@dataclass
class CodeChunk:
    """Class representing a chunk of code with metadata."""
    
    # Identification
    chunk_id: str
    chunk_type: ChunkType
    name: str
    source_file: Path
    
    # Source code
    source_code: str
    start_line: int
    end_line: int
    
    # Context
    parent_chunk_id: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Python-specific features
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False
    doc_string: Optional[str] = None
    
    # Metadata for traceability
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Convert source_file to Path if it's a string."""
        if isinstance(self.source_file, str):
            self.source_file = Path(self.source_file)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the CodeChunk to a dictionary."""
        result = {
            "chunk_id": self.chunk_id,
            "chunk_type": self.chunk_type.value,
            "name": self.name,
            "source_file": str(self.source_file),
            "source_code": self.source_code,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "imports": self.imports,
            "dependencies": self.dependencies,
            "decorators": self.decorators,
            "is_async": self.is_async,
            "metadata": self.metadata,
        }
        
        if self.parent_chunk_id:
            result["parent_chunk_id"] = self.parent_chunk_id
            
        if self.doc_string:
            result["doc_string"] = self.doc_string
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeChunk':
        """Create a CodeChunk from a dictionary."""
        chunk_type = ChunkType(data["chunk_type"])
        
        return cls(
            chunk_id=data["chunk_id"],
            chunk_type=chunk_type,
            name=data["name"],
            source_file=data["source_file"],
            source_code=data["source_code"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            parent_chunk_id=data.get("parent_chunk_id"),
            imports=data.get("imports", []),
            dependencies=data.get("dependencies", []),
            decorators=data.get("decorators", []),
            is_async=data.get("is_async", False),
            doc_string=data.get("doc_string"),
            metadata=data.get("metadata", {})
        )


class CodeChunker:
    """Base class for code chunking strategies."""
    
    def __init__(self, config: ConfigModel):
        """Initialize the code chunker.
        
        Args:
            config: Configuration object for the chunker
        """
        self.logger = get_logger("code-chunker")
        self.config = config
    
    def chunk_file(self, file_path: Union[str, Path]) -> List[CodeChunk]:
        """Chunk a file into code chunks.
        
        Args:
            file_path: Path to the file to chunk
            
        Returns:
            List[CodeChunk]: List of code chunks
        """
        raise NotImplementedError("Subclasses must implement chunk_file")
    
    def chunk_directory(self, 
                       dir_path: Union[str, Path],
                       recursive: bool = True,
                       file_pattern: str = "*") -> Dict[str, List[CodeChunk]]:
        """Chunk all files in a directory.
        
        Args:
            dir_path: Directory path to chunk
            recursive: Whether to process subdirectories
            file_pattern: File pattern to match
            
        Returns:
            Dict[str, List[CodeChunk]]: Dictionary mapping file paths to chunks
        """
        dir_path = Path(dir_path)
        result: Dict[str, List[CodeChunk]] = {}
        
        self.logger.info(f"Chunking directory: {dir_path}")
        
        # Get all matching files
        if recursive:
            files = list(dir_path.rglob(file_pattern))
        else:
            files = list(dir_path.glob(file_pattern))
        
        # Process each file
        for file_path in files:
            try:
                chunks = self.chunk_file(file_path)
                result[str(file_path)] = chunks
            except Exception as e:
                self.logger.warning(f"Failed to chunk file {file_path}: {e}")
        
        return result


class PythonCodeChunker(CodeChunker):
    """Python-specific code chunking implementation."""
    
    def __init__(self, config: ConfigModel):
        """Initialize the Python code chunker.
        
        Args:
            config: Configuration object for the chunker
        """
        super().__init__(config)
        self.parser = ASTParser(config)
        self.logger = get_logger("python-chunker")
        
        # Counter for generating unique chunk IDs
        self._chunk_counter = 0
    
    def _generate_chunk_id(self, prefix: str) -> str:
        """Generate a unique ID for a chunk.
        
        Args:
            prefix: Prefix for the chunk ID
            
        Returns:
            str: Unique chunk ID
        """
        self._chunk_counter += 1
        return f"{prefix}_{self._chunk_counter}"
    
    def chunk_file(self, file_path: Union[str, Path]) -> List[CodeChunk]:
        """Chunk a Python file into code chunks.
        
        Args:
            file_path: Path to the Python file to chunk
            
        Returns:
            List[CodeChunk]: List of code chunks
            
        Raises:
            ChunkingError: If chunking fails
        """
        file_path = Path(file_path)
        
        # Validate file extension
        if not file_path.name.endswith('.py'):
            raise ChunkingError(
                f"Not a Python file: {file_path}",
                details={"file": str(file_path)}
            )
        
        try:
            # Parse the file
            tree = self.parser.parse_file(file_path)
            
            # Get source code
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Extract all import statements
            import_visitor = ImportVisitor()
            import_visitor.visit(tree)
            imports = import_visitor.imports
            
            chunks = []
            
            # Create a module-level chunk
            module_chunk = self._create_module_chunk(file_path, tree, source_code, imports)
            chunks.append(module_chunk)
            
            # Process top-level classes and functions
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_chunks = self._process_class(node, file_path, source_code, imports, module_chunk.chunk_id)
                    chunks.extend(class_chunks)
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    function_chunk = self._process_function(node, file_path, source_code, imports, module_chunk.chunk_id)
                    chunks.append(function_chunk)
            
            # Add standalone code chunks (code outside of classes and functions)
            standalone_chunks = self._extract_standalone_code(tree, file_path, source_code, imports, module_chunk.chunk_id)
            chunks.extend(standalone_chunks)
            
            return chunks
            
        except Exception as e:
            error_msg = f"Failed to chunk file {file_path}: {e}"
            self.logger.error(error_msg)
            raise ChunkingError(error_msg, details={"file": str(file_path)})
    
    def _create_module_chunk(self, 
                           file_path: Path, 
                           tree: ast.Module, 
                           source_code: str,
                           imports: List[str]) -> CodeChunk:
        """Create a module-level chunk.
        
        Args:
            file_path: Path to the Python file
            tree: AST tree of the file
            source_code: Source code of the file
            imports: List of import statements
            
        Returns:
            CodeChunk: Module-level chunk
        """
        # Get module docstring if present
        doc_string = ast.get_docstring(tree)
        
        # Create module chunk
        return CodeChunk(
            chunk_id=self._generate_chunk_id("module"),
            chunk_type=ChunkType.MODULE,
            name=file_path.stem,
            source_file=file_path,
            source_code=source_code,
            start_line=1,
            end_line=len(source_code.splitlines()),
            imports=imports,
            dependencies=[],
            doc_string=doc_string,
            metadata={
                "path": str(file_path),
                "is_package": (file_path.parent / "__init__.py").exists(),
            }
        )
    
    def _process_class(self, 
                     node: ast.ClassDef, 
                     file_path: Path, 
                     source_code: str,
                     imports: List[str],
                     parent_chunk_id: str) -> List[CodeChunk]:
        """Process a class definition and its methods.
        
        Args:
            node: AST node for the class
            file_path: Path to the Python file
            source_code: Source code of the file
            imports: List of import statements
            parent_chunk_id: ID of the parent chunk
            
        Returns:
            List[CodeChunk]: List of chunks for the class and its methods
        """
        chunks = []
        
        # Get class source code
        class_lines = source_code.splitlines()[node.lineno-1:node.end_lineno]
        class_source = "\n".join(class_lines)
        
        # Get decorator list
        decorators = [self._get_decorator_source(d, source_code) for d in node.decorator_list]
        
        # Get docstring
        doc_string = ast.get_docstring(node)
        
        # Create class chunk
        class_chunk_id = self._generate_chunk_id("class")
        class_chunk = CodeChunk(
            chunk_id=class_chunk_id,
            chunk_type=ChunkType.CLASS if parent_chunk_id else ChunkType.NESTED_CLASS,
            name=node.name,
            source_file=file_path,
            source_code=class_source,
            start_line=node.lineno,
            end_line=node.end_lineno,
            parent_chunk_id=parent_chunk_id,
            imports=imports,
            dependencies=self._extract_base_classes(node),
            decorators=decorators,
            doc_string=doc_string,
            metadata={
                "base_classes": [self._get_node_source(b, source_code) for b in node.bases],
                "keywords": [self._get_node_source(k, source_code) for k in node.keywords]
            }
        )
        chunks.append(class_chunk)
        
        # Process methods
        for child_node in node.body:
            if isinstance(child_node, ast.FunctionDef) or isinstance(child_node, ast.AsyncFunctionDef):
                method_chunk = self._process_function(child_node, file_path, source_code, imports, class_chunk_id)
                chunks.append(method_chunk)
            elif isinstance(child_node, ast.ClassDef):
                nested_class_chunks = self._process_class(child_node, file_path, source_code, imports, class_chunk_id)
                chunks.extend(nested_class_chunks)
        
        return chunks
    
    def _process_function(self, 
                        node: Union[ast.FunctionDef, ast.AsyncFunctionDef], 
                        file_path: Path, 
                        source_code: str,
                        imports: List[str],
                        parent_chunk_id: Optional[str] = None) -> CodeChunk:
        """Process a function or method definition.
        
        Args:
            node: AST node for the function
            file_path: Path to the Python file
            source_code: Source code of the file
            imports: List of import statements
            parent_chunk_id: ID of the parent chunk (if a method)
            
        Returns:
            CodeChunk: Function or method chunk
        """
        # Get function source code
        func_lines = source_code.splitlines()[node.lineno-1:node.end_lineno]
        func_source = "\n".join(func_lines)
        
        # Get decorator list
        decorators = [self._get_decorator_source(d, source_code) for d in node.decorator_list]
        
        # Get docstring
        doc_string = ast.get_docstring(node)
        
        # Determine dependencies (imported modules/functions used)
        dependency_visitor = DependencyVisitor()
        dependency_visitor.visit(node)
        dependencies = dependency_visitor.dependencies
        
        # Determine if it's a method or function
        is_method = parent_chunk_id is not None and parent_chunk_id.startswith("class")
        chunk_type = ChunkType.METHOD if is_method else ChunkType.FUNCTION
        
        # If it's a nested function, mark it as such
        if parent_chunk_id is not None and parent_chunk_id.startswith("function"):
            chunk_type = ChunkType.NESTED_FUNCTION
        
        # Create function chunk
        return CodeChunk(
            chunk_id=self._generate_chunk_id("function"),
            chunk_type=chunk_type,
            name=node.name,
            source_file=file_path,
            source_code=func_source,
            start_line=node.lineno,
            end_line=node.end_lineno,
            parent_chunk_id=parent_chunk_id,
            imports=imports,
            dependencies=dependencies,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            doc_string=doc_string,
            metadata={
                "args": self._get_function_args(node),
                "returns": self._get_function_return_annotation(node, source_code)
            }
        )
    
    def _extract_standalone_code(self, 
                               tree: ast.Module, 
                               file_path: Path, 
                               source_code: str,
                               imports: List[str],
                               parent_chunk_id: str) -> List[CodeChunk]:
        """Extract standalone code (code outside of classes and functions).
        
        Args:
            tree: AST tree of the file
            file_path: Path to the Python file
            source_code: Source code of the file
            imports: List of import statements
            parent_chunk_id: ID of the parent module chunk
            
        Returns:
            List[CodeChunk]: List of standalone code chunks
        """
        chunks = []
        lines = source_code.splitlines()
        
        # Find regions that are not part of a class or function
        covered_lines = set()
        
        # Mark lines covered by classes and functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                for i in range(node.lineno, node.end_lineno + 1):
                    covered_lines.add(i)
        
        # Find contiguous blocks of uncovered lines (excluding imports)
        import_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for i in range(node.lineno, node.end_lineno + 1):
                    import_lines.add(i)
                    covered_lines.add(i)
        
        # Find contiguous blocks of uncovered lines
        start_line = None
        for i, _ in enumerate(lines, 1):
            if i not in covered_lines and i not in import_lines:
                if start_line is None:
                    start_line = i
            elif start_line is not None:
                end_line = i - 1
                if end_line >= start_line:  # Ensure we have at least one line
                    standalone_code = "\n".join(lines[start_line-1:end_line])
                    # Only create a chunk if it's not just whitespace or comments
                    if standalone_code.strip() and not all(l.strip().startswith('#') for l in standalone_code.strip().splitlines()):
                        chunks.append(CodeChunk(
                            chunk_id=self._generate_chunk_id("standalone"),
                            chunk_type=ChunkType.STANDALONE_CODE,
                            name=f"standalone_{start_line}_{end_line}",
                            source_file=file_path,
                            source_code=standalone_code,
                            start_line=start_line,
                            end_line=end_line,
                            parent_chunk_id=parent_chunk_id,
                            imports=imports,
                            dependencies=[],
                            metadata={
                                "context": "standalone_code"
                            }
                        ))
                start_line = None
        
        # Handle the last block if it exists
        if start_line is not None:
            end_line = len(lines)
            standalone_code = "\n".join(lines[start_line-1:end_line])
            # Only create a chunk if it's not just whitespace or comments
            if standalone_code.strip() and not all(l.strip().startswith('#') for l in standalone_code.strip().splitlines()):
                chunks.append(CodeChunk(
                    chunk_id=self._generate_chunk_id("standalone"),
                    chunk_type=ChunkType.STANDALONE_CODE,
                    name=f"standalone_{start_line}_{end_line}",
                    source_file=file_path,
                    source_code=standalone_code,
                    start_line=start_line,
                    end_line=end_line,
                    parent_chunk_id=parent_chunk_id,
                    imports=imports,
                    dependencies=[],
                    metadata={
                        "context": "standalone_code"
                    }
                ))
        
        return chunks
    
    def _get_decorator_source(self, decorator: ast.expr, source_code: str) -> str:
        """Get the source code of a decorator.
        
        Args:
            decorator: AST node for the decorator
            source_code: Source code of the file
            
        Returns:
            str: Source code of the decorator
        """
        return self._get_node_source(decorator, source_code)
    
    def _get_node_source(self, node: ast.AST, source_code: str) -> str:
        """Get the source code of an AST node.
        
        Args:
            node: AST node
            source_code: Source code of the file
            
        Returns:
            str: Source code of the node
        """
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return ""
        
        lines = source_code.splitlines()[node.lineno-1:node.end_lineno]
        return "\n".join(lines)
    
    def _extract_base_classes(self, node: ast.ClassDef) -> List[str]:
        """Extract base class names from a class definition.
        
        Args:
            node: AST node for the class
            
        Returns:
            List[str]: List of base class names
        """
        bases = []
        
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(self._get_attribute_name(base))
        
        return bases
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute (e.g., module.Class).
        
        Args:
            node: AST attribute node
            
        Returns:
            str: Full attribute name
        """
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return node.attr
    
    def _get_function_args(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Dict[str, Any]:
        """Extract function arguments with their annotations.
        
        Args:
            node: AST node for the function
            
        Returns:
            Dict[str, Any]: Dictionary of argument information
        """
        args_info = {
            "args": [],
            "defaults": [],
            "kwonlyargs": [],
            "kw_defaults": [],
            "vararg": None,
            "kwarg": None
        }
        
        # Process regular arguments
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation)
            }
            args_info["args"].append(arg_info)
        
        # Process default values
        for default in node.args.defaults:
            if isinstance(default, ast.Constant):
                args_info["defaults"].append(repr(default.value))
            else:
                args_info["defaults"].append("complex_default")
        
        # Process *args
        if node.args.vararg:
            args_info["vararg"] = {
                "name": node.args.vararg.arg,
                "annotation": self._get_annotation(node.args.vararg.annotation)
            }
        
        # Process keyword-only arguments
        for arg in node.args.kwonlyargs:
            arg_info = {
                "name": arg.arg,
                "annotation": self._get_annotation(arg.annotation)
            }
            args_info["kwonlyargs"].append(arg_info)
        
        # Process keyword-only defaults
        for default in node.args.kw_defaults:
            if default is None:
                args_info["kw_defaults"].append(None)
            elif isinstance(default, ast.Constant):
                args_info["kw_defaults"].append(repr(default.value))
            else:
                args_info["kw_defaults"].append("complex_default")
        
        # Process **kwargs
        if node.args.kwarg:
            args_info["kwarg"] = {
                "name": node.args.kwarg.arg,
                "annotation": self._get_annotation(node.args.kwarg.annotation)
            }
        
        return args_info
    
    def _get_annotation(self, annotation: Optional[ast.expr]) -> Optional[str]:
        """Get a string representation of a type annotation.
        
        Args:
            annotation: AST node for the annotation
            
        Returns:
            Optional[str]: String representation of the annotation
        """
        if annotation is None:
            return None
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            return self._get_attribute_name(annotation)
        elif isinstance(annotation, ast.Subscript):
            # Handle generic types like List[int]
            return "complex_type"
        elif isinstance(annotation, ast.Constant):
            # Handle string annotations
            return str(annotation.value)
        
        return "unknown_type"
    
    def _get_function_return_annotation(self, 
                                      node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
                                      source_code: str) -> Optional[str]:
        """Get the return annotation of a function.
        
        Args:
            node: AST node for the function
            source_code: Source code of the file
            
        Returns:
            Optional[str]: Return annotation as a string
        """
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return self._get_attribute_name(node.returns)
            elif isinstance(node.returns, ast.Subscript):
                # For complex return types, get the source code
                return self._get_node_source(node.returns, source_code)
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
        
        return None


class ImportVisitor(ast.NodeVisitor):
    """AST visitor that collects import statements."""
    
    def __init__(self):
        """Initialize the import visitor."""
        self.imports = []
    
    def visit_Import(self, node: ast.Import):
        """Visit an import statement.
        
        Args:
            node: AST import node
        """
        for name in node.names:
            if name.asname:
                self.imports.append(f"import {name.name} as {name.asname}")
            else:
                self.imports.append(f"import {name.name}")
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit an import from statement.
        
        Args:
            node: AST import from node
        """
        module = node.module or ''
        names = []
        
        for name in node.names:
            if name.asname:
                names.append(f"{name.name} as {name.asname}")
            else:
                names.append(name.name)
        
        if names:
            if module:
                self.imports.append(f"from {module} import {', '.join(names)}")
            else:
                self.imports.append(f"from . import {', '.join(names)}")


class DependencyVisitor(ast.NodeVisitor):
    """AST visitor that collects external dependencies used in code."""
    
    def __init__(self):
        """Initialize the dependency visitor."""
        self.dependencies = []
        self._names = set()
    
    def visit_Name(self, node: ast.Name):
        """Visit a name reference.
        
        Args:
            node: AST name node
        """
        if isinstance(node.ctx, ast.Load) and node.id not in self._names:
            self._names.add(node.id)
            self.dependencies.append(node.id)
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Visit an attribute reference.
        
        Args:
            node: AST attribute node
        """
        if isinstance(node.value, ast.Name):
            attr_name = f"{node.value.id}.{node.attr}"
            if attr_name not in self._names:
                self._names.add(attr_name)
                self.dependencies.append(attr_name)
        
        self.generic_visit(node) 