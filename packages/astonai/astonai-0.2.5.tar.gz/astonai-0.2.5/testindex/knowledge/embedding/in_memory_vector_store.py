#!/usr/bin/env python3
"""
In-memory implementation of vector storage for embeddings.
"""

import copy
import logging
import uuid
from typing import Dict, List, Optional, Tuple, Set, Any
import numpy as np
from dataclasses import asdict
from scipy.spatial.distance import cosine

from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import VectorOperationError, VectorInvalidDimensionError

logger = logging.getLogger(__name__)

class InMemoryVectorStore(VectorStoreInterface):
    """
    An in-memory implementation of the VectorStoreInterface.
    This implementation stores vectors in memory using dictionaries and numpy arrays.
    Provides basic vector similarity search functionality using cosine similarity.
    """

    def __init__(self):
        """Initialize an empty in-memory vector store."""
        self._vectors: Dict[str, EmbeddingVector] = {}
        self._metadata: Dict[str, EmbeddingMetadata] = {}
        self._dimension: Optional[int] = None

    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """
        Store a single vector with its metadata in memory.
        
        Args:
            vector: The embedding vector to store
            metadata: Metadata associated with the vector
            vector_id: Optional ID for the vector. If not provided, a UUID will be generated.
            
        Returns:
            The ID of the stored vector.
            
        Raises:
            VectorInvalidDimensionError: If the vector dimension doesn't match existing vectors
            VectorOperationError: If there's an error during the store operation
        """
        try:
            # Convert vector to numpy array if it isn't already
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector, dtype=np.float32)
            
            # Set dimension if this is the first vector
            if self._dimension is None:
                self._dimension = vector.shape[0]
            # Validate dimension for subsequent vectors
            elif vector.shape[0] != self._dimension:
                raise VectorInvalidDimensionError(
                    f"Vector dimension {vector.shape[0]} doesn't match store dimension {self._dimension}"
                )
            
            # Generate ID if not provided
            if vector_id is None:
                vector_id = str(uuid.uuid4())
                
            # Store vector and metadata
            self._vectors[vector_id] = vector
            self._metadata[vector_id] = metadata
            
            return vector_id
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            raise VectorOperationError(f"Failed to store vector: {str(e)}")

    async def batch_store_vectors(
        self, 
        vectors: List[EmbeddingVector], 
        metadata_list: List[EmbeddingMetadata],
        vector_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Store multiple vectors with their metadata in a batch operation.
        
        Args:
            vectors: List of embedding vectors to store
            metadata_list: List of metadata objects associated with the vectors
            vector_ids: Optional list of IDs for the vectors. If not provided, UUIDs will be generated.
            
        Returns:
            List of IDs for the stored vectors
            
        Raises:
            ValueError: If the lengths of vectors and metadata_list don't match
            VectorOperationError: If there's an error during the batch store operation
        """
        if len(vectors) != len(metadata_list):
            raise ValueError("The number of vectors must match the number of metadata items")
        
        # Generate IDs if not provided
        if vector_ids is None:
            vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        elif len(vector_ids) != len(vectors):
            raise ValueError("The number of vector_ids must match the number of vectors")
        
        # Store each vector
        result_ids = []
        for i, (vector, metadata) in enumerate(zip(vectors, metadata_list)):
            vector_id = await self.store_vector(vector, metadata, vector_ids[i])
            result_ids.append(vector_id)
            
        return result_ids

    async def get_vector(self, vector_id: str) -> Tuple[Optional[EmbeddingVector], Optional[EmbeddingMetadata]]:
        """
        Retrieve a vector and its metadata by ID.
        
        Args:
            vector_id: The ID of the vector to retrieve
            
        Returns:
            A tuple of (vector, metadata) if found, or (None, None) if not found
        """
        vector = self._vectors.get(vector_id)
        metadata = self._metadata.get(vector_id)
        return vector, metadata

    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector and its metadata by ID.
        
        Args:
            vector_id: The ID of the vector to delete
            
        Returns:
            True if the vector was deleted, False if it wasn't found
        """
        if vector_id in self._vectors:
            del self._vectors[vector_id]
            del self._metadata[vector_id]
            return True
        return False

    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors using cosine similarity.
        
        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold (0-1)
            filter_metadata: Optional metadata filter criteria as a dictionary
            
        Returns:
            List of SearchResult objects ordered by similarity (highest first)
            
        Raises:
            VectorInvalidDimensionError: If the query vector dimension doesn't match the store
            VectorOperationError: If there's an error during the search operation
        """
        try:
            if not self._vectors:
                return []
                
            # Convert query vector to numpy array if it isn't already
            if not isinstance(query_vector, np.ndarray):
                query_vector = np.array(query_vector, dtype=np.float32)
                
            # Validate dimension
            if query_vector.shape[0] != self._dimension:
                raise VectorInvalidDimensionError(
                    f"Query vector dimension {query_vector.shape[0]} doesn't match store dimension {self._dimension}"
                )
                
            # Normalize query vector for cosine similarity
            query_norm = np.linalg.norm(query_vector)
            if query_norm > 0:
                query_vector = query_vector / query_norm
                
            results = []
            for vector_id, vector in self._vectors.items():
                # Apply metadata filter if provided
                if filter_metadata and not self._matches_filter(vector_id, filter_metadata):
                    continue
                    
                # Normalize vector for cosine similarity
                vector_norm = np.linalg.norm(vector)
                if vector_norm > 0:
                    normalized_vector = vector / vector_norm
                else:
                    normalized_vector = vector
                    
                # Calculate cosine similarity
                similarity = float(np.dot(query_vector, normalized_vector))
                
                # Apply threshold
                if similarity >= score_threshold:
                    results.append(
                        SearchResult(
                            id=vector_id,
                            score=similarity,
                            metadata=self._metadata[vector_id]
                        )
                    )
                    
            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:limit]
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            raise VectorOperationError(f"Failed to search vectors: {str(e)}")

    async def count_vectors(self, filter_metadata: Optional[Dict] = None) -> int:
        """
        Count the number of vectors in the store, optionally filtered by metadata.
        
        Args:
            filter_metadata: Optional metadata filter criteria as a dictionary
            
        Returns:
            The count of vectors matching the filter (or total count if no filter)
        """
        if not filter_metadata:
            return len(self._vectors)
            
        count = 0
        for vector_id in self._vectors.keys():
            if self._matches_filter(vector_id, filter_metadata):
                count += 1
                
        return count

    async def clear(self) -> None:
        """
        Clear all vectors and metadata from the store.
        """
        self._vectors.clear()
        self._metadata.clear()
        self._dimension = None

    def _matches_filter(self, vector_id: str, filter_metadata: Dict) -> bool:
        """
        Check if a vector's metadata matches the filter criteria.
        
        Args:
            vector_id: The ID of the vector to check
            filter_metadata: Dictionary of metadata key-value pairs to match
            
        Returns:
            True if the metadata matches all filter criteria, False otherwise
        """
        metadata = asdict(self._metadata[vector_id])
        
        # Handle the additional field separately since it's a nested dictionary
        additional = metadata.pop("additional", {}) or {}
        
        # First check the top-level fields
        for key, value in filter_metadata.items():
            if key in metadata:
                if metadata[key] != value:
                    return False
            elif key in additional:
                if additional[key] != value:
                    return False
            else:
                return False
                
        return True 