# Python Code Chunking

## Overview
The Python Code Chunker is a specialized component that parses Python source code and breaks it down into meaningful chunks based on code structure. These chunks serve as the foundation for building a detailed knowledge graph representation of the codebase.

## Core Components

### CodeChunk
`CodeChunk` is the fundamental data structure used to represent a segment of Python code:

```python
class CodeChunk:
    def __init__(self, 
                 chunk_id: str,
                 name: str,
                 chunk_type: ChunkType,
                 source_file: Path,
                 start_line: int,
                 end_line: int,
                 parent_chunk_id: Optional[str] = None,
                 source_code: Optional[str] = None,
                 imports: Optional[List[str]] = None,
                 dependencies: Optional[List[str]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        # Initialize the code chunk with identifying information
```

The `CodeChunk` holds essential information about code segments, including:
- A unique identifier
- The name of the code entity (function, class, etc.)
- The type of chunk (module, function, class, etc.)
- Source file location and line numbers
- Parent-child relationships
- Dependencies and imports
- Raw source code
- Additional metadata

### ChunkType
The `ChunkType` enum classifies different kinds of code structures:

```python
class ChunkType(Enum):
    MODULE = "module"
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    NESTED_FUNCTION = "nested_function"
    NESTED_CLASS = "nested_class"
    STANDALONE_CODE = "standalone_code"
```

### PythonCodeChunker
The `PythonCodeChunker` analyzes Python source files and extracts structured chunks:

```python
class PythonCodeChunker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def chunk_file(self, file_path: Union[str, Path]) -> List[CodeChunk]:
        """Process a Python file and break it down into logical chunks."""
        # Implementation details...
        
    def chunk_directory(self, dir_path: Union[str, Path], 
                         recursive: bool = True) -> List[CodeChunk]:
        """Process all Python files in a directory."""
        # Implementation details...
```

## Chunking Process

### Parsing Strategy
The chunker uses Python's abstract syntax tree (AST) module to parse the code and extract structured information:

1. **File-Level Parsing**: 
   - Creates a MODULE chunk for the entire file
   - Extracts imports and module-level variables

2. **Function Detection**:
   - Identifies function definitions
   - Captures function arguments, return types, and decorators
   - Detects calls to other functions

3. **Class Analysis**:
   - Creates CLASS chunks for class definitions
   - Identifies base classes for inheritance relationships
   - Breaks down class methods into METHOD chunks

4. **Nested Structure Handling**:
   - Properly handles nested functions and classes
   - Maintains the parent-child relationship between chunks

5. **Dependency Tracking**:
   - Records dependencies between code entities
   - Captures imports and their usage

### Chunk ID Generation
Each chunk receives a unique identifier based on its properties:

```python
def _generate_chunk_id(self, chunk_type: ChunkType, name: str, 
                       file_path: Path, line_number: int) -> str:
    """Generate a unique identifier for a code chunk."""
    # Creates hash-based IDs that are consistent across runs
    hash_input = f"{str(file_path)}:{chunk_type.value}:{name}:{line_number}"
    return hashlib.md5(hash_input.encode()).hexdigest()
```

## Integration with Knowledge Graph

The code chunks are transformed into knowledge graph nodes through the `ChunkGraphAdapter`, which:

1. **Converts chunks to nodes**:
   - Maps MODULE chunks to ModuleNode entities
   - Maps FUNCTION, METHOD, CLASS chunks to ImplementationNode entities
   - Preserves all metadata during conversion

2. **Builds relationships**:
   - Parent-child relationships using CONTAINS
   - Function call relationships using CALLS
   - Inheritance relationships using INHERITS_FROM
   - Module dependencies using IMPORTS

3. **Processes in batches**:
   - Handles large codebases efficiently
   - Uses transaction batching for better performance

## Usage Examples

### Basic File Chunking

