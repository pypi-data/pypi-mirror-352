#!/usr/bin/env python3
"""
Custom error classes for the knowledge system.
"""

from typing import Optional, Dict, Any


class AstonKnowledgeError(Exception):
    """Base exception for Knowledge Graph errors."""
    error_code: Optional[str] = None
    default_message: str = "An unspecified error occurred in the Knowledge Graph."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.message = message or self.default_message
        if error_code:
            self.error_code = error_code
        self.context = context or {}
        msg_prefix = f"[{self.error_code}] " if self.error_code else ""
        super().__init__(f"{msg_prefix}{self.message}")


# Graph Database Errors
class Neo4jConnectionError(AstonKnowledgeError):
    """Raised when there's an error connecting to the Neo4j database."""
    error_code = "KG_NEO4J_CONN_001"
    default_message = "Failed to connect to Neo4j database."


class Neo4jQueryError(AstonKnowledgeError):
    """Raised when there's an error executing a Neo4j query."""
    error_code = "KG_NEO4J_QUERY_002"
    default_message = "Neo4j query execution failed."


class BatchOperationError(AstonKnowledgeError):
    """Raised when there's an error in a batch database operation."""
    error_code = "KG_BATCH_OP_003"
    default_message = "Graph batch operation failed."


# Static Analysis Errors
class StaticAnalysisError(AstonKnowledgeError):
    """Raised when there's an error in static code analysis."""
    error_code = "KG_STATIC_ANALYSIS_004"
    default_message = "Static code analysis failed."


# Schema Errors
class SchemaVersionMismatchError(AstonKnowledgeError):
    """Raised when the database schema version doesn't match the expected version."""
    error_code = "KG_SCHEMA_VERSION_005"
    default_message = "Schema version mismatch detected."


# Vector Store Errors
class VectorStoreError(AstonKnowledgeError):
    """Raised for errors related to the vector store."""
    error_code = "KG_VECTOR_STORE_006"
    default_message = "Vector store operation failed."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, operation: Optional[str] = None):
        final_message = message or self.default_message
        current_context = context or {}
        if operation:
            current_context['operation'] = operation
        
        super().__init__(message=final_message, error_code=error_code or self.error_code, context=current_context)
        self.operation = operation


class VectorOperationError(VectorStoreError):
    """Raised when an operation on vectors fails."""
    pass


class VectorInvalidDimensionError(VectorStoreError):
    """Raised when vector dimensions don't match expected dimensions."""
    pass


# Embedding Errors
class EmbeddingError(AstonKnowledgeError):
    """Raised for errors during embedding generation or retrieval."""
    error_code = "KG_EMBEDDING_007"
    default_message = "Embedding operation failed."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, model_name: Optional[str] = None):
        final_message = message or self.default_message
        current_context = context or {}
        if model_name:
            current_context['model_name'] = model_name

        super().__init__(message=final_message, error_code=error_code or self.error_code, context=current_context)
        self.model_name = model_name


class EmbeddingGenerationError(EmbeddingError):
    """Raised when there's an error generating embeddings."""
    pass


class EmbeddingModelError(EmbeddingError):
    """Raised when there's an issue with the embedding model."""
    pass


class EmbeddingRateLimitError(EmbeddingError):
    """Raised when API rate limits are exceeded."""
    pass


class EmbeddingTokenLimitError(EmbeddingError):
    """Raised when content exceeds token limits."""
    pass 