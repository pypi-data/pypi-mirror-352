# Knowledge Graph and Vector Embedding Infrastructure

This package provides the schema definitions, database integration, and mechanisms to store and query code relationships and semantic information for the Test Intelligence Engine.

## Overview

The `knowledge` package is responsible for:

1. Defining schema for code entities (tests, implementations, modules, fixtures)
2. Managing relationships between code entities (tests, uses_fixture, calls, imports, etc.)
3. Storing and retrieving graph data using Neo4j integration
4. Managing vector embeddings for semantic search using Pinecone
5. Integrating graph and vector storage for hybrid search and analysis

## Code Chunk Integration

The Knowledge Graph now supports integration with the Code Processing pod's chunking system. 
Code chunks (functions, classes, modules) are represented as nodes in the graph with relationships
that preserve their structure and dependencies:

- Module chunks → ModuleNode
- Function/Method chunks → ImplementationNode  
- Class chunks → ImplementationNode

This integration enables more precise code analysis and querying by breaking down large code
files into meaningful segments. See our [Chunk Integration Documentation](docs/chunk_integration.md)
for details on querying and working with chunk-based representations.

## Package Structure

```
testindex/knowledge/
├── __init__.py                # Package initialization
├── README.md                  # This file
├── schema/                    # Schema definitions
│   ├── __init__.py            # Schema exports
│   ├── base.py                # Base schema classes
│   ├── nodes.py               # Node type definitions
│   ├── relationships.py       # Relationship type definitions
│   ├── versioning.py          # Schema version management
│   ├── example.py             # Usage examples
│   └── README.md              # Schema documentation
├── graph/                     # Graph database integration (planned)
│   ├── __init__.py
│   ├── neo4j_client.py        # Neo4j client implementation
│   └── relation_builder.py    # Helper for building relationships
├── vector/                    # Vector embedding integration (planned)
│   ├── __init__.py
│   ├── pinecone_client.py     # Pinecone client implementation
│   └── embedding_manager.py   # Manages embeddings creation and storage
├── docs/                      # Documentation
│   └── chunk_integration.md   # Code chunk integration details
└── integration/               # Integration between graph and vector (planned)
    └── graph_vector_linker.py # Links graph nodes with vector embeddings
```

## Current Status

- **Completed:** Schema definitions for nodes, relationships, and properties
- **Completed:** Serialization/deserialization and validation mechanisms
- **Completed:** Schema versioning system for migrations and compatibility
- **Completed:** Unit tests for schema components
- **Planned:** Neo4j integration for graph database storage
- **Planned:** Pinecone integration for vector embedding storage
- **Planned:** Integration utilities between graph and vector components

## Usage Examples

See `schema/example.py` for comprehensive examples of schema usage. Here's a basic example:

```python
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode
from testindex.knowledge.schema.relationships import TestToImplRel

# Create nodes
test_node = NodeSchema(
    id="test_login_flow", 
    name="test_login_flow",
    labels=["Test", "Function"],
    properties={
        "file_path": "/path/to/test_auth.py",
        "function_name": "test_user_login",
        "module_name": "test_auth",
    }
)

impl_node = ImplementationNode(
    id="user_login_impl", 
    name="user_login", 
    file_path="app/auth.py"
)

# Create relationship
relationship = TestToImplRel(
    source_id=test_node.id,
    target_id=impl_node.id,
    properties={
        "confidence": 0.95,
        "detection_method": "static",
    }
)

# Serialize to JSON
json_data = test_node.to_json()

# Deserialize from JSON
deserialized_node = NodeSchema.from_json(json_data)
```

## Dependencies

- **Core Foundation Pod**: Depends on core components for configuration, logging, exceptions
- **Preprocessing Pod**: Consumes output from code processing pipeline (future integration)

## For Future Contributors

To extend the Knowledge Graph schema:

1. Review the existing schema in the `schema/` directory
2. Follow the patterns established in `schema/nodes.py` and `schema/relationships.py`
3. Extend the appropriate base classes from `schema/base.py`
4. Update `schema/__init__.py` with new exports
5. Add unit tests for new components
6. Update documentation in this README and `schema/README.md` 