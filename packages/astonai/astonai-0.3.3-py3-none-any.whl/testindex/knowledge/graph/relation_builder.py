"""
Relationship builder for the Knowledge Graph.

This module provides utilities for building relationships between nodes
based on code analysis data from the Preprocessing pod.
"""

import json
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from testindex.core.exceptions import ValidationError
from testindex.core.logging import get_logger
from testindex.knowledge.graph.neo4j_client import Neo4jClient, Neo4jQueryError
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
    ImportsRelationship,
    InheritsFromRelationship,
    CoversPathRelationship,
    ContainsRelationship,
)

logger = get_logger(__name__)


class RelationBuilder:
    """Builder for relationships between nodes in the knowledge graph.
    
    This class provides methods for creating relationships between nodes
    based on code analysis data from the Preprocessing pod.
    """
    
    def __init__(self, client: Neo4jClient):
        """Initialize the relation builder.
        
        Args:
            client: Neo4j client for database operations
        """
        self.client = client
    
    def create_test_relationship(
        self,
        test_node: Union[NodeSchema, str],
        impl_node: Union[ImplementationNode, str],
        confidence: float = 1.0,
        detection_method: str = "static",
        coverage_percentage: Optional[float] = None,
    ) -> str:
        """Create a relationship indicating a test tests an implementation.
        
        Args:
            test_node: Test node or ID
            impl_node: Implementation node or ID
            confidence: Confidence score (0-1) for the relationship
            detection_method: Method used to detect the relationship
            coverage_percentage: Percentage of implementation covered by test
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        test_id = test_node.id if isinstance(test_node, NodeSchema) else test_node
        impl_id = impl_node.id if isinstance(impl_node, ImplementationNode) else impl_node
        
        # Create relationship
        relationship = TestToImplRelationship(
            source_id=test_id,
            target_id=impl_id,
            properties={
                "confidence": confidence,
                "detection_method": detection_method,
            }
        )
        
        # Add coverage percentage if provided
        if coverage_percentage is not None:
            relationship.properties["coverage_percentage"] = coverage_percentage
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_fixture_usage_relationship(
        self,
        test_node: Union[NodeSchema, str],
        fixture_node: Union[FixtureNode, str],
        usage_type: str = "explicit",
        is_direct: bool = True,
    ) -> str:
        """Create a relationship indicating a test uses a fixture.
        
        Args:
            test_node: Test node or ID
            fixture_node: Fixture node or ID
            usage_type: How the fixture is used (explicit, autouse, etc.)
            is_direct: Whether the fixture is directly used
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        test_id = test_node.id if isinstance(test_node, NodeSchema) else test_node
        fixture_id = fixture_node.id if isinstance(fixture_node, FixtureNode) else fixture_node
        
        # Create relationship
        relationship = UsesFixtureRelationship(
            source_id=test_id,
            target_id=fixture_id,
            properties={
                "usage_type": usage_type,
                "is_direct": is_direct,
            }
        )
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_calls_relationship(
        self,
        source_node: Union[Node, str],
        target_node: Union[Node, str],
        call_count: int = 1,
        call_locations: Optional[List[int]] = None,
        is_conditional: bool = False,
    ) -> str:
        """Create a relationship indicating a function calls another function.
        
        Args:
            source_node: Source node or ID (caller)
            target_node: Target node or ID (callee)
            call_count: Number of times the function is called
            call_locations: Line numbers where the call occurs
            is_conditional: Whether the call is conditional
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        source_id = source_node.id if isinstance(source_node, Node) else source_node
        target_id = target_node.id if isinstance(target_node, Node) else target_node
        
        # Create relationship
        relationship = CallsRelationship(
            source_id=source_id,
            target_id=target_id,
            properties={
                "call_count": call_count,
                "is_conditional": is_conditional,
            }
        )
        
        # Add call locations if provided
        if call_locations:
            relationship.properties["call_locations"] = call_locations
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_imports_relationship(
        self,
        source_module: Union[ModuleNode, str],
        target_module: Union[ModuleNode, str],
        import_type: str = "import",
        is_relative: bool = False,
        imported_names: Optional[List[str]] = None,
    ) -> str:
        """Create a relationship indicating a module imports another module.
        
        Args:
            source_module: Source module node or ID (importer)
            target_module: Target module node or ID (importee)
            import_type: Type of import (import, from-import)
            is_relative: Whether the import is relative
            imported_names: Names imported from the module
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        source_id = source_module.id if isinstance(source_module, ModuleNode) else source_module
        target_id = target_module.id if isinstance(target_module, ModuleNode) else target_module
        
        # Create relationship
        relationship = ImportsRelationship(
            source_id=source_id,
            target_id=target_id,
            properties={
                "import_type": import_type,
                "is_relative": is_relative,
            }
        )
        
        # Add imported names if provided
        if imported_names:
            relationship.properties["imported_names"] = imported_names
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_inheritance_relationship(
        self,
        child_node: Union[Node, str],
        parent_node: Union[Node, str],
        inheritance_level: int = 1,
        overridden_methods: Optional[List[str]] = None,
    ) -> str:
        """Create a relationship indicating a class inherits from another class.
        
        Args:
            child_node: Child node or ID (subclass)
            parent_node: Parent node or ID (superclass)
            inheritance_level: Level of inheritance
            overridden_methods: Methods overridden from parent
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        child_id = child_node.id if isinstance(child_node, Node) else child_node
        parent_id = parent_node.id if isinstance(parent_node, Node) else parent_node
        
        # Create relationship
        relationship = InheritsFromRelationship(
            source_id=child_id,
            target_id=parent_id,
            properties={
                "inheritance_level": inheritance_level,
            }
        )
        
        # Add overridden methods if provided
        if overridden_methods:
            relationship.properties["overridden_methods"] = overridden_methods
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_covers_path_relationship(
        self,
        test_node: Union[NodeSchema, str],
        impl_node: Union[ImplementationNode, str],
        path_id: str,
        path_description: Optional[str] = None,
        code_blocks: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Create a relationship indicating a test covers a specific code path.
        
        Args:
            test_node: Test node or ID
            impl_node: Implementation node or ID
            path_id: Unique identifier for the execution path
            path_description: Human-readable description of the path
            code_blocks: List of code blocks covered (line ranges)
            conditions: List of conditions/branches covered
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        test_id = test_node.id if isinstance(test_node, NodeSchema) else test_node
        impl_id = impl_node.id if isinstance(impl_node, ImplementationNode) else impl_node
        
        # Create relationship
        relationship = CoversPathRelationship(
            source_id=test_id,
            target_id=impl_id,
            properties={
                "path_id": path_id,
            }
        )
        
        # Add optional properties if provided
        if path_description:
            relationship.properties["path_description"] = path_description
        if code_blocks:
            relationship.properties["code_blocks"] = code_blocks
        if conditions:
            relationship.properties["conditions"] = conditions
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def create_contains_relationship(
        self,
        container_node: Union[Node, str],
        contained_node: Union[Node, str],
        relation_type: str = "CONTAINS",
    ) -> str:
        """Create a relationship indicating a node contains another node.
        
        Args:
            container_node: Container node or ID
            contained_node: Contained node or ID
            relation_type: Type of containment relationship
            
        Returns:
            str: Relationship ID
        """
        # Get node IDs
        container_id = container_node.id if isinstance(container_node, Node) else container_node
        contained_id = contained_node.id if isinstance(contained_node, Node) else contained_node
        
        # Create relationship
        relationship = ContainsRelationship(
            source_id=container_id,
            target_id=contained_id,
            properties={
                "relation_type": relation_type,
            }
        )
        
        # Create in database
        return self.client.create_relationship(relationship)
    
    def build_relationships_from_static_analysis(
        self,
        analysis_data: Dict[str, Any]
    ) -> List[str]:
        """Build relationships based on static code analysis data.
        
        Args:
            analysis_data: Static analysis data from the Preprocessing pod
            
        Returns:
            List[str]: List of created relationship IDs
        """
        relationship_ids = []
        
        # Process test-implementation relationships
        if "test_implementations" in analysis_data:
            for test_impl in analysis_data["test_implementations"]:
                try:
                    rel_id = self.create_test_relationship(
                        test_node=test_impl["test_id"],
                        impl_node=test_impl["implementation_id"],
                        confidence=test_impl.get("confidence", 1.0),
                        detection_method="static",
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create test-implementation relationship: {str(e)}")
        
        # Process fixture usage
        if "fixture_usage" in analysis_data:
            for fixture_use in analysis_data["fixture_usage"]:
                try:
                    rel_id = self.create_fixture_usage_relationship(
                        test_node=fixture_use["test_id"],
                        fixture_node=fixture_use["fixture_id"],
                        usage_type=fixture_use.get("usage_type", "explicit"),
                        is_direct=fixture_use.get("is_direct", True),
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create fixture usage relationship: {str(e)}")
        
        # Process function calls
        if "function_calls" in analysis_data:
            for call in analysis_data["function_calls"]:
                try:
                    rel_id = self.create_calls_relationship(
                        source_node=call["caller_id"],
                        target_node=call["callee_id"],
                        call_count=call.get("call_count", 1),
                        call_locations=call.get("call_locations"),
                        is_conditional=call.get("is_conditional", False),
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create function call relationship: {str(e)}")
        
        # Process module imports
        if "module_imports" in analysis_data:
            for import_info in analysis_data["module_imports"]:
                try:
                    rel_id = self.create_imports_relationship(
                        source_module=import_info["importer_id"],
                        target_module=import_info["importee_id"],
                        import_type=import_info.get("import_type", "import"),
                        is_relative=import_info.get("is_relative", False),
                        imported_names=import_info.get("imported_names"),
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create module import relationship: {str(e)}")
        
        # Process class inheritance
        if "class_inheritance" in analysis_data:
            for inheritance in analysis_data["class_inheritance"]:
                try:
                    rel_id = self.create_inheritance_relationship(
                        child_node=inheritance["child_id"],
                        parent_node=inheritance["parent_id"],
                        inheritance_level=inheritance.get("inheritance_level", 1),
                        overridden_methods=inheritance.get("overridden_methods"),
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create inheritance relationship: {str(e)}")
        
        return relationship_ids
    
    def build_relationships_from_dynamic_analysis(
        self,
        analysis_data: Dict[str, Any]
    ) -> List[str]:
        """Build relationships based on dynamic code analysis data.
        
        Args:
            analysis_data: Dynamic analysis data from test execution
            
        Returns:
            List[str]: List of created relationship IDs
        """
        relationship_ids = []
        
        # Process test coverage data
        if "coverage_data" in analysis_data:
            for coverage in analysis_data["coverage_data"]:
                try:
                    # Update or create test-implementation relationship
                    rel_id = self.create_test_relationship(
                        test_node=coverage["test_id"],
                        impl_node=coverage["implementation_id"],
                        confidence=coverage.get("confidence", 1.0),
                        detection_method="dynamic",
                        coverage_percentage=coverage.get("coverage_percentage"),
                    )
                    relationship_ids.append(rel_id)
                    
                    # Create path coverage relationships if available
                    if "paths" in coverage:
                        for path in coverage["paths"]:
                            path_rel_id = self.create_covers_path_relationship(
                                test_node=coverage["test_id"],
                                impl_node=coverage["implementation_id"],
                                path_id=path["path_id"],
                                path_description=path.get("description"),
                                code_blocks=path.get("code_blocks"),
                                conditions=path.get("conditions"),
                            )
                            relationship_ids.append(path_rel_id)
                except Exception as e:
                    logger.error(f"Failed to create coverage relationship: {str(e)}")
        
        # Process actual function calls during test execution
        if "runtime_calls" in analysis_data:
            for call in analysis_data["runtime_calls"]:
                try:
                    rel_id = self.create_calls_relationship(
                        source_node=call["caller_id"],
                        target_node=call["callee_id"],
                        call_count=call.get("call_count", 1),
                        is_conditional=call.get("is_conditional", False),
                    )
                    relationship_ids.append(rel_id)
                except Exception as e:
                    logger.error(f"Failed to create runtime call relationship: {str(e)}")
        
        return relationship_ids
    
    def update_test_relationships_from_results(
        self,
        test_results: Dict[str, Any]
    ) -> List[str]:
        """Update test nodes and relationships based on test execution results.
        
        Args:
            test_results: Test execution results
            
        Returns:
            List[str]: List of updated node and relationship IDs
        """
        updated_ids = []
        
        # Process test results
        if "results" in test_results:
            for result in test_results["results"]:
                test_id = result.get("test_id")
                
                if not test_id:
                    logger.warning(f"Missing test_id in test result: {result}")
                    continue
                
                try:
                    # Get the test node
                    test_data = self.client.get_node(test_id)
                    
                    if not test_data:
                        logger.warning(f"Test node not found: {test_id}")
                        continue
                    
                    # Parse properties
                    properties = test_data.get("properties", {})
                    
                    # Update test node properties
                    properties["last_result"] = result.get("result")
                    properties["last_execution_time"] = result.get("execution_time")
                    
                    # Update node in database
                    test_data["properties"] = json.dumps(properties)
                    
                    # Create Cypher query to update the node
                    query = """
                    MATCH (n {id: $id})
                    SET n.properties = $properties, n.updated_at = $updated_at
                    RETURN n.id
                    """
                    
                    result = self.client.execute_query(query, {
                        "id": test_id,
                        "properties": test_data["properties"],
                        "updated_at": test_data["updated_at"],
                    })
                    
                    updated_ids.append(test_id)
                except Exception as e:
                    logger.error(f"Failed to update test node: {str(e)}")
        
        return updated_ids
    
    def find_related_tests(
        self,
        impl_node: Union[ImplementationNode, str]
    ) -> List[Tuple[NodeSchema, TestToImplRelationship]]:
        """Find tests related to an implementation.
        
        Args:
            impl_node: Implementation node or ID
            
        Returns:
            List[Tuple[NodeSchema, TestToImplRelationship]]: List of test nodes and relationships
        """
        # Get implementation ID
        impl_id = impl_node.id if isinstance(impl_node, ImplementationNode) else impl_node
        
        # Query for related tests
        query = """
        MATCH (t:Test)-[r:TESTS]->(i:Implementation {id: $impl_id})
        RETURN t, r
        """
        
        result = self.client.execute_query(query, {"impl_id": impl_id})
        
        related_tests = []
        for record in result:
            test_node_data = dict(record[0])
            rel_data = dict(record[1])
            
            # Create TestNode from data
            test_node = NodeSchema(
                id=test_node_data["id"],
                name=test_node_data.get("name", ""),
                file_path=test_node_data.get("file_path", ""),
                line_number=test_node_data.get("line_number", 0)
            )
            
            # Create TestToImplRelationship from data
            rel = TestToImplRelationship(
                source_id=test_node.id,
                target_id=impl_id,
                id=rel_data["id"],
                properties=dict(rel_data)
            )
            
            related_tests.append((test_node, rel))
        
        return related_tests
    
    def find_related_implementations(
        self,
        test_node: Union[NodeSchema, str]
    ) -> List[Tuple[ImplementationNode, TestToImplRelationship]]:
        """Find implementations related to a test.
        
        Args:
            test_node: Test node or ID
            
        Returns:
            List[Tuple[ImplementationNode, TestToImplRelationship]]: List of implementation nodes and relationships
        """
        # Get test ID
        test_id = test_node.id if isinstance(test_node, NodeSchema) else test_node
        
        # Query for related implementations
        query = """
        MATCH (t:Test {id: $test_id})-[r:TESTS]->(i:Implementation)
        RETURN i, r
        """
        
        result = self.client.execute_query(query, {"test_id": test_id})
        
        related_impls = []
        for record in result:
            impl_node_data = dict(record[0])
            rel_data = dict(record[1])
            
            # Create ImplementationNode from data
            impl_node = ImplementationNode(
                id=impl_node_data["id"],
                name=impl_node_data.get("name", ""),
                file_path=impl_node_data.get("file_path", ""),
                line_number=impl_node_data.get("line_number", 0)
            )
            
            # Create TestToImplRelationship from data
            rel = TestToImplRelationship(
                source_id=test_id,
                target_id=impl_node.id,
                id=rel_data["id"],
                properties=dict(rel_data)
            )
            
            related_impls.append((impl_node, rel))
        
        return related_impls
    
    def get_module_dependency_graph(self) -> Dict[str, List[str]]:
        """Get a graph of module dependencies based on imports.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping module names to lists of imported module names
        """
        # Query for module import relationships
        query = """
        MATCH (source:Module)-[r:IMPORTS]->(target:Module)
        RETURN source.name as source_name, target.name as target_name
        """
        
        result = self.client.execute_query(query)
        
        # Build dependency graph
        dependency_graph = {}
        for record in result:
            source_name = record["source_name"]
            target_name = record["target_name"]
            
            if source_name not in dependency_graph:
                dependency_graph[source_name] = []
            
            dependency_graph[source_name].append(target_name)
        
        return dependency_graph

    def get_test_node_by_name(
        self, 
        test_node: Union[NodeSchema, str]
    ) -> Optional[Dict[str, Any]]:
        """Find a test node by name.
        
        Args:
            test_node: Test node or ID
            
        Returns:
            Optional[Dict[str, Any]]: Test node data if found, None otherwise
        """
        # Get test ID
        test_id = test_node.id if isinstance(test_node, NodeSchema) else test_node
        
        # Query for test node
        query = """
        MATCH (t:Test {name: $name})
        RETURN t
        """
        
        result = self.client.execute_query(query, {"name": test_node.name})
        
        if result:
            return dict(result[0][0])
        else:
            return None 