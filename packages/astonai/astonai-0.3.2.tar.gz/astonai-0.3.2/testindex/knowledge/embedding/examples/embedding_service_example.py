#!/usr/bin/env python3
"""
Example script demonstrating how to use the Embedding Service.

This script shows how to:
1. Initialize the embedding service
2. Generate embeddings for code snippets
3. Store embeddings in a vector store
4. Perform similarity searches
5. Work with code chunks
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from testindex.knowledge.embedding.embedding_service import (
    EmbeddingService,
    EmbeddingServiceConfig,
    generate_checksum
)
from testindex.knowledge.embedding.vector_store import EmbeddingMetadata
from testindex.knowledge.embedding.examples.sqlite_vector_store import SQLiteVectorStore
from testindex.preprocessing.chunking.code_chunker import CodeChunk, ChunkType, PythonCodeChunker
from testindex.core.config import ConfigModel

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def example_basic_embedding():
    """Example of basic embedding generation."""
    logger.info("\n=== Basic Embedding Generation ===")
    
    # Initialize configuration
    config = EmbeddingServiceConfig(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        enable_cache=True
    )
    
    # Initialize embedding service
    embedding_service = EmbeddingService(config)
    
    # Generate an embedding for a code snippet
    code_snippet = '''
def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two integers."""
    return a + b
'''
    
    try:
        checksum, embedding = await embedding_service.generate_embedding(code_snippet)
        
        logger.info(f"Generated embedding with {len(embedding)} dimensions")
        logger.info(f"Checksum: {checksum}")
        logger.info(f"First 5 values: {embedding[:5]}")
        
        # Try generating again (should use cache)
        logger.info("Generating again (should use cache)...")
        checksum2, embedding2 = await embedding_service.generate_embedding(code_snippet)
        
        assert checksum == checksum2, "Checksums should match"
        logger.info("Successfully used cache for the second request")
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")


async def example_vector_store_integration():
    """Example of integration with a vector store."""
    logger.info("\n=== Vector Store Integration ===")
    
    # Initialize components
    config = EmbeddingServiceConfig(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        enable_cache=True
    )
    
    # Create an in-memory SQLite vector store
    vector_store = SQLiteVectorStore(":memory:")
    
    # Initialize embedding service with vector store
    embedding_service = EmbeddingService(config, vector_store)
    
    # Sample code snippets
    code_snippets = [
        '''
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b
''',
        '''
def subtract(a: int, b: int) -> int:
    """Subtract b from a and return the result."""
    return a - b
''',
        '''
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the result."""
    return a * b
''',
        '''
def divide(a: int, b: int) -> float:
    """Divide a by b and return the result.
    
    Raises:
        ZeroDivisionError: If b is zero
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b
'''
    ]
    
    # Metadata for each snippet
    metadatas = [
        {"function_name": "add", "module": "math_utils", "complexity": "O(1)"},
        {"function_name": "subtract", "module": "math_utils", "complexity": "O(1)"},
        {"function_name": "multiply", "module": "math_utils", "complexity": "O(1)"},
        {"function_name": "divide", "module": "math_utils", "complexity": "O(1)"}
    ]
    
    try:
        # Generate and store embeddings
        logger.info("Generating and storing embeddings...")
        vector_ids = []
        
        for i, (code, metadata) in enumerate(zip(code_snippets, metadatas)):
            vector_id = await embedding_service.embed_and_store(code, metadata)
            vector_ids.append(vector_id)
            logger.info(f"Stored embedding {i+1}/{len(code_snippets)} with ID: {vector_id}")
        
        # Search for similar code
        logger.info("\nSearching for code similar to 'add two numbers'...")
        query = "function to add two numbers"
        
        # Generate embedding for the query
        _, query_embedding = await embedding_service.generate_embedding(query)
        
        # Search the vector store
        results = await vector_store.search_vectors(query_embedding, limit=2)
        
        # Display results
        logger.info(f"Found {len(results)} similar functions:")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: Score={result.score:.4f}")
            logger.info(f"Function: {result.metadata.additional.get('function_name')}")
            logger.info(f"Content sample: {result.metadata.content[:100]}...")
            logger.info("---")
        
        # Search with metadata filter
        logger.info("\nSearching with metadata filter...")
        filter_results = await vector_store.search_vectors(
            query_embedding, 
            filter_metadata={"function_name": "divide"}
        )
        
        if filter_results:
            logger.info(f"Found result with filter: {filter_results[0].metadata.additional.get('function_name')}")
            logger.info(f"Score: {filter_results[0].score:.4f}")
        else:
            logger.info("No results found with filter")
            
        # Get vector count
        count = await vector_store.count_vectors()
        logger.info(f"\nTotal vectors in store: {count}")
        
    except Exception as e:
        logger.error(f"Error in vector store example: {str(e)}")


async def example_code_chunk_processing():
    """Example of processing code chunks."""
    logger.info("\n=== Code Chunk Processing ===")
    
    # Create a temporary file with Python code
    temp_file = Path("temp_example.py")
    
    try:
        # Write sample Python code to the file
        with open(temp_file, "w") as f:
            f.write('''
