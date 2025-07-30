"""
Neo4j client for the Knowledge Graph.

This module provides a client for interacting with Neo4j database,
including connection management, CRUD operations, and query execution.
"""

import json
import os
import functools
import time
from typing import Any, Dict, List, Optional, Union, Tuple

from neo4j import GraphDatabase, Driver, Result, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from testindex.core.config import ConfigModel
from testindex.core.exceptions import AstonError, StorageError
from testindex.core.logging import get_logger
from testindex.knowledge.schema.base import Node, Relationship, SchemaItem

logger = get_logger(__name__)


class Neo4jConnectionError(AstonError):
    """Raised when a connection to Neo4j fails."""
    error_code = "NEO4J_CONN_001"
    default_message = "Failed to connect to Neo4j database."


class Neo4jQueryError(AstonError):
    """Raised when a Neo4j query fails."""
    error_code = "NEO4J_QUERY_001"
    default_message = "Neo4j query execution failed."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, query: Optional[str] = None):
        final_message = message or self.default_message
        current_context = context or {}
        if query:
            # final_message = f"{final_message} Query: {query[:100]}..." # Adding query to message might be too verbose
            current_context['query'] = query

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=current_context
        )
        self.query = query


# Add the neo4j_retry decorator
def neo4j_retry(max_retries=3, retry_delay=5, retryable_exceptions=(Neo4jConnectionError,)):
    """Decorator to retry Neo4j operations on specified exceptions."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Neo4j operation failed, retrying in {retry_delay}s "
                            f"(attempt {attempt + 1}/{max_retries}): {str(e)}"
                        )
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Neo4j operation failed after {max_retries} attempts: {str(e)}")
                        raise
            raise last_exception
        return wrapper
    return decorator


class Neo4jConfig(ConfigModel):
    """Configuration model for Neo4j connection."""
    uri: str
    username: str
    password: str
    database: str = "neo4j"
    
    # Enhanced connection management options
    connection_pool_size: int = 50
    connection_timeout: int = 30
    max_connection_lifetime: int = 3600
    connection_acquisition_timeout: int = 60
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    encrypted: bool = True
    
    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables."""
        return cls(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            username=os.environ.get("NEO4J_USERNAME", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "password"),
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
            connection_pool_size=int(os.environ.get("NEO4J_CONNECTION_POOL_SIZE", "50")),
            connection_timeout=int(os.environ.get("NEO4J_CONNECTION_TIMEOUT", "30")),
            max_connection_lifetime=int(os.environ.get("NEO4J_MAX_CONNECTION_LIFETIME", "3600")),
            connection_acquisition_timeout=int(os.environ.get("NEO4J_CONNECTION_ACQUISITION_TIMEOUT", "60")),
            retry_attempts=int(os.environ.get("NEO4J_RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.environ.get("NEO4J_RETRY_DELAY", "5")),
            encrypted=os.environ.get("NEO4J_ENCRYPTED", "true").lower() == "true"
        )


class TransactionMetrics:
    """Collect and report metrics on Neo4j transactions."""
    
    def __init__(self):
        """Initialize the transaction metrics."""
        from collections import defaultdict
        self.transaction_counts = defaultdict(int)
        self.transaction_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        
    def record_transaction(self, operation, duration_ms, error=None):
        """Record a transaction for metrics collection.
        
        Args:
            operation: Name of the operation
            duration_ms: Duration in milliseconds
            error: Optional error that occurred
        """
        self.transaction_counts[operation] += 1
        self.transaction_times[operation].append(duration_ms)
        if error:
            self.error_counts[operation] += 1
            
    def get_metrics(self):
        """Get current transaction metrics.
        
        Returns:
            Dict: Transaction metrics including counts, average durations, and error rates
        """
        metrics = {
            "transaction_counts": dict(self.transaction_counts),
            "average_duration_ms": {
                op: sum(times) / len(times) if times else 0
                for op, times in self.transaction_times.items()
            },
            "error_rates": {
                op: self.error_counts[op] / count if count > 0 else 0
                for op, count in self.transaction_counts.items()
            }
        }
        return metrics


class Neo4jClient:
    """Client for interacting with Neo4j graph database."""

    def __init__(self, config: Union[Neo4jConfig, Dict[str, Any]]):
        """Initialize the Neo4j client.
        
        Args:
            config: Neo4j configuration object or dictionary
        """
        # Convert dictionary to config object if needed
        if isinstance(config, dict):
            self.config = Neo4jConfig(**config)
        else:
            self.config = config
            
        self.driver = None
        self.metrics = TransactionMetrics()
        self._connect()
    
    def _create_driver(self):
        """Create and configure the Neo4j driver with connection pooling."""
        try:
            self.driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
                max_connection_pool_size=self.config.connection_pool_size,
                max_connection_lifetime=self.config.max_connection_lifetime,
                connection_acquisition_timeout=self.config.connection_acquisition_timeout
            )
            return True
        except Exception as e:
            error_msg = f"Failed to create Neo4j driver: {str(e)}"
            logger.error(error_msg)
            raise Neo4jConnectionError(error_msg)
    
    def _connect(self) -> None:
        """Connect to the Neo4j database.
        
        Raises:
            Neo4jConnectionError: If connection fails
        """
        try:
            self._create_driver()
            
            # Test connection
            with self._get_session() as session:
                session.run("RETURN 1")
                
            logger.info(f"Successfully connected to Neo4j at {self.config.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j at {self.config.uri}: {str(e)}")
            raise Neo4jConnectionError(f"Failed to connect to Neo4j at {self.config.uri}: {str(e)}")
    
    def _get_session(self) -> Session:
        """Get a Neo4j session.
        
        Returns:
            Session: Neo4j session
            
        Raises:
            Neo4jConnectionError: If not connected to Neo4j
        """
        if not self.driver:
            raise Neo4jConnectionError("Not connected to Neo4j")
        return self.driver.session(database=self.config.database)
    
    def check_connection(self) -> bool:
        """Check if the Neo4j connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            with self._get_session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            logger.warning(f"Connection health check failed: {str(e)}")
            return False
    
    def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Neo4j query.
        
        Args:
            query: Cypher query to execute
            parameters: Query parameters
            
        Returns:
            List[Dict[str, Any]]: List of records as dictionaries
            
        Raises:
            Neo4jQueryError: If query execution fails
        """
        parameters = parameters or {}
        logger.debug(f"Executing Neo4j query: {query}")
        
        try:
            with self._get_session() as session:
                result = session.run(query, parameters)
                # Return all results as a list of dictionaries
                return [dict(record) for record in result]
        except Neo4jError as e:
            logger.error(f"Neo4j query error: {str(e)}")
            raise Neo4jQueryError(f"Neo4j query error: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to execute Neo4j query: {str(e)}")
            raise Neo4jQueryError(f"Failed to execute Neo4j query: {str(e)}")
            
    def with_transaction(self, work_func, access_mode="WRITE", metadata=None):
        """Execute a function within a transaction.
        
        Args:
            work_func: Function to execute within the transaction
            access_mode: Transaction access mode (READ or WRITE)
            metadata: Optional transaction metadata
            
        Returns:
            Result of the work function
            
        Raises:
            Neo4jQueryError: If the transaction fails
        """
        start_time = time.time()
        operation = work_func.__name__ if hasattr(work_func, "__name__") else "transaction"
        tx_metadata = metadata or {}
        
        try:
            with self._get_session() as session:
                if access_mode == "READ":
                    result = session.execute_read(work_func, tx_metadata)
                else:
                    result = session.execute_write(work_func, tx_metadata)
                
                duration_ms = int((time.time() - start_time) * 1000)
                self._log_transaction(tx_metadata, operation, "success", duration_ms)
                self.metrics.record_transaction(operation, duration_ms)
                return result
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_transaction(tx_metadata, operation, "error", duration_ms, error=e)
            self.metrics.record_transaction(operation, duration_ms, error=e)
            raise Neo4jQueryError(f"Transaction failed: {str(e)}")
    
    def _log_transaction(self, metadata, operation, status, duration_ms, error=None):
        """Log transaction details for monitoring and debugging."""
        log_data = {
            "operation": operation,
            "status": status,
            "duration_ms": duration_ms,
            "metadata": metadata
        }
        
        if error:
            log_data["error"] = str(error)
            logger.error(f"Transaction failed", extra=log_data)
        else:
            logger.info(f"Transaction completed", extra=log_data)
    
    def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            self.driver = None
            logger.info("Neo4j connection closed")
    
    def __enter__(self) -> 'Neo4jClient':
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        self.close()
    
    @neo4j_retry(max_retries=3, retry_delay=5)
    def initialize_database(self):
        """Initialize the Neo4j database with required constraints and indexes."""
        try:
            with self._get_session() as session:
                # Create constraints for unique node IDs
                session.run("CREATE CONSTRAINT node_id IF NOT EXISTS ON (n:Node) ASSERT n.id IS UNIQUE")
                session.run("CREATE CONSTRAINT test_id IF NOT EXISTS ON (t:NodeSchema) ASSERT t.id IS UNIQUE")
                session.run("CREATE CONSTRAINT implementation_id IF NOT EXISTS ON (i:Implementation) ASSERT i.id IS UNIQUE")
                session.run("CREATE CONSTRAINT module_id IF NOT EXISTS ON (m:Module) ASSERT m.id IS UNIQUE")
                session.run("CREATE CONSTRAINT fixture_id IF NOT EXISTS ON (f:Fixture) ASSERT f.id IS UNIQUE")
                
                # Create indexes for common query fields
                session.run("CREATE INDEX test_name IF NOT EXISTS FOR (t:Test) ON (t.name)")
                session.run("CREATE INDEX implementation_name IF NOT EXISTS FOR (i:Implementation) ON (i.name)")
                session.run("CREATE INDEX file_path IF NOT EXISTS FOR (n:Node) ON (n.file_path)")
                session.run("CREATE INDEX module_name IF NOT EXISTS FOR (m:Module) ON (m.name)")
                
                logger.info("Neo4j database initialized successfully with constraints and indexes")
                return True
        except Exception as e:
            error_msg = f"Failed to initialize Neo4j database: {str(e)}"
            logger.error(error_msg)
            raise Neo4jQueryError(error_msg)
    
    def create_node(self, node: Node) -> str:
        """Create a node in Neo4j.
        
        Args:
            node: Node to create
            
        Returns:
            str: Node ID
            
        Raises:
            Neo4jQueryError: If node creation fails
        """
        # Convert node to dictionary
        node_data = node.to_dict()
        
        # Extract node data
        node_id = node_data["id"]
        labels = node_data["labels"]
        properties = {
            "id": node_id,
            "schema_type": node_data["_schema_type"],
            "schema_version": node_data["_schema_version"],
            "created_at": node_data["created_at"],
            "updated_at": node_data["updated_at"],
            "properties": json.dumps(node_data["properties"]),
        }
        
        # Create Cypher query
        labels_str = ":".join(labels)
        query = f"""
        MERGE (n:{labels_str} {{id: $id}})
        ON CREATE SET n = $properties
        ON MATCH SET n = $properties
        RETURN n.id
        """
        
        # Execute query
        result = self.execute_query(query, {"id": node_id, "properties": properties})
        
        # Return node ID
        record = result[0]
        if not record:
            raise Neo4jQueryError(f"Failed to create node: {node_id}")
        
        logger.info(f"Created/updated Neo4j node: {node_id}")
        return record["id"]
    
    def create_relationship(self, relationship: Relationship) -> str:
        """Create a relationship in Neo4j.
        
        Args:
            relationship: Relationship to create
            
        Returns:
            str: Relationship ID
            
        Raises:
            Neo4jQueryError: If relationship creation fails
        """
        # Convert relationship to dictionary
        rel_data = relationship.to_dict()
        
        # Extract relationship data
        rel_id = rel_data["id"]
        rel_type = rel_data["type"].upper()
        source_id = rel_data["source_id"]
        target_id = rel_data["target_id"]
        properties = {
            "id": rel_id,
            "schema_type": rel_data["_schema_type"],
            "schema_version": rel_data["_schema_version"],
            "created_at": rel_data["created_at"],
            "updated_at": rel_data["updated_at"],
            "properties": json.dumps(rel_data["properties"]),
        }
        
        # Create Cypher query
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel_type} {{id: $rel_id}}]->(target)
        ON CREATE SET r = $properties
        ON MATCH SET r = $properties
        RETURN r.id
        """
        
        # Execute query
        result = self.execute_query(query, {
            "source_id": source_id,
            "target_id": target_id,
            "rel_id": rel_id,
            "properties": properties,
        })
        
        # Return relationship ID
        record = result[0]
        if not record:
            raise Neo4jQueryError(f"Failed to create relationship: {rel_id}")
        
        logger.info(f"Created/updated Neo4j relationship: {rel_id}")
        return record["id"]
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node from Neo4j by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            Optional[Dict[str, Any]]: Node data or None if not found
        """
        query = """
        MATCH (n {id: $id})
        RETURN n
        """
        
        result = self.execute_query(query, {"id": node_id})
        record = result[0]
        
        if not record:
            return None
        
        node = dict(record)
        
        # Parse properties from JSON
        if "properties" in node and isinstance(node["properties"], str):
            node["properties"] = json.loads(node["properties"])
        
        return node
    
    def get_relationship(self, relationship_id: str) -> Optional[Dict[str, Any]]:
        """Get a relationship from Neo4j by ID.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Optional[Dict[str, Any]]: Relationship data or None if not found
        """
        query = """
        MATCH ()-[r {id: $id}]->()
        RETURN r
        """
        
        result = self.execute_query(query, {"id": relationship_id})
        record = result[0]
        
        if not record:
            return None
        
        relationship = dict(record)
        
        # Parse properties from JSON
        if "properties" in relationship and isinstance(relationship["properties"], str):
            relationship["properties"] = json.dumps(relationship["properties"])
        
        return relationship
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node from Neo4j by ID.
        
        Args:
            node_id: Node ID
            
        Returns:
            bool: True if node was deleted, False if not found
        """
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        
        result = self.execute_query(query, {"id": node_id})
        record = result[0]
        
        if not record or record["deleted"] == 0:
            return False
        
        logger.info(f"Deleted Neo4j node: {node_id}")
        return True
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship from Neo4j by ID.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            bool: True if relationship was deleted, False if not found
        """
        query = """
        MATCH ()-[r {id: $id}]->()
        DELETE r
        RETURN count(r) as deleted
        """
        
        result = self.execute_query(query, {"id": relationship_id})
        record = result[0]
        
        if not record or record["deleted"] == 0:
            return False
        
        logger.info(f"Deleted Neo4j relationship: {relationship_id}")
        return True
    
    def find_nodes_by_label(self, label: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find nodes by label.
        
        Args:
            label: Node label to search for
            limit: Maximum number of nodes to return
            
        Returns:
            List[Dict[str, Any]]: List of matching nodes
        """
        query = f"""
        MATCH (n:{label})
        RETURN n
        LIMIT $limit
        """
        
        result = self.execute_query(query, {"limit": limit})
        nodes = []
        
        for record in result:
            node = dict(record)
            
            # Parse properties from JSON
            if "properties" in node and isinstance(node["properties"], str):
                node["properties"] = json.loads(node["properties"])
            
            nodes.append(node)
        
        return nodes
    
    def find_relationships_by_type(self, rel_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Find relationships by type.
        
        Args:
            rel_type: Relationship type to search for
            limit: Maximum number of relationships to return
            
        Returns:
            List[Dict[str, Any]]: List of matching relationships
        """
        query = f"""
        MATCH ()-[r:{rel_type.upper()}]->()
        RETURN r
        LIMIT $limit
        """
        
        result = self.execute_query(query, {"limit": limit})
        relationships = []
        
        for record in result:
            rel = dict(record)
            
            # Parse properties from JSON
            if "properties" in rel and isinstance(rel["properties"], str):
                rel["properties"] = json.loads(rel["properties"])
            
            relationships.append(rel)
        
        return relationships
    
    def get_node_relationships(
        self, 
        node_id: str, 
        rel_type: Optional[str] = None,
        direction: str = "both"
    ) -> List[Dict[str, Any]]:
        """Get relationships for a node.
        
        Args:
            node_id: Node ID
            rel_type: Relationship type (optional)
            direction: Relationship direction ('outgoing', 'incoming', or 'both')
            
        Returns:
            List[Dict[str, Any]]: List of relationships
        """
        if direction.lower() == "outgoing":
            pattern = "(n)-[r]->()"
        elif direction.lower() == "incoming":
            pattern = "(n)<-[r]-()"
        else:
            pattern = "(n)-[r]-()"
        
        rel_type_str = f":{rel_type.upper()}" if rel_type else ""
        
        query = f"""
        MATCH {pattern}
        WHERE n.id = $node_id {f"AND type(r) = '{rel_type.upper()}'" if rel_type else ""}
        RETURN r
        """
        
        result = self.execute_query(query, {"node_id": node_id})
        relationships = []
        
        for record in result:
            rel = dict(record)
            
            # Parse properties from JSON
            if "properties" in rel and isinstance(rel["properties"], str):
                rel["properties"] = json.loads(rel["properties"])
            
            relationships.append(rel)
        
        return relationships
    
    def create_index(self, label: str, property_name: str) -> None:
        """Create an index on a node label and property.
        
        Args:
            label: Node label
            property_name: Property name
        """
        query = f"""
        CREATE INDEX {label}_{property_name}_idx IF NOT EXISTS
        FOR (n:{label})
        ON (n.{property_name})
        """
        
        self.execute_query(query)
        logger.info(f"Created Neo4j index on {label}.{property_name}")
    
    def create_constraint(self, label: str, property_name: str) -> None:
        """Create a uniqueness constraint on a node label and property.
        
        Args:
            label: Node label
            property_name: Property name
        """
        constraint_name = f"{label}_{property_name}_unique"
        query = f"""
        CREATE CONSTRAINT {constraint_name} IF NOT EXISTS
        FOR (n:{label})
        REQUIRE n.{property_name} IS UNIQUE
        """
        
        self.execute_query(query)
        logger.info(f"Created Neo4j constraint on {label}.{property_name}")
    
    def create_schema_item(self, item: SchemaItem) -> str:
        """Create a schema item (node or relationship) in Neo4j.
        
        Args:
            item: Schema item to create
            
        Returns:
            str: Item ID
        """
        if isinstance(item, Node):
            return self.create_node(item)
        elif isinstance(item, Relationship):
            return self.create_relationship(item)
        else:
            raise ValueError(f"Unsupported schema item type: {type(item)}")
    
    def delete_schema_item(self, item: Union[SchemaItem, str]) -> bool:
        """Delete a schema item (node or relationship) from Neo4j.
        
        Args:
            item: Schema item or ID to delete
            
        Returns:
            bool: True if item was deleted, False if not found
        """
        item_id = item.id if isinstance(item, SchemaItem) else item
        
        # Try deleting as relationship first
        if self.delete_relationship(item_id):
            return True
        
        # If not a relationship, try deleting as node
        return self.delete_node(item_id)
    
    def create_schema_items(self, items: List[SchemaItem]) -> List[str]:
        """Create multiple schema items in Neo4j.
        
        Args:
            items: List of schema items to create
            
        Returns:
            List[str]: List of created item IDs
        """
        ids = []
        for item in items:
            ids.append(self.create_schema_item(item))
        return ids
    
    def clear_database(self) -> None:
        """Clear all nodes and relationships from the database.
        
        Warning: This will delete all data in the database.
        """
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        
        self.execute_query(query)
        logger.warning("Cleared all data from Neo4j database")
    
    def create_schema_indexes(self) -> None:
        """Create indexes for common node and relationship properties."""
        # Node indexes
        for label in ["NodeSchema", "ImplementationNode", "ModuleNode", "FixtureNode"]:
            self.create_index(label, "id")
            self.create_constraint(label, "id")
        
        # Other common properties
        for label in ["NodeSchema", "ImplementationNode", "ModuleNode", "FixtureNode"]:
            self.create_index(label, "properties")
        
        logger.info("Created Neo4j schema indexes") 