#!/usr/bin/env python
"""
Example script demonstrating batch operations on a knowledge graph.
This script shows how to efficiently create, update, and delete nodes and relationships in batches.
"""

import json
import random
import logging
from pathlib import Path

from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jConfig
from testindex.knowledge.graph.batch_operations import BatchOperations
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode
from testindex.knowledge.schema.relationships import TestsRelationship

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function demonstrating batch operations"""
    # Configure Neo4j client
    config = Neo4jConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password",
        database="neo4j"
    )
    client = Neo4jClient(config)
    
    # Create BatchOperations instance
    batch_ops = BatchOperations(client)
    batch_ops.set_batch_size(500)  # Set custom batch size
    
    # 1. Create a large batch of test nodes
    logger.info("Creating test nodes in batch...")
    test_nodes = [
        NodeSchema(
            id=f"test_function_{i}",
            name=f"test_function_{i}",
            file_path=f"tests/test_module_{i//10}.py",
            line_number=random.randint(10, 200),
            description=f"Test function {i} to verify module functionality"
        )
        for i in range(1000)
    ]
    test_node_ids = batch_ops.batch_create_nodes(test_nodes)
    logger.info(f"Created {len(test_node_ids)} test nodes")
    
    # 2. Create a large batch of implementation nodes
    logger.info("Creating implementation nodes in batch...")
    impl_nodes = [
        ImplementationNode(
            name=f"function_{i}",
            file_path=f"src/module_{i//10}.py",
            line_number=random.randint(5, 150),
            description=f"Implementation function {i}"
        )
        for i in range(800)
    ]
    impl_node_ids = batch_ops.batch_create_nodes(impl_nodes)
    logger.info(f"Created {len(impl_node_ids)} implementation nodes")
    
    # 3. Create relationships between tests and implementations
    logger.info("Creating test relationships in batch...")
    relationships = []
    for i in range(min(len(test_nodes), len(impl_nodes))):
        if i % 2 == 0:  # Create relationships for half of the nodes
            rel = TestsRelationship(
                source_node=test_nodes[i],
                target_node=impl_nodes[i],
                confidence=random.uniform(0.7, 1.0),
                detection_method="static_analysis"
            )
            relationships.append(rel)
    
    rel_ids = batch_ops.batch_create_relationships(relationships)
    logger.info(f"Created {len(rel_ids)} test relationships")
    
    # 4. Update properties for a subset of nodes
    logger.info("Updating node properties in batch...")
    node_updates = []
    for i in range(0, len(test_nodes), 5):  # Update every 5th node
        node_id = test_node_ids[i]
        # New properties to set
        properties = {
            "priority": random.choice(["high", "medium", "low"]),
            "last_execution_time": random.uniform(0.1, 2.5),
            "tags": json.dumps(["updated", f"batch_{i//100}"])
        }
        node_updates.append((node_id, properties))
    
    batch_ops.batch_update_node_properties(node_updates)
    logger.info(f"Updated properties for {len(node_updates)} nodes")
    
    # 5. Export nodes and relationships to JSON for backup/analysis
    export_dir = Path("./exports")
    export_dir.mkdir(exist_ok=True)
    
    logger.info("Exporting nodes to JSON...")
    batch_ops.export_nodes_to_json(
        str(export_dir / "test_nodes.json"),
        labels=["Test"],
        limit=100
    )
    
    batch_ops.export_nodes_to_json(
        str(export_dir / "implementation_nodes.json"),
        labels=["Implementation"],
        limit=100
    )
    
    logger.info("Exporting relationships to JSON...")
    batch_ops.export_relationships_to_json(
        str(export_dir / "test_relationships.json"),
        relationship_types=["TESTS"],
        limit=100
    )
    
    # 6. Delete a subset of the relationships
    logger.info("Deleting relationships in batch...")
    rel_ids_to_delete = rel_ids[::3]  # Delete every 3rd relationship
    deleted_count = batch_ops.batch_delete_relationships(rel_ids_to_delete)
    logger.info(f"Deleted {deleted_count} relationships")
    
    # 7. Delete a subset of nodes
    logger.info("Deleting nodes in batch...")
    node_ids_to_delete = test_node_ids[::4]  # Delete every 4th test node
    deleted_node_count = batch_ops.batch_delete_nodes(node_ids_to_delete)
    logger.info(f"Deleted {deleted_node_count} nodes")
    
    # 8. Get database statistics
    stats = batch_ops.get_stats()
    logger.info("Database statistics:")
    logger.info(f"  Total nodes: {stats['total_nodes']}")
    logger.info(f"  Total relationships: {stats['total_relationships']}")
    logger.info(f"  Node label counts: {stats['node_label_counts']}")
    logger.info(f"  Relationship type counts: {stats['relationship_type_counts']}")

if __name__ == "__main__":
    main() 