# Sample Python module for testing code chunking
import os
import sys
from typing import List, Dict, Optional

def process_data(data: List[str]) -> Dict[str, int]:
    """Process a list of strings and return word counts."""
    result = {}
    for item in data:
        words = item.split()
        for word in words:
            result[word] = result.get(word, 0) + 1
    return result

class DataProcessor:
    """Class for processing text data."""
    
    def __init__(self, case_sensitive: bool = True):
        """Initialize the data processor.
        
        Args:
            case_sensitive: Whether to treat words as case-sensitive
        """
        self.case_sensitive = case_sensitive
        self.processed_items = 0
    
    def process(self, data: List[str]) -> Dict[str, int]:
        """Process a list of strings and return word counts."""
        result = {}
        for item in data:
            if not self.case_sensitive:
                item = item.lower()
            
            words = item.split()
            for word in words:
                result[word] = result.get(word, 0) + 1
            
            self.processed_items += 1
        
        return result

# Main execution
if __name__ == "__main__":
    test_data = [
        "This is a test",
        "This is another test",
        "Testing code chunking"
    ]
    
    # Process with function
    result1 = process_data(test_data)
    print("Function result:", result1)
    
    # Process with class
    processor = DataProcessor(case_sensitive=False)
    result2 = processor.process(test_data)
    print("Class result:", result2)
''')
        
        # Initialize components
        config = ConfigModel()
        chunker = PythonCodeChunker(config)
        
        # Initialize embedding service with vector store
        embedding_config = EmbeddingServiceConfig(
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            enable_cache=True
        )
        vector_store = SQLiteVectorStore(":memory:")
        embedding_service = EmbeddingService(embedding_config, vector_store)
        
        # Chunk the Python file
        logger.info(f"Chunking file: {temp_file}")
        chunks = chunker.chunk_file(temp_file)
        
        logger.info(f"Generated {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            logger.info(f"Chunk {i+1}: {chunk.chunk_type.value} - {chunk.name}")
        
        # Generate embeddings for each chunk
        logger.info("\nGenerating embeddings for chunks...")
        
        for chunk in chunks:
            # Skip the module-level chunk as it contains everything
            if chunk.chunk_type == ChunkType.MODULE:
                continue
                
            # Create a mock Neo4j node ID (in a real scenario, this would come from Neo4j)
            mock_node_id = f"node-{generate_checksum(chunk.name)[:8]}"
            
            try:
                vector_id = await embedding_service.embed_chunk(chunk, mock_node_id)
                logger.info(f"Generated embedding for {chunk.chunk_type.value} '{chunk.name}', ID: {vector_id}")
            except Exception as e:
                logger.error(f"Error generating embedding for chunk {chunk.name}: {str(e)}")
        
        # Search for chunks related to "word counting"
        logger.info("\nSearching for chunks related to 'word counting'...")
        
        query = "function that counts words in text"
        _, query_embedding = await embedding_service.generate_embedding(query)
        
        results = await vector_store.search_vectors(query_embedding, limit=2)
        
        if results:
            logger.info(f"Found {len(results)} relevant chunks:")
            for i, result in enumerate(results):
                logger.info(f"Result {i+1}: Score={result.score:.4f}")
                logger.info(f"Type: {result.metadata.additional.get('code_type')}")
                logger.info(f"Name: {result.metadata.additional.get('name')}")
                logger.info(f"Content sample: {result.metadata.content[:100]}...")
                logger.info("---")
        else:
            logger.info("No relevant chunks found")
    
    finally:
        # Clean up temporary file
        if temp_file.exists():
            temp_file.unlink()


async def main():
    """Run all examples."""
    try:
        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY environment variable not set. Examples will fail.")
            logger.info("Please set the OPENAI_API_KEY environment variable and try again.")
            return
            
        # Run examples
        await example_basic_embedding()
        await example_vector_store_integration()
        await example_code_chunk_processing()
        
    except Exception as e:
        logger.error(f"Error in examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 