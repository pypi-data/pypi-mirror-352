from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, ConfigDict


class QueryType(Enum):
    """Enum defining the types of queries supported."""
    TEST_COVERAGE = auto()
    TEST_RELATIONSHIP = auto()
    IMPLEMENTATION_RELATIONSHIP = auto()
    CODE_SIMILARITY = auto()  # For future use in Phase 2
    CUSTOM = auto()  # For custom graph queries


class Query(BaseModel):
    """Abstract base class for all queries."""
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    query_type: QueryType
    limit: Optional[int] = Field(default=100, description="Maximum number of results to return")
    skip: Optional[int] = Field(default=0, description="Number of results to skip")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def execute(self, **kwargs: Any) -> 'QueryResult':
        # Implementation of execute method
        pass


class CoverageQuery(Query):
    """Query for test coverage information."""
    implementation_path: Optional[str] = None
    implementation_name: Optional[str] = None
    implementation_id: Optional[str] = None
    test_path: Optional[str] = None
    test_name: Optional[str] = None
    test_id: Optional[str] = None
    
    def __init__(self, **data):
        data.setdefault('name', self.__class__.__name__)
        data["query_type"] = QueryType.TEST_COVERAGE
        super().__init__(**data)


class RelationshipQuery(Query):
    """Query for test relationship information."""
    fixture_name: Optional[str] = None
    fixture_id: Optional[str] = None
    test_id: Optional[str] = None
    test_name: Optional[str] = None
    test_path: Optional[str] = None
    relationship_type: Optional[str] = None
    
    def __init__(self, **data):
        data.setdefault('name', self.__class__.__name__)
        data["query_type"] = QueryType.TEST_RELATIONSHIP
        super().__init__(**data)


class ImplementationRelationshipQuery(Query):
    """Query for implementation relationship information."""
    implementation_name: Optional[str] = None
    implementation_id: Optional[str] = None
    implementation_path: Optional[str] = None
    relationship_type: Optional[str] = Field(default="CALLS", description="Type of relationship (e.g., CALLS, IMPORTS)")
    
    def __init__(self, **data):
        data.setdefault('name', self.__class__.__name__)
        data["query_type"] = QueryType.IMPLEMENTATION_RELATIONSHIP
        super().__init__(**data)


class CustomQuery(Query):
    """Custom Cypher query."""
    cypher_query: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    def __init__(self, **data):
        data.setdefault('name', self.__class__.__name__)
        data["query_type"] = QueryType.CUSTOM
        super().__init__(**data)


class NodeType(BaseModel):
    """Model representing a node returned in query results."""
    id: str
    name: str
    file_path: Optional[str] = None
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class RelationshipType(BaseModel):
    """Model representing a relationship returned in query results."""
    id: str
    type: str
    source_id: str
    target_id: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class QueryResult(BaseModel):
    """Represents a query result with items and metadata."""
    items: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    query: Optional[str] = None
    nodes: Optional[List[NodeType]] = Field(default_factory=list)
    relationships: Optional[List[RelationshipType]] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True) 