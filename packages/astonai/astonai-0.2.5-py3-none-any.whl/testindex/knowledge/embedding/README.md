# Vector Embedding Service

This module provides functionality to generate and store vector embeddings for code chunks, enabling semantic search and similarity analysis of code.

## Components

### EmbeddingService

The main service that coordinates embedding generation, preprocessing, caching, and storage. It supports:

- Generating embeddings for code snippets
- Batch operations for efficient API usage
- Intelligent caching to avoid regenerating embeddings
- Integration with vector stores for persistence
- Code-specific preprocessing to optimize embedding quality
- Integration with Neo4j for hybrid graph-vector queries

### Vector Stores

The module includes multiple vector store implementations:

- **In-memory Vector Store**: For testing and small-scale usage
- **SQLite Vector Store**: A persistent, file-based vector store
- **Custom Vector Stores**: An extensible interface for implementing custom backends

### Hybrid Queries

The integration package provides the `HybridQueryService` that combines:

- Vector similarity search from embeddings
- Graph traversal and constraints from Neo4j
- Combined ranking of results based on both vector similarity and graph relationships

## Usage

Basic embedding generation:

```python
from testindex.knowledge.embedding.embedding_service import EmbeddingService, EmbeddingServiceConfig

# Initialize the service
config = EmbeddingServiceConfig(openai_api_key="your-api-key")
embedding_service = EmbeddingService(config)

# Generate an embedding
code = "def calculate_sum(a, b): return a + b"
checksum, embedding = await embedding_service.generate_embedding(code)
```

Integration with vector store:

```python
from testindex.knowledge.embedding.examples.sqlite_vector_store import SQLiteVectorStore

# Initialize components
vector_store = SQLiteVectorStore("embeddings.db")
embedding_service = EmbeddingService(config, vector_store)

# Generate and store an embedding
vector_id = await embedding_service.embed_and_store(
    code,
    metadata={"function_name": "calculate_sum", "file_path": "utils.py"}
)

# Search for similar code
query = "function to add two numbers"
_, query_embedding = await embedding_service.generate_embedding(query)
results = await vector_store.search_vectors(query_embedding, limit=5)
```

Processing code chunks:

```python
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker

# Initialize components
chunker = PythonCodeChunker(config)
chunks = chunker.chunk_file("example.py")

# Generate embeddings for chunks
for chunk in chunks:
    vector_id = await embedding_service.embed_chunk(chunk)
```

## Configuration

Key configuration options include:

- `openai_api_key`: API key for OpenAI embeddings
- `embedding_model`: Model to use (default: "text-embedding-3-small")
- `enable_cache`: Whether to cache embeddings (default: true)
- `batch_size`: Number of embeddings to process in a batch (default: 10)
- `rate_limit_requests`: Rate limiting for API requests
- `rate_limit_tokens`: Rate limiting for token usage

## Error Handling

The module provides specialized error types:

- `EmbeddingGenerationError`: Base class for embedding errors
- `EmbeddingModelError`: Issues with the embedding model
- `EmbeddingRateLimitError`: API rate limits exceeded
- `EmbeddingTokenLimitError`: Content exceeds token limits

## Examples

See the `examples` directory for complete working examples:
- `embedding_service_example.py`: Basic usage examples
- `sqlite_vector_store.py`: SQLite-based vector store implementation

## Tests

Run the tests with pytest:

```
pytest testindex/knowledge/embedding/tests/
``` 