#!/usr/bin/env python3
"""
Script to test the current Pinecone API fetch response format.
"""

import os
import time
import json
import asyncio
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Pinecone credentials from environment
PINECONE_API_KEY = os.environ.get("TESTINDEX_PINECONE__API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("TESTINDEX_PINECONE__ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.environ.get("TESTINDEX_PINECONE__INDEX_NAME", "code-embeddings")
PINECONE_NAMESPACE = os.environ.get("TESTINDEX_PINECONE__NAMESPACE", "test-api")

async def main():
    """Test the Pinecone API response format."""
    try:
        # Import here to avoid issues if import fails
        import pinecone
        
        # Initialize Pinecone
        print(f"Initializing Pinecone with API version: {pinecone.__version__}")
        pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
        
        # Connect to index
        print(f"Connecting to index: {PINECONE_INDEX_NAME}")
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Create test vector
        vector_id = f"test-vector-{int(time.time())}"
        vector = np.random.randn(1536).astype(np.float32)
        vector = vector / np.linalg.norm(vector)  # Normalize
        vector_list = vector.tolist()
        
        metadata = {
            "source_type": "test",
            "source_id": "test-id",
            "content_type": "vector",
            "content": "Test vector",
            "timestamp": time.time()
        }
        
        # Insert test vector
        print(f"Inserting test vector with ID: {vector_id}")
        index.upsert(
            vectors=[(vector_id, vector_list, metadata)],
            namespace=PINECONE_NAMESPACE
        )
        
        # Wait for indexing
        time.sleep(1)
        
        # Fetch the vector
        print("\nFetching vector and examining response structure:")
        response = index.fetch(ids=[vector_id], namespace=PINECONE_NAMESPACE)
        
        # Print response structure
        print(f"\nResponse type: {type(response)}")
        print(f"Response dir: {dir(response)}")
        print(f"Response: {response}")
        
        # Check if it's a dict-like object
        if hasattr(response, "items"):
            print("\nResponse as dict:")
            for key, value in response.items():
                print(f"Key: {key}, Value type: {type(value)}")
        
        # Check for vectors attribute
        if hasattr(response, "vectors"):
            print("\nExamining 'vectors' attribute:")
            print(f"Type: {type(response.vectors)}")
            if vector_id in response.vectors:
                print(f"Found vector_id in response.vectors")
                vector_data = response.vectors[vector_id]
                print(f"Vector data type: {type(vector_data)}")
                print(f"Vector data dir: {dir(vector_data)}")
                print(f"Vector data: {vector_data}")
        
        # Cleanup
        print("\nCleaning up test vector")
        index.delete(ids=[vector_id], namespace=PINECONE_NAMESPACE)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 