```python
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker

# Initialize the chunker
chunker = PythonCodeChunker()

# Process a single file
chunks = chunker.chunk_file("path/to/your_module.py")

# Inspect the results
for chunk in chunks:
    print(f"{chunk.chunk_type.value}: {chunk.name} (Lines {chunk.start_line}-{chunk.end_line})")
    if chunk.dependencies:
        print(f"  Dependencies: {', '.join(chunk.dependencies)}")
```

### Processing a Directory

```python
# Process an entire directory
project_chunks = chunker.chunk_directory("path/to/project", recursive=True)

# Count chunks by type
from collections import Counter
chunk_types = Counter([chunk.chunk_type.value for chunk in project_chunks])
print(f"Found {len(project_chunks)} chunks: {dict(chunk_types)}")
```

### Building a Knowledge Graph

```python
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker
from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter
from testindex.knowledge.graph.neo4j_client import Neo4jClient

# Initialize components
chunker = PythonCodeChunker()
neo4j_client = Neo4jClient(uri="bolt://localhost:7687", username="neo4j", password="password")
adapter = ChunkGraphAdapter(neo4j_client=neo4j_client)

# Process code into chunks
chunks = chunker.chunk_directory("path/to/project")

# Convert chunks to graph nodes
chunk_node_map = adapter.process_chunks(chunks)

# Build relationships between nodes
relationships = adapter.build_relationships(chunks, chunk_node_map)

print(f"Created {len(chunk_node_map)} nodes and {len(relationships)} relationships in the knowledge graph")
```

## Advanced Usage

### Filtering Chunks

```python
# Get only function chunks
function_chunks = [c for c in chunks if c.chunk_type in 
                  (ChunkType.FUNCTION, ChunkType.METHOD)]

# Find chunks with specific dependencies
import_chunks = [c for c in chunks if c.imports and 
                any("pandas" in imp for imp in c.imports)]
```

### Custom Metadata Extraction

The chunker can be extended to extract custom metadata from code:

```python
class ExtendedPythonChunker(PythonCodeChunker):
    def _extract_function_metadata(self, node, chunk):
        # Call the parent method to get basic metadata
        metadata = super()._extract_function_metadata(node, chunk)
        
        # Add custom complexity metrics
        metadata["cyclomatic_complexity"] = self._calculate_complexity(node)
        
        # Add docstring analysis
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
            metadata["has_docstring"] = True
            metadata["docstring_lines"] = node.body[0].value.s.count('\n') + 1
        
        return metadata
```

## Error Handling

The chunker includes robust error handling to manage parsing failures:

```python
try:
    chunks = chunker.chunk_file("path/to/file.py")
except SyntaxError as e:
    print(f"Syntax error in file: {e}")
except Exception as e:
    print(f"Chunking error: {str(e)}")
```

## Performance Considerations

For large codebases:

1. **Memory Usage**: The chunker stores all chunks in memory during processing
2. **Processing Time**: Scales linearly with codebase size and complexity
3. **Optimization Options**:
   - Use `chunk_directory` with targeted subdirectories
   - Process changes incrementally after initial build
   - Implement filtering to focus on specific file types

## Visualization

Code chunks can be visualized in various ways:

1. **Using Neo4j Browser**:
   ```cypher
   MATCH (m:Module)-[:CONTAINS]->(impl:Implementation)
   WHERE m.name = "target_module"
   RETURN m, impl
   ```

2. **Generating call graphs**:
   ```cypher
   MATCH path = (f:Implementation {name: "main_function"})-[:CALLS*1..3]->(called)
   RETURN path
   ```

3. **Visualization libraries**:
   - NetworkX for Python-based graph visualization
   - D3.js for web-based interactive diagrams

## Limitations and Future Work

Current limitations:
- Limited support for dynamic Python features (eval, exec)
- May miss some dependencies in highly dynamic code
- Type hints are extracted but not fully analyzed

Future enhancements:
- Integration with type inference systems
- More detailed semantic analysis
- Support for additional Python features (decorators, metaclasses)
- Performance optimizations for very large codebases 