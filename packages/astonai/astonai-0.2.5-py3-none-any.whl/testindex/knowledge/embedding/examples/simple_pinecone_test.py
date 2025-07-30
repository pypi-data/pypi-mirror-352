#!/usr/bin/env python3
"""
Simple test script for Pinecone API using direct calls.
This script doesn't depend on the custom PineconeVectorStore implementation.
"""

import os
import time
import uuid
import json
import asyncio
import numpy as np
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment
PINECONE_API_KEY = os.environ.get("TESTINDEX_PINECONE__API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("TESTINDEX_PINECONE__ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.environ.get("TESTINDEX_PINECONE__INDEX_NAME", "code-embeddings")
PINECONE_NAMESPACE = os.environ.get("TESTINDEX_PINECONE__NAMESPACE", "test-simple")

# Configuration
DIMENSION = 1536  # Updated to match the Pinecone index dimension
NUM_VECTORS = 10  # Small number for quick test
BATCH_SIZE = 5

def generate_random_vectors(num_vectors: int, dimension: int) -> List[np.ndarray]:
    """Generate random unit vectors for testing."""
    vectors = []
    for _ in range(num_vectors):
        vector = np.random.randn(dimension).astype(np.float32)
        # Normalize to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        vectors.append(vector)
    return vectors

async def main():
    """Run a simple test of Pinecone API."""
    try:
        # Check if credentials are available
        if not PINECONE_API_KEY:
            print("ERROR: TESTINDEX_PINECONE__API_KEY not found in environment")
            return
            
        print(f"Using Pinecone:")
        print(f"- Environment: {PINECONE_ENVIRONMENT}")
        print(f"- Index: {PINECONE_INDEX_NAME}")
        print(f"- Namespace: {PINECONE_NAMESPACE}")
        
        # Import here to avoid issues if import fails
        import pinecone
        
        # Initialize Pinecone
        print(f"\nInitializing Pinecone with API version: {pinecone.__version__}")
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # List indexes
        indexes = pc.list_indexes()
        index_names = [index.name for index in indexes]
        print(f"Available indexes: {', '.join(index_names)}")
        
        if PINECONE_INDEX_NAME not in index_names:
            print(f"ERROR: Index '{PINECONE_INDEX_NAME}' not found!")
            return
        
        # Connect to index
        print(f"Connecting to index: {PINECONE_INDEX_NAME}")
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Get index stats
        print("\nIndex stats:")
        stats = index.describe_index_stats()
        print(f"- Dimension: {stats.dimension}")
        print(f"- Total vectors: {stats.total_vector_count}")
        print(f"- Namespaces: {list(stats.namespaces.keys())}")
        
        # Generate test vectors
        print(f"\nGenerating {NUM_VECTORS} test vectors...")
        vectors = generate_random_vectors(NUM_VECTORS, DIMENSION)
        
        # Create metadata for test vectors
        metadata_list = [
            {
                "source_type": "test",
                "source_id": f"test-{i}",
                "content_type": "vector",
                "content": f"Test vector {i}",
                "category": i % 3,
                "timestamp": time.time()
            }
            for i in range(NUM_VECTORS)
        ]
        
        # Generate vector IDs
        vector_ids = [f"test-{uuid.uuid4()}" for _ in range(NUM_VECTORS)]
        
        # Upsert vectors in batches
        print(f"Upserting vectors to namespace: {PINECONE_NAMESPACE}")
        for i in range(0, NUM_VECTORS, BATCH_SIZE):
            end_idx = min(i + BATCH_SIZE, NUM_VECTORS)
            batch_vectors = []
            
            for j in range(i, end_idx):
                # Convert vector to list
                vector_list = vectors[j].tolist()
                batch_vectors.append((vector_ids[j], vector_list, metadata_list[j]))
            
            # Upsert batch
            index.upsert(vectors=batch_vectors, namespace=PINECONE_NAMESPACE)
            print(f"- Upserted batch {i//BATCH_SIZE + 1} with {len(batch_vectors)} vectors")
        
        # Wait a moment for indexing
        print("Waiting for vectors to be indexed...")
        time.sleep(2)
        
        # Query a vector
        print("\nQuerying a vector...")
        query_vector = vectors[0].tolist()
        query_response = index.query(
            vector=query_vector,
            top_k=5,
            namespace=PINECONE_NAMESPACE,
            include_metadata=True
        )
        
        print(f"Query results ({len(query_response.matches)} matches):")
        for i, match in enumerate(query_response.matches):
            print(f"- Match {i+1}: ID={match.id}, Score={match.score:.4f}")
            if match.metadata:
                print(f"  Metadata: {json.dumps(match.metadata, indent=2)}")
        
        # Test with filter
        print("\nQuerying with filter...")
        query_response = index.query(
            vector=query_vector,
            top_k=5,
            namespace=PINECONE_NAMESPACE,
            filter={"category": 1},
            include_metadata=True
        )
        
        print(f"Filtered query results ({len(query_response.matches)} matches):")
        for i, match in enumerate(query_response.matches):
            print(f"- Match {i+1}: ID={match.id}, Score={match.score:.4f}")
        
        # Clean up test vectors
        print(f"\nCleaning up test vectors from namespace: {PINECONE_NAMESPACE}")
        index.delete(ids=vector_ids, namespace=PINECONE_NAMESPACE)
        print("Cleanup complete!")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 