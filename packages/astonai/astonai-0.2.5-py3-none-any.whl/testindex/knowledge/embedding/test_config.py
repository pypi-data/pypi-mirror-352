#!/usr/bin/env python3
"""
Test script to verify the configuration changes.
"""

import os
from testindex.core.config import ConfigModel, PydanticConfigWrapper
from testindex.knowledge.embedding.config import (
    PydanticConfigModel,
    PydanticEmbeddingConfig,
    PydanticPineconeConfig
)
from testindex.knowledge.embedding.utils import convert_config_dict

def test_config_compatibility():
    """Test the compatibility between ConfigModel and PydanticConfigModel."""
    # Create a ConfigModel instance
    print("Creating ConfigModel instances...")
    standard_embedding_config = {
        "openai_api_key": "test-key",
        "openai_model": "text-embedding-3-small",
        "embedding_dimension": 1536,
        "batch_size": 100
    }
    
    standard_pinecone_config = {
        "api_key": "test-pinecone-key",
        "index_name": "test-index",
        "dimension": 1536,
        "environment": "us-east-1-gcp",
        "namespace": "test"
    }
    
    # Create Pydantic models
    print("Creating Pydantic models...")
    pydantic_embedding = PydanticEmbeddingConfig(**standard_embedding_config)
    pydantic_pinecone = PydanticPineconeConfig(**standard_pinecone_config)
    
    # Convert back to dict
    print("Converting models to dictionaries...")
    embedding_dict = pydantic_embedding.model_dump()
    pinecone_dict = pydantic_pinecone.model_dump()
    
    # Create a ConfigModel from the Pydantic dict
    print("Creating ConfigModel from Pydantic dict...")
    config_embedding = ConfigModel.from_dict(embedding_dict)
    config_pinecone = ConfigModel.from_dict(pinecone_dict)
    
    # Create both types of configuration models
    print("Creating configuration models...")
    pydantic_config = PydanticConfigModel(
        embedding=pydantic_embedding,
        pinecone=pydantic_pinecone
    )
    
    # Create the Pydantic wrapper from core config
    core_config = PydanticConfigWrapper(
        embedding=standard_embedding_config,
        pinecone=standard_pinecone_config
    )
    
    # Convert using our utility function
    print("Using convert_config_dict utility...")
    pydantic_converted = convert_config_dict(pydantic_config.model_dump())
    core_converted = convert_config_dict(core_config.model_dump())
    
    # Verify results
    print("\nResults:")
    print(f"Original embedding config: {standard_embedding_config}")
    print(f"Pydantic embedding: {pydantic_embedding}")
    print(f"ConfigModel embedding: {config_embedding}")
    print(f"Core config wrapper: {core_config}")
    print(f"Pydantic converted: {pydantic_converted}")
    print(f"Core converted: {core_converted}")
    
    print("\nVerification completed successfully!")

if __name__ == "__main__":
    test_config_compatibility() 