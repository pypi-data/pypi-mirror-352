#!/usr/bin/env python3
"""
Pinecone Vector Store Implementation

This module provides a production-grade implementation of the VectorStoreInterface
using Pinecone as the backend. Pinecone is a fully managed vector database
optimized for similarity search at scale.
"""

import os
import json
import time
import uuid
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from dataclasses import asdict, dataclass, field
from datetime import datetime

import numpy as np
import aiohttp
import pinecone
from pinecone import Pinecone, ServerlessSpec, PodSpec

from testindex.core.config import ConfigModel, PydanticConfigWrapper
from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import (
    VectorOperationError, 
    VectorInvalidDimensionError,
    BatchOperationError
)

# Configure logging
logger = logging.getLogger(__name__)

# TODO: [KNW-23] Refactor to use core PydanticConfigWrapper directly
# This will reduce duplication and centralize config schema
# Planned for after Week 5 integration
@dataclass
class PineconeConfig(ConfigModel):
    """Configuration for Pinecone vector store."""
    
    # API Configuration
    api_key: str
    
    # Index Configuration
    index_name: str
    dimension: int
    
    # Parameters with defaults
    environment: str = "gcp-starter"
    project_id: Optional[str] = None
    metric: str = "cosine"
    
    # Infrastructure Configuration
    pod_type: Optional[str] = None  # e.g., "p1.x1", "s1.x1"
    pods: int = 1
    replicas: int = 1
    serverless_cloud: Optional[str] = None  # e.g., "aws", "gcp", "azure"
    serverless_region: Optional[str] = None  # e.g., "us-west-2"
    
    # Connection Configuration
    connection_timeout: int = 10
    request_timeout: int = 60
    pooling_maxsize: int = 100
    
    # Operation Configuration
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Metadata Configuration
    metadata_sharding: bool = False
    namespace: str = ""
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    
    @classmethod
    def from_environment(cls) -> 'PineconeConfig':
        """Create configuration from environment variables."""
        return cls(
            api_key=os.environ.get("PINECONE_API_KEY", ""),
            index_name=os.environ.get("PINECONE_INDEX_NAME", "knowledge-index"),
            dimension=int(os.environ.get("PINECONE_DIMENSION", "1536")),
            environment=os.environ.get("PINECONE_ENVIRONMENT", "gcp-starter"),
            project_id=os.environ.get("PINECONE_PROJECT_ID"),
            metric=os.environ.get("PINECONE_METRIC", "cosine"),
            pod_type=os.environ.get("PINECONE_POD_TYPE"),
            pods=int(os.environ.get("PINECONE_PODS", "1")),
            replicas=int(os.environ.get("PINECONE_REPLICAS", "1")),
            serverless_cloud=os.environ.get("PINECONE_SERVERLESS_CLOUD"),
            serverless_region=os.environ.get("PINECONE_SERVERLESS_REGION"),
            connection_timeout=int(os.environ.get("PINECONE_CONNECTION_TIMEOUT", "10")),
            request_timeout=int(os.environ.get("PINECONE_REQUEST_TIMEOUT", "60")),
            pooling_maxsize=int(os.environ.get("PINECONE_POOLING_MAXSIZE", "100")),
            batch_size=int(os.environ.get("PINECONE_BATCH_SIZE", "100")),
            max_retries=int(os.environ.get("PINECONE_MAX_RETRIES", "3")),
            retry_delay=float(os.environ.get("PINECONE_RETRY_DELAY", "1.0")),
            metadata_sharding=os.environ.get("PINECONE_METADATA_SHARDING", "false").lower() == "true",
            namespace=os.environ.get("PINECONE_NAMESPACE", ""),
            rate_limit_per_minute=int(os.environ.get("PINECONE_RATE_LIMIT", "100")),
        )


