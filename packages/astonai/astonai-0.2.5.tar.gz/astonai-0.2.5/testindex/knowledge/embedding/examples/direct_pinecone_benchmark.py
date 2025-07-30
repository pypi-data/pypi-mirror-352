#!/usr/bin/env python3
"""
Direct Pinecone benchmark without using the custom PineconeVectorStore class.
This uses the official Pinecone Python client directly.
"""

import os
import time
import uuid
import asyncio
import numpy as np
from typing import List, Dict, Any
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment
PINECONE_API_KEY = os.environ.get("TESTINDEX_PINECONE__API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("TESTINDEX_PINECONE__ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.environ.get("TESTINDEX_PINECONE__INDEX_NAME", "code-embeddings")
PINECONE_NAMESPACE = "benchmark-direct"  # Use a separate namespace for direct benchmarks

# Configuration
DIMENSION = 1536  # Match the index dimension
NUM_VECTORS = 100  # Number of vectors to benchmark
BATCH_SIZE = 20  # Size of batches for batch operations

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

def generate_metadata(index: int) -> Dict[str, Any]:
    """Generate test metadata."""
    return {
        "source_type": "benchmark",
        "source_id": f"test-{index}",
        "content_type": "vector",
        "content": f"Test vector {index}",
        "category": index % 5,
        "importance": index % 3,
        "timestamp": time.time()
    }

async def benchmark_insertion(index, vectors, metadata_list, vector_ids):
    """Benchmark vector insertion performance."""
    print("\nBenchmarking insertion...")
    
    # Single insertion
    single_ids = vector_ids[:10]
    single_vectors = vectors[:10]
    single_metadata = metadata_list[:10]
    
    # Benchmark single insertion
    start_time = time.time()
    for i in tqdm(range(10), desc="Single insertion"):
        index.upsert(
            vectors=[(single_ids[i], single_vectors[i].tolist(), single_metadata[i])],
            namespace=PINECONE_NAMESPACE
        )
    single_insert_time = (time.time() - start_time) / 10
    print(f"Average time for single insertion: {single_insert_time:.6f} seconds")

    # Benchmark batch insertion
    start_time = time.time()
    for i in range(0, NUM_VECTORS, BATCH_SIZE):
        end_idx = min(i + BATCH_SIZE, NUM_VECTORS)
        batch_vectors = []
        
        for j in range(i, end_idx):
            batch_vectors.append((
                vector_ids[j], 
                vectors[j].tolist(), 
                metadata_list[j]
            ))
        
        index.upsert(
            vectors=batch_vectors,
            namespace=PINECONE_NAMESPACE
        )
        
    batch_insert_time = (time.time() - start_time) / (NUM_VECTORS / BATCH_SIZE)
    print(f"Average time for batch insertion ({BATCH_SIZE} vectors): {batch_insert_time:.6f} seconds")
    
    return single_insert_time, batch_insert_time

async def benchmark_retrieval(index, vector_ids):
    """Benchmark vector retrieval performance."""
    print("\nBenchmarking retrieval...")
    
    # Sample some vector IDs for retrieval testing
    sample_ids = np.random.choice(vector_ids, 10, replace=False)
    
    # Benchmark retrieval
    start_time = time.time()
    for vector_id in tqdm(sample_ids, desc="Retrieval"):
        response = index.fetch(ids=[vector_id], namespace=PINECONE_NAMESPACE)
        assert vector_id in response.vectors, f"Failed to retrieve vector {vector_id}"
    
    retrieval_time = (time.time() - start_time) / 10
    print(f"Average time for vector retrieval: {retrieval_time:.6f} seconds")
    
    return retrieval_time

async def benchmark_search(index, vectors):
    """Benchmark vector search performance."""
    print("\nBenchmarking similarity search...")
    
    # Random sample of query vectors
    query_indices = np.random.choice(range(len(vectors)), 10)
    query_vectors = [vectors[i] for i in query_indices]
    
    # Search without filter
    start_time = time.time()
    for i, query_vector in enumerate(tqdm(query_vectors, desc="Search")):
        results = index.query(
            namespace=PINECONE_NAMESPACE,
            vector=query_vector.tolist(),
            top_k=10,
            include_metadata=True
        )
    search_time = (time.time() - start_time) / 10
    print(f"Average time for vector search (top 10): {search_time:.6f} seconds")

    # Search with metadata filter
    start_time = time.time()
    for i, query_vector in enumerate(tqdm(query_vectors, desc="Filtered search")):
        category = i % 5
        results = index.query(
            namespace=PINECONE_NAMESPACE,
            vector=query_vector.tolist(),
            top_k=10,
            include_metadata=True,
            filter={"category": category}
        )
    filtered_search_time = (time.time() - start_time) / 10
    print(f"Average time for filtered search: {filtered_search_time:.6f} seconds")
    
    return search_time, filtered_search_time

async def run_benchmark():
    """Run the complete benchmark suite."""
    try:
        # Check if credentials are available
        if not PINECONE_API_KEY:
            print("ERROR: TESTINDEX_PINECONE__API_KEY not found in environment")
            return
            
        # Import Pinecone
        import pinecone
        
        print(f"Starting Direct Pinecone benchmark with {NUM_VECTORS} vectors of dimension {DIMENSION}")
        print(f"Pinecone API version: {pinecone.__version__}")
        print(f"Using index: {PINECONE_INDEX_NAME} with namespace: {PINECONE_NAMESPACE}")
        
        # Initialize Pinecone
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        indexes = pc.list_indexes()
        index_names = [index.name for index in indexes]
        
        if PINECONE_INDEX_NAME not in index_names:
            print(f"ERROR: Pinecone index '{PINECONE_INDEX_NAME}' does not exist")
            return
        
        # Connect to index
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Generate test data
        print(f"Generating {NUM_VECTORS} random test vectors...")
        vectors = generate_random_vectors(NUM_VECTORS, DIMENSION)
        metadata_list = [generate_metadata(i) for i in range(NUM_VECTORS)]
        vector_ids = [f"bench-direct-{uuid.uuid4()}" for _ in range(NUM_VECTORS)]
        
        # Clear existing vectors in the namespace
        print(f"Clearing existing vectors from namespace: {PINECONE_NAMESPACE}...")
        try:
            # Check if namespace exists
            stats = index.describe_index_stats()
            
            if PINECONE_NAMESPACE in stats.namespaces:
                print(f"Namespace '{PINECONE_NAMESPACE}' exists with {stats.namespaces[PINECONE_NAMESPACE].vector_count} vectors - clearing")
                index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
            else:
                print(f"Namespace '{PINECONE_NAMESPACE}' doesn't exist yet - nothing to clear")
                
        except Exception as e:
            print(f"Warning: Error when clearing namespace: {str(e)}")
            # Continue with the benchmark anyway
        
        try:
            # Run benchmark tests
            single_insert, batch_insert = await benchmark_insertion(index, vectors, metadata_list, vector_ids)
            retrieval_time = await benchmark_retrieval(index, vector_ids)
            search_time, filtered_search_time = await benchmark_search(index, vectors)
            
            # Print summary
            print("\n===== BENCHMARK SUMMARY =====")
            print(f"Vector dimension: {DIMENSION}")
            print(f"Number of vectors: {NUM_VECTORS}")
            print(f"Batch size: {BATCH_SIZE}")
            print(f"Single insertion: {single_insert:.6f}s")
            print(f"Batch insertion: {batch_insert:.6f}s per batch")
            print(f"Retrieval: {retrieval_time:.6f}s")
            print(f"Search: {search_time:.6f}s")
            print(f"Filtered search: {filtered_search_time:.6f}s")
            
        finally:
            # Clean up test vectors
            print(f"\nCleaning up test vectors from namespace: {PINECONE_NAMESPACE}...")
            index.delete(delete_all=True, namespace=PINECONE_NAMESPACE)
            print("Cleanup complete!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_benchmark()) 