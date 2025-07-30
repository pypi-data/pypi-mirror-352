#!/usr/bin/env python3
"""
Example demonstrating how to use the core configuration system with PineconeVectorStore.

This example shows:
1. Loading PineconeConfig from the core configuration system
2. Using it with our PineconeVectorStore
3. Basic vector operations (storing, retrieving, searching)
"""

import os
import asyncio
import numpy as np
from dotenv import load_dotenv

from testindex.core.config import PineconeConfig as CorePineconeConfig
from testindex.core.config import ConfigLoader
from testindex.knowledge.embedding.pinecone_store import PineconeVectorStore
from testindex.knowledge.embedding.vector_store import EmbeddingMetadata


async def example_with_core_config():
    """Example using the core configuration system."""
    print("\n--- Example with Core Configuration System ---")
    
    # Load from environment variables using the core ConfigLoader
    # This will use the TI_ prefix for environment variables
    core_config = ConfigLoader.load_config(
        config_class=CorePineconeConfig,
        env_prefix="TI_",
        default_values={
            "index_name": "example-index",
            "namespace": "core-config-example",
            "dimension": 4,  # Small dimension for demonstration
            "metric": "cosine"
        }
    )
    
    print("Core configuration loaded:")
    print(f"- API Key: {'Set' if core_config.api_key else 'Not set'}")
    print(f"- Environment: {core_config.environment}")
    print(f"- Index Name: {core_config.index_name}")
    print(f"- Namespace: {core_config.namespace}")
    print(f"- Dimension: {core_config.dimension}")
    
    # Initialize vector store with core config
    # Our PineconeVectorStore will automatically convert it to the extended config
    vector_store = PineconeVectorStore(core_config)
    
    # Check if we have an API key to proceed with operations
    if not core_config.api_key:
        print("Skipping vector operations as no API key is set")
        return
    
    # Create a test vector and metadata
    vector = np.array([0.1, 0.2, 0.3, 0.4])
    metadata = EmbeddingMetadata(
        source_type="example",
        source_id="core-config-test",
        content_type="vector",
        content="Test vector from core config example",
        additional={
            "example_type": "core_config"
        }
    )
    
    # Store the vector
    vector_id = await vector_store.store_vector(vector, metadata)
    print(f"Stored vector with ID: {vector_id}")
    
    # Retrieve the vector
    retrieved_vector, retrieved_metadata = await vector_store.get_vector(vector_id)
    print("Retrieved vector successfully")
    print(f"Vector values: {retrieved_vector[:2]}... (truncated)")
    print(f"Source type: {retrieved_metadata.source_type}")
    print(f"Content: {retrieved_metadata.content}")
    
    # Search for similar vectors
    search_results = await vector_store.search_vectors(vector, limit=5)
    print(f"Found {len(search_results)} similar vectors")
    
    # Clean up
    await vector_store.delete_vector(vector_id)
    print(f"Deleted vector {vector_id}")


async def main():
    """Run the core config example."""
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Set up a default API key for testing if not in environment
    if not os.environ.get("TI_PINECONE_API_KEY") and os.environ.get("PINECONE_API_KEY"):
        os.environ["TI_PINECONE_API_KEY"] = os.environ.get("PINECONE_API_KEY")
    
    try:
        await example_with_core_config()
    except Exception as e:
        print(f"Error running example: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 