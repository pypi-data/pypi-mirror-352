"""
Unit tests for the SymbolExtractor class.
"""
import ast
import unittest
from unittest.mock import patch, MagicMock
import pytest

from testindex.core.config import ConfigModel
from testindex.core.exceptions import AstonError
from testindex.preprocessing.parsing.ast_parser import ASTParser
from testindex.preprocessing.parsing.symbol_extractor import SymbolExtractor, TestSymbolExtractor, ExtractionError, SymbolExtractionError


class SymbolExtractorTests(unittest.TestCase):
    """Test the SymbolExtractor class functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.config = ConfigModel()
        self.parser = MagicMock(spec=ASTParser)
        self.extractor = SymbolExtractor(self.config, self.parser)
    
    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(self.extractor.config, self.config)
        self.assertEqual(self.extractor.parser, self.parser)
    
    @patch('testindex.preprocessing.parsing.symbol_extractor.detect_framework')
    @patch('testindex.preprocessing.parsing.symbol_extractor.FunctionVisitor')
    @patch('testindex.preprocessing.parsing.symbol_extractor.ClassVisitor')
    @patch('testindex.preprocessing.parsing.symbol_extractor.TestVisitor')
    def test_extract_symbols_from_file(self, MockTestVisitor, MockClassVisitor, MockFuncVisitor, mock_detect):
        """Test extracting symbols from a file."""
        # Mock the dependencies
        mock_detect.return_value = "pytest"
        
        # Mock the visitors
        mock_func_visitor = MagicMock()
        mock_func_visitor.functions = []
        mock_func_visitor.imports = {}
        mock_func_visitor.call_graph = {}
        
        mock_class_visitor = MagicMock()
        mock_class_visitor.classes = []
        mock_class_visitor.methods = {}
        mock_class_visitor.inheritance_graph = {}
        
        mock_test_visitor = MagicMock()
        mock_test_visitor.test_functions = []
        mock_test_visitor.test_classes = []
        mock_test_visitor.fixtures = []
        mock_test_visitor.module_markers = []
        mock_test_visitor.dependencies = set()
        
        MockFuncVisitor.return_value = mock_func_visitor
        MockClassVisitor.return_value = mock_class_visitor
        MockTestVisitor.return_value = mock_test_visitor
        
        # Mock the AST
        mock_ast = MagicMock()
        self.parser.parse_file.return_value = mock_ast
        
        # Test the method
        result = self.extractor.extract_symbols_from_file("test_file.py")
        
        # Verify the calls
        self.parser.parse_file.assert_called_once_with("test_file.py")
        mock_detect.assert_called_once()
        MockFuncVisitor.assert_called_once()
        MockClassVisitor.assert_called_once()
        MockTestVisitor.assert_called_once()
        
        # Verify the result structure
        self.assertIn("file_path", result)
        self.assertIn("module_name", result)
        self.assertIn("test_framework", result)
        self.assertIn("functions", result)
        self.assertIn("classes", result)
        self.assertIn("methods", result)
        self.assertIn("test_functions", result)
        self.assertIn("test_classes", result)
        self.assertIn("fixtures", result)
        self.assertEqual(result["test_framework"], "pytest")


class TestExtractorForTests(unittest.TestCase):
    """Test the TestSymbolExtractor class functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.config = ConfigModel()
        self.parser = MagicMock(spec=ASTParser)
        self.extractor = TestSymbolExtractor(self.config, self.parser)
    
    def test_initialization(self):
        """Test extractor initialization."""
        self.assertEqual(self.extractor.config, self.config)
        self.assertEqual(self.extractor.parser, self.parser)
        
    @patch('testindex.preprocessing.parsing.symbol_extractor.detect_framework')
    @patch('testindex.preprocessing.parsing.symbol_extractor.FunctionVisitor')
    @patch('testindex.preprocessing.parsing.symbol_extractor.TestVisitor')
    def test_extract_test_symbols(self, MockTestVisitor, MockFuncVisitor, mock_detect):
        """Test extracting test symbols from a file."""
        # Mock the dependencies
        mock_detect.return_value = "unittest"
        
        # Mock the visitors
        mock_func_visitor = MagicMock()
        mock_func_visitor.call_graph = {}
        
        mock_test_visitor = MagicMock()
        mock_test_visitor.test_functions = []
        mock_test_visitor.test_classes = []
        mock_test_visitor.fixtures = []
        mock_test_visitor.module_markers = []
        mock_test_visitor.imports = set()
        mock_test_visitor.dependencies = set()
        
        MockFuncVisitor.return_value = mock_func_visitor
        MockTestVisitor.return_value = mock_test_visitor
        
        # Mock the AST
        mock_ast = MagicMock()
        self.parser.parse_file.return_value = mock_ast
        
        # Test the method
        result = self.extractor.extract_test_symbols("test_unittest.py")
        
        # Verify the calls
        self.parser.parse_file.assert_called_once_with("test_unittest.py")
        mock_detect.assert_called_once()
        MockFuncVisitor.assert_called_once()
        MockTestVisitor.assert_called_once()
        
        # Verify the result structure
        self.assertIn("file_path", result)
        self.assertIn("test_framework", result)
        self.assertIn("test_functions", result)
        self.assertIn("test_classes", result)
        self.assertIn("fixtures", result)
        self.assertIn("call_graph", result)
        self.assertEqual(result["test_framework"], "unittest")


if __name__ == "__main__":
    unittest.main() 