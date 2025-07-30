# Knowledge Graph Schema

This directory contains the schema definitions for the Knowledge Graph, including node types, relationship types, and property schemas. These schema definitions are used to validate, serialize, and deserialize graph data.

## Overview

The Knowledge Graph schema is organized as follows:

- **Base Classes**: Abstract base classes for nodes, relationships, and properties (`base.py`)
- **Node Types**: Concrete node types such as TestNode, ImplementationNode, etc. (`nodes.py`)
- **Relationship Types**: Concrete relationship types such as TestToImplRel, UsesFixtureRelationship, etc. (`relationships.py`)
- **Versioning**: Schema versioning system for compatibility and migrations (`versioning.py`)
- **Example**: Example code demonstrating usage (`example.py`)

## Schema Versioning

All schema components have a version number (e.g., `1.0.0`). When deserializing data, the schema version is checked to ensure compatibility. The versioning system allows for:

- Backward compatibility checks
- Schema migrations
- Version-specific serialization/deserialization

## Node Types

| Node Type | Description | Key Properties |
|-----------|-------------|----------------|
| TestNode | Represents a test function or method | name, file_path, function_name, module_name |
| ImplementationNode | Represents an implementation function or method | name, file_path, function_name, module_name, complexity |
| ModuleNode | Represents a Python module | name, file_path, package_name, imports |
| FixtureNode | Represents a test fixture | name, file_path, function_name, module_name, scope |
| NodeSchema | Represents a test function or method | name, file_path, function_name, module_name |

## Relationship Types

| Relationship Type | Description | Source → Target | Key Properties |
|-------------------|-------------|----------------|----------------|
| TestToImplRel | Test tests an implementation | NodeSchema → ImplementationNode | confidence, coverage_percentage |
| UsesFixtureRelationship | Test uses a fixture | NodeSchema → FixtureNode | usage_type, is_direct |
| CallsRelationship | Function calls another function | Any Node → Any Node | call_count, call_locations |
| ImportsRelationship | Module imports another module | ModuleNode → ModuleNode | import_type, imported_names |
| InheritsFromRelationship | Class inherits from another class | Any Node → Any Node | inheritance_level, overridden_methods |
| CoversPathRelationship | Test covers a specific execution path | NodeSchema → ImplementationNode | path_id, path_description |
| ContainsRelationship | Module/Class contains member | ModuleNode/ImplementationNode → Any Node | position, is_nested |

## Code Chunk Integration

The schema now supports code chunk integration through additional properties and relationships. This enables a more granular representation of code structure in the knowledge graph.

### Chunk Properties for Node Types

Node types have been extended with chunk-specific properties:

#### ModuleNode

```python
{
    "chunk_id": "module_123",       # Unique identifier from the chunker
    "start_line": 1,                # First line of the module
    "end_line": 150,                # Last line of the module
    "imports": ["os", "sys"],       # Module imports
    "is_package": False             # Whether it's a package module
}
```

#### ImplementationNode

For Functions:
```python
{
    "chunk_id": "function_456",     # Unique identifier from the chunker
    "chunk_type": "function",       # Type of chunk (function, method, class)
    "start_line": 10,               # First line of the function
    "end_line": 20,                 # Last line of the function
    "is_async": False,              # Whether it's an async function
    "decorators": ["@staticmethod"],# Function decorators
    "function_args": {              # Function arguments with type hints
        "arg1": {"type_hint": "str", "default": None}
    },
    "return_type": "None",          # Return type hint
    "complexity": 5                 # Cyclomatic complexity
}
```

For Classes:
```python
{
    "chunk_id": "class_789",        # Unique identifier from the chunker
    "chunk_type": "class",          # Type of chunk
    "start_line": 30,               # First line of the class
    "end_line": 100,                # Last line of the class
    "base_classes": ["BaseClass"],  # Base classes for inheritance
    "methods_count": 5              # Number of methods in the class
}
```

