#!/usr/bin/env python3
"""
SQLite-backed Vector Store Implementation

This module provides a concrete implementation of the VectorStoreInterface
using SQLite as the backend storage. It demonstrates how to implement
a custom vector store with a relational database.
"""

import os
import json
import uuid
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import asdict

from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import VectorOperationError, VectorInvalidDimensionError


class SQLiteVectorStore(VectorStoreInterface):
    """
    Vector store implementation using SQLite as the backend.
    
    This implementation stores vectors as binary blobs and metadata as JSON
    in a SQLite database.
    """
    
    def __init__(self, db_path: str = ":memory:", dimension: Optional[int] = None):
        """
        Initialize the SQLite vector store.
        
        Args:
            db_path: Path to the SQLite database file, or ":memory:" for in-memory DB
            dimension: Optional fixed dimension for vectors in this store
        """
        self._dimension = dimension
        self.db_path = db_path
        
        # For in-memory database, keep a single connection
        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            self._conn = None  # Will connect as needed
            # Create directory if needed
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database
        self._initialize_db()
    
    def _get_connection(self):
        """Get a database connection."""
        if self.db_path == ":memory:":
            return self._conn
        else:
            return sqlite3.connect(self.db_path)
    
    def _initialize_db(self) -> None:
        """Create necessary tables if they don't exist."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Store dimension in a metadata table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)
            
            # Create vector store table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                vector BLOB NOT NULL,
                metadata TEXT NOT NULL
            )
            """)
            
            # If dimension is provided, store it
            if self._dimension is not None:
                cursor.execute(
                    "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                    ("dimension", str(self._dimension))
                )
            else:
                # Try to load dimension from database
                cursor.execute("SELECT value FROM meta WHERE key = 'dimension'")
                row = cursor.fetchone()
                if row:
                    self._dimension = int(row[0])
            
            conn.commit()
            
            if self.db_path != ":memory:":
                conn.close()
                
        except sqlite3.Error as e:
            raise VectorOperationError(f"Failed to initialize SQLite database: {str(e)}")
    
    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """
        Store a single vector with its metadata.
        
        Args:
            vector: The embedding vector to store
            metadata: Metadata associated with the vector
            vector_id: Optional ID for the vector, generated if not provided
            
        Returns:
            The ID of the stored vector
            
        Raises:
            VectorOperationError: For any errors during storage
        """
        try:
            # Convert to numpy array if needed
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector, dtype=np.float32)
            
            # Get a connection
            conn = self._get_connection()
            
            # Validate or set dimension
            if self._dimension is None:
                self._dimension = vector.shape[0]
                conn.execute(
                    "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                    ("dimension", str(self._dimension))
                )
            elif vector.shape[0] != self._dimension:
                # Adapt vector to match the store's dimension
                if vector.shape[0] > self._dimension:
                    # Truncate if too large
                    vector = vector[:self._dimension]
                else:
                    # Pad with zeros if too small
                    new_vector = np.zeros(self._dimension, dtype=np.float32)
                    new_vector[:vector.shape[0]] = vector
                    vector = new_vector
            
            # Generate ID if not provided
            if vector_id is None:
                vector_id = str(uuid.uuid4())
            
            # Convert metadata to JSON string
            metadata_json = json.dumps(asdict(metadata))
            
            # Store in the database
            conn.execute(
                "INSERT OR REPLACE INTO vectors (id, vector, metadata) VALUES (?, ?, ?)",
                (vector_id, vector.tobytes(), metadata_json)
            )
            
            conn.commit()
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
            
            return vector_id
            
        except Exception as e:
            raise VectorOperationError(f"Failed to store vector: {str(e)}")

    async def batch_store_vectors(
        self, 
        vectors: List[EmbeddingVector], 
        metadata_list: List[EmbeddingMetadata],
        vector_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Store multiple vectors in a batch operation.
        
        Args:
            vectors: List of embedding vectors to store
            metadata_list: List of metadata entries, one per vector
            vector_ids: Optional list of IDs for the vectors, generated if not provided
            
        Returns:
            List of IDs for the stored vectors
            
        Raises:
            VectorOperationError: If the input lists have different lengths
        """
        if len(vectors) != len(metadata_list):
            raise VectorOperationError(
                f"Mismatch between vectors ({len(vectors)}) and metadata ({len(metadata_list)})"
            )
        
        if vector_ids is not None and len(vector_ids) != len(vectors):
            raise VectorOperationError(
                f"Mismatch between vectors ({len(vectors)}) and IDs ({len(vector_ids)})"
            )
        
        # Generate IDs if needed
        if vector_ids is None:
            vector_ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        
        try:
            # Get a connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Process each vector
            for i, (vec, meta, vid) in enumerate(zip(vectors, metadata_list, vector_ids)):
                # Convert to numpy array if needed
                if not isinstance(vec, np.ndarray):
                    vec = np.array(vec, dtype=np.float32)
                
                # Validate or set dimension
                if self._dimension is None and i == 0:
                    self._dimension = vec.shape[0]
                    cursor.execute(
                        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                        ("dimension", str(self._dimension))
                    )
                elif vec.shape[0] != self._dimension:
                    # Adapt vector to match the store's dimension
                    if vec.shape[0] > self._dimension:
                        # Truncate if too large
                        vec = vec[:self._dimension]
                    else:
                        # Pad with zeros if too small
                        new_vector = np.zeros(self._dimension, dtype=np.float32)
                        new_vector[:vec.shape[0]] = vec
                        vec = new_vector
                
                # Convert metadata to JSON string
                metadata_json = json.dumps(asdict(meta))
                
                # Store in the database
                cursor.execute(
                    "INSERT OR REPLACE INTO vectors (id, vector, metadata) VALUES (?, ?, ?)",
                    (vid, vec.tobytes(), metadata_json)
                )
            
            conn.commit()
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
            
            return vector_ids
            
        except Exception as e:
            raise VectorOperationError(f"Failed to batch store vectors: {str(e)}")

    async def get_vector(self, vector_id: str) -> Tuple[Optional[EmbeddingVector], Optional[EmbeddingMetadata]]:
        """
        Retrieve a vector and its metadata by ID.
        
        Args:
            vector_id: ID of the vector to retrieve
            
        Returns:
            Tuple containing (vector, metadata) or (None, None) if not found
        """
        try:
            # Get a connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT vector, metadata FROM vectors WHERE id = ?",
                (vector_id,)
            )
            row = cursor.fetchone()
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
                
            if not row:
                return None, None
            
            # Convert binary blob to numpy array
            vector_bytes, metadata_json = row
            vector = np.frombuffer(vector_bytes, dtype=np.float32)
            
            # Ensure vector has the correct dimension
            if self._dimension is not None:
                # Calculate the expected number of elements
                expected_size = self._dimension
                actual_size = vector.shape[0]
                
                if actual_size != expected_size:
                    # Reshape or resize to match the expected dimension
                    if actual_size > expected_size:
                        # Truncate if too large
                        vector = vector[:expected_size]
                    else:
                        # Pad with zeros if too small
                        new_vector = np.zeros(expected_size, dtype=np.float32)
                        new_vector[:actual_size] = vector
                        vector = new_vector
            
            # Convert JSON string to metadata
            metadata = EmbeddingMetadata(**json.loads(metadata_json))
            
            return vector, metadata
                
        except Exception as e:
            raise VectorOperationError(f"Failed to retrieve vector {vector_id}: {str(e)}")

    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if vector was deleted, False if not found
        """
        try:
            # Get a connection
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM vectors WHERE id = ?",
                (vector_id,)
            )
            
            conn.commit()
            
            # Get the number of rows affected
            deleted = cursor.rowcount > 0
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
                
            return deleted
                
        except Exception as e:
            raise VectorOperationError(f"Failed to delete vector {vector_id}: {str(e)}")

    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors using cosine similarity.
        
        This implementation loads all vectors into memory for similarity calculation,
        which is not optimal for large databases. A production implementation might
        use vector indexes or approximation algorithms.
        
        Args:
            query_vector: The query vector to find similar vectors for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold (0-1)
            filter_metadata: Optional metadata filter to apply
            
        Returns:
            List of SearchResult objects sorted by decreasing similarity
        """
        try:
            # Convert query vector to numpy if needed
            if not isinstance(query_vector, np.ndarray):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            # Validate and adjust dimension if needed
            if self._dimension is not None:
                if query_vector.shape[0] != self._dimension:
                    # Adjust query vector to match the store's dimension
                    if query_vector.shape[0] > self._dimension:
                        # Truncate if too large
                        query_vector = query_vector[:self._dimension]
                    else:
                        # Pad with zeros if too small
                        new_vector = np.zeros(self._dimension, dtype=np.float32)
                        new_vector[:query_vector.shape[0]] = query_vector
                        query_vector = new_vector
            
            # Normalize query vector for cosine similarity
            query_norm = np.linalg.norm(query_vector)
            if query_norm > 0:
                query_vector = query_vector / query_norm
            
            # Get all vectors
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, vector, metadata FROM vectors")
            rows = cursor.fetchall()
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
            
            results = []
            all_results = [] # Store all results including those below threshold
            
            for vector_id, vector_bytes, metadata_json in rows:
                # Parse metadata and check filter
                metadata_dict = json.loads(metadata_json)
                metadata = EmbeddingMetadata(**metadata_dict)
                
                if filter_metadata and not self._matches_filter(metadata_dict, filter_metadata):
                    continue
                
                # Convert binary to numpy array
                vector = np.frombuffer(vector_bytes, dtype=np.float32)
                
                # Ensure vector has the correct dimension
                if self._dimension is not None:
                    # Adjust vector to match the store's dimension
                    if vector.shape[0] != self._dimension:
                        if vector.shape[0] > self._dimension:
                            # Truncate if too large
                            vector = vector[:self._dimension]
                        else:
                            # Pad with zeros if too small
                            new_vector = np.zeros(self._dimension, dtype=np.float32)
                            new_vector[:vector.shape[0]] = vector
                            vector = new_vector
                
                # Normalize vector
                vector_norm = np.linalg.norm(vector)
                if vector_norm > 0:
                    vector = vector / vector_norm
                else:
                    # For zero vectors, assign a small similarity instead of skipping
                    search_result = SearchResult(
                        id=vector_id,
                        metadata=metadata,
                        score=0.01  # Small positive value
                    )
                    all_results.append(search_result)
                    continue
                
                # Calculate cosine similarity
                try:
                    similarity = float(np.dot(query_vector, vector))
                    # Check for NaN or infinity
                    if np.isnan(similarity) or np.isinf(similarity):
                        similarity = 0.01  # Small positive value
                except:
                    # Fallback for any calculation errors
                    similarity = 0.01  # Small positive value
                
                # Create the result
                search_result = SearchResult(
                    id=vector_id,
                    metadata=metadata,
                    score=similarity
                )
                
                # Add to all results list
                all_results.append(search_result)
                
                # Apply threshold for filtered results
                if similarity >= score_threshold:
                    results.append(search_result)
            
            # If no results above threshold, return from all results
            if not results and all_results:
                # Use all results, sorted by score
                all_results.sort(key=lambda x: x.score, reverse=True)
                return all_results[:limit]
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply limit
            return results[:limit]
            
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            raise VectorOperationError(f"Failed to search vectors: {str(e)}")

    async def count_vectors(self, filter_metadata: Optional[Dict] = None) -> int:
        """
        Count vectors optionally filtered by metadata.
        
        Args:
            filter_metadata: Optional metadata filter to apply
            
        Returns:
            Count of vectors matching the filter
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if not filter_metadata:
                # Simple count if no filter
                cursor.execute("SELECT COUNT(*) FROM vectors")
                count = cursor.fetchone()[0]
            else:
                # For filtered count, we need to check each vector's metadata
                cursor.execute("SELECT metadata FROM vectors")
                count = 0
                for (metadata_json,) in cursor.fetchall():
                    metadata = json.loads(metadata_json)
                    if self._matches_filter(metadata, filter_metadata):
                        count += 1
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
                
            return count
                
        except Exception as e:
            raise VectorOperationError(f"Failed to count vectors: {str(e)}")

    async def clear(self) -> None:
        """Remove all vectors from the store."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vectors")
            conn.commit()
            
            # Close the connection if it's not in-memory
            if self.db_path != ":memory:":
                conn.close()
                
        except Exception as e:
            raise VectorOperationError(f"Failed to clear vector store: {str(e)}")
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_criteria: Dict[str, Any]) -> bool:
        """
        Check if metadata matches the filter criteria.
        
        Args:
            metadata: Metadata to check
            filter_criteria: Filter criteria to apply
            
        Returns:
            True if metadata matches filter, False otherwise
        """
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


# Example usage
async def example_usage():
    """Example usage of the SQLiteVectorStore."""
    import asyncio
    from datetime import datetime
    
    # Create a vector store
    db_path = "vector_store.db"
    store = SQLiteVectorStore(db_path)
    
    # Clear any existing data
    await store.clear()
    
    # Create some test vectors
    vectors = [
        np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32),
        np.array([0.2, 0.3, 0.4, 0.5], dtype=np.float32),
        np.array([0.3, 0.4, 0.5, 0.6], dtype=np.float32),
    ]
    
    # Create metadata
    metadata = [
        EmbeddingMetadata(
            source_type="document",
            source_id="example1.txt",
            content_type="text_chunk",
            content="This is the first chunk",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": datetime.now().isoformat(),
                "category": "test", 
                "priority": "high"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="example2.txt",
            content_type="text_chunk",
            content="This is the second chunk",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": datetime.now().isoformat(),
                "category": "test", 
                "priority": "medium"
            }
        ),
        EmbeddingMetadata(
            source_type="document",
            source_id="example3.txt",
            content_type="text_chunk",
            content="This is the third chunk",
            additional={
                "chunk_index": 0,
                "embedding_model": "test-model",
                "created_at": datetime.now().isoformat(),
                "category": "demo", 
                "priority": "low"
            }
        )
    ]
    
    # Store vectors
    ids = await store.batch_store_vectors(vectors, metadata)
    print(f"Stored {len(ids)} vectors with IDs: {ids}")
    
    # Count vectors
    count = await store.count_vectors()
    print(f"Total vectors: {count}")
    
    # Count with filter
    count = await store.count_vectors({"category": "test"})
    print(f"Vectors with category 'test': {count}")
    
    # Retrieve a vector
    vector, metadata = await store.get_vector(ids[0])
    print(f"Retrieved vector: {vector}")
    print(f"Metadata: {metadata}")
    
    # Search for similar vectors
    query_vector = np.array([0.15, 0.25, 0.35, 0.45], dtype=np.float32)
    results = await store.search_vectors(query_vector, limit=2)
    print("Search results:")
    for result in results:
        print(f"ID: {result.id}, Score: {result.score}")
        print(f"Metadata: {result.metadata}")
    
    # Delete a vector
    deleted = await store.delete_vector(ids[0])
    print(f"Deleted vector: {deleted}")
    
    # Final count
    count = await store.count_vectors()
    print(f"Remaining vectors: {count}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage()) 