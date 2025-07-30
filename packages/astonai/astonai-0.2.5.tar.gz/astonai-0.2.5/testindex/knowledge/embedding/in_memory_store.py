#!/usr/bin/env python3
"""
In-memory implementation of the vector store interface.
This is primarily for testing and development purposes.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import uuid

from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import VectorOperationError


class InMemoryVectorStore(VectorStoreInterface):
    """
    In-memory implementation of the VectorStoreInterface.
    
    This implementation stores vectors in memory using dictionaries.
    It's intended for testing, development, and small-scale use cases.
    """
    
    def __init__(self):
        """Initialize an empty in-memory vector store."""
        self._vectors = {}  # id -> EmbeddingVector
        self._metadata = {}  # id -> EmbeddingMetadata
    
    async def store_vector(self, vector: EmbeddingVector, metadata: EmbeddingMetadata) -> str:
        """
        Store a vector in memory with its associated metadata.
        
        Args:
            vector: The embedding vector to store
            metadata: Metadata associated with the vector
            
        Returns:
            The ID of the stored vector
            
        Raises:
            VectorOperationError: If the vector cannot be stored
        """
        try:
            # Generate a unique ID if not provided
            vector_id = metadata.id or str(uuid.uuid4())
            
            # Store the vector and metadata
            self._vectors[vector_id] = vector
            
            # Create a new metadata object with the ID
            if not metadata.id:
                metadata = EmbeddingMetadata(
                    id=vector_id,
                    text=metadata.text,
                    source=metadata.source,
                    type=metadata.type,
                    additional=metadata.additional
                )
            
            self._metadata[vector_id] = metadata
            return vector_id
        except Exception as e:
            raise VectorOperationError(
                f"Failed to store vector: {str(e)}",
                operation="store"
            ) from e
    
    async def batch_store_vectors(
        self, vectors: List[EmbeddingVector], metadata_list: List[EmbeddingMetadata]
    ) -> List[str]:
        """
        Store multiple vectors in memory with their associated metadata.
        
        Args:
            vectors: List of embedding vectors to store
            metadata_list: List of metadata associated with each vector
            
        Returns:
            List of IDs for the stored vectors
            
        Raises:
            VectorOperationError: If vectors cannot be stored
            ValueError: If lengths of vectors and metadata_list don't match
        """
        if len(vectors) != len(metadata_list):
            raise ValueError("Number of vectors and metadata entries must be the same")
        
        try:
            ids = []
            for vector, metadata in zip(vectors, metadata_list):
                vector_id = await self.store_vector(vector, metadata)
                ids.append(vector_id)
            return ids
        except Exception as e:
            raise VectorOperationError(
                f"Failed to batch store vectors: {str(e)}",
                operation="batch_store",
                vector_count=len(vectors)
            ) from e
    
    async def get_vector(self, vector_id: str) -> Tuple[EmbeddingVector, EmbeddingMetadata]:
        """
        Retrieve a vector by its ID.
        
        Args:
            vector_id: The ID of the vector to retrieve
            
        Returns:
            A tuple of (vector, metadata)
            
        Raises:
            VectorOperationError: If the vector cannot be found or retrieved
        """
        try:
            if vector_id not in self._vectors:
                raise KeyError(f"Vector with ID {vector_id} not found")
                
            return self._vectors[vector_id], self._metadata[vector_id]
        except KeyError as e:
            raise VectorOperationError(
                f"Vector not found: {str(e)}",
                operation="get",
                vector_count=1
            ) from e
        except Exception as e:
            raise VectorOperationError(
                f"Failed to retrieve vector: {str(e)}",
                operation="get",
                vector_count=1
            ) from e
    
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by its ID.
        
        Args:
            vector_id: The ID of the vector to delete
            
        Returns:
            True if the vector was deleted, False if it wasn't found
            
        Raises:
            VectorOperationError: If the vector cannot be deleted
        """
        try:
            if vector_id in self._vectors:
                del self._vectors[vector_id]
                del self._metadata[vector_id]
                return True
            return False
        except Exception as e:
            raise VectorOperationError(
                f"Failed to delete vector: {str(e)}",
                operation="delete",
                vector_count=1
            ) from e
    
    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for vectors similar to the query vector.
        
        Args:
            query_vector: The vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1) for results
            filter_criteria: Optional dictionary of metadata key-value pairs to filter by
            
        Returns:
            List of search results sorted by similarity (highest first)
            
        Raises:
            VectorOperationError: If the search fails
        """
        try:
            results = []
            
            for vector_id, vector in self._vectors.items():
                # Skip if the vector doesn't match filter criteria
                if filter_criteria and not self._matches_filter(vector_id, filter_criteria):
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_vector, vector)
                
                # Skip if below threshold
                if similarity < score_threshold:
                    continue
                
                results.append(SearchResult(
                    id=vector_id,
                    score=similarity,
                    metadata=self._metadata[vector_id]
                ))
            
            # Sort by similarity score (highest first)
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Return top results
            return results[:limit]
        except Exception as e:
            raise VectorOperationError(
                f"Failed to search vectors: {str(e)}",
                operation="search"
            ) from e
    
    async def count_vectors(self, filter_criteria: Optional[Dict[str, Any]] = None) -> int:
        """
        Count the number of vectors in the store, optionally filtered.
        
        Args:
            filter_criteria: Optional dictionary of metadata key-value pairs to filter by
            
        Returns:
            The number of matching vectors
            
        Raises:
            VectorOperationError: If the counting operation fails
        """
        try:
            if filter_criteria is None:
                return len(self._vectors)
            
            count = 0
            for vector_id in self._vectors:
                if self._matches_filter(vector_id, filter_criteria):
                    count += 1
            
            return count
        except Exception as e:
            raise VectorOperationError(
                f"Failed to count vectors: {str(e)}",
                operation="count"
            ) from e
    
    async def clear(self) -> None:
        """
        Clear all vectors from the store.
        
        Raises:
            VectorOperationError: If the clear operation fails
        """
        try:
            self._vectors.clear()
            self._metadata.clear()
        except Exception as e:
            raise VectorOperationError(
                f"Failed to clear vector store: {str(e)}",
                operation="clear"
            ) from e
    
    def _cosine_similarity(self, vec1: EmbeddingVector, vec2: EmbeddingVector) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity (0-1)
        """
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        dot_product = np.dot(vec1_array, vec2_array)
        norm_v1 = np.linalg.norm(vec1_array)
        norm_v2 = np.linalg.norm(vec2_array)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        return float(dot_product / (norm_v1 * norm_v2))
    
    def _matches_filter(self, vector_id: str, filter_criteria: Dict[str, Any]) -> bool:
        """
        Check if a vector's metadata matches the filter criteria.
        
        Args:
            vector_id: The ID of the vector to check
            filter_criteria: Dictionary of metadata key-value pairs to match
            
        Returns:
            True if all criteria match, False otherwise
        """
        metadata = self._metadata[vector_id]
        
        # Check top-level metadata fields
        for key, value in filter_criteria.items():
            if key in ["text", "source", "type", "id"]:
                if getattr(metadata, key) != value:
                    return False
        
        # Check additional metadata
        if metadata.additional:
            for key, value in filter_criteria.items():
                if key not in ["text", "source", "type", "id"]:
                    if key not in metadata.additional or metadata.additional[key] != value:
                        return False
        
        return True 