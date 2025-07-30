"""
Batch operations for the knowledge graph.

This module provides utilities for efficient batch operations on the
knowledge graph, such as bulk imports, updates, and deletions.
"""

import json
import os
import tempfile
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from testindex.core.exceptions import AstonError
from testindex.core.logging import get_logger
from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jQueryError
from testindex.knowledge.schema.base import Node, Relationship, SchemaItem
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

logger = get_logger(__name__)


class BatchOperationError(AstonError):
    """Exception raised for errors during batch operations on the graph in this module."""
    error_code = "KG_BATCH_OPS_001"
    default_message = "An error occurred during a graph batch operation."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, operation: Optional[str] = None, batch_size: Optional[int] = None):
        final_message = message or self.default_message
        current_context = context or {}
        if operation:
            current_context['operation'] = operation
        if batch_size is not None:
            current_context['batch_size'] = batch_size

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=current_context
        )
        self.operation = operation
        self.batch_size = batch_size


class BatchOperations:
    """Batch operations for the knowledge graph.
    
    This class provides methods for efficient batch operations on the
    knowledge graph, such as bulk imports, updates, and deletions.
    """
    
    def __init__(self, client: Neo4jClient):
        """Initialize batch operations.
        
        Args:
            client: Neo4j client
        """
        self.client = client
        self.batch_size = 1000  # Default batch size
    
    def set_batch_size(self, batch_size: int) -> None:
        """Set the batch size for operations.
        
        Args:
            batch_size: Batch size
        """
        if batch_size < 1:
            raise ValueError("Batch size must be at least 1")
        self.batch_size = batch_size
        logger.info(f"Batch size set to {batch_size}")
    
    def batch_create_nodes(self, nodes: List[Node]) -> List[str]:
        """Create multiple nodes in batches.
        
        Args:
            nodes: List of nodes to create
            
        Returns:
            List[str]: List of created node IDs
        """
        if not nodes:
            return []
        
        created_ids = []
        total_nodes = len(nodes)
        logger.info(f"Creating {total_nodes} nodes in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_nodes, self.batch_size):
            batch = nodes[i:i + self.batch_size]
            
            # Prepare batch data
            batch_data = []
            for node in batch:
                node_data = node.to_dict()
                batch_data.append({
                    "id": node_data["id"],
                    "labels": node_data["labels"],
                    "schema_type": node_data["_schema_type"],
                    "schema_version": node_data["_schema_version"],
                    "created_at": node_data["created_at"],
                    "updated_at": node_data["updated_at"],
                    "properties": json.dumps(node_data["properties"]),
                })
            
            # Create query
            query = """
            UNWIND $batch as row
            MERGE (n:Node {id: row.id})
            SET n = row,
                n += {properties: row.properties}
            WITH n, row
            CALL apoc.create.addLabels(n, row.labels) YIELD node
            RETURN collect(n.id) as ids
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch_data})
                record = result.single()
                if record and record[0]:
                    created_ids.extend(record[0])
                logger.info(f"Created {len(batch)} nodes (batch {i // self.batch_size + 1}/{(total_nodes - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error creating node batch: {str(e)}")
                raise BatchOperationError(f"Failed to create node batch: {str(e)}")
        
        return created_ids
    
    def batch_create_relationships(self, relationships: List[Relationship]) -> List[str]:
        """Create multiple relationships in batches.
        
        Args:
            relationships: List of relationships to create
            
        Returns:
            List[str]: List of created relationship IDs
        """
        if not relationships:
            return []
        
        created_ids = []
        total_rels = len(relationships)
        logger.info(f"Creating {total_rels} relationships in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_rels, self.batch_size):
            batch = relationships[i:i + self.batch_size]
            
            # Prepare batch data
            batch_data = []
            for rel in batch:
                rel_data = rel.to_dict()
                batch_data.append({
                    "id": rel_data["id"],
                    "type": rel_data["type"].upper(),
                    "source_id": rel_data["source_id"],
                    "target_id": rel_data["target_id"],
                    "schema_type": rel_data["_schema_type"],
                    "schema_version": rel_data["_schema_version"],
                    "created_at": rel_data["created_at"],
                    "updated_at": rel_data["updated_at"],
                    "properties": json.dumps(rel_data["properties"]),
                })
            
            # Create query
            query = """
            UNWIND $batch as row
            MATCH (source {id: row.source_id})
            MATCH (target {id: row.target_id})
            CALL apoc.merge.relationship(source, row.type, {id: row.id}, 
                {
                    id: row.id,
                    schema_type: row.schema_type,
                    schema_version: row.schema_version,
                    created_at: row.created_at,
                    updated_at: row.updated_at,
                    properties: row.properties
                }, target) YIELD rel
            RETURN collect(rel.id) as ids
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch_data})
                record = result.single()
                if record and record[0]:
                    created_ids.extend(record[0])
                logger.info(f"Created {len(batch)} relationships (batch {i // self.batch_size + 1}/{(total_rels - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error creating relationship batch: {str(e)}")
                raise BatchOperationError(f"Failed to create relationship batch: {str(e)}")
        
        return created_ids
    
    def batch_delete_nodes(self, node_ids: List[str]) -> int:
        """Delete multiple nodes in batches.
        
        Args:
            node_ids: List of node IDs to delete
            
        Returns:
            int: Number of deleted nodes
        """
        if not node_ids:
            return 0
        
        total_deleted = 0
        total_nodes = len(node_ids)
        logger.info(f"Deleting {total_nodes} nodes in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_nodes, self.batch_size):
            batch = node_ids[i:i + self.batch_size]
            
            # Create query
            query = """
            UNWIND $batch as id
            MATCH (n {id: id})
            DETACH DELETE n
            RETURN count(n) as deleted
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch})
                record = result.single()
                if record:
                    batch_deleted = record[0]
                    total_deleted += batch_deleted
                    logger.info(f"Deleted {batch_deleted} nodes (batch {i // self.batch_size + 1}/{(total_nodes - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error deleting node batch: {str(e)}")
                raise BatchOperationError(f"Failed to delete node batch: {str(e)}")
        
        return total_deleted
    
    def batch_delete_relationships(self, relationship_ids: List[str]) -> int:
        """Delete multiple relationships in batches.
        
        Args:
            relationship_ids: List of relationship IDs to delete
            
        Returns:
            int: Number of deleted relationships
        """
        if not relationship_ids:
            return 0
        
        total_deleted = 0
        total_rels = len(relationship_ids)
        logger.info(f"Deleting {total_rels} relationships in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_rels, self.batch_size):
            batch = relationship_ids[i:i + self.batch_size]
            
            # Create query
            query = """
            UNWIND $batch as id
            MATCH ()-[r {id: id}]->()
            DELETE r
            RETURN count(r) as deleted
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch})
                record = result.single()
                if record:
                    batch_deleted = record[0]
                    total_deleted += batch_deleted
                    logger.info(f"Deleted {batch_deleted} relationships (batch {i // self.batch_size + 1}/{(total_rels - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error deleting relationship batch: {str(e)}")
                raise BatchOperationError(f"Failed to delete relationship batch: {str(e)}")
        
        return total_deleted
    
    def batch_create_schema_items(self, items: List[SchemaItem]) -> Dict[str, List[str]]:
        """Create multiple schema items (nodes and relationships) in batches.
        
        Args:
            items: List of schema items to create
            
        Returns:
            Dict[str, List[str]]: Dictionary with lists of created node and relationship IDs
        """
        if not items:
            return {"nodes": [], "relationships": []}
        
        # Separate nodes and relationships
        nodes = []
        relationships = []
        for item in items:
            if isinstance(item, Node):
                nodes.append(item)
            elif isinstance(item, Relationship):
                relationships.append(item)
            else:
                logger.warning(f"Unsupported schema item type: {type(item)}")
        
        # Create nodes first, then relationships
        node_ids = self.batch_create_nodes(nodes)
        relationship_ids = self.batch_create_relationships(relationships)
        
        return {
            "nodes": node_ids,
            "relationships": relationship_ids,
        }
    
    def batch_delete_schema_items(self, items: List[Union[SchemaItem, str]]) -> Dict[str, int]:
        """Delete multiple schema items (nodes and relationships) in batches.
        
        Args:
            items: List of schema items or IDs to delete
            
        Returns:
            Dict[str, int]: Dictionary with counts of deleted nodes and relationships
        """
        if not items:
            return {"nodes": 0, "relationships": 0}
        
        # Convert items to IDs
        item_ids = [item.id if isinstance(item, SchemaItem) else item for item in items]
        
        # We need to query the database to determine which IDs are nodes and which are relationships
        try:
            # Check which IDs are relationships
            query = """
            UNWIND $ids as id
            OPTIONAL MATCH ()-[r {id: id}]->()
            WITH id, r
            WHERE r IS NOT NULL
            RETURN collect(id) as rel_ids
            """
            result = self.client.execute_query(query, {"ids": item_ids})
            record = result.single()
            rel_ids = record[0] if record and record[0] else []
            
            # All other IDs are assumed to be nodes
            node_ids = [id for id in item_ids if id not in rel_ids]
            
            # Delete relationships first (to avoid constraint violations)
            rels_deleted = self.batch_delete_relationships(rel_ids)
            nodes_deleted = self.batch_delete_nodes(node_ids)
            
            return {
                "relationships": rels_deleted,
                "nodes": nodes_deleted,
            }
        except Neo4jQueryError as e:
            logger.error(f"Error identifying item types: {str(e)}")
            raise BatchOperationError(f"Failed to identify item types: {str(e)}")
    
    def batch_update_node_properties(self, updates: List[Dict[str, Any]]) -> int:
        """Update properties of multiple nodes in batches.
        
        Args:
            updates: List of update objects, each containing:
                - node_id: ID of the node to update
                - properties: Dict of properties to update or add
                
        Returns:
            int: Number of updated nodes
        """
        if not updates:
            return 0
        
        total_updated = 0
        total_updates = len(updates)
        logger.info(f"Updating {total_updates} nodes in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_updates, self.batch_size):
            batch = updates[i:i + self.batch_size]
            
            # Prepare batch data
            batch_data = []
            for update in batch:
                batch_data.append({
                    "id": update["node_id"],
                    "properties": json.dumps(update["properties"]),
                })
            
            # Create query
            query = """
            UNWIND $batch as row
            MATCH (n {id: row.id})
            WITH n, row, apoc.convert.fromJsonMap(n.properties) as old_props
            WITH n, row, apoc.map.merge(old_props, apoc.convert.fromJsonMap(row.properties)) as merged_props
            SET n.properties = apoc.convert.toJson(merged_props),
                n.updated_at = datetime()
            RETURN count(n) as updated
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch_data})
                record = result.single()
                if record:
                    batch_updated = record[0]
                    total_updated += batch_updated
                    logger.info(f"Updated {batch_updated} nodes (batch {i // self.batch_size + 1}/{(total_updates - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error updating node batch: {str(e)}")
                raise BatchOperationError(f"Failed to update node batch: {str(e)}")
        
        return total_updated
    
    def batch_update_relationship_properties(self, updates: List[Dict[str, Any]]) -> int:
        """Update properties of multiple relationships in batches.
        
        Args:
            updates: List of update objects, each containing:
                - relationship_id: ID of the relationship to update
                - properties: Dict of properties to update or add
                
        Returns:
            int: Number of updated relationships
        """
        if not updates:
            return 0
        
        total_updated = 0
        total_updates = len(updates)
        logger.info(f"Updating {total_updates} relationships in batches of {self.batch_size}")
        
        # Process in batches
        for i in range(0, total_updates, self.batch_size):
            batch = updates[i:i + self.batch_size]
            
            # Prepare batch data
            batch_data = []
            for update in batch:
                batch_data.append({
                    "id": update["relationship_id"],
                    "properties": json.dumps(update["properties"]),
                })
            
            # Create query
            query = """
            UNWIND $batch as row
            MATCH ()-[r {id: row.id}]->()
            WITH r, row, apoc.convert.fromJsonMap(r.properties) as old_props
            WITH r, row, apoc.map.merge(old_props, apoc.convert.fromJsonMap(row.properties)) as merged_props
            SET r.properties = apoc.convert.toJson(merged_props),
                r.updated_at = datetime()
            RETURN count(r) as updated
            """
            
            try:
                result = self.client.execute_query(query, {"batch": batch_data})
                record = result.single()
                if record:
                    batch_updated = record[0]
                    total_updated += batch_updated
                    logger.info(f"Updated {batch_updated} relationships (batch {i // self.batch_size + 1}/{(total_updates - 1) // self.batch_size + 1})")
            except Neo4jQueryError as e:
                logger.error(f"Error updating relationship batch: {str(e)}")
                raise BatchOperationError(f"Failed to update relationship batch: {str(e)}")
        
        return total_updated
    
    def import_json_nodes(self, json_file: str) -> int:
        """Import nodes from a JSON file.
        
        Args:
            json_file: Path to JSON file containing node data
                Format: List of dictionaries with node properties
                
        Returns:
            int: Number of imported nodes
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of node data")
            
            # Create query
            query = """
            CALL apoc.load.json($file) YIELD value
            UNWIND value as node
            MERGE (n:Node {id: node.id})
            SET n = node,
                n += {properties: node.properties}
            WITH n, node
            CALL apoc.create.addLabels(n, node.labels) YIELD node as updated_node
            RETURN count(updated_node) as imported
            """
            
            result = self.client.execute_query(query, {"file": os.path.abspath(json_file)})
            record = result.single()
            
            imported_count = record[0] if record else 0
            logger.info(f"Imported {imported_count} nodes from {json_file}")
            
            return imported_count
        except Exception as e:
            logger.error(f"Error importing nodes from JSON: {str(e)}")
            raise BatchOperationError(f"Failed to import nodes from JSON: {str(e)}")
    
    def import_json_relationships(self, json_file: str) -> int:
        """Import relationships from a JSON file.
        
        Args:
            json_file: Path to JSON file containing relationship data
                Format: List of dictionaries with relationship properties
                
        Returns:
            int: Number of imported relationships
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON file must contain a list of relationship data")
            
            # Create query
            query = """
            CALL apoc.load.json($file) YIELD value
            UNWIND value as rel
            MATCH (source {id: rel.source_id})
            MATCH (target {id: rel.target_id})
            CALL apoc.merge.relationship(source, rel.type, {id: rel.id}, rel, target) YIELD rel as created_rel
            RETURN count(created_rel) as imported
            """
            
            result = self.client.execute_query(query, {"file": os.path.abspath(json_file)})
            record = result.single()
            
            imported_count = record[0] if record else 0
            logger.info(f"Imported {imported_count} relationships from {json_file}")
            
            return imported_count
        except Exception as e:
            logger.error(f"Error importing relationships from JSON: {str(e)}")
            raise BatchOperationError(f"Failed to import relationships from JSON: {str(e)}")
    
    def export_nodes_to_json(self, file_path: str, labels: Optional[List[str]] = None, limit: int = 10000) -> int:
        """Export nodes to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
            labels: Optional list of node labels to filter by
            limit: Maximum number of nodes to export
            
        Returns:
            int: Number of exported nodes
        """
        try:
            # Create the query
            if labels:
                label_str = ':' + ':'.join(labels)
                query = f"""
                MATCH (n{label_str})
                RETURN n LIMIT $limit
                """
            else:
                query = """
                MATCH (n)
                RETURN n LIMIT $limit
                """
            
            # Execute the query
            result = self.client.execute_query(query, {"limit": limit})
            
            # Extract nodes
            nodes = []
            for record in result:
                node = dict(record[0])
                nodes.append(node)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(nodes, f, indent=2)
            
            logger.info(f"Exported {len(nodes)} nodes to {file_path}")
            return len(nodes)
        except Exception as e:
            logger.error(f"Error exporting nodes to JSON: {str(e)}")
            raise BatchOperationError(f"Failed to export nodes to JSON: {str(e)}")
    
    def export_relationships_to_json(self, file_path: str, types: Optional[List[str]] = None, limit: int = 10000) -> int:
        """Export relationships to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
            types: Optional list of relationship types to filter by
            limit: Maximum number of relationships to export
            
        Returns:
            int: Number of exported relationships
        """
        try:
            # Create the query
            if types:
                type_str = '|'.join([t.upper() for t in types])
                query = f"""
                MATCH ()-[r:{type_str}]->()
                RETURN r LIMIT $limit
                """
            else:
                query = """
                MATCH ()-[r]->()
                RETURN r LIMIT $limit
                """
            
            # Execute the query
            result = self.client.execute_query(query, {"limit": limit})
            
            # Extract relationships
            relationships = []
            for record in result:
                rel = dict(record[0])
                relationships.append(rel)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(relationships, f, indent=2)
            
            logger.info(f"Exported {len(relationships)} relationships to {file_path}")
            return len(relationships)
        except Exception as e:
            logger.error(f"Error exporting relationships to JSON: {str(e)}")
            raise BatchOperationError(f"Failed to export relationships to JSON: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Dict[str, Any]: Dictionary with database statistics
        """
        try:
            # Node count by label
            node_query = """
            MATCH (n)
            RETURN labels(n) as label, count(n) as count
            """
            node_result = self.client.execute_query(node_query)
            
            node_counts = {}
            for record in node_result:
                labels = record[0]
                count = record[1]
                label_key = ':'.join(labels) if labels else 'unlabeled'
                node_counts[label_key] = count
            
            # Relationship count by type
            rel_query = """
            MATCH ()-[r]->()
            RETURN type(r) as type, count(r) as count
            """
            rel_result = self.client.execute_query(rel_query)
            
            rel_counts = {}
            for record in rel_result:
                rel_type = record[0]
                count = record[1]
                rel_counts[rel_type] = count
            
            # Database info
            info_query = """
            CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version
            """
            info_result = self.client.execute_query(info_query)
            
            db_info = {}
            for record in info_result:
                name = record[0]
                version = record[1]
                db_info[name] = version
            
            return {
                "node_counts": node_counts,
                "relationship_counts": rel_counts,
                "total_nodes": sum(node_counts.values()),
                "total_relationships": sum(rel_counts.values()),
                "database_info": db_info,
            }
        except Exception as e:
            logger.error(f"Error getting database statistics: {str(e)}")
            raise BatchOperationError(f"Failed to get database statistics: {str(e)}") 