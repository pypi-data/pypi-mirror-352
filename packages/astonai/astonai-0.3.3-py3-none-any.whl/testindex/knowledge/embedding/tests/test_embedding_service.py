#!/usr/bin/env python3
"""
Unit tests for the embedding service.

These tests verify the functionality of the embedding service,
code preprocessing, and integration with vector stores.
"""

import os
import json
import pytest
import asyncio
import unittest.mock as mock
from datetime import datetime
from typing import Dict, List, Any, Tuple

import numpy as np
from testindex.knowledge.embedding.embedding_service import (
    EmbeddingService,
    EmbeddingServiceConfig,
    OpenAIEmbeddingProvider,
    generate_checksum,
    EmbeddingRequest,
    EmbeddingResult
)
from testindex.knowledge.embedding.vector_store import (
    VectorStoreInterface,
    EmbeddingVector,
    EmbeddingMetadata,
    SearchResult
)
from testindex.knowledge.errors import (
    EmbeddingGenerationError,
    EmbeddingModelError,
    EmbeddingRateLimitError,
    EmbeddingTokenLimitError
)
from testindex.preprocessing.chunking.code_chunker import CodeChunk, ChunkType


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status: int, data: Dict[str, Any], headers: Dict[str, str] = None):
        self.status = status
        self._data = data
        self.headers = headers or {}
    
    async def json(self):
        return self._data


class MockSession:
    """Mock HTTP session for testing."""
    
    def __init__(self, responses: List[Tuple[int, Dict[str, Any], Dict[str, str]]]):
        self.responses = [MockResponse(status, data, headers) for status, data, headers in responses]
        self.response_index = 0
        self.requests = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def post(self, url, headers=None, json=None):
        self.requests.append((url, headers, json))
        response = self.responses[self.response_index]
        self.response_index += 1
        return response


class MockClientSession:
    """Mock aiohttp.ClientSession for testing."""
    
    def __init__(self, responses):
        self.responses = responses
    
    def __call__(self):
        return MockSession(self.responses)


class MockVectorStore(VectorStoreInterface):
    """Mock vector store for testing."""
    
    def __init__(self):
        self.vectors = {}
        self.metadata = {}
    
    async def store_vector(
        self, vector: EmbeddingVector, metadata: EmbeddingMetadata, vector_id: str = None
    ) -> str:
        if vector_id is None:
            vector_id = f"vector-{len(self.vectors)}"
        self.vectors[vector_id] = vector
        self.metadata[vector_id] = metadata
        return vector_id
    
    async def batch_store_vectors(
        self, vectors: List[EmbeddingVector], metadata_list: List[EmbeddingMetadata],
        vector_ids: List[str] = None
    ) -> List[str]:
        if vector_ids is None:
            start_id = len(self.vectors)
            vector_ids = [f"vector-{start_id + i}" for i in range(len(vectors))]
        
        for i, (vector, metadata, vector_id) in enumerate(zip(vectors, metadata_list, vector_ids)):
            self.vectors[vector_id] = vector
            self.metadata[vector_id] = metadata
        
        return vector_ids
    
    async def get_vector(self, vector_id: str) -> Tuple[EmbeddingVector, EmbeddingMetadata]:
        if vector_id not in self.vectors:
            return None, None
        return self.vectors[vector_id], self.metadata[vector_id]
    
    async def delete_vector(self, vector_id: str) -> bool:
        if vector_id not in self.vectors:
            return False
        del self.vectors[vector_id]
        del self.metadata[vector_id]
        return True
    
    async def search_vectors(
        self, query_vector: EmbeddingVector, limit: int = 10, 
        score_threshold: float = 0.0, filter_metadata: Dict = None
    ) -> List[SearchResult]:
        results = []
        for vector_id, vector in self.vectors.items():
            metadata = self.metadata[vector_id]
            
            # Apply filter if provided
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if key in metadata.additional:
                        if metadata.additional[key] != value:
                            match = False
                            break
                    else:
                        match = False
                        break
                
                if not match:
                    continue
            
            # If query_vector is None, just return all vectors (for testing)
            if query_vector is None:
                score = 1.0
            else:
                # Calculate cosine similarity
                query_norm = np.linalg.norm(query_vector)
                vector_norm = np.linalg.norm(vector)
                
                if query_norm > 0 and vector_norm > 0:
                    vector = vector / vector_norm
                    query_vector_normalized = query_vector / query_norm
                    score = float(np.dot(query_vector_normalized, vector))
                else:
                    score = 0.0
            
            if score >= score_threshold:
                results.append(SearchResult(
                    id=vector_id,
                    score=score,
                    metadata=metadata
                ))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    async def count_vectors(self, filter_metadata: Dict = None) -> int:
        if not filter_metadata:
            return len(self.vectors)
        
        count = 0
        for vector_id in self.vectors:
            metadata = self.metadata[vector_id]
            match = True
            for key, value in filter_metadata.items():
                if key in metadata.additional:
                    if metadata.additional[key] != value:
                        match = False
                        break
                else:
                    match = False
                    break
            
            if match:
                count += 1
        
        return count
    
    async def clear(self) -> None:
        self.vectors.clear()
        self.metadata.clear()


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    return [
        (200, {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0
                }
            ],
            "model": "text-embedding-3-small",
            "usage": {
                "prompt_tokens": 10,
                "total_tokens": 10
            }
        }, {})
    ]


