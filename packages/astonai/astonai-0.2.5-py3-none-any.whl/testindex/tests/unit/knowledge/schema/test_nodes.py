"""
Unit tests for the concrete node schema classes.

Tests the functionality of TestNode, ImplementationNode, ModuleNode,
and FixtureNode classes.
"""

import unittest
from datetime import datetime

from testindex.core.exceptions import ValidationError
from testindex.knowledge.schema.nodes import (
    TestNode,
    ImplementationNode,
    ModuleNode,
    FixtureNode,
)


class TestTestNode(unittest.TestCase):
    """Test the TestNode class."""
    
    def test_creation_with_valid_properties(self):
        """Test creating a TestNode with valid properties."""
        node = TestNode(
            labels=["Test", "Function"],
            properties={
                "name": "test_login",
                "file_path": "/path/to/test_auth.py",
                "function_name": "test_login",
                "module_name": "test_auth",
                "class_name": "TestAuthentication",
                "test_framework": "pytest",
                "docstring": "Test login functionality",
                "last_result": "pass",
                "last_execution_time": 0.25,
                "parameters": ["username", "password"],
                "tags": ["auth", "login"],
            }
        )
        
        # Check that properties are correctly set
        self.assertEqual(node.properties["name"], "test_login")
        self.assertEqual(node.properties["file_path"], "/path/to/test_auth.py")
        self.assertEqual(node.properties["function_name"], "test_login")
        self.assertEqual(node.properties["module_name"], "test_auth")
        self.assertEqual(node.properties["class_name"], "TestAuthentication")
        self.assertEqual(node.properties["test_framework"], "pytest")
        self.assertEqual(node.properties["docstring"], "Test login functionality")
        self.assertEqual(node.properties["last_result"], "pass")
        self.assertEqual(node.properties["last_execution_time"], 0.25)
        self.assertEqual(node.properties["parameters"], ["username", "password"])
        self.assertEqual(node.properties["tags"], ["auth", "login"])
    
    def test_validation_of_required_properties(self):
        """Test validation of required properties."""
        # Missing required properties
        node = TestNode(
            labels=["Test"],
            properties={
                # Missing name, file_path, function_name, module_name
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()
        
        # With required properties
        node = TestNode(
            labels=["Test"],
            properties={
                "name": "test_login",
                "file_path": "/path/to/test_auth.py",
                "function_name": "test_login",
                "module_name": "test_auth",
            }
        )
        
        # Should not raise an exception
        node.validate_properties()
    
    def test_property_type_validation(self):
        """Test validation of property types."""
        # Wrong type for last_execution_time
        node = TestNode(
            labels=["Test"],
            properties={
                "name": "test_login",
                "file_path": "/path/to/test_auth.py",
                "function_name": "test_login",
                "module_name": "test_auth",
                "last_execution_time": "not a number",  # Should be a float
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()
        
        # Wrong type for tags
        node = TestNode(
            labels=["Test"],
            properties={
                "name": "test_login",
                "file_path": "/path/to/test_auth.py",
                "function_name": "test_login",
                "module_name": "test_auth",
                "tags": "not a list",  # Should be a list
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()


class TestImplementationNode(unittest.TestCase):
    """Test the ImplementationNode class."""
    
    def test_creation_with_valid_properties(self):
        """Test creating an ImplementationNode with valid properties."""
        node = ImplementationNode(
            labels=["Implementation", "Function"],
            properties={
                "name": "login",
                "file_path": "/path/to/auth.py",
                "function_name": "login",
                "module_name": "auth",
                "class_name": "AuthService",
                "docstring": "Login function",
                "complexity": 5,
                "line_count": 30,
                "parameters": ["username", "password"],
                "return_type": "bool",
            }
        )
        
        # Check that properties are correctly set
        self.assertEqual(node.properties["name"], "login")
        self.assertEqual(node.properties["file_path"], "/path/to/auth.py")
        self.assertEqual(node.properties["function_name"], "login")
        self.assertEqual(node.properties["module_name"], "auth")
        self.assertEqual(node.properties["class_name"], "AuthService")
        self.assertEqual(node.properties["docstring"], "Login function")
        self.assertEqual(node.properties["complexity"], 5)
        self.assertEqual(node.properties["line_count"], 30)
        self.assertEqual(node.properties["parameters"], ["username", "password"])
        self.assertEqual(node.properties["return_type"], "bool")
    
    def test_validation_of_required_properties(self):
        """Test validation of required properties."""
        # Missing required properties
        node = ImplementationNode(
            labels=["Implementation"],
            properties={
                # Missing name, file_path, function_name, module_name
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()
        
        # With required properties
        node = ImplementationNode(
            labels=["Implementation"],
            properties={
                "name": "login",
                "file_path": "/path/to/auth.py",
                "function_name": "login",
                "module_name": "auth",
            }
        )
        
        # Should not raise an exception
        node.validate_properties()


class TestModuleNode(unittest.TestCase):
    """Test the ModuleNode class."""
    
    def test_creation_with_valid_properties(self):
        """Test creating a ModuleNode with valid properties."""
        node = ModuleNode(
            labels=["Module"],
            properties={
                "name": "auth",
                "file_path": "/path/to/auth.py",
                "package_name": "app.services",
                "docstring": "Authentication module",
                "is_package": False,
                "imports": ["os", "sys", "hashlib"],
                "line_count": 150,
                "classes": ["AuthService", "User"],
                "functions": ["hash_password", "verify_password"],
            }
        )
        
        # Check that properties are correctly set
        self.assertEqual(node.properties["name"], "auth")
        self.assertEqual(node.properties["file_path"], "/path/to/auth.py")
        self.assertEqual(node.properties["package_name"], "app.services")
        self.assertEqual(node.properties["docstring"], "Authentication module")
        self.assertEqual(node.properties["is_package"], False)
        self.assertEqual(node.properties["imports"], ["os", "sys", "hashlib"])
        self.assertEqual(node.properties["line_count"], 150)
        self.assertEqual(node.properties["classes"], ["AuthService", "User"])
        self.assertEqual(node.properties["functions"], ["hash_password", "verify_password"])
    
    def test_validation_of_required_properties(self):
        """Test validation of required properties."""
        # Missing required properties
        node = ModuleNode(
            labels=["Module"],
            properties={
                # Missing name, file_path
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()
        
        # With required properties
        node = ModuleNode(
            labels=["Module"],
            properties={
                "name": "auth",
                "file_path": "/path/to/auth.py",
            }
        )
        
        # Should not raise an exception
        node.validate_properties()


class TestFixtureNode(unittest.TestCase):
    """Test the FixtureNode class."""
    
    def test_creation_with_valid_properties(self):
        """Test creating a FixtureNode with valid properties."""
        node = FixtureNode(
            labels=["Fixture"],
            properties={
                "name": "db_connection",
                "file_path": "/path/to/conftest.py",
                "function_name": "db_connection",
                "module_name": "conftest",
                "scope": "session",
                "docstring": "Database connection fixture",
                "autouse": True,
                "dependencies": ["config"],
                "return_type": "Connection",
            }
        )
        
        # Check that properties are correctly set
        self.assertEqual(node.properties["name"], "db_connection")
        self.assertEqual(node.properties["file_path"], "/path/to/conftest.py")
        self.assertEqual(node.properties["function_name"], "db_connection")
        self.assertEqual(node.properties["module_name"], "conftest")
        self.assertEqual(node.properties["scope"], "session")
        self.assertEqual(node.properties["docstring"], "Database connection fixture")
        self.assertEqual(node.properties["autouse"], True)
        self.assertEqual(node.properties["dependencies"], ["config"])
        self.assertEqual(node.properties["return_type"], "Connection")
    
    def test_validation_of_required_properties(self):
        """Test validation of required properties."""
        # Missing required properties
        node = FixtureNode(
            labels=["Fixture"],
            properties={
                # Missing name, file_path, function_name, module_name
            }
        )
        
        with self.assertRaises(ValidationError):
            node.validate_properties()
        
        # With required properties
        node = FixtureNode(
            labels=["Fixture"],
            properties={
                "name": "db_connection",
                "file_path": "/path/to/conftest.py",
                "function_name": "db_connection",
                "module_name": "conftest",
            }
        )
        
        # Should not raise an exception
        node.validate_properties()
    
    def test_default_values(self):
        """Test default values for optional properties."""
        node = FixtureNode(
            labels=["Fixture"],
            properties={
                "name": "db_connection",
                "file_path": "/path/to/conftest.py",
                "function_name": "db_connection",
                "module_name": "conftest",
            }
        )
        
        node.validate_properties()
        
        # Check default values
        self.assertEqual(node.properties["scope"], "function")
        self.assertEqual(node.properties["autouse"], False)


if __name__ == "__main__":
    unittest.main() 