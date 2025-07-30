"""
AST parsing utilities for Python code analysis.
"""
import ast
import re
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any, Type

try:
    import parso
    HAS_PARSO = True
except ImportError:
    HAS_PARSO = False

try:
    import libcst as cst
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False

from testindex.core.logging import get_logger
from testindex.core.exceptions import AstonError
from testindex.core.config import ConfigModel
from parso.python import tree
from parso import ParserSyntaxError

# Define exceptions
class ParsingError(AstonError):
    """Custom exception for errors during AST parsing."""
    error_code = "PARSE001" # Default error code for this specific exception type
    default_message = "An error occurred during AST parsing." # Default message for this type

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, source_file: Optional[str] = None):
        # If a specific error_code isn't provided for the instance, it will use the class's error_code.
        # If a specific message isn't provided, it will use the class's default_message.
        final_message = message or self.default_message
        if source_file:
            final_message = f"{final_message} in file {source_file}"
        
        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code, 
            context=context
        )
        self.source_file = source_file

class FileParsingError(ParsingError):
    """Exception raised when parsing a file fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a file parsing error."""
        super().__init__(message=message, details=details)

class ASTParsingError(ParsingError):
    """Exception raised when AST parsing fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize an AST parsing error."""
        super().__init__(message=message, details=details)

class FrameworkDetectionError(ParsingError):
    """Exception raised when framework detection fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a framework detection error."""
        super().__init__(message=message, details=details)