@pytest.fixture
def mock_openai_batch_response():
    """Create a mock OpenAI API batch response."""
    return [
        (200, {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "index": 0
                },
                {
                    "object": "embedding",
                    "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
                    "index": 1
                },
                {
                    "object": "embedding",
                    "embedding": [0.3, 0.4, 0.5, 0.6, 0.7],
                    "index": 2
                }
            ],
            "model": "text-embedding-3-small",
            "usage": {
                "prompt_tokens": 30,
                "total_tokens": 30
            }
        }, {})
    ]


@pytest.fixture
def embedding_service_config():
    """Create a test embedding service configuration."""
    return EmbeddingServiceConfig(
        openai_api_key="test-api-key",
        openai_api_base="https://api.openai.com/v1",
        embedding_model="text-embedding-3-small",
        enable_cache=True
    )


@pytest.fixture
def mock_vector_store():
    """Create a mock vector store."""
    return MockVectorStore()


@pytest.fixture
def embedding_service(embedding_service_config, mock_vector_store, mock_openai_response):
    """Create a test embedding service with mocked API responses."""
    service = EmbeddingService(embedding_service_config, mock_vector_store)
    
    # Mock the aiohttp.ClientSession
    mock_session = MockClientSession(mock_openai_response)
    service.embedding_provider._session = mock_session
    
    return service


@pytest.fixture
def code_chunk():
    """Create a test code chunk."""
    return CodeChunk(
        chunk_id="test-chunk-1",
        chunk_type=ChunkType.FUNCTION,
        name="test_function",
        source_file=Path("test_file.py"),
        source_code="def test_function():\n    return 'test'",
        start_line=1,
        end_line=2,
        doc_string="Test function",
        metadata={"test_key": "test_value"}
    )