### Example: Creating Nodes from Chunks

```python
from testindex.knowledge.schema.nodes import ModuleNode, ImplementationNode

# Create a module node from a chunk
module_node = ModuleNode(
    name="example_module",
    file_path="/path/to/example.py",
    package_name="example_package",
    properties={
        "chunk_id": "module_123",
        "start_line": 1,
        "end_line": 100,
        "imports": ["import os", "from sys import path"],
        "is_package": False
    }
)

# Create an implementation node from a function chunk
function_node = ImplementationNode(
    name="example_function",
    file_path="/path/to/example.py",
    function_name="example_function",
    module_name="example_module",
    line_number=10,
    properties={
        "chunk_id": "function_456",
        "chunk_type": "function",
        "start_line": 10,
        "end_line": 20,
        "is_async": False,
        "decorators": ["@staticmethod"],
        "function_args": {"arg1": {"type_hint": "str"}},
        "return_type": "str",
        "complexity": 3
    }
)
```

### Chunk-Related Relationships

New properties have been added to the relationship types to represent chunk dependencies:

#### ContainsRelationship

```python
{
    "position": 0,                 # Position within the parent
    "is_nested": True,             # Whether it's a nested relationship
    "chunk_relation": "parent_child" # Type of containment relationship
}
```

#### CallsRelationship

```python
{
    "call_count": 3,               # Number of calls
    "is_conditional": True,        # Whether call is within conditional
    "call_locations": [12, 15, 18] # Line numbers where calls occur
}
```

## Example Usage

### Creating Nodes

```python
from testindex.knowledge.schema.nodes import NodeSchema

# Create a test node
test_node = NodeSchema(
    id="test_example_login",
    name="test_example_login",
    file_path="tests/test_auth.py",
    function_name="test_user_login",
    module_name="test_auth",
    class_name="TestAuthentication",
    test_framework="pytest",
    docstring="Test that users can login with valid credentials",
    tags=["authentication", "smoke"],
)

# Validate properties
test_node.validate_properties()
```

### Creating Relationships

```python
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode
from testindex.knowledge.schema.relationships import TestToImplRel

# Create nodes
test_node = NodeSchema(id="test_example_login", name="test_example_login", file_path="tests/test_auth.py")
impl_node = ImplementationNode(id="login_function", name="login", file_path="app/auth.py")

# Create a relationship
tests_rel = TestToImplRel(
    source_id=test_node.id,
    target_id=impl_node.id,
    properties={
        "confidence": 0.95,
        "detection_method": "static",
        "coverage_percentage": 0.8,
    }
)
```

### Serialization and Deserialization

```python
# Serialize to dictionary
node_dict = test_node.to_dict()

# Serialize to JSON
node_json = test_node.to_json()

# Deserialize from dictionary
deserialized_node_from_dict = NodeSchema.from_dict(node_dict)

# Deserialize from JSON
deserialized_node_from_json = NodeSchema.from_json(node_json)
```

### Schema Migration

```python
from testindex.knowledge.schema.versioning import migrate_schema_item

# Migrate a node to a new version
migrated_node = migrate_schema_item(test_node, "1.1.0")
```

## Extending the Schema

To add a new node or relationship type:

1. Create a new class that inherits from `Node` or `Relationship`
2. Define a unique `_schema_type` class variable
3. Implement the `get_property_definitions()` method to define properties
4. Add the new class to the appropriate exports in `__init__.py`

Example:

```python
from typing import ClassVar, List
from testindex.knowledge.schema.base import Node, Property, PropertyType

class NewNodeType(Node):
    """Custom node type for specific use case."""
    _schema_type: ClassVar[str] = "new_node_type"
    
    @classmethod
    def get_property_definitions(cls) -> List[Property]:
        return [
            Property(
                name="custom_prop",
                type=PropertyType.STRING,
                description="Custom property",
                required=True,
            ),
            # Add more properties as needed
        ]
``` 
