"""
Base schema definitions for the Knowledge Graph.

This module provides abstract base classes for nodes, relationships, and properties,
including serialization/deserialization and validation mechanisms.
"""

import abc
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Union, ClassVar

from pydantic import BaseModel, Field, validator, root_validator, ConfigDict

from testindex.core.exceptions import ValidationError
from testindex.core.logging import get_logger

logger = get_logger(__name__)


class SchemaVersionMismatchError(ValidationError):
    """Raised when attempting to deserialize a schema with version mismatch."""
    error_code = "KNOWLEDGE001"


class PropertyType(str, Enum):
    """Enumeration of property types supported in the knowledge graph."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    LIST = "list"
    DICT = "dict"


class Property(BaseModel):
    """Base class for schema properties.
    
    Properties are used to define the attributes of nodes and relationships.
    They include type information, validation, and serialization/deserialization.
    """
    name: str
    type: PropertyType
    description: str
    required: bool = False
    default: Optional[Any] = None
    
    def validate(self, value: Any) -> Any:
        """Validate a value against this property's type and constraints.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated value, possibly with type conversion
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            if self.required:
                raise ValidationError(f"Property '{self.name}' is required")
            return self.default
            
        try:
            if self.type == PropertyType.STRING:
                return str(value)
            elif self.type == PropertyType.INTEGER:
                return int(value)
            elif self.type == PropertyType.FLOAT:
                return float(value)
            elif self.type == PropertyType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes")
                return bool(value)
            elif self.type == PropertyType.DATETIME:
                if isinstance(value, str):
                    return datetime.fromisoformat(value)
                return value
            elif self.type == PropertyType.LIST:
                if not isinstance(value, list):
                    raise ValidationError(f"Property '{self.name}' must be a list")
                return value
            elif self.type == PropertyType.DICT:
                if not isinstance(value, dict):
                    raise ValidationError(f"Property '{self.name}' must be a dictionary")
                return value
            else:
                raise ValidationError(f"Unsupported property type: {self.type}")
        except Exception as e:
            raise ValidationError(f"Failed to validate property '{self.name}': {str(e)}")


class SchemaItem(BaseModel, abc.ABC):
    """Abstract base class for all schema items (nodes and relationships).
    
    Provides common functionality for schema version management,
    serialization/deserialization, and validation.
    """
    # Class variables
    _schema_version: ClassVar[str] = "1.0.0"
    _schema_type: ClassVar[str] = "base"  # Will be overridden by subclasses
    
    # Instance variables
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to the current time."""
        self.updated_at = datetime.now(timezone.utc)
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="allow"
    )
    
    def validate_properties(self) -> None:
        """Validate all properties according to their definitions.
        
        Raises:
            ValidationError: If any property fails validation
        """
        for prop_def in self.get_property_definitions():
            value = self.properties.get(prop_def.name)
            validated_value = prop_def.validate(value)
            if validated_value is not None:  # Don't set None values
                self.properties[prop_def.name] = validated_value
    
    @classmethod
    def schema_version(cls) -> str:
        """Get the schema version of this class."""
        return cls._schema_version
    
    @classmethod
    def schema_type(cls) -> str:
        """Get the schema type of this class."""
        return cls._schema_type
        
    @classmethod
    def get_property_definitions(cls) -> List[Property]:
        """Get the property definitions for this schema item."""
        return []
    
    def to_dict(self, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert the schema item to a dictionary.
        
        Args:
            exclude_none: Whether to exclude None values (default: True)
            
        Returns:
            Dict[str, Any]: The schema item as a dictionary
        """
        self.update_timestamp()
        
        # Convert to dictionary
        data = {
            "_schema_version": self._schema_version,
            "_schema_type": self._schema_type,
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "properties": self.properties,
        }
        return data
    
    def to_json(self) -> str:
        """Convert the schema item to a JSON string.
        
        Returns:
            str: The schema item as a JSON string
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaItem":
        """Create a schema item from a dictionary representation.
        
        Args:
            data: Dictionary with schema item data
            
        Returns:
            SchemaItem: A new schema item instance
            
        Raises:
            SchemaVersionMismatchError: If the schema version doesn't match
        """
        # Check schema version
        schema_version = data.get("_schema_version")
        if schema_version != cls._schema_version:
            raise SchemaVersionMismatchError(
                f"Schema version mismatch: expected {cls._schema_version}, got {schema_version}"
            )
        
        # Check schema type
        schema_type = data.get("_schema_type")
        if schema_type != cls._schema_type:
            logger.warning(
                f"Schema type mismatch: expected {cls._schema_type}, got {schema_type}"
            )
        
        # Create instance with basic fields
        instance = cls(
            id=data.get("id", str(uuid.uuid4())),
            created_at=(
                cls.parse_datetime(data["created_at"])
                if "created_at" in data
                else datetime.now(timezone.utc)
            ),
            updated_at=(
                cls.parse_datetime(data["updated_at"])
                if "updated_at" in data
                else datetime.now(timezone.utc)
            ),
            properties=data.get("properties", {})
        )
        
        # Validate properties
        instance.validate_properties()
        
        return instance
    
    @classmethod
    def from_json(cls, json_str: str) -> "SchemaItem":
        """Create a schema item from a JSON string.
        
        Args:
            json_str: JSON string with schema item data
            
        Returns:
            SchemaItem: A new schema item instance
            
        Raises:
            ValidationError: If the JSON is invalid
            SchemaVersionMismatchError: If the schema version doesn't match
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON: {str(e)}")


class Node(SchemaItem):
    """Base class for all nodes in the knowledge graph.
    
    Nodes represent entities in the knowledge graph, such as test functions,
    implementation modules, and fixtures.
    """
    _schema_type: ClassVar[str] = "node"
    
    # Node-specific fields
    labels: List[str] = Field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the node to a dictionary representation.
        
        Returns:
            Dict[str, Any]: The node as a dictionary
        """
        data = super().to_dict()
        data["labels"] = self.labels
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        """Create a node from a dictionary representation.
        
        Args:
            data: Dictionary with node data
            
        Returns:
            Node: A new node instance
        """
        instance = super().from_dict(data)
        instance.labels = data.get("labels", [])
        return instance


class Relationship(SchemaItem):
    """Base class for all relationships in the knowledge graph.
    
    Relationships connect nodes in the knowledge graph, representing
    semantic connections such as "tests", "uses_fixture", etc.
    """
    _schema_type: ClassVar[str] = "relationship"
    
    # Relationship-specific fields
    source_id: str
    target_id: str
    type: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary representation.
        
        Returns:
            Dict[str, Any]: The relationship as a dictionary
        """
        data = super().to_dict()
        data.update({
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """Create a relationship from a dictionary representation.
        
        Args:
            data: Dictionary with relationship data
            
        Returns:
            Relationship: A new relationship instance
            
        Raises:
            ValidationError: If required fields are missing
        """
        instance = super().from_dict(data)
        
        # Check required fields
        if "source_id" not in data:
            raise ValidationError("Relationship requires source_id")
        if "target_id" not in data:
            raise ValidationError("Relationship requires target_id")
        if "type" not in data:
            raise ValidationError("Relationship requires type")
        
        instance.source_id = data["source_id"]
        instance.target_id = data["target_id"]
        instance.type = data["type"]
        
        return instance 