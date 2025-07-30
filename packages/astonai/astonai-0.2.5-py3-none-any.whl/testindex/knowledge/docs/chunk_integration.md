# Code Chunk Integration

## Introduction
This document describes how code chunks from the Processing pod are integrated into the Knowledge Graph. This integration enables more precise code analysis and querying by breaking down large code files into meaningful segments that maintain their structural relationships.

## Node Representation
Code chunks are represented as nodes in the graph with the following mapping:

| Chunk Type        | Knowledge Graph Node Type | Properties Added                    |
|-------------------|---------------------------|------------------------------------|
| MODULE            | ModuleNode                | chunk_id, source_file, start_line, end_line, imports, is_package |
| FUNCTION          | ImplementationNode        | chunk_id, is_method, is_async, function_args, return_type, source_code |
| METHOD            | ImplementationNode        | chunk_id, class_name, decorators, is_async, function_args, return_type |
| CLASS             | ImplementationNode        | chunk_id, base_classes, methods_count |
| NESTED_FUNCTION   | ImplementationNode        | chunk_id, parent_name, nesting_level |
| NESTED_CLASS      | ImplementationNode        | chunk_id, parent_name, nesting_level |
| STANDALONE_CODE   | ImplementationNode        | chunk_id, type="standalone" |

## Relationship Types

The following relationships are created between chunk nodes:

| Source Chunk Type | Relationship Type | Target Chunk Type | Properties                       |
|-------------------|------------------|--------------------|----------------------------------|
| Any               | CONTAINS         | Any                | position, is_nested              |
| FUNCTION/METHOD   | CALLS            | FUNCTION/METHOD    | call_count, is_conditional       |
| CLASS             | INHERITS_FROM    | CLASS              | inheritance_level                |
| MODULE            | IMPORTS          | MODULE             | import_type, imported_names      |

## Integration Architecture

The `ChunkGraphAdapter` serves as a bridge between the preprocessing pod and the knowledge graph pod:

```
┌─────────────────┐      ┌──────────────────┐      ┌────────────────┐
│ CodeChunker     │      │ ChunkGraphAdapter│      │ Knowledge Graph│
│                 │─────▶│                  │─────▶│                │
│ (Preprocessing) │      │ (Integration)    │      │ (Neo4j)        │
└─────────────────┘      └──────────────────┘      └────────────────┘
```

The adapter:
1. Converts code chunks to appropriate node types
2. Maps dependencies between chunks to graph relationships
3. Supports batch processing for large codebases
4. Optimizes memory usage for efficient processing

## Query Examples

### Finding All Functions in a Module

This query finds all function implementations contained within a specific module:

```cypher
MATCH (m:Module {name: "example_module"})-[:CONTAINS]->(f:Implementation)
WHERE f.metadata.chunk_type IN ["function", "method"]
RETURN f.name, f.line_number, f.metadata.is_async
```

### Finding Test Functions for an Implementation

This query finds all test functions that test a specific implementation:

```cypher
MATCH (i:Implementation {name: "example_function"})
MATCH (t:Implementation)-[:TESTS]->(i)
WHERE t.metadata.chunk_type IN ["function", "method"] 
  AND t.name STARTS WITH "test_"
RETURN t.name, t.file_path, t.line_number
```

### Analyzing Function Call Hierarchies

This query identifies all functions called (directly or indirectly) by a given function:

```cypher
MATCH path = (f1:Implementation {name: "example_function"})-[:CALLS*1..5]->(f2:Implementation)
RETURN path
```

### Finding Code Chunks with High Complexity

This query identifies implementation chunks with high cyclomatic complexity:

```cypher
MATCH (i:Implementation)
WHERE i.metadata.complexity > 10
RETURN i.name, i.file_path, i.metadata.complexity
ORDER BY i.metadata.complexity DESC
LIMIT 10
```

### Finding Parent-Child Chunk Relationships

This query shows the containment hierarchy of chunks:

```cypher
MATCH path = (parent)-[:CONTAINS*]->(child)
WHERE parent.metadata.chunk_id = "module_123"
RETURN path
```

## Performance Considerations

When working with large codebases:

1. **Batch Processing**: Nodes and relationships are created in batches of 100 by default
2. **Indexing**: The following indices are automatically created for chunk-related queries:
   - Implementation.chunk_id
   - Module.chunk_id
   - Implementation.name
   - Module.name
3. **Memory Usage**: For codebases over 100K lines, consider increasing Neo4j heap allocation
4. **Selective Processing**: Only process changed files after initial processing for incremental updates

## Programmatic Usage Example

```python
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker
from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter
from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jConfig

# Create a code chunker and process a file
chunker = PythonCodeChunker()
chunks = chunker.chunk_file("path/to/file.py")

# Create a Neo4j client
neo4j_config = Neo4jConfig(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password"
)
neo4j_client = Neo4jClient(neo4j_config)

# Create an adapter with the Neo4j client
adapter = ChunkGraphAdapter(neo4j_client)

# Process chunks and create nodes/relationships in Neo4j
chunk_node_map = adapter.process_chunks(chunks)
relationships = adapter.build_relationships(chunks, chunk_node_map)

print(f"Created {len(chunk_node_map)} nodes and {len(relationships)} relationships")
```

## Error Handling

The integration provides robust error handling through the `ChunkGraphAdapterError` exception class, which gives detailed information about failures during the conversion or integration process.

Common error scenarios include:
- Invalid chunk types
- Missing chunk dependencies
- Database connection issues
- Duplicate node creation attempts

Example error handling:

```python
from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter, ChunkGraphAdapterError

adapter = ChunkGraphAdapter()

try:
    chunk_node_map = adapter.process_chunks(chunks)
    relationships = adapter.build_relationships(chunks, chunk_node_map)
except ChunkGraphAdapterError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
    # Implement recovery mechanism
```

## Visualization Tips

When visualizing chunk-based graphs in Neo4j Browser:

1. Use the following Cypher query to visualize module hierarchies:
   ```cypher
   MATCH path = (m:Module)-[:CONTAINS*1..3]->(n)
   WHERE m.name = "example_module"
   RETURN path LIMIT 25
   ```

2. For function call graphs, use:
   ```cypher
   MATCH path = (f:Implementation {name: "main_function"})-[:CALLS*1..3]->(called)
   RETURN path
   ```

3. To improve visualization, configure node labels in Neo4j Browser to show:
   - Module nodes: name property
   - Implementation nodes: name + chunk_type properties

## Future Development

Upcoming enhancements to the chunk integration include:

1. Support for more languages beyond Python
2. Dynamic analysis integration for runtime call graphs
3. Improved performance for large-scale codebases
4. Enhanced querying capabilities for specific code patterns 