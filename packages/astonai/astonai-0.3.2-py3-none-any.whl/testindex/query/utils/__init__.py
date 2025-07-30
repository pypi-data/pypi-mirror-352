"""Utility functions for the testindex.query module."""

from typing import Dict, List, Any, Optional
from testindex.query.model.base import Query, QueryResult
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.core.config import ConfigModel


def create_neo4j_client(config: Optional[ConfigModel] = None) -> Neo4jClient:
    """Create a Neo4j client instance from configuration.
    
    Args:
        config: Optional configuration model. If not provided, default config is used.
        
    Returns:
        Neo4jClient: Configured Neo4j client.
    """
    from testindex.knowledge.graph.neo4j_client import Neo4jClient
    
    if config is None:
        config = ConfigModel()
    
    return Neo4jClient(config)


def extract_query_stats(result: QueryResult) -> Dict[str, Any]:
    """Extract statistics about a query result.
    
    Args:
        result: The query result to analyze.
        
    Returns:
        Dict[str, Any]: Dictionary of statistics about the query result.
    """
    stats = {
        "result_count": len(result.data),
        "node_count": len(result.nodes),
        "relationship_count": len(result.relationships) if result.relationships else 0,
        "query_type": result.metadata.get("query_type", "Unknown")
    }
    
    # Add type-specific stats
    node_types = {}
    for node in result.nodes:
        node_type = node.type
        if node_type not in node_types:
            node_types[node_type] = 0
        node_types[node_type] += 1
    
    stats["node_types"] = node_types
    
    if result.relationships:
        rel_types = {}
        for rel in result.relationships:
            rel_type = rel.type
            if rel_type not in rel_types:
                rel_types[rel_type] = 0
            rel_types[rel_type] += 1
        
        stats["relationship_types"] = rel_types
    
    return stats


def merge_query_results(results: List[QueryResult]) -> QueryResult:
    """Merge multiple query results into a single result.
    
    Args:
        results: List of query results to merge.
        
    Returns:
        QueryResult: Merged query result.
    """
    if not results:
        return QueryResult()
    
    # Combine data
    combined_data = []
    for result in results:
        combined_data.extend(result.data)
    
    # Combine metadata
    combined_metadata = {
        "merged_results": len(results),
        "total_records": sum(len(result.data) for result in results)
    }
    
    # Combine nodes (avoiding duplicates by ID)
    combined_nodes = {}
    for result in results:
        for node in result.nodes:
            if node.id not in combined_nodes:
                combined_nodes[node.id] = node
    
    # Combine relationships (avoiding duplicates by ID)
    combined_relationships = {}
    for result in results:
        if result.relationships:
            for rel in result.relationships:
                if rel.id not in combined_relationships:
                    combined_relationships[rel.id] = rel
    
    return QueryResult(
        data=combined_data,
        metadata=combined_metadata,
        nodes=list(combined_nodes.values()),
        relationships=list(combined_relationships.values())
    )
