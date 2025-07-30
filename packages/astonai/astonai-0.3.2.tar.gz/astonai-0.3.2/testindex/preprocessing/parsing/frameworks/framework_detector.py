"""
Test framework detection utilities.
"""
import ast
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from testindex.core.logging import get_logger

# Import here to avoid circular imports
from testindex.preprocessing.parsing.frameworks.pytest import PyTestDetector
from testindex.preprocessing.parsing.frameworks.unittest import UnittestDetector

# Initialize logger
logger = get_logger("framework-detector")

class ImportVisitor(ast.NodeVisitor):
    """AST visitor to find import statements."""
    
    def __init__(self):
        self.imports: Set[str] = set()
        self.from_imports: Dict[str, List[str]] = {}
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit an import statement and record imported modules."""
        for name in node.names:
            self.imports.add(name.name)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit an import from statement and record imported modules and names."""
        if node.module:
            module = node.module
            if module not in self.from_imports:
                self.from_imports[module] = []
            
            for name in node.names:
                if name.name != '*':
                    self.from_imports[module].append(name.name)

def detect_framework(parser, file_path: Union[str, Path]) -> str:
    """Detect testing framework used in a Python file.
    
    Args:
        parser: The AST parser instance
        file_path: Path to the Python file
        
    Returns:
        str: Detected framework name or "unknown"
    """
    try:
        # Parse the file
        tree = parser.parse_file(file_path)
        
        # Detect framework based on imports and patterns
        detector_classes = [
            PyTestDetector,
            UnittestDetector
        ]
        
        for detector_class in detector_classes:
            detector = detector_class()
            if detector.detect(tree, file_path):
                return detector.framework_name
        
        # If no framework is detected, check for imports
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        # Check imports for common testing frameworks
        if "pytest" in visitor.imports:
            return "pytest"
        if "unittest" in visitor.imports:
            return "unittest"
        if "nose" in visitor.imports:
            return "nose"
        
        # Check from imports
        for module, names in visitor.from_imports.items():
            if module == "pytest":
                return "pytest"
            if module == "unittest":
                return "unittest"
            if module.startswith("unittest."):
                return "unittest"
            if module == "nose" or module.startswith("nose."):
                return "nose"
        
        # Default to unknown
        return "unknown"
        
    except Exception as e:
        logger.error(f"Framework detection failed for {file_path}: {e}")
        return "unknown"

class FrameworkDetector:
    """Base class for framework-specific detectors."""
    
    def __init__(self):
        """Initialize the detector."""
        self.framework_name: str = "unknown"
    
    def detect(self, tree: ast.AST, file_path: Optional[Union[str, Path]] = None) -> bool:
        """Detect if this file uses the framework.
        
        Args:
            tree: The AST to analyze
            file_path: Optional path to the file (for context)
            
        Returns:
            bool: True if framework is detected, False otherwise
        """
        raise NotImplementedError("Subclasses must implement detect method") 