class TestEmbeddingService:
    """Tests for the EmbeddingService class."""
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_service, mock_openai_response):
        """Test generating an embedding."""
        with mock.patch('aiohttp.ClientSession', MockClientSession(mock_openai_response)):
            checksum, embedding = await embedding_service.generate_embedding("Test code")
            
            # Verify checksum was generated
            assert checksum == generate_checksum("Test code")
            
            # Verify embedding has the right shape
            assert len(embedding) == 5
            assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, embedding_service, mock_openai_response):
        """Test that the cache is used for repeated requests."""
        with mock.patch('aiohttp.ClientSession', MockClientSession(mock_openai_response * 2)):
            # First request should hit the API
            code = "def test(): return True"
            checksum1, embedding1 = await embedding_service.generate_embedding(code)
            
            # Second request for the same code should use the cache
            checksum2, embedding2 = await embedding_service.generate_embedding(code)
            
            assert checksum1 == checksum2
            assert embedding1 == embedding2
            
            # Verify that only one API call was made
            assert len(embedding_service.embedding_provider._session().requests) == 1
    
    @pytest.mark.asyncio
    async def test_batch_generate_embeddings(self, embedding_service_config, mock_vector_store, 
                                          mock_openai_batch_response):
        """Test batch generation of embeddings."""
        service = EmbeddingService(embedding_service_config, mock_vector_store)
        
        with mock.patch('aiohttp.ClientSession', MockClientSession(mock_openai_batch_response)):
            codes = ["def a(): pass", "def b(): pass", "def c(): pass"]
            metadatas = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
            
            results = await service.batch_generate_embeddings(codes, metadatas)
            
            assert len(results) == 3
            
            # Verify checksums
            checksums = [checksum for checksum, _ in results]
            expected_checksums = [generate_checksum(code) for code in codes]
            assert checksums == expected_checksums
            
            # Verify embeddings
            embeddings = [embedding for _, embedding in results]
            assert embeddings[0] == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert embeddings[1] == [0.2, 0.3, 0.4, 0.5, 0.6]
            assert embeddings[2] == [0.3, 0.4, 0.5, 0.6, 0.7]
    
    @pytest.mark.asyncio
    async def test_preprocess_code(self, embedding_service):
        """Test code preprocessing."""
        # Test whitespace normalization
        code = "def test():\r\n\tpass"
        processed = embedding_service.preprocess_code(code)
        assert "\r\n" not in processed
        assert "\t" not in processed
        
        # Test docstring extraction
        code = '''
def test():
    """This is a docstring."""
    pass
'''
        processed = embedding_service.preprocess_code(code)
        assert "This is a docstring" in processed
        
        # Test import extraction
        code = '''
import os
import sys
from typing import List, Dict

def test():
    pass
'''
        processed = embedding_service.preprocess_code(code)
        assert "import os" in processed
        assert "import sys" in processed
        assert "from typing import List, Dict" in processed
        
        # Test signature extraction
        code = '''
def test_function(a: int, b: str) -> bool:
    pass

class TestClass:
    def test_method(self):
        pass
'''
        processed = embedding_service.preprocess_code(code)
        assert "def test_function(a: int, b: str) -> bool" in processed
        assert "class TestClass" in processed
    
    @pytest.mark.asyncio
    async def test_embed_and_store(self, embedding_service, mock_openai_response):
        """Test generating an embedding and storing it in the vector store."""
        with mock.patch('aiohttp.ClientSession', MockClientSession(mock_openai_response)):
            code = "def test(): return True"
            metadata = {"function_name": "test", "module": "test_module"}
            
            vector_id = await embedding_service.embed_and_store(code, metadata)
            
            # Verify vector was stored
            vector, stored_metadata = await embedding_service.vector_store.get_vector(vector_id)
            
            assert vector is not None
            assert stored_metadata is not None
            assert stored_metadata.source_type == "code"
            assert stored_metadata.content_type == "code_chunk"
            assert stored_metadata.additional["function_name"] == "test"
            assert stored_metadata.additional["module"] == "test_module"
            assert stored_metadata.additional["checksum"] == generate_checksum(code)
            assert stored_metadata.additional["embedding_model"] == "text-embedding-3-small"
    
    @pytest.mark.asyncio
    async def test_embed_chunk(self, embedding_service, code_chunk, mock_openai_response):
        """Test generating an embedding for a code chunk."""
        with mock.patch('aiohttp.ClientSession', MockClientSession(mock_openai_response)):
            # Test without Neo4j node ID
            vector_id = await embedding_service.embed_chunk(code_chunk)
            
            # Verify vector was stored
            vector, stored_metadata = await embedding_service.vector_store.get_vector(vector_id)
            
            assert vector is not None
            assert stored_metadata is not None
            assert stored_metadata.source_type == "code_chunk"
            assert stored_metadata.content_type == "function"
            assert stored_metadata.additional["code_type"] == "function"
            assert stored_metadata.additional["name"] == "test_function"
            
            # Test with Neo4j node ID
            vector_id = await embedding_service.embed_chunk(code_chunk, "test-node-id")
            
            # Verify vector was stored with node ID
            vector, stored_metadata = await embedding_service.vector_store.get_vector(vector_id)
            
            assert vector is not None
            assert stored_metadata is not None
            assert stored_metadata.additional["node_id"] == "test-node-id"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, embedding_service_config, mock_vector_store):
        """Test error handling in the embedding service."""
        service = EmbeddingService(embedding_service_config, mock_vector_store)
        
        # Test rate limit error
        rate_limit_response = [(429, {"error": {"message": "Rate limit exceeded"}}, 
                             {"Retry-After": "30"})]
        with mock.patch('aiohttp.ClientSession', MockClientSession(rate_limit_response)):
            with pytest.raises(EmbeddingRateLimitError):
                await service.generate_embedding("Test code")
        
        # Test token limit error
        token_limit_response = [(400, {"error": {"message": "Token limit exceeded"}}, {})]
        with mock.patch('aiohttp.ClientSession', MockClientSession(token_limit_response)):
            with pytest.raises(EmbeddingTokenLimitError):
                await service.generate_embedding("Test code")
        
        # Test model error
        model_error_response = [(400, {"error": {"message": "Model not found"}}, {})]
        with mock.patch('aiohttp.ClientSession', MockClientSession(model_error_response)):
            with pytest.raises(EmbeddingModelError):
                await service.generate_embedding("Test code")
        
        # Test general API error
        api_error_response = [(500, {"error": {"message": "Internal server error"}}, {})]
        with mock.patch('aiohttp.ClientSession', MockClientSession(api_error_response)):
            with pytest.raises(EmbeddingGenerationError):
                await service.generate_embedding("Test code")
    
    def test_clear_cache(self, embedding_service):
        """Test clearing the embedding cache."""
        # Add something to the cache
        embedding_service._cache["test"] = EmbeddingResult(
            vector=[0.1, 0.2, 0.3],
            metadata={"test": "data"},
            token_count=10,
            model="test-model",
            checksum="test-checksum"
        )
        
        assert "test" in embedding_service._cache
        
        # Clear the cache
        embedding_service.clear_cache()
        
        assert "test" not in embedding_service._cache
        assert len(embedding_service._cache) == 0


