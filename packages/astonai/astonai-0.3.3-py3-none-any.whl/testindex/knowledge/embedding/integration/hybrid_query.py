#!/usr/bin/env python3
"""
Hybrid Query Service for combining vector similarity with graph queries.

This module provides a service for executing queries that combine
vector similarity search with graph traversal constraints.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.knowledge.embedding.vector_store import VectorStoreInterface
from testindex.knowledge.embedding.embedding_service import EmbeddingService
from testindex.knowledge.errors import (
    EmbeddingError,
    Neo4jQueryError,
    VectorStoreError
)

# Setup logging
logger = logging.getLogger(__name__)


class HybridQueryService:
    """Service for executing hybrid graph + vector queries."""
    
    def __init__(self, neo4j_client: Neo4jClient, vector_store: VectorStoreInterface, 
                embedding_service: EmbeddingService):
        """Initialize hybrid query service.
        
        Args:
            neo4j_client: Neo4j client for graph queries
            vector_store: Vector store for similarity search
            embedding_service: Embedding service for generating embeddings
        """
        self.neo4j_client = neo4j_client
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    async def find_similar_code(
        self,
        code_query: str,
        limit: int = 10,
        node_labels: Optional[List[str]] = None,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find code similar to the query with optional graph constraints.
        
        Args:
            code_query: Code or text query to find similar code
            limit: Maximum number of results to return
            node_labels: Optional filter for Neo4j node labels
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of results with metadata from both vector store and graph
            
        Raises:
            EmbeddingError: If embedding generation fails
            Neo4jQueryError: If graph query fails
            VectorStoreError: If vector search fails
        """
        try:
            # Generate embedding for the query
            _, query_vector = await self.embedding_service.generate_embedding(code_query)
            
            # Prepare metadata filter for node labels
            filter_metadata = {}
            if node_labels:
                filter_metadata["node_labels"] = node_labels
            
            # Search vector store
            search_results = await self.vector_store.search_vectors(
                query_vector=query_vector,
                limit=limit * 2,  # Get more results than needed to filter
                score_threshold=similarity_threshold,
                filter_metadata=filter_metadata
            )
            
            # Collect Neo4j node IDs from results
            node_ids = []
            for result in search_results:
                node_id = result.metadata.additional.get("node_id")
                if node_id:
                    node_ids.append(node_id)
            
            # If we have node IDs and Neo4j integration is enabled, enrich results with graph data
            hybrid_results = []
            
            if node_ids and len(node_ids) > 0:
                # Fetch node details from Neo4j
                node_details = {}
                
                try:
                    # Build parameterized query
                    query = """
                    MATCH (n)
                    WHERE n.id IN $node_ids
                    RETURN n.id as id, labels(n) as labels, n.schema_type as schema_type,
                           n.properties as properties
                    """
                    
                    result = self.neo4j_client.execute_query(query, {"node_ids": node_ids})
                    
                    for record in result:
                        node_id = record["id"]
                        node_details[node_id] = {
                            "id": node_id,
                            "labels": record["labels"],
                            "schema_type": record["schema_type"],
                            "properties": record["properties"]
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch Neo4j node details: {str(e)}")
                
                # Combine vector search results with graph data
                for result in search_results:
                    hybrid_result = {
                        "score": result.score,
                        "vector_id": result.id,
                        "content": result.metadata.content,
                        "source_type": result.metadata.source_type,
                        "source_id": result.metadata.source_id,
                        "content_type": result.metadata.content_type,
                        "metadata": result.metadata.additional,
                    }
                    
                    # Add Neo4j data if available
                    node_id = result.metadata.additional.get("node_id")
                    if node_id and node_id in node_details:
                        hybrid_result["graph_node"] = node_details[node_id]
                    
                    hybrid_results.append(hybrid_result)
            else:
                # Just return vector search results if no Neo4j integration
                for result in search_results:
                    hybrid_result = {
                        "score": result.score,
                        "vector_id": result.id,
                        "content": result.metadata.content,
                        "source_type": result.metadata.source_type,
                        "source_id": result.metadata.source_id,
                        "content_type": result.metadata.content_type,
                        "metadata": result.metadata.additional,
                    }
                    hybrid_results.append(hybrid_result)
            
            # Limit results
            return hybrid_results[:limit]
            
        except Exception as e:
            if isinstance(e, (EmbeddingError, Neo4jQueryError, VectorStoreError)):
                raise
            logger.error(f"Hybrid query failed: {str(e)}")
            raise RuntimeError(f"Failed to execute hybrid query: {str(e)}")
    
    async def find_related_implementations(
        self,
        test_node_id: str,
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find implementations related to a test using both graph and similarity.
        
        Args:
            test_node_id: Neo4j node ID of the test
            similarity_threshold: Minimum similarity score (0-1)
            limit: Maximum number of results to return
            
        Returns:
            List of related implementations with metadata
            
        Raises:
            Neo4jQueryError: If graph query fails
            EmbeddingError: If embedding retrieval fails
            VectorStoreError: If vector search fails
        """
        try:
            # First, get the test node and its metadata
            test_node = self.neo4j_client.get_node(test_node_id)
            if not test_node:
                raise Neo4jQueryError(f"Test node not found: {test_node_id}")
            
            # Find directly related implementations via graph relationships
            related_via_graph = []
            
            try:
                # Find implementations that this test targets (via graph relationships)
                query = """
                MATCH (test {id: $test_id})-[:TESTS]->(impl)
                RETURN impl.id as id, labels(impl) as labels, impl.schema_type as schema_type,
                       impl.properties as properties, 'direct' as relationship_type
                UNION
                MATCH (test {id: $test_id})-[:TESTS]->()-[:DEPENDS_ON]->(impl)
                RETURN impl.id as id, labels(impl) as labels, impl.schema_type as schema_type,
                       impl.properties as properties, 'indirect' as relationship_type
                """
                
                result = self.neo4j_client.execute_query(query, {"test_id": test_node_id})
                
                for record in result:
                    related_via_graph.append({
                        "id": record["id"],
                        "labels": record["labels"],
                        "schema_type": record["schema_type"],
                        "properties": record["properties"],
                        "relationship_type": record["relationship_type"]
                    })
            except Exception as e:
                logger.warning(f"Failed to find related implementations via graph: {str(e)}")
            
            # Get embedding for the test node
            test_embedding = None
            filter_metadata = {"node_id": test_node_id}
            
            # Search vector store for the test node's embedding
            try:
                test_vectors = await self.vector_store.search_vectors(
                    query_vector=None,  # Not using similarity here, just retrieving
                    filter_metadata=filter_metadata,
                    limit=1
                )
                
                if test_vectors and len(test_vectors) > 0:
                    # Get the vector from the vector store
                    test_vector, _ = await self.vector_store.get_vector(test_vectors[0].id)
                    test_embedding = test_vector
            except Exception as e:
                logger.warning(f"Failed to get test embedding from vector store: {str(e)}")
            
            # If we couldn't find the embedding, try to get the code from Neo4j and generate it
            if test_embedding is None:
                try:
                    # Extract code from the test node
                    test_properties = test_node.get("properties", {})
                    if isinstance(test_properties, str):
                        import json
                        test_properties = json.loads(test_properties)
                    
                    test_code = test_properties.get("code", "")
                    
                    if test_code:
                        # Generate embedding for the test code
                        _, test_embedding = await self.embedding_service.generate_embedding(test_code)
                    else:
                        logger.warning(f"No code found for test node: {test_node_id}")
                        # Return just the graph results if we can't get an embedding
                        return [{"graph_node": node, "score": 1.0 if node["relationship_type"] == "direct" else 0.9}
                                for node in related_via_graph]
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for test code: {str(e)}")
                    # Return just the graph results if we can't get an embedding
                    return [{"graph_node": node, "score": 1.0 if node["relationship_type"] == "direct" else 0.9}
                            for node in related_via_graph]
            
            # Now search for similar code using the test embedding
            similar_results = await self.vector_store.search_vectors(
                query_vector=test_embedding,
                limit=limit * 2,  # Get more than needed to filter
                score_threshold=similarity_threshold,
                filter_metadata={"content_type": "function"}  # Focus on implementations
            )
            
            # Combine results from graph and vector search
            graph_node_ids = {node["id"] for node in related_via_graph}
            hybrid_results = []
            
            # Add graph-related nodes first (they get priority)
            for node in related_via_graph:
                node_id = node["id"]
                
                # Check if we also have vector data for this node
                vector_result = None
                for result in similar_results:
                    if result.metadata.additional.get("node_id") == node_id:
                        vector_result = result
                        break
                
                # Calculate a combined score
                # Direct relationships get a boost
                relationship_score = 1.0 if node["relationship_type"] == "direct" else 0.8
                similarity_score = vector_result.score if vector_result else relationship_score
                
                # Combined score gives more weight to graph relationships
                combined_score = (relationship_score * 0.7) + (similarity_score * 0.3)
                
                hybrid_results.append({
                    "graph_node": node,
                    "score": combined_score,
                    "vector_score": similarity_score if vector_result else None,
                    "graph_score": relationship_score,
                    "vector_id": vector_result.id if vector_result else None,
                    "content": vector_result.metadata.content if vector_result else None,
                })
            
            # Add vector-only results (not found via graph)
            for result in similar_results:
                node_id = result.metadata.additional.get("node_id")
                if node_id and node_id not in graph_node_ids:
                    hybrid_results.append({
                        "vector_id": result.id,
                        "content": result.metadata.content,
                        "score": result.score * 0.9,  # Slightly lower weight for vector-only results
                        "vector_score": result.score,
                        "graph_score": None,
                        "metadata": result.metadata.additional,
                    })
            
            # Sort by score and limit results
            hybrid_results.sort(key=lambda x: x["score"], reverse=True)
            return hybrid_results[:limit]
            
        except Exception as e:
            if isinstance(e, (EmbeddingError, Neo4jQueryError, VectorStoreError)):
                raise
            logger.error(f"Hybrid query for related implementations failed: {str(e)}")
            raise RuntimeError(f"Failed to find related implementations: {str(e)}") 