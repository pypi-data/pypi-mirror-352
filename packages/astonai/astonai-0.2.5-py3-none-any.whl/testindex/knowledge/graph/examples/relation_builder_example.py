#!/usr/bin/env python
"""
Example script demonstrating the RelationBuilder for creating relationships
between nodes in the knowledge graph based on code analysis results.
"""

import logging
from typing import List, Dict, Any

from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jConfig
from testindex.knowledge.graph.relation_builder import RelationBuilder
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode, ModuleNode
from testindex.knowledge.schema.relationships import (
    TestsRelationship,
    ImportRelationship,
    ContainsRelationship
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function demonstrating relation builder operations"""
    # Configure Neo4j client
    config = Neo4jConfig(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password",
        database="neo4j"
    )
    client = Neo4jClient(config)
    
    # Create RelationBuilder instance
    relation_builder = RelationBuilder(client)
    
    # Create example nodes
    logger.info("Creating example nodes...")
    
    # Module nodes representing Python modules
    auth_module = ModuleNode(
        name="auth",
        file_path="src/auth.py",
        description="Authentication module providing user verification"
    )
    
    user_module = ModuleNode(
        name="user",
        file_path="src/user.py",
        description="User management module"
    )
    
    test_auth_module = ModuleNode(
        name="test_auth",
        file_path="tests/test_auth.py",
        description="Tests for authentication module"
    )
    
    # Implementation nodes
    login_func = ImplementationNode(
        name="login",
        file_path="src/auth.py",
        line_number=12,
        description="Function to authenticate user credentials"
    )
    
    verify_token_func = ImplementationNode(
        name="verify_token",
        file_path="src/auth.py",
        line_number=45,
        description="Function to verify JWT token"
    )
    
    get_user_func = ImplementationNode(
        name="get_user",
        file_path="src/user.py",
        line_number=23,
        description="Function to retrieve user details"
    )
    
    # Test nodes
    test_login_func = NodeSchema(
        id="test_login_function",
        name="test_login_function",
        file_path="tests/test_auth.py",
        line_number=15,
        description="Test for login functionality"
    )
    
    test_verify_token_func = NodeSchema(
        id="test_verify_token_function",
        name="test_verify_token_function",
        file_path="tests/test_auth.py",
        line_number=38,
        description="Test for token verification"
    )
    
    # Save all nodes to the database
    nodes = [
        auth_module, user_module, test_auth_module,
        login_func, verify_token_func, get_user_func,
        test_login_func, test_verify_token_func
    ]
    
    node_ids = []
    for node in nodes:
        node_id = client.create_node(node)
        node.id = node_id
        node_ids.append(node_id)
        logger.info(f"Created node: {node.name} with ID: {node_id}")
    
    # Example 1: Create test relationships
    logger.info("Building test relationships based on code coverage analysis...")
    
    # Simulate code coverage data from a coverage report
    code_coverage_data = [
        {"test": "test_login", "implementation": "login", "coverage_percent": 92.5},
        {"test": "test_verify_token", "implementation": "verify_token", "coverage_percent": 87.8},
        {"test": "test_login", "implementation": "verify_token", "coverage_percent": 15.2}
    ]
    
    # Build relationships based on coverage data
    for coverage_item in code_coverage_data:
        # Find the test node
        test_node = next(
            (n for n in nodes if isinstance(n, NodeSchema) and n.name == coverage_item["test"]),
            None
        )
        
        # Find the implementation node
        impl_node = next(
            (n for n in nodes if isinstance(n, ImplementationNode) and n.name == coverage_item["implementation"]),
            None
        )
        
        if test_node and impl_node:
            # Create the relationship with confidence based on coverage percentage
            confidence = coverage_item["coverage_percent"] / 100.0
            relationship = relation_builder.create_test_relationship(
                test_node,
                impl_node,
                confidence=confidence,
                detection_method="code_coverage"
            )
            logger.info(
                f"Created test relationship: {test_node.name} TESTS {impl_node.name} "
                f"with confidence {confidence:.2f}"
            )
    
    # Example 2: Create module hierarchy relationships
    logger.info("Building module containment relationships...")
    
    # Create containment relationships between modules and functions
    relation_builder.create_contains_relationship(
        auth_module, login_func, relation_type="CONTAINS_FUNCTION"
    )
    
    relation_builder.create_contains_relationship(
        auth_module, verify_token_func, relation_type="CONTAINS_FUNCTION"
    )
    
    relation_builder.create_contains_relationship(
        user_module, get_user_func, relation_type="CONTAINS_FUNCTION"
    )
    
    relation_builder.create_contains_relationship(
        test_auth_module, test_login_func, relation_type="CONTAINS_TEST"
    )
    
    relation_builder.create_contains_relationship(
        test_auth_module, test_verify_token_func, relation_type="CONTAINS_TEST"
    )
    
    # Example 3: Create import relationships based on static analysis
    logger.info("Building import relationships based on static analysis...")
    
    # Simulate import data from static analysis
    import_data = [
        {"source": "test_auth", "target": "auth", "import_type": "module"},
        {"source": "user", "target": "auth", "import_type": "module"},
    ]
    
    for import_item in import_data:
        source_module = next(
            (n for n in nodes if isinstance(n, ModuleNode) and n.name == import_item["source"]),
            None
        )
        
        target_module = next(
            (n for n in nodes if isinstance(n, ModuleNode) and n.name == import_item["target"]),
            None
        )
        
        if source_module and target_module:
            import_relationship = relation_builder.create_import_relationship(
                source_module,
                target_module,
                import_type=import_item["import_type"]
            )
            logger.info(
                f"Created import relationship: {source_module.name} IMPORTS {target_module.name}"
            )
    
    # Example 4: Find related test for an implementation
    logger.info("Finding related tests for implementations...")
    related_tests = relation_builder.find_related_tests(login_func)
    logger.info(f"Tests related to {login_func.name}:")
    for test, relationship in related_tests:
        logger.info(f"  - {test.name} (confidence: {relationship.properties.get('confidence', 'N/A')})")
    
    # Example 5: Find related implementations for a test
    related_impls = relation_builder.find_related_implementations(test_login_func)
    logger.info(f"Implementations related to {test_login_func.name}:")
    for impl, relationship in related_impls:
        logger.info(f"  - {impl.name} (confidence: {relationship.properties.get('confidence', 'N/A')})")
    
    # Example 6: Get module dependency graph
    logger.info("Generating module dependency graph...")
    dependency_graph = relation_builder.get_module_dependency_graph()
    
    logger.info("Module dependencies:")
    for source, targets in dependency_graph.items():
        logger.info(f"  {source} imports:")
        for target in targets:
            logger.info(f"    - {target}")

if __name__ == "__main__":
    main() 