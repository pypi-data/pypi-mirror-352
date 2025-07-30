"""
Unit tests for the base schema classes.

Tests the functionality of the SchemaItem, Node, and Relationship base classes.
"""

import json
import unittest
from datetime import datetime
from uuid import UUID

from testindex.core.exceptions import ValidationError
from testindex.knowledge.schema.base import (
    Node,
    Property,
    PropertyType,
    Relationship,
    SchemaItem,
    SchemaVersionMismatchError,
)


class TestProperty(unittest.TestCase):
    """Test the Property class."""
    
    def test_property_creation(self):
        """Test property creation with various types."""
        # String property
        string_prop = Property(
            name="test_string",
            type=PropertyType.STRING,
            description="A test string property",
            required=True,
        )
        self.assertEqual(string_prop.name, "test_string")
        self.assertEqual(string_prop.type, PropertyType.STRING)
        self.assertTrue(string_prop.required)
        
        # Integer property with default
        int_prop = Property(
            name="test_int",
            type=PropertyType.INTEGER,
            description="A test integer property",
            required=False,
            default=42,
        )
        self.assertEqual(int_prop.default, 42)
        self.assertFalse(int_prop.required)
    
    def test_property_validation(self):
        """Test property validation with different types and values."""
        # String property
        string_prop = Property(
            name="test_string",
            type=PropertyType.STRING,
            description="A test string property",
        )
        self.assertEqual(string_prop.validate("hello"), "hello")
        self.assertEqual(string_prop.validate(123), "123")  # Convert to string
        
        # Integer property
        int_prop = Property(
            name="test_int",
            type=PropertyType.INTEGER,
            description="A test integer property",
        )
        self.assertEqual(int_prop.validate(42), 42)
        self.assertEqual(int_prop.validate("42"), 42)  # Convert to int
        with self.assertRaises(ValidationError):
            int_prop.validate("not an int")
        
        # Boolean property
        bool_prop = Property(
            name="test_bool",
            type=PropertyType.BOOLEAN,
            description="A test boolean property",
        )
        self.assertEqual(bool_prop.validate(True), True)
        self.assertEqual(bool_prop.validate("true"), True)  # Convert to bool
        self.assertEqual(bool_prop.validate("false"), False)
        
        # Required property with None
        required_prop = Property(
            name="required_prop",
            type=PropertyType.STRING,
            description="A required property",
            required=True,
        )
        with self.assertRaises(ValidationError):
            required_prop.validate(None)
        
        # Optional property with None
        optional_prop = Property(
            name="optional_prop",
            type=PropertyType.STRING,
            description="An optional property",
            required=False,
            default="default",
        )
        self.assertEqual(optional_prop.validate(None), "default")


class TestNode(unittest.TestCase):
    """Test the Node class."""
    
    def test_node_creation(self):
        """Test node creation and basic properties."""
        node = Node(labels=["Test", "Example"])
        
        # Check basic properties
        self.assertIsNotNone(node.id)
        try:
            # Verify ID is a valid UUID
            UUID(node.id)
        except ValueError:
            self.fail("Node ID is not a valid UUID")
        
        self.assertIsInstance(node.created_at, datetime)
        self.assertIsInstance(node.updated_at, datetime)
        self.assertEqual(node.labels, ["Test", "Example"])
        self.assertEqual(node.properties, {})
    
    def test_node_serialization(self):
        """Test node serialization to dictionary and JSON."""
        node = Node(
            id="test-id-123",
            labels=["Test"],
            properties={"name": "test_node", "value": 42},
        )
        
        # Test to_dict()
        node_dict = node.to_dict()
        self.assertEqual(node_dict["id"], "test-id-123")
        self.assertEqual(node_dict["labels"], ["Test"])
        self.assertEqual(node_dict["properties"]["name"], "test_node")
        self.assertEqual(node_dict["properties"]["value"], 42)
        self.assertEqual(node_dict["_schema_type"], "node")
        self.assertEqual(node_dict["_schema_version"], "1.0.0")
        
        # Test to_json()
        node_json = node.to_json()
        parsed_json = json.loads(node_json)
        self.assertEqual(parsed_json["id"], "test-id-123")
    
    def test_node_deserialization(self):
        """Test node deserialization from dictionary and JSON."""
        # Create a dictionary representation
        node_dict = {
            "_schema_version": "1.0.0",
            "_schema_type": "node",
            "id": "test-id-456",
            "created_at": "2023-06-01T12:00:00",
            "updated_at": "2023-06-01T12:30:00",
            "labels": ["Test", "Example"],
            "properties": {"name": "test_node", "value": 42},
        }
        
        # Deserialize from dictionary
        node = Node.from_dict(node_dict)
        self.assertEqual(node.id, "test-id-456")
        self.assertEqual(node.labels, ["Test", "Example"])
        self.assertEqual(node.properties["name"], "test_node")
        
        # Deserialize from JSON
        node_json = json.dumps(node_dict)
        node = Node.from_json(node_json)
        self.assertEqual(node.id, "test-id-456")
    
    def test_version_mismatch(self):
        """Test handling of schema version mismatch."""
        node_dict = {
            "_schema_version": "2.0.0",  # Different version
            "_schema_type": "node",
            "id": "test-id-789",
            "created_at": "2023-06-01T12:00:00",
            "updated_at": "2023-06-01T12:30:00",
            "labels": ["Test"],
            "properties": {},
        }
        
        with self.assertRaises(SchemaVersionMismatchError):
            Node.from_dict(node_dict)


