"""
Symbol extraction utilities for Python code.
"""
import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from testindex.core.logging import get_logger
from testindex.core.exceptions import AstonError
from testindex.core.config import ConfigModel

from testindex.preprocessing.parsing.ast_parser import ASTParser, ParsingError
from testindex.preprocessing.parsing.visitors.function_visitor import FunctionVisitor
from testindex.preprocessing.parsing.visitors.class_visitor import ClassVisitor
from testindex.preprocessing.parsing.visitors.test_visitor import TestVisitor
from testindex.preprocessing.parsing.frameworks.framework_detector import detect_framework

# Define exceptions
class ExtractionError(AstonError):
    """Custom exception for errors during symbol extraction."""
    error_code = "EXTRACT001"
    default_message = "An error occurred during symbol extraction."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize an extraction error."""
        super().__init__(
            message=message or self.default_message,
            error_code=error_code or self.error_code,
            context=context or details
        )

class SymbolExtractionError(ExtractionError):
    """Exception raised when symbol extraction fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a symbol extraction error."""
        super().__init__(message=message, error_code="EXTRACT001", details=details)

class SymbolExtractor:
    """Extracts symbols (functions, classes, tests) from Python files."""
    
    def __init__(self, config: ConfigModel, parser: Optional[ASTParser] = None):
        """Initialize the symbol extractor.
        
        Args:
            config: Configuration object
            parser: Optional AST parser to use
        """
        self.logger = get_logger("symbol-extractor")
        self.config = config
        self.parser = parser or ASTParser(config)
    
    def extract_symbols_from_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract all symbols from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dict: Symbol information extracted from the file
            
        Raises:
            SymbolExtractionError: If extraction fails
        """
        self.logger.debug(f"Extracting symbols from {file_path}")
        
        try:
            # Parse the file
            tree = self.parser.parse_file(file_path)
            
            # Get module name
            module_name = self._get_module_name(file_path)
            
            # Detect framework
            framework = detect_framework(self.parser, file_path)
            
            # Extract functions
            function_visitor = FunctionVisitor(file_path=str(file_path), module_name=module_name)
            function_visitor.visit(tree)
            
            # Extract classes
            class_visitor = ClassVisitor(file_path=str(file_path), module_name=module_name)
            class_visitor.visit(tree)
            
            # Extract tests
            test_visitor = TestVisitor(file_path=str(file_path), framework=framework)
            test_visitor.visit(tree)
            
            # Combine all symbols
            symbols = {
                "file_path": str(file_path),
                "module_name": module_name,
                "test_framework": framework,
                "functions": function_visitor.functions,
                "classes": class_visitor.classes,
                "methods": class_visitor.methods,
                "test_functions": test_visitor.test_functions,
                "test_classes": test_visitor.test_classes,
                "fixtures": test_visitor.fixtures,
                "imports": list(function_visitor.imports.keys()),
                "call_graph": function_visitor.call_graph,
                "inheritance_graph": class_visitor.inheritance_graph,
                "module_markers": test_visitor.module_markers,
                "dependencies": list(test_visitor.dependencies)
            }
            
            return symbols
            
        except ParsingError as e:
            error_msg = f"Failed to parse file for symbol extraction: {e}"
            self.logger.error(error_msg)
            raise SymbolExtractionError(error_msg, details={"file": str(file_path)})
        except Exception as e:
            error_msg = f"Symbol extraction failed: {e}"
            self.logger.error(error_msg)
            raise SymbolExtractionError(error_msg, details={"file": str(file_path)})
    
    def extract_symbols_from_directory(self, dir_path: Union[str, Path], 
                                      recursive: bool = True,
                                      ignore_errors: bool = False) -> Dict[str, Dict[str, Any]]:
        """Extract symbols from all Python files in a directory.
        
        Args:
            dir_path: Directory path to process
            recursive: Whether to process subdirectories
            ignore_errors: Whether to ignore errors during extraction
            
        Returns:
            Dict: Mapping of file paths to symbol information
        """
        dir_path = Path(dir_path)
        self.logger.info(f"Extracting symbols from directory: {dir_path}")
        
        result: Dict[str, Dict[str, Any]] = {}
        
        try:
            # Get all Python files
            python_files = self._get_python_files(dir_path, recursive)
            
            for file_path in python_files:
                try:
                    symbols = self.extract_symbols_from_file(file_path)
                    result[str(file_path)] = symbols
                except (SymbolExtractionError, ParsingError) as e:
                    if not ignore_errors:
                        raise
                    self.logger.warning(f"Ignoring error in {file_path}: {e}")
            
            self.logger.info(f"Extracted symbols from {len(result)} Python files in {dir_path}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to extract symbols from directory {dir_path}: {e}"
            self.logger.error(error_msg)
            raise ExtractionError(error_msg, details={"directory": str(dir_path)})
    
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
    
    def _get_module_name(self, file_path: Union[str, Path]) -> Optional[str]:
        """Try to determine the module name from the file path.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Optional[str]: Module name if determinable, None otherwise
        """
        file_path = Path(file_path)
        
        # Get the file name without extension
        module_name = file_path.stem
        
        # Get parent directories up to a package boundary (where an __init__.py exists)
        # This is a simplified approach and doesn't handle all package structures
        parts = []
        current_dir = file_path.parent
        
        # Traverse up the directory tree until we hit a non-package directory
        while current_dir.exists() and (current_dir / "__init__.py").exists():
            parts.insert(0, current_dir.name)
            current_dir = current_dir.parent
        
        # Combine parts to form module name
        if parts:
            parts.append(module_name)
            return ".".join(parts)
        
        return module_name

class TestSymbolExtractor(SymbolExtractor):
    """Specialized symbol extractor for test files."""
    
    def extract_test_symbols(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract test-specific symbols from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dict: Test symbol information
        """
        self.logger.debug(f"Extracting test symbols from {file_path}")
        
        try:
            # Parse the file
            tree = self.parser.parse_file(file_path)
            
            # Detect framework
            framework = detect_framework(self.parser, file_path)
            
            # Extract tests
            test_visitor = TestVisitor(file_path=str(file_path), framework=framework)
            test_visitor.visit(tree)
            
            # Extract functions for call graph
            function_visitor = FunctionVisitor(file_path=str(file_path))
            function_visitor.visit(tree)
            
            # Combine test symbols
            symbols = {
                "file_path": str(file_path),
                "test_framework": framework,
                "test_functions": test_visitor.test_functions,
                "test_classes": test_visitor.test_classes,
                "fixtures": test_visitor.fixtures,
                "module_markers": test_visitor.module_markers,
                "imports": list(test_visitor.imports),
                "call_graph": function_visitor.call_graph,
                "dependencies": list(test_visitor.dependencies)
            }
            
            return symbols
            
        except ParsingError as e:
            error_msg = f"Failed to parse test file: {e}"
            self.logger.error(error_msg)
            raise SymbolExtractionError(error_msg, details={"file": str(file_path)})
        except Exception as e:
            error_msg = f"Test symbol extraction failed: {e}"
            self.logger.error(error_msg)
            raise SymbolExtractionError(error_msg, details={"file": str(file_path)})
    
    def extract_test_symbols_from_directory(self, dir_path: Union[str, Path],
                                           recursive: bool = True,
                                           ignore_errors: bool = False) -> Dict[str, Dict[str, Any]]:
        """Extract test symbols from Python files in a directory.
        
        Args:
            dir_path: Directory path to process
            recursive: Whether to process subdirectories
            ignore_errors: Whether to ignore errors during extraction
            
        Returns:
            Dict: Mapping of file paths to test symbol information
        """
        dir_path = Path(dir_path)
        self.logger.info(f"Extracting test symbols from directory: {dir_path}")
        
        result: Dict[str, Dict[str, Any]] = {}
        
        try:
            # Get test files (using naming conventions)
            test_files = self._get_test_files(dir_path, recursive)
            
            for file_path in test_files:
                try:
                    symbols = self.extract_test_symbols(file_path)
                    result[str(file_path)] = symbols
                except (SymbolExtractionError, ParsingError) as e:
                    if not ignore_errors:
                        raise
                    self.logger.warning(f"Ignoring error in {file_path}: {e}")
            
            self.logger.info(f"Extracted test symbols from {len(result)} test files in {dir_path}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to extract test symbols from directory {dir_path}: {e}"
            self.logger.error(error_msg)
            raise ExtractionError(error_msg, details={"directory": str(dir_path)})
    
    def _get_test_files(self, dir_path: Path, recursive: bool = True) -> List[Path]:
        """Get all Python test files in a directory.
        
        Args:
            dir_path: Directory path
            recursive: Whether to include subdirectories
            
        Returns:
            List[Path]: List of test file paths
        """
        files = []
        
        if recursive:
            # Walk through all subdirectories
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    # Common test file patterns
                    if (filename.endswith('.py') and 
                        (filename.startswith('test_') or 
                         filename.endswith('_test.py') or
                         filename.startswith('test') or
                         'test' in filename.lower())):
                        files.append(Path(root) / filename)
        else:
            # Only get files in the current directory
            for item in dir_path.iterdir():
                if (item.is_file() and item.name.endswith('.py') and
                    (item.name.startswith('test_') or 
                     item.name.endswith('_test.py') or
                     item.name.startswith('test') or
                     'test' in item.name.lower())):
                    files.append(item)
        
        return files 