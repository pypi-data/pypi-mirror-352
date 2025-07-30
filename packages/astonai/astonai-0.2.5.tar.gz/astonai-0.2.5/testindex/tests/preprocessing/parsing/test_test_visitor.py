"""
Unit tests for the TestVisitor class.
"""
import ast
import unittest
from unittest.mock import patch, MagicMock

from testindex.preprocessing.parsing.visitors.test_visitor import TestVisitor


class TestTestVisitor(unittest.TestCase):
    """Test the TestVisitor class functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.visitor = TestVisitor(file_path="test_file.py", framework="pytest")
    
    def test_initialization(self):
        """Test visitor initialization."""
        self.assertEqual(self.visitor.file_path, "test_file.py")
        self.assertEqual(self.visitor.framework, "pytest")
        self.assertEqual(len(self.visitor.test_functions), 0)
        self.assertEqual(len(self.visitor.test_classes), 0)
        self.assertEqual(len(self.visitor.fixtures), 0)
    
    def test_process_pytest_function(self):
        """Test processing a pytest test function."""
        # Create a simple test function AST node
        code = """
def test_example():
    assert True
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        # Process the function
        self.visitor._process_pytest_function(func_node)
        
        # Verify it was added as a test function
        self.assertEqual(len(self.visitor.test_functions), 1)
        test_func = self.visitor.test_functions[0]
        self.assertEqual(test_func["name"], "test_example")
        self.assertEqual(test_func["framework"], "pytest")
    
    def test_fixture_detection(self):
        """Test detection of pytest fixtures."""
        # Create a fixture function AST node
        code = """
@pytest.fixture
def my_fixture():
    return 42
"""
        tree = ast.parse(code)
        decorator = tree.body[0].decorator_list[0]
        decorator.func = ast.Name(id='fixture', ctx=ast.Load())
        
        # Process the function
        self.visitor._process_pytest_function(tree.body[0])
        
        # Verify it was added as a fixture
        self.assertEqual(len(self.visitor.fixtures), 1)
        fixture = self.visitor.fixtures[0]
        self.assertEqual(fixture["name"], "my_fixture")


if __name__ == "__main__":
    unittest.main() 