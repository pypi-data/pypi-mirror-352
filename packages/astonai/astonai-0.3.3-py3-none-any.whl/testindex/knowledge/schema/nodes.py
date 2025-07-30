"""
Node classes for the Knowledge Graph schema.

This module defines node classes that represent entities in the Knowledge Graph.
"""

from typing import Any, Dict, List, Optional

from testindex.knowledge.schema.base import Node


class NodeSchema(Node):
    """Represents a test function or method in the knowledge graph."""
    
    def __init__(
        self,
        name: str,
        file_path: str,
        line_number: Optional[int] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new NodeSchema.
        
        Args:
            name: Name of the test
            file_path: Path to the file containing the test
            line_number: Line number where the test is defined
            description: Description of the test (docstring)
            id: Node ID (default: None to generate a new ID)
            properties: Optional node properties
        """
        labels = ["Test"]
        super().__init__(
            labels=labels,
            id=id,
            properties=properties or {}
        )
        self.properties["name"] = name
        self.properties["file_path"] = file_path
        if line_number is not None:
            self.properties["line_number"] = line_number
        if description is not None:
            self.properties["description"] = description

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeSchema":
        # Extract only the constructor parameters from data
        constructor_params = {
            "name": data.get("properties", {}).get("name"),
            "file_path": data.get("properties", {}).get("file_path"),
            "line_number": data.get("properties", {}).get("line_number"),
            "description": data.get("properties", {}).get("description"),
            "id": data.get("id"),
            "properties": data.get("properties", {}),
        }
        # Remove None values
        constructor_params = {k: v for k, v in constructor_params.items() if v is not None}
        return cls(**constructor_params)


class ImplementationNode(Node):
    """Node representing an implementation function, method, or class."""
    
    def __init__(
        self,
        name: str,
        file_path: str,
        line_number: Optional[int] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new ImplementationNode.
        
        Args:
            name: Name of the implementation
            file_path: Path to the file containing the implementation
            line_number: Line number where the implementation is defined
            description: Description of the implementation (docstring)
            id: Node ID (default: None to generate a new ID)
            properties: Optional node properties
        """
        labels = ["Node", "Implementation"]
        super().__init__(
            labels=labels,
            id=id,
            properties=properties or {}
        )
        self.properties["name"] = name
        self.properties["file_path"] = file_path
        if line_number is not None:
            self.properties["line_number"] = line_number
        if description is not None:
            self.properties["description"] = description


class ModuleNode(Node):
    """Node representing a module (Python file)."""
    
    def __init__(
        self,
        name: str,
        file_path: str,
        description: Optional[str] = None,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new ModuleNode.
        
        Args:
            name: Name of the module
            file_path: Path to the module file
            description: Description of the module
            id: Node ID (default: None to generate a new ID)
            properties: Optional node properties
        """
        labels = ["Node", "Module"]
        super().__init__(
            labels=labels,
            id=id,
            properties=properties or {}
        )
        self.properties["name"] = name
        self.properties["file_path"] = file_path
        if description is not None:
            self.properties["description"] = description


class FixtureNode(Node):
    """Node representing a test fixture."""
    
    def __init__(
        self,
        name: str,
        file_path: str,
        line_number: Optional[int] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new FixtureNode.
        
        Args:
            name: Name of the fixture
            file_path: Path to the file containing the fixture
            line_number: Line number where the fixture is defined
            description: Description of the fixture (docstring)
            id: Node ID (default: None to generate a new ID)
            properties: Optional node properties
        """
        labels = ["Node", "Fixture"]
        super().__init__(
            labels=labels,
            id=id,
            properties=properties or {}
        )
        self.properties["name"] = name
        self.properties["file_path"] = file_path
        if line_number is not None:
            self.properties["line_number"] = line_number
        if description is not None:
            self.properties["description"] = description 