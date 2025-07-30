#!/usr/bin/env python3
"""
Example script demonstrating how to query the knowledge graph.

This example shows various ways to extract insights from a knowledge graph
that has been built using the StaticAnalyzer.
"""

import logging
import os
from pathlib import Path

from testindex.knowledge.graph import GraphDatabase
from testindex.knowledge.graph.static_analyzer import StaticAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_code():
    """Create sample Python files for demonstration."""
    sample_dir = Path("./sample_project")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a simple module with utility functions
    with open(sample_dir / "utils.py", "w") as f:
        f.write("""
def format_string(text):
    return text.strip().lower()

def validate_input(value, min_val=0, max_val=100):
    return min_val <= value <= max_val
""")
    
    # Create a calculator module that imports utils
    with open(sample_dir / "calculator.py", "w") as f:
        f.write("""
from sample_project.utils import validate_input

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        if validate_input(a) and validate_input(b):
            self.result = a + b
            return self.result
        raise ValueError("Invalid input")
    
    def subtract(self, a, b):
        if validate_input(a) and validate_input(b):
            self.result = a - b
            return self.result
        raise ValueError("Invalid input")
    
    def multiply(self, a, b):
        self.result = a * b
        return self.result
    
    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        self.result = a / b
        return self.result
""")
    
    # Create test file for calculator
    with open(sample_dir / "test_calculator.py", "w") as f:
        f.write("""
import pytest
from sample_project.calculator import Calculator

class TestCalculator:
    def setup_method(self):
        self.calc = Calculator()
    
    def test_add(self):
        assert self.calc.add(2, 3) == 5
    
    def test_subtract(self):
        assert self.calc.subtract(5, 3) == 2
    
    def test_multiply(self):
        assert self.calc.multiply(2, 3) == 6
    
    def test_divide(self):
        assert self.calc.divide(6, 3) == 2
    
    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            self.calc.divide(6, 0)
    
    def test_invalid_input(self):
        with pytest.raises(ValueError):
            self.calc.add(101, 50)
""")
    
    return sample_dir

def main():
    """
    Main function to demonstrate querying the knowledge graph.
    """
    # Create sample code files
    sample_dir = create_sample_code()
    logger.info(f"Created sample code in {sample_dir}")
    
    # Initialize the graph database (in-memory for demo)
    graph_db = GraphDatabase(
        uri="bolt://localhost:7687", 
        username="neo4j",
        password="password"
    )
    
    # Create a static analyzer and analyze the files
    analyzer = StaticAnalyzer(graph_db)
    analyzer.analyze_directory(str(sample_dir))
    logger.info("Built knowledge graph from sample project")
    
    # Get the query engine
    query_engine = graph_db.get_query_engine()
    
    # Demonstrate different types of queries
    
    # 1. Find all modules in the project
    modules = query_engine.find_modules()
    logger.info(f"Found {len(modules)} modules in the project:")
    for module in modules:
        logger.info(f"  - {module['name']}")
    
    # 2. Find classes in the project
    classes = query_engine.find_classes()
    logger.info(f"\nFound {len(classes)} classes in the project:")
    for cls in classes:
        logger.info(f"  - {cls['name']} in {cls['module']}")
        
        # Find methods in this class
        methods = query_engine.find_methods_in_class(cls['name'])
        logger.info(f"    Methods:")
        for method in methods:
            logger.info(f"    - {method['name']}")
    
    # 3. Find all test classes and what they test
    test_classes = query_engine.find_test_classes()
    logger.info(f"\nFound {len(test_classes)} test classes:")
    for test_class in test_classes:
        logger.info(f"  - {test_class['name']} tests {test_class.get('tests_implementation', 'N/A')}")
        
        # Find test methods in this class
        test_methods = query_engine.find_test_methods_in_class(test_class['name'])
        logger.info(f"    Test methods:")
        for test_method in test_methods:
            logger.info(f"    - {test_method['name']} tests {test_method.get('tests_implementation', 'N/A')}")
    
    # 4. Find all functions that call validate_input
    validate_callers = query_engine.find_callers("validate_input")
    logger.info(f"\nFunctions that call validate_input:")
    for caller in validate_callers:
        logger.info(f"  - {caller['name']} in {caller.get('class_name', 'N/A')}")
    
    # 5. Find all imports
    imports = query_engine.find_import_relationships()
    logger.info(f"\nImport relationships:")
    for imp in imports:
        logger.info(f"  - {imp['source']} imports {imp['target']}")
    
    # 6. Find all error handling patterns
    error_handlers = query_engine.find_error_handlers()
    logger.info(f"\nError handling patterns:")
    for handler in error_handlers:
        logger.info(f"  - {handler['name']} handles {handler['exception_type']}")
    
    # 7. Find test coverage for Calculator.add
    coverage = query_engine.find_tests_for_implementation("Calculator.add")
    logger.info(f"\nTest coverage for Calculator.add:")
    for test in coverage:
        logger.info(f"  - {test['name']} in {test.get('class_name', 'N/A')}")
    
    # 8. Find implementation dependencies for Calculator.add
    dependencies = query_engine.find_implementation_dependencies("Calculator.add")
    logger.info(f"\nDependencies for Calculator.add:")
    for dep in dependencies:
        logger.info(f"  - {dep['name']} in {dep.get('module', 'N/A')}")
    
    # Clean up sample directory
    # Uncomment to remove sample code after running
    # import shutil
    # shutil.rmtree(sample_dir)

if __name__ == "__main__":
    main() 