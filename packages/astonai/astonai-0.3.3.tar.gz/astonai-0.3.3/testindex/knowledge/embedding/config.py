"""
Pydantic configuration models for the embedding and vector store modules.

This file defines Pydantic models for configuration that can be used alongside 
the existing ConfigModel class from testindex.core.config.
"""
# TODO: [KNW-23] Refactor to use core PydanticConfigWrapper directly
# This will reduce duplication and centralize config schema
# Planned for after Week 5 integration

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

# Define Pydantic models for configuration

class PydanticEmbeddingConfig(BaseModel):
    """Pydantic configuration for embedding services."""
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    openai_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    batch_size: int = 100
    retry_attempts: int = 3
    
    @classmethod
    def from_config_model(cls, config_dict: Dict[str, Any]) -> 'PydanticEmbeddingConfig':
        """Convert ConfigModel dict to PydanticEmbeddingConfig."""
        return cls(**config_dict)


class PydanticPineconeConfig(BaseModel):
    """Pydantic configuration for Pinecone vector database."""
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: str = "code-embeddings"
    namespace: str = "testindex"
    dimension: int = 1536
    project_id: Optional[str] = None
    metric: str = "cosine"
    pod_type: Optional[str] = None
    pods: int = 1
    replicas: int = 1
    serverless_cloud: Optional[str] = None
    serverless_region: Optional[str] = None
    connection_timeout: int = 10
    request_timeout: int = 60
    pooling_maxsize: int = 100
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: float = 1.0
    metadata_sharding: bool = False
    rate_limit_per_minute: int = 100
    
    @classmethod
    def from_config_model(cls, config_dict: Dict[str, Any]) -> 'PydanticPineconeConfig':
        """Convert ConfigModel dict to PydanticPineconeConfig."""
        return cls(**config_dict)


class PydanticConfigModel(BaseModel):
    """Root configuration model using Pydantic."""
    embedding: PydanticEmbeddingConfig = Field(default_factory=PydanticEmbeddingConfig)
    pinecone: PydanticPineconeConfig = Field(default_factory=PydanticPineconeConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PydanticConfigModel':
        """Create PydanticConfigModel from a dictionary."""
        config = {}
        if 'embedding' in config_dict:
            config['embedding'] = PydanticEmbeddingConfig.from_config_model(config_dict['embedding'])
        if 'pinecone' in config_dict:
            config['pinecone'] = PydanticPineconeConfig.from_config_model(config_dict['pinecone'])
        return cls(**config) 