class ASTParser:
    """Robust AST parser with fallback strategies for Python code analysis."""
    
    def __init__(self, config: ConfigModel):
        """Initialize the AST parser.
        
        Args:
            config: Configuration object
        """
        self.logger = get_logger("ast-parser")
        self.config = config
        self.cache: Dict[str, ast.AST] = {}
        self.parsing_stats = {"ast": 0, "parso": 0, "libcst": 0, "regex": 0, "failed": 0}
        
    def parse_file(self, file_path: Union[str, Path]) -> ast.Module:
        """Parse a Python file into an AST.
        
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            ast.Module: The parsed AST
            
        Raises:
            FileParsingError: If the file cannot be read
            ASTParsingError: If the file cannot be parsed
        """
        file_path = Path(file_path)
        abs_path = str(file_path.absolute())
        
        # Check cache
        if abs_path in self.cache:
            self.logger.debug(f"Using cached AST for {file_path}")
            return self.cache[abs_path]
        
        self.logger.debug(f"Parsing {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            self.logger.error(error_msg)
            raise FileParsingError(error_msg, details={"file": str(file_path)})
        
        return self.parse_source_robust(source, file_path=abs_path)
    
    def parse_source(self, source: str, file_path: Optional[str] = None) -> ast.Module:
        """Parse Python source code into an AST (legacy method for compatibility).
        
        Args:
            source: The source code to parse
            file_path: Optional file path for caching
            
        Returns:
            ast.Module: The parsed AST
            
        Raises:
            ASTParsingError: If the source code cannot be parsed
        """
        return self.parse_source_robust(source, file_path)
    
    def parse_source_robust(self, source: str, file_path: Optional[str] = None) -> Optional[ast.Module]:
        """Parse Python source code with robust fallback strategies.
        
        Args:
            source: The source code to parse
            file_path: Optional file path for caching and debugging
            
        Returns:
            ast.Module: The parsed AST, or None if all strategies fail
        """
        # Strategy 1: Standard AST (fastest)
        try:
            tree = ast.parse(source)
            self.parsing_stats["ast"] += 1
            
            # Cache if file_path is provided
            if file_path:
                self.cache[file_path] = tree
                
            return tree
        except SyntaxError as e:
            self.logger.debug(f"Standard AST failed for {file_path}: {e}")
        except Exception as e:
            self.logger.debug(f"Standard AST failed for {file_path}: {e}")
        
        # For code chunks (indented code), try to fix indentation
        if source.strip() and source.startswith((' ', '\t')):
            try:
                # Remove common leading whitespace
                import textwrap
                dedented_source = textwrap.dedent(source)
                tree = ast.parse(dedented_source)
                self.parsing_stats["ast"] += 1
                
                if file_path:
                    self.cache[file_path] = tree
                    
                return tree
            except (SyntaxError, Exception) as e:
                self.logger.debug(f"Dedented AST failed for {file_path}: {e}")
        
        # Strategy 2: Parso fallback
        if HAS_PARSO:
            try:
                tree = self._parse_with_parso(source, file_path)
                if tree:
                    self.parsing_stats["parso"] += 1
                    return tree
            except Exception as e:
                self.logger.debug(f"Parso failed for {file_path}: {e}")
        
        # Strategy 3: LibCST fallback
        if HAS_LIBCST:
            try:
                tree = self._parse_with_libcst(source, file_path)
                if tree:
                    self.parsing_stats["libcst"] += 1
                    return tree
            except Exception as e:
                self.logger.debug(f"LibCST failed for {file_path}: {e}")
        
        # Strategy 4: Regex fallback (last resort)
        try:
            tree = self._parse_with_regex(source, file_path)
            if tree:
                self.parsing_stats["regex"] += 1
                return tree
        except Exception as e:
            self.logger.debug(f"Regex fallback failed for {file_path}: {e}")
        
        # All strategies failed
        self.parsing_stats["failed"] += 1
        self.logger.warning(f"All parsing strategies failed for {file_path}")
        
        # For compatibility, raise an exception like the original implementation
        error_msg = f"Failed to parse {'source' if not file_path else file_path}: All parsing strategies failed"
        raise ASTParsingError(error_msg, details={"file": file_path})
    
    def _parse_with_parso(self, source: str, file_path: Optional[str] = None) -> Optional[ast.Module]:
        """Parse using parso with error recovery."""
        try:
            # For indented code chunks, try to make them parseable
            if source.strip() and source.startswith((' ', '\t')):
                import textwrap
                source = textwrap.dedent(source)
            
            # Parso can handle syntax errors gracefully
            parso_tree = parso.parse(source, error_recovery=True)
            
            # Create a minimal AST module for compatibility
            module = ast.Module(body=[], type_ignores=[])
            
            # Extract function calls from parso tree
            calls = self._extract_calls_from_parso(parso_tree)
            
            # Store calls in a way that can be accessed later
            setattr(module, '_parso_calls', calls)
            setattr(module, '_parsing_strategy', 'parso')
            
            return module
            
        except Exception as e:
            self.logger.debug(f"Parso parsing failed: {e}")
            return None
    
    def _parse_with_libcst(self, source: str, file_path: Optional[str] = None) -> Optional[ast.Module]:
        """Parse using LibCST."""
        try:
            # For indented code chunks, try to make them parseable
            if source.strip() and source.startswith((' ', '\t')):
                import textwrap
                source = textwrap.dedent(source)
            
            # LibCST is more robust with syntax errors
            cst_tree = cst.parse_module(source)
            
            # Convert CST to AST (simplified)
            module = ast.Module(body=[], type_ignores=[])
            
            # Extract calls from CST
            calls = self._extract_calls_from_cst(cst_tree)
            setattr(module, '_libcst_calls', calls)
            setattr(module, '_parsing_strategy', 'libcst')
            
            return module
            
        except Exception as e:
            self.logger.debug(f"LibCST parsing failed: {e}")
            return None
    
    def _parse_with_regex(self, source: str, file_path: Optional[str] = None) -> Optional[ast.Module]:
        """Parse using regex as last resort."""
        try:
            # Create a minimal AST module for compatibility
            module = ast.Module(body=[], type_ignores=[])
            
            # Extract calls using regex
            calls = self._extract_calls_regex(source)
            setattr(module, '_regex_calls', calls)
            setattr(module, '_parsing_strategy', 'regex')
            
            return module
            
        except Exception as e:
            self.logger.debug(f"Regex parsing failed: {e}")
            return None
    
    def _extract_calls_from_parso(self, tree) -> List[str]:
        """Extract function calls from parso tree."""
        calls = []
        
        def visit_node(node):
            # Check for function calls in parso tree
            if hasattr(node, 'type'):
                # Look for 'atom_expr' which represents function calls
                if node.type == 'atom_expr':
                    children = getattr(node, 'children', [])
                    if len(children) >= 2:
                        # Check if this atom_expr has a trailer with parentheses (indicating a call)
                        has_call_trailer = False
                        for child in children[1:]:  # Skip first child (the name)
                            if (hasattr(child, 'type') and child.type == 'trailer' and
                                hasattr(child, 'children') and len(child.children) > 0):
                                first_child = child.children[0]
                                if hasattr(first_child, 'value') and first_child.value == '(':
                                    has_call_trailer = True
                                    break
                        
                        if has_call_trailer:
                            # Extract the full call name
                            call_parts = []
                            for child in children:
                                if hasattr(child, 'type'):
                                    if child.type == 'name':
                                        # Simple name
                                        if hasattr(child, 'value'):
                                            call_parts.append(child.value)
                                    elif child.type == 'trailer':
                                        # Handle attribute access (e.g., .method_name)
                                        trailer_children = getattr(child, 'children', [])
                                        for tc in trailer_children:
                                            if hasattr(tc, 'type') and tc.type == 'name':
                                                if hasattr(tc, 'value'):
                                                    call_parts.append('.' + tc.value)
                                            elif hasattr(tc, 'value') and tc.value == '(':
                                                # Stop at the opening parenthesis
                                                break
                            
                            if call_parts:
                                func_name = ''.join(call_parts)
                                if func_name:
                                    calls.append(func_name)
            
            # Recursively visit children
            if hasattr(node, 'children'):
                for child in node.children:
                    visit_node(child)
        
        visit_node(tree)
        
        # Remove duplicates and filter out invalid names
        unique_calls = []
        seen = set()
        for call in calls:
            if call not in seen and len(call) > 0:
                # Basic validation - should look like a function name
                clean_call = call.replace('.', '_').replace('_', '')
                if clean_call.isalnum() and not call.startswith('.'):
                    unique_calls.append(call)
                    seen.add(call)
        
        return unique_calls
    
    def _extract_calls_from_cst(self, tree) -> List[str]:
        """Extract function calls from LibCST tree."""
        calls = []
        
        class CallVisitor(cst.CSTVisitor):
            def visit_Call(self, node: cst.Call) -> None:
                # Extract function name from call
                if isinstance(node.func, cst.Name):
                    calls.append(node.func.value)
                elif isinstance(node.func, cst.Attribute):
                    # Handle method calls like obj.method()
                    call_name = self._get_full_name(node.func)
                    if call_name:
                        calls.append(call_name)
            
            def _get_full_name(self, node) -> str:
                """Get full qualified name from attribute access."""
                if isinstance(node, cst.Name):
                    return node.value
                elif isinstance(node, cst.Attribute):
                    base = self._get_full_name(node.value)
                    return f"{base}.{node.attr.value}" if base else node.attr.value
                return ""
        
        visitor = CallVisitor()
        tree.visit(visitor)
        return calls
    
    def _extract_calls_regex(self, source: str) -> List[str]:
        """Extract function calls using regex as last resort."""
        # Pattern for function calls: word followed by parentheses
        call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\('
        matches = re.findall(call_pattern, source)
        
        # Filter out keywords and common false positives
        keywords = {
            'if', 'for', 'while', 'def', 'class', 'with', 'try', 'except', 
            'elif', 'else', 'finally', 'import', 'from', 'as', 'return',
            'yield', 'raise', 'assert', 'del', 'pass', 'break', 'continue',
            'global', 'nonlocal', 'lambda', 'and', 'or', 'not', 'in', 'is'
        }
        
        # Filter out keywords and duplicates
        filtered_calls = []
        seen = set()
        for match in matches:
            if match not in keywords and match not in seen:
                filtered_calls.append(match)
                seen.add(match)
        
        return filtered_calls
    
    def get_parsing_stats(self) -> Dict[str, int]:
        """Get statistics on which parsers were used."""
        return self.parsing_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset parsing statistics."""
        self.parsing_stats = {"ast": 0, "parso": 0, "libcst": 0, "regex": 0, "failed": 0}
        
    def clear_cache(self) -> None:
        """Clear the parser cache."""
        self.cache.clear()
        
    def parse_directory(self, dir_path: Union[str, Path], 
                       recursive: bool = True,
                       ignore_errors: bool = False) -> Dict[str, ast.Module]:
        """Parse all Python files in a directory.
        
        Args:
            dir_path: Directory path to parse
            recursive: Whether to parse subdirectories
            ignore_errors: Whether to ignore parsing errors
            
        Returns:
            Dict[str, ast.Module]: Dictionary mapping file paths to ASTs
        """
        dir_path = Path(dir_path)
        result: Dict[str, ast.Module] = {}
        
        self.logger.info(f"Parsing directory: {dir_path}")
        
        try:
            files = self._get_python_files(dir_path, recursive)
            
            for file_path in files:
                try:
                    ast_module = self.parse_file(file_path)
                    result[str(file_path)] = ast_module
                except (FileParsingError, ASTParsingError) as e:
                    if not ignore_errors:
                        raise
                    self.logger.warning(f"Ignoring error in {file_path}: {e}")
            
            self.logger.info(f"Parsed {len(result)} Python files in {dir_path}")
            return result
        
        except Exception as e:
            error_msg = f"Failed to parse directory {dir_path}: {e}"
            self.logger.error(error_msg)
            raise ParsingError(error_msg, details={"directory": str(dir_path)})
    
    def _get_python_files(self, dir_path: Path, recursive: bool = True) -> List[Path]:
        """Get all Python files in a directory.
        
        Args:
            dir_path: Directory path
            recursive: Whether to include subdirectories
            
        Returns:
            List[Path]: List of Python file paths
        """
        files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    if filename.endswith('.py'):
                        files.append(Path(root) / filename)
        else:
            # Only get files in the current directory
            for item in dir_path.iterdir():
                if item.is_file() and item.name.endswith('.py'):
                    files.append(item)
        
        return files

    def visit_file_with_visitor(self, file_path: Union[str, Path], 
                                visitor_class: Type[ast.NodeVisitor],
                                visitor_args: Optional[Dict[str, Any]] = None) -> ast.NodeVisitor:
        """Parse a file and apply a visitor to its AST.
        
        Args:
            file_path: Path to the Python file
            visitor_class: AST visitor class to use
            visitor_args: Optional arguments to pass to the visitor constructor
            
        Returns:
            ast.NodeVisitor: The visitor instance after traversal
        """
        file_path = Path(file_path)
        visitor_args = visitor_args or {}
        
        try:
            tree = self.parse_file(file_path)
            visitor = visitor_class(file_path=str(file_path), **visitor_args)
            visitor.visit(tree)
            return visitor
        except Exception as e:
            error_msg = f"Failed to visit AST for {file_path}: {e}"
            self.logger.error(error_msg)
            raise ParsingError(error_msg, details={"file": str(file_path)})
    
    def detect_framework(self, file_path: Union[str, Path]) -> str:
        """Detect testing framework used in a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            str: Detected framework name or "unknown"
        """
        # This functionality is implemented in framework_detector.py
        from testindex.preprocessing.parsing.frameworks.framework_detector import detect_framework
        
        try:
            return detect_framework(self, file_path)
        except Exception as e:
            error_msg = f"Framework detection failed for {file_path}: {e}"
            self.logger.error(error_msg)
            raise FrameworkDetectionError(error_msg, details={"file": str(file_path)})


# Backward compatibility alias
RobustASTParser = ASTParser 