def test_generate_checksum():
    """Test checksum generation."""
    # Same content should produce the same checksum
    content1 = "Test content"
    content2 = "Test content"
    
    assert generate_checksum(content1) == generate_checksum(content2)
    
    # Different content should produce different checksums
    content3 = "Different content"
    
    assert generate_checksum(content1) != generate_checksum(content3)
    
    # Empty content should have a valid checksum
    empty_content = ""
    
    assert generate_checksum(empty_content) is not None
    assert isinstance(generate_checksum(empty_content), str)


class TestOpenAIEmbeddingProvider:
    """Tests for the OpenAIEmbeddingProvider class."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, embedding_service_config):
        """Test rate limiting in the embedding provider."""
        provider = OpenAIEmbeddingProvider(embedding_service_config)
        
        # Set up rate limiting state to be near the limit
        provider._request_timestamps = [time.time() for _ in range(provider.config.rate_limit_requests - 1)]
        provider._token_counts = [100 for _ in range(provider.config.rate_limit_requests - 1)]
        
        # The next request should exceed the rate limit
        with pytest.raises(EmbeddingRateLimitError):
            await provider._apply_rate_limiting(2, 100)
        
        # But a single request should still be allowed
        await provider._apply_rate_limiting(1, 100)
        
        # If tokens would exceed the limit, it should raise an error
        provider._token_counts = [provider.config.rate_limit_tokens // 2 for _ in range(2)]
        with pytest.raises(EmbeddingRateLimitError):
            await provider._apply_rate_limiting(1, provider.config.rate_limit_tokens)
    
    def test_update_rate_limiting(self, embedding_service_config):
        """Test updating rate limiting state."""
        provider = OpenAIEmbeddingProvider(embedding_service_config)
        
        # Update should add to the tracking lists
        initial_requests = len(provider._request_timestamps)
        initial_tokens = len(provider._token_counts)
        
        provider._update_rate_limiting(100)
        
        assert len(provider._request_timestamps) == initial_requests + 1
        assert len(provider._token_counts) == initial_tokens + 1
        assert provider._token_counts[-1] == 100


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 