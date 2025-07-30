"""
Utility functions for test coverage analysis.

This module provides utility functions and classes for the coverage analysis module.
"""

import os
import logging
from typing import Dict, List, Any, Optional

# Simple Neo4j client that doesn't rely on the existing implementation
class SimpleNeo4jClient:
    """A simplified Neo4j client to interact with the Knowledge Graph.
    
    This is used to avoid dependency issues with the full client in testindex.knowledge.
    """
    
    def __init__(self, 
                 uri=None, 
                 username=None, 
                 password=None,
                 database=None):
        """Initialize with Neo4j connection parameters.
        
        Args:
            uri: Neo4j connection URI (default: from environment variable NEO4J_URI)
            username: Neo4j username (default: from environment variable NEO4J_USER)
            password: Neo4j password (default: from environment variable NEO4J_PASS)
            database: Neo4j database name (default: from environment variable NEO4J_DATABASE)
        """
        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASS", "testindexdev")
        self.database = database or os.environ.get("NEO4J_DATABASE", "neo4j")
        self._driver = None
        
    def run_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Run a Cypher query against Neo4j.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of dictionaries representing the query results
            
        Raises:
            Exception: If query execution fails
        """
        try:
            from neo4j import GraphDatabase
            
            if not self._driver:
                self._driver = GraphDatabase.driver(
                    self.uri, 
                    auth=(self.username, self.password)
                )
                
            with self._driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
                
        except Exception as e:
            logging.error(f"Neo4j query failed: {str(e)}")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self._driver:
            self._driver.close()
            self._driver = None 