#!/usr/bin/env python
"""
Example script demonstrating the StaticAnalyzer for analyzing Python code
and building a knowledge graph based on the static analysis results.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample code to analyze
SAMPLE_CODE_DIR = Path("./sample_code")

def create_sample_code():
    """Create sample Python files for static analysis"""
    # Create directory if it doesn't exist
    os.makedirs(SAMPLE_CODE_DIR, exist_ok=True)
    
    # Create a simple module
    with open(SAMPLE_CODE_DIR / "utils.py", "w") as f:
        f.write('''
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def calculate_product(a, b):
    """Calculate the product of two numbers."""
    return a * b
''')
    
    # Create a module that imports the utils module
    with open(SAMPLE_CODE_DIR / "calculator.py", "w") as f:
        f.write('''
from utils import calculate_sum, calculate_product

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        """Initialize the calculator."""
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = calculate_sum(a, b)
        self.history.append(f"Added {a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        result = calculate_product(a, b)
        self.history.append(f"Multiplied {a} * {b} = {result}")
        return result
    
    def get_history(self):
        """Get calculation history."""
        return self.history
''')
    
    # Create a test module
    with open(SAMPLE_CODE_DIR / "test_calculator.py", "w") as f:
        f.write('''
import unittest
from calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()
    
    def test_add(self):
        """Test the add method."""
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
    
    def test_multiply(self):
        """Test the multiply method."""
        self.assertEqual(self.calc.multiply(2, 3), 6)
        self.assertEqual(self.calc.multiply(-1, 1), -1)
    
    def test_history(self):
        """Test the history functionality."""
        self.calc.add(2, 3)
        self.calc.multiply(4, 5)
        history = self.calc.get_history()
        self.assertEqual(len(history), 2)

if __name__ == "__main__":
    unittest.main()
''')
    
    logger.info(f"Created sample code in {SAMPLE_CODE_DIR}")

# Mock classes for demonstration without Neo4j
class MockNeo4jClient:
    """Mock Neo4j client for demonstration purposes."""
    
    def __init__(self, config=None):
        """Initialize the mock client."""
        self.nodes = {}
        self.relationships = {}
        self.query_results = {
            "MATCH (m:Module) RETURN m.name as name, m.file_path as file_path": [
                {"name": "utils", "file_path": "sample_code/utils.py"},
                {"name": "calculator", "file_path": "sample_code/calculator.py"},
                {"name": "test_calculator", "file_path": "sample_code/test_calculator.py"}
            ],
            "MATCH (i:Implementation) RETURN i.name as name, i.file_path as file_path, i.line_number as line": [
                {"name": "calculate_sum", "file_path": "sample_code/utils.py", "line": 2},
                {"name": "calculate_product", "file_path": "sample_code/utils.py", "line": 6},
                {"name": "Calculator", "file_path": "sample_code/calculator.py", "line": 4},
                {"name": "add", "file_path": "sample_code/calculator.py", "line": 12},
                {"name": "multiply", "file_path": "sample_code/calculator.py", "line": 18},
                {"name": "get_history", "file_path": "sample_code/calculator.py", "line": 24}
            ],
            "MATCH (t:Test) RETURN t.name as name, t.file_path as file_path, t.line_number as line": [
                {"name": "test_add", "file_path": "sample_code/test_calculator.py", "line": 8},
                {"name": "test_multiply", "file_path": "sample_code/test_calculator.py", "line": 13},
                {"name": "test_history", "file_path": "sample_code/test_calculator.py", "line": 18}
            ],
            """
            MATCH (a)-[r]->(b)
            RETURN type(r) as type, a.name as source, b.name as target, count(r) as count
            ORDER BY type, source, target
            """: [
                {"type": "CALLS", "source": "add", "target": "calculate_sum", "count": 1},
                {"type": "CALLS", "source": "multiply", "target": "calculate_product", "count": 1},
                {"type": "IMPORTS", "source": "calculator", "target": "utils", "count": 1},
                {"type": "IMPORTS", "source": "test_calculator", "target": "calculator", "count": 1},
                {"type": "TESTS", "source": "test_add", "target": "add", "count": 1},
                {"type": "TESTS", "source": "test_multiply", "target": "multiply", "count": 1},
                {"type": "TESTS", "source": "test_history", "target": "get_history", "count": 1}
            ]
        }
    
    def create_node(self, node):
        """Mock creating a node."""
        self.nodes[node.id] = node
        return node.id
    
    def create_relationship(self, relationship):
        """Mock creating a relationship."""
        self.relationships[relationship.id] = relationship
        return relationship.id
    
    def execute_query(self, query, parameters=None):
        """Mock executing a query."""
        # Simple query matching for demonstration
        for q, results in self.query_results.items():
            if query.strip().replace("\n", " ") in q.strip().replace("\n", " "):
                return MockResult(results)
        return MockResult([])


class MockResult:
    """Mock result from a Neo4j query."""
    
    def __init__(self, records):
        """Initialize with records."""
        self.records = records
        self.current = 0
    
    def single(self):
        """Get the first record."""
        return self.records[0] if self.records else None
    
    def __iter__(self):
        """Iterator for records."""
        self.current = 0
        return self
    
    def __next__(self):
        """Get the next record."""
        if self.current < len(self.records):
            record = self.records[self.current]
            self.current += 1
            return record
        raise StopIteration


class MockRelationBuilder:
    """Mock relation builder."""
    
    def __init__(self, client):
        """Initialize with client."""
        self.client = client
    
    def create_test_relationship(self, test_node, impl_node, **kwargs):
        """Mock creating a test relationship."""
        return "test_relationship_id"
    
    def create_imports_relationship(self, source_module, target_module, **kwargs):
        """Mock creating an import relationship."""
        return "import_relationship_id"


class MockStaticAnalyzer:
    """Mock static analyzer for demonstration."""
    
    def __init__(self, client, relation_builder):
        """Initialize with client and relation builder."""
        self.client = client
        self.relation_builder = relation_builder
    
    def analyze_file(self, file_path, is_test_file=False):
        """Mock analyzing a file."""
        logger.info(f"Analyzing file: {file_path}")
        
        # Convert Path object to string if necessary
        file_path_str = str(file_path)
        
        if "utils.py" in file_path_str:
            return {
                "file_path": file_path_str,
                "is_test_file": False,
                "functions": [
                    {"name": "calculate_sum", "line_number": 2, "docstring": "Calculate the sum of two numbers."},
                    {"name": "calculate_product", "line_number": 6, "docstring": "Calculate the product of two numbers."}
                ],
                "classes": [],
                "imports": [],
                "test_classes": []  # Empty for non-test files
            }
        elif "calculator.py" in file_path_str and "test_" not in file_path_str:
            return {
                "file_path": file_path_str,
                "is_test_file": False,
                "functions": [],
                "classes": [
                    {
                        "name": "Calculator",
                        "line_number": 4,
                        "docstring": "A simple calculator class.",
                        "methods": [
                            {"name": "__init__", "line_number": 7, "docstring": "Initialize the calculator."},
                            {"name": "add", "line_number": 12, "docstring": "Add two numbers."},
                            {"name": "multiply", "line_number": 18, "docstring": "Multiply two numbers."},
                            {"name": "get_history", "line_number": 24, "docstring": "Get calculation history."}
                        ]
                    }
                ],
                "imports": [
                    {"from_module": "utils", "name": "calculate_sum"},
                    {"from_module": "utils", "name": "calculate_product"}
                ],
                "test_classes": []  # Empty for non-test files
            }
        elif "test_calculator.py" in file_path_str:
            test_classes = [
                {
                    "name": "TestCalculator",
                    "line_number": 4,
                    "file_path": file_path_str,
                    "test_methods": [
                        {"name": "setUp", "line_number": 5},
                        {"name": "test_add", "line_number": 8, "docstring": "Test the add method."},
                        {"name": "test_multiply", "line_number": 13, "docstring": "Test the multiply method."},
                        {"name": "test_history", "line_number": 18, "docstring": "Test the history functionality."}
                    ]
                }
            ]
            return {
                "file_path": file_path_str,
                "is_test_file": True,
                "functions": [],
                "classes": [],
                "imports": [
                    {"name": "unittest"},
                    {"from_module": "calculator", "name": "Calculator"}
                ],
                "test_classes": test_classes
            }
        return {
            "file_path": file_path_str,
            "is_test_file": is_test_file,
            "functions": [],
            "classes": [],
            "imports": [],
            "test_classes": []
        }
    
    def process_directory(self, directory_path):
        """Mock processing a directory."""
        logger.info(f"Processing directory: {directory_path}")
        return {
            "directory_path": directory_path,
            "files_analyzed": 3,
            "test_files": 1,
            "implementation_files": 2,
            "nodes_created": 12,
            "relationships_created": 7
        }


def main():
    """Main function demonstrating static analyzer operations"""
    # Create sample code for analysis
    create_sample_code()
    
    # Create mock client and analyzer instead of using actual Neo4j
    client = MockNeo4jClient()
    relation_builder = MockRelationBuilder(client)
    static_analyzer = MockStaticAnalyzer(client, relation_builder)
    
    # Example 1: Analyze a single Python file
    logger.info("Analyzing utils.py...")
    utils_file_path = SAMPLE_CODE_DIR / "utils.py"
    utils_analysis = static_analyzer.analyze_file(str(utils_file_path))
    
    logger.info(f"Analysis results for {utils_file_path}:")
    logger.info(f"  Functions detected: {len(utils_analysis.get('functions', []))}")
    for func in utils_analysis.get("functions", []):
        logger.info(f"    - {func['name']} at line {func['line_number']}")
    
    # Example 2: Analyze a file with class definitions
    logger.info("Analyzing calculator.py...")
    calculator_file_path = SAMPLE_CODE_DIR / "calculator.py"
    calculator_analysis = static_analyzer.analyze_file(str(calculator_file_path))
    
    logger.info(f"Analysis results for {calculator_file_path}:")
    logger.info(f"  Classes detected: {len(calculator_analysis.get('classes', []))}")
    for cls in calculator_analysis.get("classes", []):
        logger.info(f"    - Class: {cls['name']} at line {cls['line_number']}")
        for method in cls.get("methods", []):
            logger.info(f"      Method: {method['name']} at line {method['line_number']}")
    
    logger.info(f"  Imports detected: {len(calculator_analysis.get('imports', []))}")
    for imp in calculator_analysis.get("imports", []):
        logger.info(f"    - From: {imp.get('from_module', 'N/A')} Import: {imp.get('name', 'N/A')}")
    
    # Example 3: Analyze a test file
    logger.info("Analyzing test_calculator.py...")
    test_file_path = SAMPLE_CODE_DIR / "test_calculator.py"
    test_analysis = static_analyzer.analyze_file(str(test_file_path), is_test_file=True)
    
    logger.info(f"Analysis results for {test_file_path}:")
    logger.info(f"  Test classes detected: {len(test_analysis.get('test_classes', []))}")
    for test_cls in test_analysis.get("test_classes", []):
        logger.info(f"    - Test class: {test_cls['name']} at line {test_cls['line_number']}")
        for test_method in test_cls.get("test_methods", []):
            logger.info(f"      Test method: {test_method['name']} at line {test_method['line_number']}")
    
    # Example 4: Process a directory and build knowledge graph
    logger.info("Processing entire sample code directory...")
    results = static_analyzer.process_directory(str(SAMPLE_CODE_DIR))
    logger.info(f"Processing results:")
    logger.info(f"  Files analyzed: {results['files_analyzed']}")
    logger.info(f"  Test files: {results['test_files']}")
    logger.info(f"  Implementation files: {results['implementation_files']}")
    logger.info(f"  Nodes created: {results['nodes_created']}")
    logger.info(f"  Relationships created: {results['relationships_created']}")
    
    # Example 5: Query the knowledge graph to get insights
    logger.info("Querying the knowledge graph for insights...")
    
    # Get all module nodes
    modules = client.execute_query(
        "MATCH (m:Module) RETURN m.name as name, m.file_path as file_path"
    )
    logger.info("Modules in the knowledge graph:")
    for module in modules:
        logger.info(f"  - {module['name']} ({module['file_path']})")
    
    # Get all implementation nodes
    implementations = client.execute_query(
        "MATCH (i:Implementation) RETURN i.name as name, i.file_path as file_path, i.line_number as line"
    )
    logger.info("Implementation nodes in the knowledge graph:")
    for impl in implementations:
        logger.info(f"  - {impl['name']} in {impl['file_path']} at line {impl['line']}")
    
    # Get all test nodes
    tests = client.execute_query(
        "MATCH (t:Test) RETURN t.name as name, t.file_path as file_path, t.line_number as line"
    )
    logger.info("Test nodes in the knowledge graph:")
    for test in tests:
        logger.info(f"  - {test['name']} in {test['file_path']} at line {test['line']}")
    
    # Get all relationships
    relationships = client.execute_query(
        """
        MATCH (a)-[r]->(b)
        RETURN type(r) as type, a.name as source, b.name as target, count(r) as count
        ORDER BY type, source, target
        """
    )
    
    logger.info("Relationships in the knowledge graph:")
    for rel in relationships:
        logger.info(f"  - {rel['source']} -{rel['type']}-> {rel['target']}")
    
    logger.info("Example completed successfully!")

if __name__ == "__main__":
    main() 