"""
Relationship classes for the Knowledge Graph schema.

This module defines relationship classes that connect nodes in the Knowledge Graph.
"""

from typing import Any, Dict, Optional

from testindex.knowledge.schema.base import Relationship


class TestToImplRelationship(Relationship):
    """Relationship indicating a test tests an implementation."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 0.9,
    ):
        """Initialize a new TestToImplRelationship.
        
        Args:
            source_id: ID of the source node (test)
            target_id: ID of the target node (implementation)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
            confidence: Confidence score of the relationship (0-1)
        """
        props = properties or {}
        props["confidence"] = confidence
        
        super().__init__(
            type="TESTS",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=props
        )
        
    @property
    def confidence(self) -> float:
        """Get the confidence score for this relationship."""
        return self.properties.get("confidence", 0.9)
        
    @confidence.setter
    def confidence(self, value: float) -> None:
        """Set the confidence score for this relationship."""
        if not 0 <= value <= 1:
            raise ValueError("Confidence score must be between 0 and 1")
        self.properties["confidence"] = value


class ImportsRelationship(Relationship):
    """Relationship indicating a module imports another module."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new ImportsRelationship.
        
        Args:
            source_id: ID of the source node (importer)
            target_id: ID of the target node (importee)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="IMPORTS",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        )


class UsesFixtureRelationship(Relationship):
    """Relationship indicating a test uses a fixture."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new UsesFixtureRelationship.
        
        Args:
            source_id: ID of the source node (test)
            target_id: ID of the target node (fixture)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="USES_FIXTURE",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        )


class CallsRelationship(Relationship):
    """Relationship indicating a function calls another function."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new CallsRelationship.
        
        Args:
            source_id: ID of the source node (caller)
            target_id: ID of the target node (callee)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="CALLS",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        )


class InheritsFromRelationship(Relationship):
    """Relationship indicating a class inherits from another class."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new InheritsFromRelationship.
        
        Args:
            source_id: ID of the source node (child)
            target_id: ID of the target node (parent)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="INHERITS_FROM",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        )


class CoversPathRelationship(Relationship):
    """Relationship indicating a test covers a specific code path."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new CoversPathRelationship.
        
        Args:
            source_id: ID of the source node (test)
            target_id: ID of the target node (implementation)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="COVERS_PATH",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        )


class ContainsRelationship(Relationship):
    """Relationship indicating a node contains another node."""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a new ContainsRelationship.
        
        Args:
            source_id: ID of the source node (container)
            target_id: ID of the target node (contained)
            id: Relationship ID (default: None to generate a new ID)
            properties: Optional relationship properties
        """
        super().__init__(
            type="CONTAINS",
            source_id=source_id,
            target_id=target_id,
            id=id,
            properties=properties or {}
        ) 