# Guide to Implementing a Custom Vector Store

This document provides instructions and best practices for implementing a custom vector store for the embedding system.

## Overview

The vector store system uses a common interface (`VectorStoreInterface`) that allows for different backend implementations. Currently, an in-memory implementation exists, but you can create your own implementation for different storage backends such as:

- Database-backed vector stores (PostgreSQL, Redis, etc.)
- Cloud-based vector databases (Pinecone, Weaviate, etc.)
- File-based vector stores
- Distributed vector stores

## Implementation Requirements

To implement a custom vector store, you need to create a class that inherits from `VectorStoreInterface` and implements all of its abstract methods.

### Required Components

1. **Import the Interface and Data Classes**

```python
from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import VectorOperationError, VectorInvalidDimensionError
```

2. **Implement All Abstract Methods**

Your class must implement these methods:

- `store_vector`: Store a single vector with metadata
- `batch_store_vectors`: Store multiple vectors in a batch operation
- `get_vector`: Retrieve a vector and its metadata by ID
- `delete_vector`: Delete a vector by ID
- `search_vectors`: Search for similar vectors
- `count_vectors`: Count vectors optionally filtered by metadata
- `clear`: Remove all vectors from the store

## Implementation Template

Here's a template to get started:

```python
class CustomVectorStore(VectorStoreInterface):
    """
    A custom implementation of the VectorStoreInterface using [YOUR BACKEND].
    """

    def __init__(self, connection_params):
        """Initialize the vector store with connection parameters."""
        # Initialize your backend storage
        # Set up any required connections
        # Initialize dimension information

    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """Store a single vector with its metadata."""
        try:
            # Validate vector format
            # Normalize if required by your backend
            # Generate ID if not provided
            # Store vector in your backend
            # Handle any backend-specific operations
            return vector_id
        except Exception as e:
            # Convert backend-specific errors to standardized errors
            raise VectorOperationError(f"Failed to store vector: {str(e)}")

    async def batch_store_vectors(
        self, 
        vectors: List[EmbeddingVector], 
        metadata_list: List[EmbeddingMetadata],
        vector_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Store multiple vectors in a batch operation."""
        # Implementation here
        pass

    async def get_vector(self, vector_id: str) -> Tuple[Optional[EmbeddingVector], Optional[EmbeddingMetadata]]:
        """Retrieve a vector and its metadata by ID."""
        # Implementation here
        pass

    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        # Implementation here
        pass

    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search for similar vectors."""
        # Implementation here
        pass

    async def count_vectors(self, filter_metadata: Optional[Dict] = None) -> int:
        """Count vectors optionally filtered by metadata."""
        # Implementation here
        pass

    async def clear(self) -> None:
        """Remove all vectors from the store."""
        # Implementation here
        pass
```

## Best Practices

### Error Handling

Always handle potential errors and convert them to standardized error types:

- Use `VectorInvalidDimensionError` for dimension mismatch issues
- Use `VectorOperationError` for general operation failures
- Provide detailed error messages for debugging

Example:
```python
try:
    # Vector operation code
except BackendSpecificError as e:
    raise VectorOperationError(f"Failed to search vectors: {str(e)}")
```

### Dimension Validation

Always validate vector dimensions:

```python
# Set dimension with first vector
if self._dimension is None:
    self._dimension = len(vector)
# Validate subsequent vectors
elif len(vector) != self._dimension:
    raise VectorInvalidDimensionError(
        f"Vector dimension {len(vector)} doesn't match store dimension {self._dimension}"
    )
```

### Vector Normalization

For similarity search, normalize vectors for consistent results:

```python
def normalize_vector(vector):
    norm = np.linalg.norm(vector)
    if norm > 0:
        return vector / norm
    return vector
```

### Metadata Handling

When implementing metadata filtering, follow this approach:

```python
def matches_filter(metadata, filter_criteria):
    # Handle nested additional field
    additional = metadata.get("additional", {}) or {}
    
    # Check top-level fields first
    for key, value in filter_criteria.items():
        if key in metadata:
            if metadata[key] != value:
                return False
        elif key in additional:
            if additional[key] != value:
                return False
        else:
            return False
    return True
```

## Performance Considerations

- For large vector collections, implement backend-specific optimizations
- Consider batch operations where possible
- Use appropriate indexes for your backend
- Implement caching for frequently accessed vectors
- For distributed systems, consider sharding strategies

## Testing Your Implementation

1. Create unit tests that verify:
   - Basic CRUD operations (create, read, update, delete)
   - Dimension validation
   - Metadata filtering
   - Similarity search accuracy
   - Error handling
   - Edge cases (empty store, large batches, etc.)

2. Benchmark against the reference implementation for:
   - Storage speed
   - Retrieval speed
   - Search accuracy
   - Memory usage

## Example: Redis-Backed Vector Store

Here's a simplified example for a Redis backend using redis-py:

```python
import redis
import numpy as np
import json
import uuid
from typing import Dict, List, Optional, Tuple

from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import VectorOperationError, VectorInvalidDimensionError

class RedisVectorStore(VectorStoreInterface):
    """Vector store implementation using Redis."""
    
    def __init__(self, host='localhost', port=6379, prefix='vectors:'):
        """Initialize Redis connection."""
        self.redis = redis.Redis(host=host, port=port)
        self.prefix = prefix
        self._dimension_key = f"{prefix}dimension"
        
        # Get dimension from Redis or set to None
        dim = self.redis.get(self._dimension_key)
        self._dimension = int(dim) if dim else None
    
    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """Store vector and metadata in Redis."""
        try:
            # Convert to numpy and validate
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector, dtype=np.float32)
                
            # Set or validate dimension
            if self._dimension is None:
                self._dimension = vector.shape[0]
                self.redis.set(self._dimension_key, self._dimension)
            elif vector.shape[0] != self._dimension:
                raise VectorInvalidDimensionError(
                    f"Vector dimension {vector.shape[0]} doesn't match store dimension {self._dimension}"
                )
            
            # Generate ID if not provided
            if vector_id is None:
                vector_id = str(uuid.uuid4())
            
            # Store vector and metadata using Redis hash
            vector_key = f"{self.prefix}{vector_id}"
            pipeline = self.redis.pipeline()
            pipeline.hset(vector_key, "vector", vector.tobytes())
            pipeline.hset(vector_key, "metadata", json.dumps(asdict(metadata)))
            pipeline.execute()
            
            return vector_id
            
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            raise VectorOperationError(f"Failed to store vector in Redis: {str(e)}")
    
    # Implement remaining methods...
```

## Common Pitfalls

1. **Not handling dimension consistency**: Always validate dimensions across operations
2. **Ignoring metadata serialization**: Properly serialize/deserialize complex metadata
3. **Poor error handling**: Convert backend-specific errors to standard errors
4. **Ignoring concurrency**: Ensure thread/process safety for shared resources
5. **Not optimizing for scale**: Consider performance with large vector collections

## Resources

- [Vector Store Interface Documentation](path/to/docs)
- [In-Memory Implementation Reference](testindex/knowledge/embedding/in_memory_vector_store.py)
- [Error Handling Guide](path/to/error/guide) 