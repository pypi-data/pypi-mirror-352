#!/usr/bin/env python3
"""
Interface and data classes for vector store implementations.
Provides a common interface for different vector store backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# Type alias for embedding vectors
EmbeddingVector = Union[List[float], np.ndarray]


@dataclass
class EmbeddingMetadata:
    """Metadata associated with an embedding vector."""
    
    # Source information
    source_type: str  # e.g., "code", "doc", "test", etc.
    source_id: str  # identifier for the source
    
    # Content information
    content_type: str  # e.g., "function", "class", "comment", etc.
    content: str  # the actual text content
    
    # Additional metadata as a flexible dictionary
    additional: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Result of a vector search operation."""
    
    # ID of the matching vector
    id: str
    
    # Similarity score (higher is more similar)
    score: float
    
    # Associated metadata
    metadata: EmbeddingMetadata


class VectorStoreInterface(ABC):
    """
    Abstract interface for vector store implementations.
    All vector store backends should implement this interface.
    """
    
    @abstractmethod
    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """
        Store a single vector with its metadata.
        
        Args:
            vector: The embedding vector to store
            metadata: Metadata associated with the vector
            vector_id: Optional ID for the vector
            
        Returns:
            The ID of the stored vector
        """
        pass
    
    @abstractmethod
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
            vector_ids: Optional list of IDs for the vectors
            
        Returns:
            List of IDs for the stored vectors
        """
        pass
    
    @abstractmethod
    async def get_vector(self, vector_id: str) -> Tuple[Optional[EmbeddingVector], Optional[EmbeddingMetadata]]:
        """
        Retrieve a vector and its metadata by ID.
        
        Args:
            vector_id: The ID of the vector to retrieve
            
        Returns:
            A tuple of (vector, metadata) if found, or (None, None) if not found
        """
        pass
    
    @abstractmethod
    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector and its metadata by ID.
        
        Args:
            vector_id: The ID of the vector to delete
            
        Returns:
            True if the vector was deleted, False if it wasn't found
        """
        pass
    
    @abstractmethod
    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filter_metadata: Optional metadata filter criteria
            
        Returns:
            List of SearchResult objects ordered by similarity (highest first)
        """
        pass
    
    @abstractmethod
    async def count_vectors(self, filter_metadata: Optional[Dict] = None) -> int:
        """
        Count the number of vectors in the store, optionally filtered by metadata.
        
        Args:
            filter_metadata: Optional metadata filter criteria
            
        Returns:
            The count of vectors matching the filter (or total count if no filter)
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """
        Clear all vectors and metadata from the store.
        """
        pass
        
    async def close(self) -> None:
        """
        Close any open connections or resources.
        Default implementation does nothing.
        Override this method for stores that need to clean up resources.
        """
        pass 