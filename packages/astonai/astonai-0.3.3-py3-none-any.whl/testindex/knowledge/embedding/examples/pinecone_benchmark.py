#!/usr/bin/env python3
"""
Benchmark for Pinecone Vector Store integration.

This script benchmarks various operations for the Pinecone vector store:
- Insertion (single and batch)
- Retrieval 
- Similarity search
- Metadata filtering
"""

import os
import time
import asyncio
import numpy as np
from dotenv import load_dotenv
from tqdm import tqdm

from testindex.core.config import PydanticConfigWrapper
from testindex.knowledge.embedding.pinecone_store import PineconeVectorStore
from testindex.knowledge.embedding.config import PydanticPineconeConfig
from testindex.knowledge.embedding.utils import generate_random_vectors, convert_config_dict
from testindex.knowledge.embedding.vector_store import EmbeddingMetadata

# Load environment variables
load_dotenv()

# Configuration
DIMENSION = 1536  # Updated to match the Pinecone index dimension
NUM_VECTORS = 100  # Reduced for faster benchmarking
BATCH_SIZE = 20
INDEX_NAME = "benchmark-test"
NAMESPACE = "benchmark"


async def benchmark_insertion(vector_store, vectors, metadata_list):
    """Benchmark vector insertion performance."""
    print("\nBenchmarking insertion...")
    
    # Single insertion
    start_time = time.time()
    for i in tqdm(range(10), desc="Single insertion"):
        await vector_store.store_vector(
            vector_id=f"single-{i}",
            vector=vectors[i],
            metadata=metadata_list[i]
        )
    single_insert_time = (time.time() - start_time) / 10
    print(f"Average time for single insertion: {single_insert_time:.6f} seconds")

    # Batch insertion
    vector_ids = [f"batch-{i}" for i in range(NUM_VECTORS)]
    start_time = time.time()
    for i in range(0, NUM_VECTORS, BATCH_SIZE):
        end_idx = min(i + BATCH_SIZE, NUM_VECTORS)
        batch_ids = vector_ids[i:end_idx]
        batch_vectors = vectors[i:end_idx]
        batch_metadata = metadata_list[i:end_idx]
        
        await vector_store.batch_store_vectors(
            vector_ids=batch_ids,
            vectors=batch_vectors,
            metadata_list=batch_metadata
        )
    batch_insert_time = (time.time() - start_time) / (NUM_VECTORS / BATCH_SIZE)
    print(f"Average time for batch insertion ({BATCH_SIZE} vectors): {batch_insert_time:.6f} seconds")
    
    return single_insert_time, batch_insert_time


async def benchmark_retrieval(vector_store, vector_ids):
    """Benchmark vector retrieval performance."""
    print("\nBenchmarking retrieval...")
    
    # Single retrieval
    sample_ids = np.random.choice(vector_ids, 10, replace=False)
    start_time = time.time()
    for vector_id in tqdm(sample_ids, desc="Retrieval"):
        result = await vector_store.get_vector(vector_id)
        assert result is not None, f"Failed to retrieve vector {vector_id}"
    retrieval_time = (time.time() - start_time) / 10
    print(f"Average time for vector retrieval: {retrieval_time:.6f} seconds")
    
    return retrieval_time


async def benchmark_search(vector_store, vectors):
    """Benchmark vector search performance."""
    print("\nBenchmarking similarity search...")
    
    # Random sample of query vectors
    query_vectors = np.random.choice(range(len(vectors)), 10)
    
    # Search without filter
    start_time = time.time()
    for i in tqdm(query_vectors, desc="Search"):
        results = await vector_store.search_vectors(
            query_vector=vectors[i],
            limit=10
        )
        # Note: With random vectors, results may be empty, which is normal
    search_time = (time.time() - start_time) / 10
    print(f"Average time for vector search (top 10): {search_time:.6f} seconds")

    # Search with metadata filter
    start_time = time.time()
    for i in tqdm(query_vectors, desc="Filtered search"):
        category = i % 5
        results = await vector_store.search_vectors(
            query_vector=vectors[i],
            limit=10,
            filter_metadata={"category": category}
        )
        # Note: With filters, results may be empty, which is expected
    filtered_search_time = (time.time() - start_time) / 10
    print(f"Average time for filtered search: {filtered_search_time:.6f} seconds")
    
    return search_time, filtered_search_time


async def run_benchmark():
    """Run the complete benchmark suite."""
    print(f"Starting Pinecone benchmark with {NUM_VECTORS} vectors of dimension {DIMENSION}")
    
    # TODO: [KNW-23] Refactor to use core PydanticConfigWrapper directly
    # This will reduce duplication and centralize config schema
    # Planned for after Week 5 integration
    
    # Use PydanticPineconeConfig for configuration
    config = PydanticPineconeConfig(
        api_key=os.environ.get("TESTINDEX_PINECONE__API_KEY"),
        index_name=os.environ.get("TESTINDEX_PINECONE__INDEX_NAME", "code-embeddings"),
        dimension=DIMENSION,
        environment=os.environ.get("TESTINDEX_PINECONE__ENVIRONMENT", "us-east-1"),
        namespace=os.environ.get("TESTINDEX_PINECONE__NAMESPACE", "benchmark")
    )
    
    if not config.api_key:
        print("ERROR: TESTINDEX_PINECONE__API_KEY not found in environment")
        return
        
    print(f"Using Pinecone index: {config.index_name} in namespace: {config.namespace}")
    
    # Convert the config to a format compatible with PineconeVectorStore
    config_dict = convert_config_dict(config.model_dump())
    vector_store = PineconeVectorStore(config_dict)
    
    # Generate random test data
    print(f"Generating {NUM_VECTORS} random test vectors...")
    vectors = generate_random_vectors(NUM_VECTORS, DIMENSION)
    metadata_list = [
        EmbeddingMetadata(
            source_type="benchmark",
            source_id=f"test-{i}",
            content_type="vector",
            content=f"Test vector {i}",
            additional={
                "category": i % 5,
                "importance": i % 3,
                "timestamp": time.time()
            }
        )
        for i in range(NUM_VECTORS)
    ]
    vector_ids = [f"bench-{i}" for i in range(NUM_VECTORS)]
    
    # Clear the vector store before benchmarking
    print(f"Clearing existing vectors from namespace: {config.namespace}...")
    await vector_store.clear()
    
    try:
        # Run benchmark tests
        single_insert, batch_insert = await benchmark_insertion(vector_store, vectors, metadata_list)
        retrieval_time = await benchmark_retrieval(vector_store, vector_ids)
        search_time, filtered_search_time = await benchmark_search(vector_store, vectors)
        
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
        # Clean up (optional)
        if os.environ.get("BENCHMARK_CLEANUP", "true").lower() == "true":
            print(f"\nCleaning up test vectors from namespace: {config.namespace}...")
            await vector_store.clear()
        
        # Close connections
        await vector_store.close()


if __name__ == "__main__":
    asyncio.run(run_benchmark()) 