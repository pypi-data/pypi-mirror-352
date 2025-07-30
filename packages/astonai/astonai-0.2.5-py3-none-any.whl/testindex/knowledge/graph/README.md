# Knowledge Graph Module

This module provides tools and utilities for creating, managing, and querying knowledge graphs, with a particular focus on code analysis and semantic relationships between software components.

## Overview

The knowledge graph module allows you to:

1. Create graph representations of code and documentation
2. Extract relationships between software components
3. Store metadata and content for efficient retrieval
4. Query the graph to gain insights about your codebase
5. Track relationships between tests and implementations

## Architecture

The module consists of several key components:

### GraphDatabase

The `GraphDatabase` class provides the core functionality for interacting with the underlying graph database (Neo4j). It handles:

- Connection management
- Transaction handling
- Query execution
- Schema management
- Batch operations

### StaticAnalyzer

The `StaticAnalyzer` analyzes Python code to extract:

- Function definitions and calls
- Class hierarchies
- Module dependencies
- Import relationships
- Test relationships

This information is then used to build a comprehensive knowledge graph of your codebase.

### QueryEngine

The `QueryEngine` provides a high-level API for querying the knowledge graph, allowing you to:

- Find related components
- Discover test coverage
- Analyze dependencies
- Identify entry points
- Track function usage

## Getting Started

### Installation

Ensure you have Neo4j installed and running. The module requires Python 3.8+ and the following dependencies:

```bash
pip install neo4j py2neo libcst
```

### Basic Usage

```python
from testindex.knowledge.graph import GraphDatabase, StaticAnalyzer

# Initialize the graph database
graph_db = GraphDatabase(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password"
)

# Create a static analyzer
analyzer = StaticAnalyzer(graph_db)

# Analyze a file
analyzer.analyze_file("/path/to/your/file.py")

# Analyze an entire directory
analyzer.analyze_directory("/path/to/your/project")

# Query the knowledge graph
query_engine = graph_db.get_query_engine()
implementations = query_engine.find_implementations("SomeClass")
tests = query_engine.find_tests_for_implementation("SomeClass.some_method")
```

### Examples

See the `examples` directory for complete examples:

- `static_analyzer_example.py`: Demonstrates analyzing Python code and building a knowledge graph
- `knowledge_query_example.py`: Shows how to query the knowledge graph for insights

## Schema

The knowledge graph uses the following primary node types:

- `Module`: Represents a Python module
- `Class`: Represents a Python class
- `Function`: Represents a function or method
- `TestClass`: Represents a test class
- `TestFunction`: Represents a test function or method

And the following relationship types:

- `IMPORTS`: Module imports another module
- `CONTAINS`: Module contains class/function, or class contains method
- `CALLS`: Function calls another function
- `INHERITS_FROM`: Class inherits from another class
- `TESTS`: Test function/class tests an implementation

## Code Chunk Integration

The knowledge graph now integrates with the Code Processing pod's chunking system, allowing for more precise code analysis and querying.

### Chunk-Based Queries

#### Find High-Complexity Functions

```cypher
MATCH (i:Implementation)
WHERE i.metadata.complexity > 10
RETURN i.name, i.file_path, i.metadata.complexity
ORDER BY i.metadata.complexity DESC
LIMIT 10
```

#### Find Function Call Hierarchies

```cypher
MATCH path = (f1:Implementation {name: "main"})-[:CALLS*1..5]->(f2:Implementation)
RETURN path
```

#### Find Nested Functions

```cypher
MATCH (parent:Implementation)-[:CONTAINS]->(child:Implementation)
WHERE child.metadata.chunk_type = "nested_function"
RETURN parent.name, child.name, child.line_number
```

#### Find Test Coverage for Functions

```cypher
MATCH (i:Implementation)
WHERE i.metadata.chunk_type = "function"
OPTIONAL MATCH (t:Implementation)-[:TESTS]->(i)
RETURN i.name, 
       count(t) as test_count,
       collect(t.name) as test_names
ORDER BY test_count DESC
```

### Visualization Tips

When working with chunk-based graphs in Neo4j Browser:

1. Use the following style settings for better visualization:
   ```
   :style
   node.Module {
     color: #68BDF6;
     diameter: 50px;
     caption: '{name}';
   }
   node.Implementation {
     color: #6DCE9E;
     diameter: 40px;
     caption: '{name}';
   }
   relationship.CONTAINS {
     color: #68BDF6;
     shaft-width: 3px;
   }
   relationship.CALLS {
     color: #FF756E;
     shaft-width: 2px;
   }
   ```

2. For better performance with large graphs, use the `LIMIT` clause and filter by specific modules:
   ```cypher
   MATCH path = (m:Module {name: "target_module"})-[:CONTAINS*1..2]->(n)
   RETURN path LIMIT 50
   ```

### Performance Considerations

When working with chunk-based analysis of large codebases:

1. **Index Critical Properties**:
   ```cypher
   CREATE INDEX ON :Implementation(chunk_id);
   CREATE INDEX ON :Module(chunk_id);
   CREATE INDEX ON :Implementation(name, chunk_type);
   ```

2. **Use Query Parameters** for better query performance:
   ```python
   query = """
   MATCH (i:Implementation)
   WHERE i.name = $name AND i.metadata.chunk_type = $chunk_type
   RETURN i
   """
   result = graph_db.execute_query(query, {"name": "example_function", "chunk_type": "function"})
   ```

3. **Batch Operations** for importing large codebases:
   ```python
   # Process in batches of 500 chunks
   chunk_node_map = adapter.process_chunks(chunks, batch_size=500)
   ```

## Best Practices

1. **Incremental Updates**: After the initial analysis, only analyze files that have changed
2. **Regular Backups**: Back up your graph database regularly
3. **Schema Versioning**: Keep track of schema versions when updating the module
4. **Query Optimization**: Use the provided query API rather than raw Cypher when possible
5. **Batching**: Use batch operations for analyzing multiple files

## Error Handling

See the `errors.py` module for specific exceptions. The main exception types are:

- `Neo4jConnectionError`: Issues connecting to the database
- `Neo4jQueryError`: Issues with query syntax or execution
- `BatchOperationError`: Issues with batch operations
- `StaticAnalysisError`: Issues during code analysis
- `SchemaVersionMismatchError`: Issues with schema version compatibility
- `ChunkGraphAdapterError`: Issues with code chunk integration

## Contributing

When contributing to this module:

1. Follow the existing patterns and naming conventions
2. Write tests for new functionality
3. Update documentation and examples
4. Ensure backward compatibility where possible

## Further Resources

- For detailed information on code chunk integration, see [Chunk Integration Documentation](../docs/chunk_integration.md)
- Check the schema documentation for node and relationship type definitions
- Explore example queries in the `examples` directory

## License

This module is licensed under the MIT License - see the LICENSE file for details. 