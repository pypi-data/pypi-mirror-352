#!/usr/bin/env python3
"""
Embedding Service for code chunks.

This module provides a service for generating vector embeddings from code chunks,
using the OpenAI API initially, with the design supporting alternative models in the future.
"""

import os
import json
import hashlib
import logging
import asyncio
import time
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union, Type, TypeVar
from dataclasses import dataclass, asdict, field

import aiohttp
import numpy as np
from pydantic import BaseModel, Field

from testindex.core.config import ConfigModel
from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface, 
    EmbeddingVector, 
    EmbeddingMetadata,
    SearchResult
)
from testindex.preprocessing.chunking.code_chunker import CodeChunk
from testindex.knowledge.errors import (
    EmbeddingGenerationError,
    EmbeddingModelError,
    EmbeddingRateLimitError,
    EmbeddingTokenLimitError
)

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class EmbeddingRequest:
    """Request data for embedding generation."""
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Generate checksum if not provided."""
        if not self.checksum:
            self.checksum = generate_checksum(self.text)


@dataclass
class EmbeddingResult:
    """Result data from embedding generation."""
    vector: EmbeddingVector
    metadata: Dict[str, Any]
    token_count: int
    model: str
    checksum: str
    generated_at: datetime = field(default_factory=datetime.now)


class EmbeddingServiceConfig(ConfigModel):
    """Configuration model for the embedding service."""
    
    # API Configuration
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"
    embedding_model: str = "text-embedding-3-small"
    batch_size: int = 10
    
    # Rate Limiting
    rate_limit_requests: int = 50  # requests per minute
    rate_limit_tokens: int = 150000  # tokens per minute
    
    # Retry Configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    
    # Caching
    enable_cache: bool = True
    cache_ttl: int = 86400  # seconds (24 hours)
    
    # Token Limits
    max_tokens_per_request: int = 8191  # OpenAI's limit for text-embedding-3-small
    
    # Neo4j Integration
    enable_neo4j_integration: bool = False
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    
    @classmethod
    def from_environment(cls) -> 'EmbeddingServiceConfig':
        """Create config from environment variables."""
        return cls(
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_api_base=os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
            embedding_model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
            batch_size=int(os.environ.get("EMBEDDING_BATCH_SIZE", "10")),
            rate_limit_requests=int(os.environ.get("EMBEDDING_RATE_LIMIT_REQUESTS", "50")),
            rate_limit_tokens=int(os.environ.get("EMBEDDING_RATE_LIMIT_TOKENS", "150000")),
            max_retries=int(os.environ.get("EMBEDDING_MAX_RETRIES", "3")),
            retry_delay=float(os.environ.get("EMBEDDING_RETRY_DELAY", "1.0")),
            enable_cache=os.environ.get("EMBEDDING_ENABLE_CACHE", "true").lower() == "true",
            cache_ttl=int(os.environ.get("EMBEDDING_CACHE_TTL", "86400")),
            max_tokens_per_request=int(os.environ.get("EMBEDDING_MAX_TOKENS", "8191")),
            enable_neo4j_integration=os.environ.get("EMBEDDING_ENABLE_NEO4J", "false").lower() == "true",
            neo4j_uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            neo4j_username=os.environ.get("NEO4J_USERNAME", "neo4j"),
            neo4j_password=os.environ.get("NEO4J_PASSWORD", "password"),
        )


def generate_checksum(content: str) -> str:
    """Generate a checksum for content to detect changes.
    
    Args:
        content: The content to generate a checksum for
        
    Returns:
        str: Content checksum
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class EmbeddingProviderInterface:
    """Interface for embedding providers."""
    
    async def generate_embedding(self, text: str) -> Tuple[List[float], int]:
        """Generate embedding for text.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            Tuple[List[float], int]: A tuple containing (embedding vector, token count)
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def batch_generate_embeddings(
        self, texts: List[str]
    ) -> List[Tuple[List[float], int]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List[Tuple[List[float], int]]: List of tuples containing (embedding vector, token count)
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    @property
    def model_name(self) -> str:
        """Get the name of the embedding model.
        
        Returns:
            str: Model name
        """
        raise NotImplementedError("Subclasses must implement this method")


class OpenAIEmbeddingProvider(EmbeddingProviderInterface):
    """OpenAI embedding provider implementation."""
    
    def __init__(self, config: EmbeddingServiceConfig):
        """Initialize the OpenAI embedding provider.
        
        Args:
            config: Embedding service configuration
        """
        self.config = config
        self.api_key = config.openai_api_key
        self.api_base = config.openai_api_base
        self.model = config.embedding_model
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay
        
        # Rate limiting state
        self._request_timestamps = []
        self._token_counts = []
    
    async def generate_embedding(self, text: str) -> Tuple[List[float], int]:
        """Generate embedding for text using OpenAI API.
        
        Args:
            text: The text to generate an embedding for
            
        Returns:
            Tuple[List[float], int]: A tuple containing (embedding vector, token count)
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
            EmbeddingRateLimitError: If rate limits are exceeded
            EmbeddingTokenLimitError: If text exceeds token limits
            EmbeddingModelError: If there's an issue with the model
        """
        # Check if text exceeds token limit
        # This is an approximation - OpenAI doesn't expose a tokenizer for embeddings
        if len(text) > self.config.max_tokens_per_request * 4:  # Assuming 4 chars per token
            raise EmbeddingTokenLimitError(
                f"Text exceeds maximum token limit of {self.config.max_tokens_per_request}"
            )
        
        # Apply rate limiting
        await self._apply_rate_limiting(1, len(text) // 4)  # Approximate token count
        
        # Prepare request
        url = f"{self.api_base}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "input": text,
            "model": self.model,
            "encoding_format": "float"
        }
        
        # Execute request with retries
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", "60"))
                            logger.warning(f"Rate limit exceeded. Retry after {retry_after}s")
                            raise EmbeddingRateLimitError(
                                f"OpenAI API rate limit exceeded. Retry after {retry_after}s"
                            )
                        
                        response_data = await response.json()
                        
                        if response.status != 200:
                            error_msg = response_data.get("error", {}).get("message", "Unknown error")
                            logger.error(f"OpenAI API error: {error_msg}")
                            
                            if "token" in error_msg.lower() and "limit" in error_msg.lower():
                                raise EmbeddingTokenLimitError(error_msg)
                            elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                                raise EmbeddingRateLimitError(error_msg)
                            elif "model" in error_msg.lower():
                                raise EmbeddingModelError(error_msg)
                            else:
                                raise EmbeddingGenerationError(f"OpenAI API error: {error_msg}")
                        
                        # Extract embedding and token count
                        embedding_data = response_data["data"][0]
                        embedding_vector = embedding_data["embedding"]
                        token_count = response_data["usage"]["prompt_tokens"]
                        
                        # Update rate limiting state
                        self._update_rate_limiting(token_count)
                        
                        return embedding_vector, token_count
                        
            except (EmbeddingRateLimitError, EmbeddingModelError, EmbeddingTokenLimitError) as e:
                # Don't retry these exceptions
                raise
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Embedding generation attempt {attempt+1} failed: {str(e)}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All embedding generation attempts failed: {str(e)}")
                    raise EmbeddingGenerationError(f"Failed to generate embedding after {self.max_retries} attempts: {str(e)}")
    
    async def batch_generate_embeddings(
        self, texts: List[str]
    ) -> List[Tuple[List[float], int]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List[Tuple[List[float], int]]: List of tuples containing (embedding vector, token count)
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        # Check total token count (approximate)
        total_tokens = sum(len(text) // 4 for text in texts)  # Approximate
        
        # Apply rate limiting
        await self._apply_rate_limiting(len(texts), total_tokens)
        
        # Prepare request
        url = f"{self.api_base}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "input": texts,
            "model": self.model,
            "encoding_format": "float"
        }
        
        # Execute request with retries
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", "60"))
                            logger.warning(f"Rate limit exceeded. Retry after {retry_after}s")
                            raise EmbeddingRateLimitError(
                                f"OpenAI API rate limit exceeded. Retry after {retry_after}s"
                            )
                        
                        response_data = await response.json()
                        
                        if response.status != 200:
                            error_msg = response_data.get("error", {}).get("message", "Unknown error")
                            logger.error(f"OpenAI API error: {error_msg}")
                            
                            if "token" in error_msg.lower() and "limit" in error_msg.lower():
                                raise EmbeddingTokenLimitError(error_msg)
                            elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                                raise EmbeddingRateLimitError(error_msg)
                            elif "model" in error_msg.lower():
                                raise EmbeddingModelError(error_msg)
                            else:
                                raise EmbeddingGenerationError(f"OpenAI API error: {error_msg}")
                        
                        # Extract embeddings and token count
                        results = []
                        embeddings_data = response_data["data"]
                        
                        # Make sure embeddings are in the correct order
                        embeddings_data = sorted(embeddings_data, key=lambda x: x["index"])
                        
                        total_tokens = response_data["usage"]["prompt_tokens"]
                        token_count_per_text = total_tokens // len(texts)  # Approximate distribution
                        
                        for embedding_data in embeddings_data:
                            embedding_vector = embedding_data["embedding"]
                            results.append((embedding_vector, token_count_per_text))
                        
                        # Update rate limiting state
                        self._update_rate_limiting(total_tokens)
                        
                        return results
                        
            except (EmbeddingRateLimitError, EmbeddingModelError, EmbeddingTokenLimitError) as e:
                # Don't retry these exceptions
                raise
            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Batch embedding generation attempt {attempt+1} failed: {str(e)}. Retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All batch embedding generation attempts failed: {str(e)}")
                    raise EmbeddingGenerationError(f"Failed to generate batch embeddings after {self.max_retries} attempts: {str(e)}")
    
    async def _apply_rate_limiting(self, request_count: int, token_count: int) -> None:
        """Apply rate limiting before making a request.
        
        Args:
            request_count: Number of requests to be made
            token_count: Number of tokens to be processed
            
        Raises:
            EmbeddingRateLimitError: If rate limits would be exceeded
        """
        current_time = time.time()
        one_minute_ago = current_time - 60
        
        # Clean up old timestamps
        self._request_timestamps = [t for t in self._request_timestamps if t >= one_minute_ago]
        self._token_counts = self._token_counts[-self.config.rate_limit_requests:]
        
        # Check if limits would be exceeded
        if len(self._request_timestamps) + request_count > self.config.rate_limit_requests:
            # Calculate time until we can make the request
            oldest_timestamp = self._request_timestamps[0]
            wait_time = 60 - (current_time - oldest_timestamp)
            logger.warning(f"Request rate limit would be exceeded. Waiting {wait_time:.2f}s")
            raise EmbeddingRateLimitError(
                f"Request rate limit exceeded. Try again in {wait_time:.2f}s"
            )
        
        recent_tokens = sum(self._token_counts)
        if recent_tokens + token_count > self.config.rate_limit_tokens:
            # Calculate time until we can make the request
            wait_time = 60  # Simplified - we wait a full minute
            logger.warning(f"Token rate limit would be exceeded. Waiting {wait_time}s")
            raise EmbeddingRateLimitError(
                f"Token rate limit exceeded. Try again in {wait_time}s"
            )
    
    def _update_rate_limiting(self, token_count: int) -> None:
        """Update rate limiting state after a successful request.
        
        Args:
            token_count: Number of tokens processed
        """
        current_time = time.time()
        self._request_timestamps.append(current_time)
        self._token_counts.append(token_count)
    
    @property
    def model_name(self) -> str:
        """Get the name of the embedding model.
        
        Returns:
            str: Model name
        """
        return self.model


class EmbeddingService:
    """Service for generating code embeddings."""
    
    def __init__(self, config: Union[EmbeddingServiceConfig, Dict[str, Any]], 
                 vector_store: Optional[VectorStoreInterface] = None):
        """Initialize embedding service with configuration.
        
        Args:
            config: Configuration for the embedding service
            vector_store: Optional vector store interface
        """
        if isinstance(config, dict):
            self.config = EmbeddingServiceConfig(**config)
        else:
            self.config = config
            
        # Initialize embedding provider
        self.embedding_provider = OpenAIEmbeddingProvider(self.config)
        
        # Initialize vector store if provided
        self.vector_store = vector_store
        
        # Initialize cache
        self._cache = {}  # checksum -> EmbeddingResult
        
        # Neo4j client (if enabled)
        self._neo4j_client = None
        if self.config.enable_neo4j_integration:
            try:
                from testindex.knowledge.graph.neo4j_client import Neo4jClient
                self._neo4j_client = Neo4jClient({
                    "uri": self.config.neo4j_uri,
                    "username": self.config.neo4j_username,
                    "password": self.config.neo4j_password
                })
                logger.info("Neo4j integration enabled")
            except ImportError:
                logger.warning("Neo4j integration enabled but neo4j_client module not found")
    
    async def generate_embedding(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[str, List[float]]:
        """Generate embedding for a single code snippet.
        
        Args:
            code: The code snippet to generate an embedding for
            metadata: Optional metadata to associate with the embedding
            
        Returns:
            Tuple[str, List[float]]: (checksum, embedding vector)
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        metadata = metadata or {}
        
        # Preprocess code
        preprocessed_code = self.preprocess_code(code)
        
        # Generate checksum
        checksum = generate_checksum(preprocessed_code)
        
        # Check cache
        if self.config.enable_cache and checksum in self._cache:
            cache_entry = self._cache[checksum]
            logger.info(f"Using cached embedding for checksum {checksum[:8]}...")
            return checksum, cache_entry.vector
        
        # Generate embedding
        embedding_vector, token_count = await self.embedding_provider.generate_embedding(preprocessed_code)
        
        # Store in cache
        if self.config.enable_cache:
            self._cache[checksum] = EmbeddingResult(
                vector=embedding_vector,
                metadata=metadata,
                token_count=token_count,
                model=self.embedding_provider.model_name,
                checksum=checksum
            )
        
        return checksum, embedding_vector
    
    async def batch_generate_embeddings(
        self, 
        codes: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[Tuple[str, List[float]]]:
        """Generate embeddings for multiple code snippets.
        
        Args:
            codes: List of code snippets to generate embeddings for
            metadatas: Optional list of metadata to associate with the embeddings
            
        Returns:
            List[Tuple[str, List[float]]]: List of (checksum, embedding vector) tuples
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        if not codes:
            return []
            
        if metadatas is None:
            metadatas = [{} for _ in codes]
            
        if len(codes) != len(metadatas):
            raise ValueError(f"Number of codes ({len(codes)}) must match number of metadatas ({len(metadatas)})")
        
        # Preprocess codes
        preprocessed_codes = [self.preprocess_code(code) for code in codes]
        
        # Generate checksums
        checksums = [generate_checksum(code) for code in preprocessed_codes]
        
        # Check cache and collect uncached codes
        uncached_indices = []
        uncached_codes = []
        results = [None] * len(codes)
        
        if self.config.enable_cache:
            for i, checksum in enumerate(checksums):
                if checksum in self._cache:
                    cache_entry = self._cache[checksum]
                    logger.debug(f"Using cached embedding for checksum {checksum[:8]}...")
                    results[i] = (checksum, cache_entry.vector)
                else:
                    uncached_indices.append(i)
                    uncached_codes.append(preprocessed_codes[i])
        else:
            uncached_indices = list(range(len(codes)))
            uncached_codes = preprocessed_codes
        
        # Generate embeddings for uncached codes
        if uncached_codes:
            batch_results = await self.embedding_provider.batch_generate_embeddings(uncached_codes)
            
            # Process results
            for batch_idx, (vector, token_count) in enumerate(batch_results):
                original_idx = uncached_indices[batch_idx]
                checksum = checksums[original_idx]
                
                # Store in cache
                if self.config.enable_cache:
                    self._cache[checksum] = EmbeddingResult(
                        vector=vector,
                        metadata=metadatas[original_idx],
                        token_count=token_count,
                        model=self.embedding_provider.model_name,
                        checksum=checksum
                    )
                
                results[original_idx] = (checksum, vector)
        
        return results
    
    def preprocess_code(self, code: str) -> str:
        """Preprocess code for embedding generation.
        
        Args:
            code: The code to preprocess
            
        Returns:
            str: Preprocessed code
        """
        # Skip if empty
        if not code or not code.strip():
            return ""
        
        # Normalize whitespace
        code = code.replace("\r\n", "\n").replace("\t", "    ")
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Handle comments and docstrings
        # This is a simplified approach - a more robust solution would use an AST parser
        
        # Extract docstrings
        docstring = ""
        docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
        
        # Extract important parts: imports, function signatures, class declarations
        important_parts = []
        
        # Get import statements
        import_lines = []
        for line in code.split("\n"):
            if line.startswith("import ") or line.startswith("from "):
                import_lines.append(line)
        
        if import_lines:
            important_parts.append("\n".join(import_lines))
        
        # Get function and class signatures
        signatures = []
        for line in code.split("\n"):
            line = line.strip()
            if line.startswith("def ") or line.startswith("class ") or line.startswith("async def "):
                signatures.append(line)
        
        if signatures:
            important_parts.append("\n".join(signatures))
            
        # Combine important elements with the original code
        # If the code is very long, we prioritize these important parts
        if len(code) > self.config.max_tokens_per_request * 3:  # Approximate threshold
            # Truncate the code but keep important parts
            summary = "\n\n".join([docstring] + important_parts)
            return f"{summary}\n\n# Original code was truncated due to length limitations"
        
        return code
    
    async def embed_and_store(self, code: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate embedding and store it in the vector store.
        
        Args:
            code: The code to generate an embedding for
            metadata: Optional metadata to associate with the embedding
            
        Returns:
            str: ID of the stored vector
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
            VectorOperationError: If storing in vector store fails
        """
        if self.vector_store is None:
            raise ValueError("No vector store provided")
            
        metadata = metadata or {}
        
        # Generate embedding
        checksum, embedding_vector = await self.generate_embedding(code, metadata)
        
        # Prepare metadata
        embedding_metadata = EmbeddingMetadata(
            source_type=metadata.get("source_type", "code"),
            source_id=metadata.get("source_id", checksum),
            content_type=metadata.get("content_type", "code_chunk"),
            content=code[:1000],  # Store first 1000 chars of code
            additional={
                "checksum": checksum,
                "embedding_model": self.embedding_provider.model_name,
                "created_at": datetime.now().isoformat(),
                "token_count": metadata.get("token_count", 0),
                "node_id": metadata.get("node_id"),
                "node_labels": metadata.get("node_labels", []),
                "file_path": metadata.get("file_path"),
                "code_type": metadata.get("code_type"),
                **{k: v for k, v in metadata.items() if k not in 
                   ["source_type", "source_id", "content_type", "checksum", "embedding_model", 
                    "created_at", "token_count", "node_id", "node_labels", "file_path", "code_type"]}
            }
        )
        
        # Store in vector store
        vector_id = await self.vector_store.store_vector(
            embedding_vector, 
            embedding_metadata,
            vector_id=metadata.get("vector_id")
        )
        
        return vector_id
    
    async def embed_chunk(self, chunk: CodeChunk, node_id: Optional[str] = None) -> str:
        """Generate embedding for a code chunk with Neo4j node reference.
        
        Args:
            chunk: The code chunk to generate an embedding for
            node_id: Optional Neo4j node ID to associate with the embedding
            
        Returns:
            str: ID of the stored vector
            
        Raises:
            EmbeddingGenerationError: If embedding generation fails
        """
        if self.vector_store is None:
            raise ValueError("No vector store provided")
            
        # Extract relevant information from the chunk
        metadata = {
            "source_type": "code_chunk",
            "source_id": chunk.chunk_id,
            "content_type": chunk.chunk_type.value,
            "file_path": str(chunk.source_file),
            "code_type": chunk.chunk_type.value,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "name": chunk.name,
            "parent_chunk_id": chunk.parent_chunk_id,
            "imports": chunk.imports,
            "dependencies": chunk.dependencies,
            "is_async": chunk.is_async
        }
        
        # Add Neo4j information if available
        if node_id:
            metadata["node_id"] = node_id
            
            # Add node labels if Neo4j integration is enabled
            if self._neo4j_client:
                try:
                    node_data = self._neo4j_client.get_node(node_id)
                    if node_data:
                        metadata["node_labels"] = node_data.get("labels", [])
                except Exception as e:
                    logger.warning(f"Failed to get Neo4j node labels: {str(e)}")
        
        # Generate and store embedding
        return await self.embed_and_store(chunk.source_code, metadata)
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
        logger.info("Embedding cache cleared")


# Neo4j integration model
@dataclass
class EmbeddingNodeMetadata:
    """Metadata structure for embedding-graph integration."""
    node_id: str  # Neo4j node ID
    node_labels: List[str]  # Neo4j node labels
    chunk_id: str  # Original chunk ID
    file_path: str  # Source file path
    code_type: str  # 'function', 'class', 'module', etc.
    checksum: str  # Hash of the code content
    timestamp: datetime = field(default_factory=datetime.now)
    embedding_model: str = "text-embedding-3-small"
    token_count: int = 0 