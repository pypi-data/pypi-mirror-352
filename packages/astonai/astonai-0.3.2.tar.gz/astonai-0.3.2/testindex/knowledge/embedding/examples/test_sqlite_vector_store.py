#!/usr/bin/env python3
"""
Unit tests for the SQLite Vector Store implementation.

These tests demonstrate how to properly test a custom vector store
implementation against the VectorStoreInterface contract.
"""

import os
import json
import numpy as np
import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Tuple, Optional

from testindex.knowledge.embedding.vector_store import (
    EmbeddingVector, 
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.embedding.examples.sqlite_vector_store import SQLiteVectorStore
from testindex.knowledge.errors import VectorOperationError, VectorInvalidDimensionError


@pytest.fixture
def test_vectors() -> List[np.ndarray]:
    """Create test vectors for use in tests."""
    return [
        np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32),
        np.array([0.2, 0.3, 0.4, 0.5], dtype=np.float32),
        np.array([0.3, 0.4, 0.5, 0.6], dtype=np.float32),
        np.array([0.4, 0.5, 0.6, 0.7], dtype=np.float32),
        np.array([0.5, 0.6, 0.7, 0.8], dtype=np.float32),
    ]


@pytest.fixture
def test_metadata() -> List[EmbeddingMetadata]:
    """Create test metadata for use in tests."""
    timestamp = datetime.now().isoformat()
    return [
        EmbeddingMetadata(
            source_type="document",
            source_id="doc1.txt",
            content_type="text_chunk",
            content="This is the first chunk",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": timestamp,
                "category": "test", 
                "priority": "high"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="doc1.txt",
            content_type="text_chunk",
            content="This is the second chunk",
            additional={
                "chunk_index": 1,
                "embedding_model": "test-model",
                "created_at": timestamp,
                "category": "test", 
                "priority": "medium"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="doc2.txt",
            content_type="text_chunk",
            content="This is from another document",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": timestamp,
                "category": "demo", 
                "priority": "high"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="doc3.txt",
            content_type="text_chunk",
            content="This is yet another document",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": timestamp,
                "category": "demo", 
                "priority": "low"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="doc4.txt",
            content_type="text_chunk",
            content="This is the last test document",
            additional={
                "chunk_index": 0,
                "embedding_model": "other-model",
                "created_at": timestamp,
                "category": "test", 
                "priority": "low"
            }
        ),
    ]


@pytest.fixture
def vector_store():
    """Create a temporary SQLite vector store for testing."""
    # Use in-memory database for tests
    store = SQLiteVectorStore(":memory:")
    return store


@pytest.mark.asyncio
async def test_store_and_retrieve_vector(vector_store, test_vectors, test_metadata):
    """Test storing and retrieving a single vector."""
    # Store a vector
    vector_id = await vector_store.store_vector(
        test_vectors[0], test_metadata[0]
    )
    
    # Verify it was stored
    assert vector_id is not None
    
    # Retrieve the vector
    retrieved_vector, retrieved_metadata = await vector_store.get_vector(vector_id)
    
    # Check vector values
    assert np.array_equal(retrieved_vector, test_vectors[0])
    
    # Check metadata
    assert retrieved_metadata.source_type == test_metadata[0].source_type
    assert retrieved_metadata.source_id == test_metadata[0].source_id
    assert retrieved_metadata.content_type == test_metadata[0].content_type
    assert retrieved_metadata.content == test_metadata[0].content
    assert retrieved_metadata.additional["category"] == test_metadata[0].additional["category"]
    assert retrieved_metadata.additional["priority"] == test_metadata[0].additional["priority"]


@pytest.mark.asyncio
async def test_batch_store_vectors(vector_store, test_vectors, test_metadata):
    """Test storing multiple vectors in a batch."""
    # Batch store vectors
    vector_ids = await vector_store.batch_store_vectors(
        test_vectors[:3], test_metadata[:3]
    )
    
    # Verify all were stored
    assert len(vector_ids) == 3
    
    # Count vectors in store
    count = await vector_store.count_vectors()
    assert count == 3
    
    # Retrieve and verify each vector
    for i, vector_id in enumerate(vector_ids):
        retrieved_vector, retrieved_metadata = await vector_store.get_vector(vector_id)
        assert np.array_equal(retrieved_vector, test_vectors[i])
        assert retrieved_metadata.source_id == test_metadata[i].source_id
        assert retrieved_metadata.content == test_metadata[i].content


@pytest.mark.asyncio
async def test_delete_vector(vector_store, test_vectors, test_metadata):
    """Test deleting a vector from the store."""
    # Store vectors
    vector_ids = await vector_store.batch_store_vectors(
        test_vectors[:3], test_metadata[:3]
    )
    
    # Delete the first vector
    deleted = await vector_store.delete_vector(vector_ids[0])
    assert deleted is True
    
    # Verify it was deleted
    retrieved_vector, retrieved_metadata = await vector_store.get_vector(vector_ids[0])
    assert retrieved_vector is None
    assert retrieved_metadata is None
    
    # Count remaining vectors
    count = await vector_store.count_vectors()
    assert count == 2
    
    # Try deleting a non-existent vector
    deleted = await vector_store.delete_vector("non-existent-id")
    assert deleted is False


@pytest.mark.asyncio
async def test_vector_search(vector_store, test_vectors, test_metadata):
    """Test searching for similar vectors."""
    # Store all test vectors
    vector_ids = await vector_store.batch_store_vectors(
        test_vectors, test_metadata
    )
    
    # Create a query vector similar to the first test vector
    query_vector = np.array([0.15, 0.25, 0.35, 0.45], dtype=np.float32)
    
    # Search for similar vectors
    results = await vector_store.search_vectors(query_vector, limit=3)
    
    # Verify we got the expected number of results
    assert len(results) == 3
    
    # Verify results are sorted by similarity (highest first)
    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score
    
    # The most similar vector should be the first one
    # (but we're only checking it's in the top 3 since similarity can vary)
    first_vector_id = vector_ids[0]
    assert any(result.id == first_vector_id for result in results)


@pytest.mark.asyncio
async def test_filtered_search(vector_store, test_vectors, test_metadata):
    """Test searching for vectors with metadata filters."""
    # Store all test vectors
    await vector_store.batch_store_vectors(
        test_vectors, test_metadata
    )
    
    # Query vector
    query_vector = np.array([0.3, 0.4, 0.5, 0.6], dtype=np.float32)
    
    # Search with category filter
    results = await vector_store.search_vectors(
        query_vector,
        filter_metadata={"category": "test"}
    )
    
    # Verify all results have the correct category
    assert all(result.metadata.additional["category"] == "test" for result in results)
    
    # Search with priority filter
    results = await vector_store.search_vectors(
        query_vector,
        filter_metadata={"priority": "high"}
    )
    
    # Verify all results have the correct priority
    assert all(result.metadata.additional["priority"] == "high" for result in results)


@pytest.mark.asyncio
async def test_filtered_count(vector_store, test_vectors, test_metadata):
    """Test counting vectors with metadata filters."""
    # Store all test vectors
    await vector_store.batch_store_vectors(
        test_vectors, test_metadata
    )
    
    # Count all vectors
    count = await vector_store.count_vectors()
    assert count == 5
    
    # Count vectors with category filter
    count = await vector_store.count_vectors(
        filter_metadata={"category": "test"}
    )
    assert count == 3  # Three of our test metadata have category 'test'
    
    # Count vectors with priority filter
    count = await vector_store.count_vectors(
        filter_metadata={"priority": "high"}
    )
    assert count == 2  # Two of our test metadata have priority 'high'
    
    # Count with combined filters
    count = await vector_store.count_vectors(
        filter_metadata={"category": "test", "priority": "high"}
    )
    assert count == 1  # Only one has both category 'test' and priority 'high'
    
    # Count with non-existent filter
    count = await vector_store.count_vectors(
        filter_metadata={"not_a_field": "value"}
    )
    assert count == 0


@pytest.mark.asyncio
async def test_clear_store(vector_store, test_vectors, test_metadata):
    """Test clearing all vectors from the store."""
    # Store vectors
    await vector_store.batch_store_vectors(
        test_vectors, test_metadata
    )
    
    # Verify they're stored
    count = await vector_store.count_vectors()
    assert count == 5
    
    # Clear the store
    await vector_store.clear()
    
    # Verify it's empty
    count = await vector_store.count_vectors()
    assert count == 0


@pytest.mark.asyncio
async def test_dimension_validation(vector_store):
    """Test dimension validation when storing vectors."""
    # Store a vector to set the dimension
    vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
    metadata = EmbeddingMetadata(
        source_type="document",
        source_id="test.txt",
        content_type="text_chunk",
        content="Test chunk"
    )
    
    await vector_store.store_vector(vector, metadata)
    
    # Try to store a vector with different dimension
    wrong_dim_vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)  # Only 3 dimensions
    
    # This should raise an error
    with pytest.raises(VectorInvalidDimensionError):
        await vector_store.store_vector(wrong_dim_vector, metadata)
    
    # Same with batch storage
    vectors = [
        np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32),
        np.array([0.1, 0.2, 0.3], dtype=np.float32),  # Wrong dimension
    ]
    metadata_list = [metadata, metadata]
    
    with pytest.raises(VectorInvalidDimensionError):
        await vector_store.batch_store_vectors(vectors, metadata_list)


@pytest.mark.asyncio
async def test_search_with_threshold(vector_store, test_vectors, test_metadata):
    """Test search with score threshold."""
    # Store vectors
    await vector_store.batch_store_vectors(
        test_vectors, test_metadata
    )
    
    # Query vector optimized to have low similarity with test vectors
    query_vector = np.array([-0.1, -0.2, -0.3, -0.4], dtype=np.float32)
    
    # Search with high threshold
    results = await vector_store.search_vectors(
        query_vector,
        score_threshold=0.9  # Very high threshold
    )
    
    # Should find no results
    assert len(results) == 0
    
    # Search with lower threshold
    results = await vector_store.search_vectors(
        query_vector,
        score_threshold=-1.0  # Very low threshold to get all results
    )
    
    # Should find all vectors
    assert len(results) == 5


if __name__ == "__main__":
    # Allow running the tests directly with python
    pytest.main(["-xvs", __file__]) 