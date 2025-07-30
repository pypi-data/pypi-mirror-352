"""
Example usage of the Knowledge Graph schema.

This module demonstrates how to create, serialize, and deserialize
nodes and relationships using the schema definitions.
"""

import json
from typing import Dict, Any, List

from testindex.core.logging import get_logger
from testindex.knowledge.schema.base import Node, Relationship
from testindex.knowledge.schema.nodes import (
    NodeSchema,
    ImplementationNode,
    ModuleNode,
    FixtureNode,
)
from testindex.knowledge.schema.relationships import (
    TestToImplRelationship,
    UsesFixtureRelationship,
    CallsRelationship,
)

logger = get_logger(__name__)


def create_test_node() -> NodeSchema:
    """Create an example NodeSchema."""
    node = NodeSchema(
        id="test-unique-id-123",
        name="test_example_function",
        labels=["Test", "Function"],
        properties={
            "name": "test_user_login",
            "file_path": "/path/to/test_auth.py",
            "function_name": "test_user_login",
            "module_name": "test_auth",
            "class_name": "TestAuthentication",
            "test_framework": "pytest",
            "docstring": "Test that users can login with valid credentials",
            "tags": ["authentication", "smoke"],
        }
    )
    return node


def create_implementation_node() -> ImplementationNode:
    """Create an example ImplementationNode."""
    node = ImplementationNode(
        labels=["Implementation", "Method"],
        properties={
            "name": "user_login",
            "file_path": "/path/to/auth.py",
            "function_name": "user_login",
            "module_name": "auth",
            "class_name": "AuthenticationService",
            "docstring": "Authenticate a user with username and password",
            "complexity": 4,
            "line_count": 25,
            "parameters": ["username", "password"],
            "return_type": "bool",
        }
    )
    return node


def create_module_node() -> ModuleNode:
    """Create an example ModuleNode."""
    node = ModuleNode(
        labels=["Module"],
        properties={
            "name": "auth",
            "file_path": "/path/to/auth.py",
            "package_name": "myapp.services",
            "docstring": "Authentication services for the application",
            "is_package": False,
            "imports": ["os", "sys", "hashlib", "myapp.models.user"],
            "line_count": 120,
            "classes": ["AuthenticationService", "PermissionChecker"],
            "functions": ["hash_password", "check_password"],
        }
    )
    return node


def create_fixture_node() -> FixtureNode:
    """Create an example FixtureNode."""
    node = FixtureNode(
        labels=["Fixture"],
        properties={
            "name": "authenticated_user",
            "file_path": "/path/to/conftest.py",
            "function_name": "authenticated_user",
            "module_name": "conftest",
            "scope": "function",
            "docstring": "Fixture providing an authenticated user",
            "autouse": False,
            "dependencies": ["user_factory", "db_connection"],
            "return_type": "User",
        }
    )
    return node


def create_tests_relationship(test_node: NodeSchema, impl_node: ImplementationNode) -> TestToImplRelationship:
    """Create an example TestToImplRelationship between a NodeSchema and ImplementationNode."""
    rel = TestToImplRelationship(
        source_id=test_node.id,
        target_id=impl_node.id,
        properties={
            "confidence": 0.95,
            "detection_method": "static",
            "coverage_percentage": 0.8,
        }
    )
    return rel


def create_uses_fixture_relationship(test_node: NodeSchema, fixture_node: FixtureNode) -> UsesFixtureRelationship:
    """Create an example UsesFixtureRelationship between a NodeSchema and FixtureNode."""
    rel = UsesFixtureRelationship(
        source_id=test_node.id,
        target_id=fixture_node.id,
        properties={
            "usage_type": "explicit",
            "is_direct": True,
        }
    )
    return rel


def demonstrate_serialization(node: Node) -> Dict[str, Any]:
    """Demonstrate serialization of a node to dictionary and JSON."""
    # Convert to dictionary
    node_dict = node.to_dict()
    logger.info(f"Node dictionary: {json.dumps(node_dict, indent=2)}")
    
    # Convert to JSON
    node_json = node.to_json()
    logger.info(f"Node JSON: {node_json}")
    
    return node_dict


def demonstrate_deserialization(node_dict: Dict[str, Any], node_class: type) -> Node:
    """Demonstrate deserialization of a node from dictionary and JSON."""
    # From dictionary
    node = node_class.from_dict(node_dict)
    logger.info(f"Deserialized node: {node}")
    
    # From JSON
    node_json = json.dumps(node_dict)
    node = node_class.from_json(node_json)
    logger.info(f"Deserialized node from JSON: {node}")
    
    return node


def build_knowledge_graph_example() -> Dict[str, List[Any]]:
    """Build a small example knowledge graph with nodes and relationships."""
    # Create nodes
    test_node = create_test_node()
    impl_node = create_implementation_node()
    module_node = create_module_node()
    fixture_node = create_fixture_node()
    
    # Create relationships
    tests_rel = create_tests_relationship(test_node, impl_node)
    uses_fixture_rel = create_uses_fixture_relationship(test_node, fixture_node)
    calls_rel = CallsRelationship(
        source_id=impl_node.id,
        target_id=impl_node.id,  # Example of calling itself
        properties={
            "call_count": 2,
            "call_locations": [15, 23],
            "is_conditional": True,
        }
    )
    
    # Build graph
    graph = {
        "nodes": [
            test_node.to_dict(),
            impl_node.to_dict(),
            module_node.to_dict(),
            fixture_node.to_dict(),
        ],
        "relationships": [
            tests_rel.to_dict(),
            uses_fixture_rel.to_dict(),
            calls_rel.to_dict(),
        ],
    }
    
    return graph


def demonstrate_validation():
    """Demonstrate validation of node properties."""
    # Create a node with invalid properties
    try:
        invalid_node = NodeSchema(
            id="test-invalid-props-789",
            name="test_with_invalid_properties",
            labels=["Test"],
            properties={
                "name": "test_invalid",
                # Missing required properties
                "complexity": "not a number",  # Wrong type
            }
        )
        invalid_node.validate_properties()
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
    
    # Create a node with valid properties
    valid_node = NodeSchema(
        id="test-valid-props-456",
        name="test_with_valid_properties",
        labels=["Test"],
        properties={
            "name": "test_valid",
            "file_path": "/path/to/test.py",
            "function_name": "test_valid",
            "module_name": "test_module",
            "last_execution_time": 0.25,  # Correct type
        }
    )
    valid_node.validate_properties()
    logger.info(f"Valid node: {valid_node.to_dict()}")


def main():
    """Run example demonstrations."""
    logger.info("Creating example nodes")
    test_node = create_test_node()
    impl_node = create_implementation_node()
    
    logger.info("Demonstrating serialization")
    node_dict = demonstrate_serialization(test_node)
    
    logger.info("Demonstrating deserialization")
    deserialized_node = demonstrate_deserialization(node_dict, NodeSchema)
    print(f"Deserialized Node (NodeSchema): {deserialized_node.name}, ID: {deserialized_node.id}")
    
    logger.info("Building example knowledge graph")
    graph = build_knowledge_graph_example()
    logger.info(f"Graph contains {len(graph['nodes'])} nodes and {len(graph['relationships'])} relationships")
    
    logger.info("Demonstrating validation")
    demonstrate_validation()


if __name__ == "__main__":
    main() 