class PineconeRateLimiter:
    """Rate limiter for Pinecone API calls."""
    
    def __init__(self, requests_per_minute: int):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self._request_timestamps: List[float] = []
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a rate limit slot, waiting if necessary."""
        async with self._lock:
            current_time = time.time()
            one_minute_ago = current_time - 60
            
            # Remove timestamps older than one minute
            self._request_timestamps = [t for t in self._request_timestamps if t >= one_minute_ago]
            
            # Check if we're at the limit
            if len(self._request_timestamps) >= self.requests_per_minute:
                # Calculate how long to wait
                wait_time = 60 - (current_time - self._request_timestamps[0])
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting for {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Add current timestamp
            self._request_timestamps.append(time.time())


class PineconeVectorStore(VectorStoreInterface):
    """Production vector store implementation using Pinecone."""
    
    def __init__(self, config: Union[PineconeConfig, Dict[str, Any]]):
        """Initialize Pinecone vector store with configuration.
        
        Args:
            config: Configuration for Pinecone, either a PineconeConfig object, 
                   a dict from a PydanticPineconeConfig, or a raw dict
            
        Raises:
            VectorOperationError: If initialization fails
        """
        # Convert dict to config if needed
        if isinstance(config, dict):
            self.config = PineconeConfig(**config)
        else:
            self.config = config
        
        # Initialize Pinecone client
        self._client = None
        self._index = None
        self._rate_limiter = PineconeRateLimiter(self.config.rate_limit_per_minute)
        
        # Connect and initialize index
        self._initialize_pinecone()
    
    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone client and create index if it doesn't exist.
        
        Raises:
            VectorOperationError: If initialization fails
        """
        try:
            # Initialize Pinecone client
            self._client = Pinecone(api_key=self.config.api_key)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self._client.list_indexes()]
            
            if self.config.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.config.index_name}")
                
                # Determine if we're using serverless or pod-based
                if self.config.serverless_cloud and self.config.serverless_region:
                    # Serverless specification
                    spec = ServerlessSpec(
                        cloud=self.config.serverless_cloud,
                        region=self.config.serverless_region
                    )
                    self._client.create_index(
                        name=self.config.index_name,
                        dimension=self.config.dimension,
                        metric=self.config.metric,
                        spec=spec
                    )
                else:
                    # Pod-based specification
                    spec = PodSpec(
                        environment=self.config.environment,
                        pod_type=self.config.pod_type or "p1.x1",
                        pods=self.config.pods,
                        replicas=self.config.replicas,
                        shards=1,
                        metadata_config=None if not self.config.metadata_sharding else {
                            "indexed": ["source_type", "content_type"]
                        }
                    )
                    self._client.create_index(
                        name=self.config.index_name,
                        dimension=self.config.dimension,
                        metric=self.config.metric,
                        spec=spec
                    )
                
                logger.info(f"Waiting for index to be ready: {self.config.index_name}")
                while not self._client.describe_index(self.config.index_name).status["ready"]:
                    time.sleep(1)
            
            # Connect to the index
            self._index = self._client.Index(self.config.index_name)
            logger.info(f"Connected to Pinecone index: {self.config.index_name}")
            
        except Exception as e:
            error_msg = f"Failed to initialize Pinecone: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: Optional[str] = None
    ) -> str:
        """Store a single vector with its metadata in Pinecone.
        
        Args:
            vector: The embedding vector to store
            metadata: Metadata associated with the vector
            vector_id: Optional ID for the vector, generated if not provided
            
        Returns:
            The ID of the stored vector
            
        Raises:
            VectorInvalidDimensionError: If vector dimension doesn't match configuration
            VectorOperationError: For any other errors during storage
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Convert to numpy array if needed
            if not isinstance(vector, np.ndarray):
                vector = np.array(vector, dtype=np.float32)
            
            # Validate dimension
            if vector.shape[0] != self.config.dimension:
                raise VectorInvalidDimensionError(
                    f"Vector dimension {vector.shape[0]} doesn't match index dimension {self.config.dimension}"
                )
            
            # Generate ID if not provided
            if vector_id is None:
                vector_id = str(uuid.uuid4())
            
            # Convert vector to list for Pinecone
            vector_list = vector.tolist()
            
            # Convert metadata to dictionary format for Pinecone
            metadata_dict = self._prepare_metadata_for_pinecone(metadata)
            
            # Insert the vector with metadata
            await self._upsert_with_retry(
                vectors=[(vector_id, vector_list, metadata_dict)],
                namespace=self.config.namespace
            )
            
            return vector_id
            
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            error_msg = f"Failed to store vector: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def batch_store_vectors(
        self, 
        vectors: List[EmbeddingVector], 
        metadata_list: List[EmbeddingMetadata],
        vector_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Store multiple vectors in a batch operation.
        
        Args:
            vectors: List of embedding vectors to store
            metadata_list: List of metadata associated with the vectors
            vector_ids: Optional list of IDs for the vectors, generated if not provided
            
        Returns:
            List of IDs for the stored vectors
            
        Raises:
            VectorOperationError: If the input lists have different lengths
            VectorInvalidDimensionError: If any vector doesn't match the index dimension
            BatchOperationError: If batch operation fails
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
            # Process in batches to respect Pinecone's batch size limits
            batch_size = self.config.batch_size
            num_vectors = len(vectors)
            num_batches = (num_vectors + batch_size - 1) // batch_size  # Ceiling division
            
            for batch_idx in range(num_batches):
                # Apply rate limiting
                await self._rate_limiter.acquire()
                
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, num_vectors)
                
                batch_vectors = []
                
                for i in range(start_idx, end_idx):
                    # Convert vector to numpy if needed
                    if not isinstance(vectors[i], np.ndarray):
                        vector = np.array(vectors[i], dtype=np.float32)
                    else:
                        vector = vectors[i]
                    
                    # Validate dimension
                    if vector.shape[0] != self.config.dimension:
                        raise VectorInvalidDimensionError(
                            f"Vector at index {i} dimension {vector.shape[0]} doesn't match index dimension {self.config.dimension}"
                        )
                    
                    # Convert vector to list for Pinecone
                    vector_list = vector.tolist()
                    
                    # Convert metadata to dictionary format for Pinecone
                    metadata_dict = self._prepare_metadata_for_pinecone(metadata_list[i])
                    
                    batch_vectors.append((vector_ids[i], vector_list, metadata_dict))
                
                # Upsert the batch
                await self._upsert_with_retry(
                    vectors=batch_vectors,
                    namespace=self.config.namespace
                )
                
                logger.debug(f"Inserted batch {batch_idx+1}/{num_batches} with {len(batch_vectors)} vectors")
            
            return vector_ids
            
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            error_msg = f"Failed to batch store vectors: {str(e)}"
            logger.error(error_msg)
            raise BatchOperationError(error_msg)
    
    async def get_vector(self, vector_id: str) -> Tuple[Optional[EmbeddingVector], Optional[EmbeddingMetadata]]:
        """Retrieve a vector and its metadata by ID.
        
        Args:
            vector_id: ID of the vector to retrieve
            
        Returns:
            Tuple containing (vector, metadata) or (None, None) if not found
            
        Raises:
            VectorOperationError: If retrieval fails
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Fetch the vector
            response = await self._fetch_with_retry(
                ids=[vector_id],
                namespace=self.config.namespace
            )
            
            # Check if vector was found
            if not response.vectors or vector_id not in response.vectors:
                return None, None
            
            vector_data = response.vectors[vector_id]
            
            # Convert vector values to numpy array
            vector = np.array(vector_data.values, dtype=np.float32)
            
            # Convert Pinecone metadata to EmbeddingMetadata
            metadata_dict = vector_data.metadata or {}
            metadata = self._create_metadata_from_pinecone(metadata_dict)
            
            return vector, metadata
            
        except Exception as e:
            error_msg = f"Failed to retrieve vector {vector_id}: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if vector was deleted, False if not found
            
        Raises:
            VectorOperationError: If deletion fails
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Check if the vector exists first
            response = await self._fetch_with_retry(
                ids=[vector_id],
                namespace=self.config.namespace
            )
            
            # If vector doesn't exist, return False
            if not response.matches or not response.matches[0].values:
                return False
            
            # Delete the vector
            await self._delete_with_retry(
                ids=[vector_id],
                namespace=self.config.namespace
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete vector {vector_id}: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def search_vectors(
        self, 
        query_vector: EmbeddingVector, 
        limit: int = 10, 
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search for similar vectors in Pinecone.
        
        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score threshold
            filter_metadata: Optional metadata filter criteria
            
        Returns:
            List of SearchResult objects ordered by similarity (highest first)
            
        Raises:
            VectorInvalidDimensionError: If query vector dimension doesn't match index dimension
            VectorOperationError: If search fails
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Convert to numpy array if needed
            if not isinstance(query_vector, np.ndarray):
                query_vector = np.array(query_vector, dtype=np.float32)
            
            # Validate dimension
            if query_vector.shape[0] != self.config.dimension:
                raise VectorInvalidDimensionError(
                    f"Query vector dimension {query_vector.shape[0]} doesn't match index dimension {self.config.dimension}"
                )
            
            # Convert vector to list for Pinecone
            query_vector_list = query_vector.tolist()
            
            # Convert filter_metadata to Pinecone filter format
            filter_dict = self._prepare_filter_for_pinecone(filter_metadata) if filter_metadata else None
            
            # Perform the search
            response = await self._query_with_retry(
                vector=query_vector_list,
                top_k=limit,
                namespace=self.config.namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Process results
            results = []
            
            for match in response.matches:
                # Skip results below threshold
                if match.score < score_threshold:
                    continue
                
                # Convert Pinecone metadata to EmbeddingMetadata
                metadata_dict = match.metadata or {}
                metadata = self._create_metadata_from_pinecone(metadata_dict)
                
                results.append(SearchResult(
                    id=match.id,
                    score=match.score,
                    metadata=metadata
                ))
            
            return results
            
        except Exception as e:
            if isinstance(e, VectorInvalidDimensionError):
                raise
            error_msg = f"Failed to search vectors: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def count_vectors(self, filter_metadata: Optional[Dict] = None) -> int:
        """Count vectors optionally filtered by metadata.
        
        Args:
            filter_metadata: Optional metadata filter criteria
            
        Returns:
            Count of vectors matching the filter (or total if no filter)
            
        Raises:
            VectorOperationError: If count operation fails
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Convert filter_metadata to Pinecone filter format
            filter_dict = self._prepare_filter_for_pinecone(filter_metadata) if filter_metadata else None
            
            # Use describe_index_stats to get counts
            stats = self._index.describe_index_stats()
            namespace = self.config.namespace
            
            # If no filter, return total count
            if filter_dict is None:
                # Get count for the specific namespace if provided
                if namespace and namespace in stats.namespaces:
                    return stats.namespaces[namespace].vector_count
                # Otherwise, return total count
                return stats.total_vector_count
            
            # For filtered count, we need to use a more complex approach
            # Pinecone doesn't provide a direct way to count with filters,
            # so we'll use a workaround by sending a dummy query with top_k=0
            dummy_vector = [0.0] * self.config.dimension
            response = await self._query_with_retry(
                vector=dummy_vector,
                top_k=0,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=False
            )
            
            # The total_count field gives us the number of matching vectors
            return response.total_count
            
        except Exception as e:
            error_msg = f"Failed to count vectors: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    async def clear(self) -> None:
        """Remove all vectors from the store.
        
        Raises:
            VectorOperationError: If the operation fails
        """
        # Apply rate limiting
        await self._rate_limiter.acquire()
        
        try:
            # Check if the namespace exists
            stats = self._index.describe_index_stats()
            namespace = self.config.namespace
            
            # If namespace doesn't exist or is empty, nothing to clear
            if namespace not in stats.namespaces or stats.namespaces[namespace].vector_count == 0:
                logger.info(f"Namespace '{namespace}' doesn't exist or is empty - nothing to clear")
                return
                
            # Delete all vectors in the namespace
            self._index.delete(delete_all=True, namespace=self.config.namespace)
            logger.info(f"Cleared all vectors from namespace '{self.config.namespace}'")
            
        except Exception as e:
            # Ignore 404 errors for namespace not found
            if "Namespace not found" in str(e):
                logger.info(f"Namespace '{self.config.namespace}' doesn't exist - nothing to clear")
                return
                
            error_msg = f"Failed to clear vector store: {str(e)}"
            logger.error(error_msg)
            raise VectorOperationError(error_msg)
    
    def _prepare_metadata_for_pinecone(self, metadata: EmbeddingMetadata) -> Dict[str, Any]:
        """Convert EmbeddingMetadata to a format suitable for Pinecone.
        
        Args:
            metadata: The metadata to convert
            
        Returns:
            Dictionary of metadata formatted for Pinecone
        """
        # Convert metadata to dictionary
        metadata_dict = asdict(metadata)
        
        # Flatten the additional field if it exists
        additional = metadata_dict.pop("additional", {}) or {}
        
        # Merge additional fields into top level
        metadata_dict.update(additional)
        
        # Handle JSON serialization for nested objects
        # Pinecone doesn't support nested objects, so convert them to strings
        for key, value in list(metadata_dict.items()):
            if isinstance(value, (dict, list)):
                metadata_dict[key] = json.dumps(value)
        
        return metadata_dict
    
    def _create_metadata_from_pinecone(self, metadata_dict: Dict[str, Any]) -> EmbeddingMetadata:
        """Convert Pinecone metadata to EmbeddingMetadata.
        
        Args:
            metadata_dict: Dictionary of metadata from Pinecone
            
        Returns:
            EmbeddingMetadata object
        """
        # Extract required fields for EmbeddingMetadata
        source_type = metadata_dict.pop("source_type", "unknown")
        source_id = metadata_dict.pop("source_id", "unknown")
        content_type = metadata_dict.pop("content_type", "unknown")
        content = metadata_dict.pop("content", "")
        
        # All other fields go into 'additional'
        return EmbeddingMetadata(
            source_type=source_type,
            source_id=source_id,
            content_type=content_type,
            content=content,
            additional=metadata_dict
        )
    
    def _prepare_filter_for_pinecone(self, filter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert filter metadata to Pinecone filter format.
        
        Args:
            filter_metadata: Filter criteria
            
        Returns:
            Dictionary formatted as a Pinecone filter
        """
        pinecone_filter = {}
        
        # Convert each filter field
        for key, value in filter_metadata.items():
            # Handle different value types
            if isinstance(value, (str, int, float, bool)):
                # Simple equality
                pinecone_filter[key] = {"$eq": value}
            elif isinstance(value, list):
                # $in operator for lists
                pinecone_filter[key] = {"$in": value}
            elif isinstance(value, dict) and len(value) == 1:
                # Handle comparison operators
                op, val = next(iter(value.items()))
                if op.startswith("$"):
                    pinecone_filter[key] = {op: val}
                else:
                    # Nested field
                    pinecone_filter[f"{key}.{op}"] = {"$eq": val}
        
        return pinecone_filter
    
    async def _retry_operation(self, operation_func, *args, **kwargs):
        """Retry an operation with exponential backoff.
        
        Args:
            operation_func: Function to retry
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function
            
        Raises:
            Exception: If all retries fail
        """
        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                return operation_func(*args, **kwargs)
            except Exception as e:
                if attempt < max_retries:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Operation failed (attempt {attempt+1}/{max_retries+1}): {str(e)}. Retrying in {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                else:
                    # Last attempt failed, re-raise the exception
                    logger.error(f"Operation failed after {max_retries+1} attempts: {str(e)}")
                    raise
    
    async def _upsert_with_retry(self, vectors, namespace):
        """Upsert vectors with retry logic."""
        return await self._retry_operation(
            lambda: self._index.upsert(vectors=vectors, namespace=namespace)
        )
    
    async def _fetch_with_retry(self, ids, namespace):
        """Fetch vectors with retry logic."""
        return await self._retry_operation(
            lambda: self._index.fetch(ids=ids, namespace=namespace)
        )
    
    async def _delete_with_retry(self, ids, namespace):
        """Delete vectors with retry logic."""
        return await self._retry_operation(
            lambda: self._index.delete(ids=ids, namespace=namespace)
        )
    
    async def _query_with_retry(self, vector, top_k, namespace, filter=None, include_metadata=True):
        """Query vectors with retry logic."""
        return await self._retry_operation(
            lambda: self._index.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=include_metadata
            )
        ) 