"""
Static code analyzer for the Knowledge Graph.

This module provides utilities for analyzing Python code and extracting
information about classes, functions, imports, and tests to build a knowledge graph.
"""

import os
import ast
import glob
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

from testindex.core.exceptions import AstonError
from testindex.core.logging import get_logger
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.knowledge.graph.relation_builder import RelationBuilder
from testindex.knowledge.schema.nodes import (
    NodeSchema,
    ImplementationNode,
    ModuleNode,
    FixtureNode,
)

logger = get_logger(__name__)

class StaticAnalysisError(AstonError):
    """Custom exception for errors during static analysis in this module."""
    error_code = "STATIC_ANLYS_001"
    default_message = "An error occurred during static analysis."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None, parser: Optional[str] = None):
        final_message = message or self.default_message
        current_context = context or {}
        if file_path:
            current_context['file_path'] = file_path
        if parser:
            current_context['parser'] = parser

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=current_context
        )
        self.file_path = file_path
        self.parser = parser

class StaticAnalyzer:
    """Static code analyzer for Python files.
    
    This class analyzes Python code to extract information about functions,
    classes, imports, and tests, and builds a knowledge graph based on the
    analysis results.
    """
    
    def __init__(self, client: Neo4jClient, relation_builder: RelationBuilder):
        """Initialize the static analyzer.
        
        Args:
            client: Neo4j client for database operations
            relation_builder: Relation builder for creating relationships
        """
        self.client = client
        self.relation_builder = relation_builder
    
    def analyze_file(self, file_path: str, is_test_file: bool = False) -> Dict[str, Any]:
        """Analyze a Python file and extract code information.
        
        Args:
            file_path: Path to the Python file
            is_test_file: Whether the file is a test file
            
        Returns:
            Dict[str, Any]: Analysis results containing functions, classes, imports, etc.
        """
        try:
            logger.info(f"Analyzing file: {file_path}")
            
            # Read the file
            with open(file_path, "r") as f:
                code = f.read()
            
            # Parse the AST
            tree = ast.parse(code)
            
            # Extract information from the AST
            functions = self._extract_functions(tree, file_path)
            classes = self._extract_classes(tree, file_path)
            imports = self._extract_imports(tree)
            
            # Extract test-specific information if it's a test file
            test_classes = []
            if is_test_file:
                test_classes = self._extract_test_classes(tree, file_path)
            
            # Build the result dictionary
            result = {
                "file_path": file_path,
                "is_test_file": is_test_file,
                "functions": functions,
                "classes": classes,
                "imports": imports,
            }
            
            if is_test_file:
                result["test_classes"] = test_classes
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            raise StaticAnalysisError(f"Failed to analyze file {file_path}: {str(e)}")
    
    def process_directory(self, directory_path: str, test_pattern: str = "test_*.py") -> Dict[str, Any]:
        """Process a directory of Python files and build a knowledge graph.
        
        Args:
            directory_path: Path to the directory
            test_pattern: Glob pattern for test files
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            logger.info(f"Processing directory: {directory_path}")
            
            # Get all Python files in the directory
            python_files = glob.glob(os.path.join(directory_path, "**", "*.py"), recursive=True)
            
            # Separate test files and implementation files
            test_files = [f for f in python_files if os.path.basename(f).startswith("test_")]
            impl_files = [f for f in python_files if not os.path.basename(f).startswith("test_")]
            
            # Process all files
            analysis_results = {}
            nodes_created = []
            
            # Process implementation files first
            for file_path in impl_files:
                logger.info(f"Processing implementation file: {file_path}")
                analysis = self.analyze_file(file_path, is_test_file=False)
                analysis_results[file_path] = analysis
                
                # Create module node
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                module_node = ModuleNode(
                    name=module_name,
                    file_path=file_path,
                    description=f"Module {module_name}"
                )
                self.client.create_node(module_node)
                nodes_created.append(module_node.id)
                
                # Create implementation nodes for functions and classes
                for func in analysis.get("functions", []):
                    impl_node = ImplementationNode(
                        name=func["name"],
                        file_path=file_path,
                        line_number=func["line_number"],
                        description=func.get("docstring", "")
                    )
                    self.client.create_node(impl_node)
                    nodes_created.append(impl_node.id)
                
                for cls in analysis.get("classes", []):
                    impl_node = ImplementationNode(
                        name=cls["name"],
                        file_path=file_path,
                        line_number=cls["line_number"],
                        description=cls.get("docstring", ""),
                        properties={"type": "class"}
                    )
                    self.client.create_node(impl_node)
                    nodes_created.append(impl_node.id)
            
            # Process test files
            for file_path in test_files:
                logger.info(f"Processing test file: {file_path}")
                analysis = self.analyze_file(file_path, is_test_file=True)
                analysis_results[file_path] = analysis
                
                # Create module node
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                module_node = ModuleNode(
                    name=module_name,
                    file_path=file_path,
                    description=f"Test module {module_name}",
                    properties={"is_test": True}
                )
                self.client.create_node(module_node)
                nodes_created.append(module_node.id)
                
                # Create test nodes for test classes and methods
                for test_cls in analysis.get("test_classes", []):
                    for test_method in test_cls.get("test_methods", []):
                        test_node = NodeSchema(
                            name=test_method["name"],
                            file_path=file_path,
                            line_number=test_method["line_number"],
                            description=test_method.get("docstring", ""),
                            properties={"class": test_cls["name"]}
                        )
                        self.client.create_node(test_node)
                        nodes_created.append(test_node.id)
            
            # Build relationships based on analysis results
            relationships_created = []
            
            # Create import relationships
            for file_path, analysis in analysis_results.items():
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                
                for imp in analysis.get("imports", []):
                    from_module = imp.get("from_module")
                    import_name = imp.get("name")
                    
                    # Find source module node
                    source_module_query = f"""
                    MATCH (m:Module {{name: "{module_name}"}})
                    RETURN m
                    """
                    source_result = self.client.execute_query(source_module_query)
                    source_record = source_result.single()
                    
                    if source_record:
                        source_module_id = source_record[0]["id"]
                        
                        # Find target module node
                        target_module_name = from_module or import_name
                        target_module_query = f"""
                        MATCH (m:Module {{name: "{target_module_name}"}})
                        RETURN m
                        """
                        target_result = self.client.execute_query(target_module_query)
                        target_record = target_result.single()
                        
                        if target_record:
                            target_module_id = target_record[0]["id"]
                            
                            # Create import relationship
                            rel_id = self.relation_builder.create_imports_relationship(
                                source_module=source_module_id,
                                target_module=target_module_id,
                                import_type="from_import" if from_module else "import",
                                imported_names=[import_name] if import_name != target_module_name else []
                            )
                            relationships_created.append(rel_id)
            
            # Create test relationships based on naming conventions
            for file_path, analysis in analysis_results.items():
                if analysis.get("is_test_file"):
                    for test_cls in analysis.get("test_classes", []):
                        for test_method in test_cls.get("test_methods", []):
                            test_name = test_method["name"]
                            
                            # Extract potential implementation name
                            if test_name.startswith("test_"):
                                impl_name = test_name[5:]  # Remove "test_"
                            else:
                                impl_name = test_name
                            
                            # Find test node
                            test_query = f"""
                            MATCH (t:NodeSchema {{name: "{test_name}"}})
                            RETURN t
                            """
                            test_result = self.client.execute_query(test_query)
                            test_record = test_result.single()
                            
                            if test_record:
                                test_id = test_record[0]["id"]
                                
                                # Find implementation node with similar name
                                impl_query = f"""
                                MATCH (i:Implementation)
                                WHERE i.name CONTAINS "{impl_name}" OR "{impl_name}" CONTAINS i.name
                                RETURN i
                                """
                                impl_result = self.client.execute_query(impl_query)
                                
                                # Create test relationship for each matching implementation
                                for impl_record in impl_result:
                                    impl_id = impl_record[0]["id"]
                                    
                                    # Calculate confidence based on name similarity
                                    impl_name_actual = impl_record[0]["name"]
                                    name_similarity = len(impl_name) / max(len(impl_name), len(impl_name_actual))
                                    
                                    # Create test relationship
                                    rel_id = self.relation_builder.create_test_relationship(
                                        test_node=test_id,
                                        impl_node=impl_id,
                                        confidence=name_similarity,
                                        detection_method="naming_convention"
                                    )
                                    relationships_created.append(rel_id)
            
            return {
                "directory_path": directory_path,
                "files_analyzed": len(python_files),
                "test_files": len(test_files),
                "implementation_files": len(impl_files),
                "nodes_created": len(nodes_created),
                "relationships_created": len(relationships_created)
            }
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            raise StaticAnalysisError(f"Failed to process directory {directory_path}: {str(e)}")
    
    def _extract_functions(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Extract functions from an AST.
        
        Args:
            tree: AST tree
            file_path: Path to the Python file
            
        Returns:
            List[Dict[str, Any]]: List of functions
        """
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if it's a method in a class
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.iter_child_nodes(tree)):
                    function = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "file_path": file_path,
                    }
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        function["docstring"] = docstring
                    
                    functions.append(function)
        
        return functions
    
    def _extract_classes(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Extract classes from an AST.
        
        Args:
            tree: AST tree
            file_path: Path to the Python file
            
        Returns:
            List[Dict[str, Any]]: List of classes
        """
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                cls = {
                    "name": node.name,
                    "line_number": node.lineno,
                    "file_path": file_path,
                    "methods": []
                }
                
                # Extract docstring
                docstring = ast.get_docstring(node)
                if docstring:
                    cls["docstring"] = docstring
                
                # Extract base classes
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                if bases:
                    cls["bases"] = bases
                
                # Extract methods
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        method = {
                            "name": child.name,
                            "line_number": child.lineno,
                        }
                        
                        # Extract docstring
                        method_docstring = ast.get_docstring(child)
                        if method_docstring:
                            method["docstring"] = method_docstring
                        
                        cls["methods"].append(method)
                
                classes.append(cls)
        
        return classes
    
    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract imports from an AST.
        
        Args:
            tree: AST tree
            
        Returns:
            List[Dict[str, Any]]: List of imports
        """
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        "name": name.name,
                        "asname": name.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    imports.append({
                        "from_module": module,
                        "name": name.name,
                        "asname": name.asname
                    })
        
        return imports
    
    def _extract_test_classes(self, tree: ast.AST, file_path: str) -> List[Dict[str, Any]]:
        """Extract test classes from an AST.
        
        Args:
            tree: AST tree
            file_path: Path to the Python file
            
        Returns:
            List[Dict[str, Any]]: List of test classes
        """
        test_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a test class
                is_test_class = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and "Test" in base.id:
                        is_test_class = True
                        break
                
                if is_test_class or node.name.startswith("Test"):
                    test_class = {
                        "name": node.name,
                        "line_number": node.lineno,
                        "file_path": file_path,
                        "test_methods": []
                    }
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node)
                    if docstring:
                        test_class["docstring"] = docstring
                    
                    # Extract test methods
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef) and (child.name.startswith("test_") or "test" in child.name.lower()):
                            test_method = {
                                "name": child.name,
                                "line_number": child.lineno,
                            }
                            
                            # Extract docstring
                            method_docstring = ast.get_docstring(child)
                            if method_docstring:
                                test_method["docstring"] = method_docstring
                            
                            test_class["test_methods"].append(test_method)
                    
                    test_classes.append(test_class)
        
        return test_classes 