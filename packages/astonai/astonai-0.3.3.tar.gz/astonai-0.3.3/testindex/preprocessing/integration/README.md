# Code Chunk to Knowledge Graph Integration

This package provides adapters and utilities for integrating the preprocessing components with other pods in the TestIndex system.

## Overview

The primary component is the `ChunkGraphAdapter`, which converts `CodeChunk` objects from the code chunking module into appropriate Knowledge Graph nodes and relationships. This integration enables:

- Representation of code structure in a graph database
- Efficient querying of code relationships
- Visualization of dependencies between code components
- Traceability between chunks and their dependencies

## Architecture

### ChunkGraphAdapter

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

## Chunk to Node Mapping

| Chunk Type        | Knowledge Graph Node Type |
|-------------------|---------------------------|
| MODULE            | ModuleNode                |
| FUNCTION          | ImplementationNode        |
| METHOD            | ImplementationNode        |
| CLASS             | ImplementationNode        |
| NESTED_FUNCTION   | ImplementationNode        |
| NESTED_CLASS      | ImplementationNode        |
| STANDALONE_CODE   | ImplementationNode        |

## Relationship Types

| Source Chunk Type | Relationship Type | Target Chunk Type | Description                     |
|-------------------|------------------|--------------------|----------------------------------|
| Any               | CONTAINS         | Any                | Parent-child relationship        |
| FUNCTION/METHOD   | CALLS            | FUNCTION/METHOD    | Function call                    |
| CLASS             | INHERITS_FROM    | CLASS              | Class inheritance                |
| MODULE            | IMPORTS          | MODULE             | Module import                    |

## Memory Optimization

The adapter includes memory optimization techniques for processing large codebases:

- Batch processing with configurable batch sizes
- Streaming approach for relationship building
- Efficient chunk-to-node mapping

## Example Usage

### Basic Usage

```python
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker
from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter

# Create a code chunker and process a file
chunker = PythonCodeChunker(config)
chunks = chunker.chunk_file("path/to/file.py")

# Create an adapter and process the chunks
adapter = ChunkGraphAdapter()
chunk_node_map = adapter.process_chunks(chunks)
relationships = adapter.build_relationships(chunks, chunk_node_map)

# The result is a graph representation of the code structure
print(f"Created {len(chunk_node_map)} nodes and {len(relationships)} relationships")
```

### Integration with Neo4j

```python
from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jConfig

# Create a Neo4j client
neo4j_config = Neo4jConfig.from_environment()
neo4j_client = Neo4jClient(neo4j_config)

# Create an adapter with the Neo4j client
adapter = ChunkGraphAdapter(neo4j_client)

# Process chunks and create nodes/relationships in Neo4j
chunk_node_map = adapter.process_chunks(chunks)
relationships = adapter.build_relationships(chunks, chunk_node_map)
```

## Example Scripts

For a complete demonstration, see the provided example script:

- `examples/chunk_graph_example.py`: Shows the full workflow from code chunking to graph integration

Run the example with:

```bash
python examples/chunk_graph_example.py --output ./output --neo4j --query
```

## Error Handling

The adapter provides robust error handling through the `ChunkGraphAdapterError` exception class, which gives detailed information about any failures during the conversion or graph integration process. 