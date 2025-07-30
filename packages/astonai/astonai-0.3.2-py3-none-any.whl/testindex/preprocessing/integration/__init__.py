"""
Integration package for connecting preprocessing components with other pods.

This package provides adapters and utilities for integrating preprocessing
components with other pods, such as the Knowledge Graph.
"""

from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter, ChunkGraphAdapterError

__all__ = ["ChunkGraphAdapter", "ChunkGraphAdapterError"] 