class TestRelationship(unittest.TestCase):
    """Test the Relationship class."""
    
    def test_relationship_creation(self):
        """Test relationship creation and basic properties."""
        rel = Relationship(
            source_id="source-123",
            target_id="target-456",
            type="test_relationship",
        )
        
        # Check basic properties
        self.assertIsNotNone(rel.id)
        self.assertEqual(rel.source_id, "source-123")
        self.assertEqual(rel.target_id, "target-456")
        self.assertEqual(rel.type, "test_relationship")
    
    def test_relationship_serialization(self):
        """Test relationship serialization to dictionary and JSON."""
        rel = Relationship(
            id="rel-id-123",
            source_id="source-123",
            target_id="target-456",
            type="test_relationship",
            properties={"weight": 0.8, "is_primary": True},
        )
        
        # Test to_dict()
        rel_dict = rel.to_dict()
        self.assertEqual(rel_dict["id"], "rel-id-123")
        self.assertEqual(rel_dict["source_id"], "source-123")
        self.assertEqual(rel_dict["target_id"], "target-456")
        self.assertEqual(rel_dict["type"], "test_relationship")
        self.assertEqual(rel_dict["properties"]["weight"], 0.8)
        self.assertEqual(rel_dict["_schema_type"], "relationship")
        
        # Test to_json()
        rel_json = rel.to_json()
        parsed_json = json.loads(rel_json)
        self.assertEqual(parsed_json["id"], "rel-id-123")
    
    def test_relationship_deserialization(self):
        """Test relationship deserialization from dictionary and JSON."""
        # Create a dictionary representation
        rel_dict = {
            "_schema_version": "1.0.0",
            "_schema_type": "relationship",
            "id": "rel-id-456",
            "created_at": "2023-06-01T12:00:00",
            "updated_at": "2023-06-01T12:30:00",
            "source_id": "source-789",
            "target_id": "target-012",
            "type": "test_relationship",
            "properties": {"weight": 0.5, "is_primary": False},
        }
        
        # Deserialize from dictionary
        rel = Relationship.from_dict(rel_dict)
        self.assertEqual(rel.id, "rel-id-456")
        self.assertEqual(rel.source_id, "source-789")
        self.assertEqual(rel.target_id, "target-012")
        self.assertEqual(rel.properties["weight"], 0.5)
        
        # Deserialize from JSON
        rel_json = json.dumps(rel_dict)
        rel = Relationship.from_json(rel_json)
        self.assertEqual(rel.id, "rel-id-456")
    
    def test_required_fields(self):
        """Test that required fields are enforced."""
        # Missing source_id
        rel_dict = {
            "_schema_version": "1.0.0",
            "_schema_type": "relationship",
            "id": "rel-id-456",
            "created_at": "2023-06-01T12:00:00",
            "updated_at": "2023-06-01T12:30:00",
            # Missing "source_id": "source-789",
            "target_id": "target-012",
            "type": "test_relationship",
            "properties": {},
        }
        
        with self.assertRaises(ValidationError):
            Relationship.from_dict(rel_dict)
        
        # Missing target_id
        rel_dict = {
            "_schema_version": "1.0.0",
            "_schema_type": "relationship",
            "id": "rel-id-456",
            "created_at": "2023-06-01T12:00:00",
            "updated_at": "2023-06-01T12:30:00",
            "source_id": "source-789",
            # Missing "target_id": "target-012",
            "type": "test_relationship",
            "properties": {},
        }
        
        with self.assertRaises(ValidationError):
            Relationship.from_dict(rel_dict)


if __name__ == "__main__":
    unittest.main() 