from typing import Dict, List, Optional, Any, Union
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.core.config import ConfigModel
from testindex.core.logging import get_logger
from testindex.core.exceptions import AstonError
from testindex.query.model.base import (
    Query, CoverageQuery, RelationshipQuery, 
    ImplementationRelationshipQuery, CustomQuery, QueryResult,
    NodeType, RelationshipType, QueryType
)


class QueryExecutionError(AstonError):
    """Exception raised for query execution errors."""
    error_code = "QUERY001"


class GraphQueryExecutor:
    """Executor for Neo4j graph database queries."""

    def __init__(self, client: Neo4jClient, config: Optional[ConfigModel] = None):
        self.client = client
        self.config = config or ConfigModel()
        self.logger = get_logger("query-executor")

    def execute(self, query: Query) -> QueryResult:
        """Execute the given query and return standardized results.
        
        Args:
            query: The query to execute.
            
        Returns:
            QueryResult: Standardized result of the query execution.
            
        Raises:
            QueryExecutionError: If the query execution fails.
        """
        try:
            if query.query_type == QueryType.TEST_COVERAGE:
                return self._execute_test_coverage_query(query)
            elif query.query_type == QueryType.TEST_RELATIONSHIP:
                return self._execute_test_relationship_query(query)
            elif query.query_type == QueryType.IMPLEMENTATION_RELATIONSHIP:
                return self._execute_implementation_relationship_query(query)
            elif query.query_type == QueryType.CUSTOM:
                return self._execute_custom_query(query)
            else:
                raise QueryExecutionError(f"Unsupported query type: {query.query_type}")
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise QueryExecutionError(f"Query execution failed: {str(e)}") from e

    def _execute_test_coverage_query(self, query: CoverageQuery) -> QueryResult:
        """Execute a test coverage query.
        
        Finds tests that cover specific implementations or implementations covered by specific tests.
        """
        cypher = "MATCH "
        params = {}
        
        # Build the query based on available parameters
        if query.implementation_id or query.implementation_name or query.implementation_path:
            cypher += "(t:Test)-[:TESTS]->(i:Implementation) WHERE "
            
            conditions = []
            if query.implementation_id:
                conditions.append("i.id = $impl_id")
                params["impl_id"] = query.implementation_id
            if query.implementation_name:
                conditions.append("i.name = $impl_name")
                params["impl_name"] = query.implementation_name
            if query.implementation_path:
                conditions.append("i.file_path = $impl_path")
                params["impl_path"] = query.implementation_path
                
            cypher += " AND ".join(conditions)
            cypher += " RETURN t.id as test_id, t.name as test_name, t.file_path as test_path, "
            cypher += "i.id as impl_id, i.name as impl_name, i.file_path as impl_path"
            
        elif query.test_id or query.test_name or query.test_path:
            cypher += "(t:Test)-[:TESTS]->(i:Implementation) WHERE "
            
            conditions = []
            if query.test_id:
                conditions.append("t.id = $test_id")
                params["test_id"] = query.test_id
            if query.test_name:
                conditions.append("t.name = $test_name")
                params["test_name"] = query.test_name
            if query.test_path:
                conditions.append("t.file_path = $test_path")
                params["test_path"] = query.test_path
                
            cypher += " AND ".join(conditions)
            cypher += " RETURN t.id as test_id, t.name as test_name, t.file_path as test_path, "
            cypher += "i.id as impl_id, i.name as impl_name, i.file_path as impl_path"
        else:
            # If no specifics, return all test-implementation relationships
            cypher = "MATCH (t:Test)-[:TESTS]->(i:Implementation) "
            cypher += "RETURN t.id as test_id, t.name as test_name, t.file_path as test_path, "
            cypher += "i.id as impl_id, i.name as impl_name, i.file_path as impl_path"
            
        # Add pagination
        cypher += f" SKIP {query.skip} LIMIT {query.limit}"
        
        result = self.client.execute_query(cypher, params)
        
        # Process results
        data = []
        nodes = []
        node_ids = set()
        
        for record in result:
            data.append({
                "test_id": record.get("test_id"),
                "test_name": record.get("test_name"),
                "test_path": record.get("test_path"),
                "implementation_id": record.get("impl_id"),
                "implementation_name": record.get("impl_name"),
                "implementation_path": record.get("impl_path")
            })
            
            # Create node objects for unique nodes
            if record.get("test_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("test_id"),
                    name=record.get("test_name"),
                    file_path=record.get("test_path"),
                    type="Test",
                    properties={}
                ))
                node_ids.add(record.get("test_id"))
                
            if record.get("impl_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("impl_id"),
                    name=record.get("impl_name"),
                    file_path=record.get("impl_path"),
                    type="Implementation",
                    properties={}
                ))
                node_ids.add(record.get("impl_id"))
                
        return QueryResult(
            items=data,
            nodes=nodes,
            metadata={
                "query_type": str(query.query_type),
                "result_count": len(data),
                "cypher": cypher
            },
            query=cypher
        )
        
    def _execute_test_relationship_query(self, query: RelationshipQuery) -> QueryResult:
        """Execute a test relationship query.
        
        Finds relationships between tests and fixtures or other related entities.
        """
        cypher = ""
        params = {}
        
        # Handle fixture relationships
        if query.fixture_name or query.fixture_id:
            cypher = "MATCH (t:Test)-[:USES_FIXTURE]->(f:Fixture) WHERE "
            
            conditions = []
            if query.fixture_id:
                conditions.append("f.id = $fixture_id")
                params["fixture_id"] = query.fixture_id
            if query.fixture_name:
                conditions.append("f.name = $fixture_name")
                params["fixture_name"] = query.fixture_name
            if query.test_id:
                conditions.append("t.id = $test_id")
                params["test_id"] = query.test_id
            if query.test_name:
                conditions.append("t.name = $test_name")
                params["test_name"] = query.test_name
            if query.test_path:
                conditions.append("t.file_path = $test_path")
                params["test_path"] = query.test_path
                
            cypher += " AND ".join(conditions)
            cypher += " RETURN t.id as test_id, t.name as test_name, t.file_path as test_path, "
            cypher += "f.id as fixture_id, f.name as fixture_name, f.file_path as fixture_path"
            
        # Add pagination
        cypher += f" SKIP {query.skip} LIMIT {query.limit}"
        
        result = self.client.execute_query(cypher, params)
        
        # Process results
        data = []
        nodes = []
        relationships = []
        node_ids = set()
        
        for record in result:
            data.append({
                "test_id": record.get("test_id"),
                "test_name": record.get("test_name"),
                "test_path": record.get("test_path"),
                "fixture_id": record.get("fixture_id"),
                "fixture_name": record.get("fixture_name"),
                "fixture_path": record.get("fixture_path")
            })
            
            # Create node objects for unique nodes
            if record.get("test_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("test_id"),
                    name=record.get("test_name"),
                    file_path=record.get("test_path"),
                    type="Test",
                    properties={}
                ))
                node_ids.add(record.get("test_id"))
                
            if record.get("fixture_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("fixture_id"),
                    name=record.get("fixture_name"),
                    file_path=record.get("fixture_path"),
                    type="Fixture",
                    properties={}
                ))
                node_ids.add(record.get("fixture_id"))
                
            # Create relationship objects
            relationship_id = f"{record.get('test_id')}_USES_FIXTURE_{record.get('fixture_id')}"
            relationships.append(RelationshipType(
                id=relationship_id,
                type="USES_FIXTURE",
                source_id=record.get("test_id"),
                target_id=record.get("fixture_id"),
                properties={}
            ))
                
        return QueryResult(
            items=data,
            nodes=nodes,
            relationships=relationships,
            metadata={
                "query_type": str(query.query_type),
                "result_count": len(data),
                "cypher": cypher
            },
            query=cypher
        )
        
    def _execute_implementation_relationship_query(self, query: ImplementationRelationshipQuery) -> QueryResult:
        """Execute an implementation relationship query.
        
        Finds relationships between implementations (e.g., calls, imports).
        """
        cypher = ""
        params = {}
        
        # Handle implementation relationships
        if query.implementation_name or query.implementation_id or query.implementation_path:
            relationship_type = query.relationship_type or "CALLS"
            cypher = f"MATCH (i1:Implementation)-[r:{relationship_type}]->(i2:Implementation) WHERE "
            
            conditions = []
            if query.implementation_id:
                conditions.append("i1.id = $impl_id")
                params["impl_id"] = query.implementation_id
            if query.implementation_name:
                conditions.append("i1.name = $impl_name")
                params["impl_name"] = query.implementation_name
            if query.implementation_path:
                conditions.append("i1.file_path = $impl_path")
                params["impl_path"] = query.implementation_path
                
            cypher += " AND ".join(conditions)
            cypher += " RETURN i1.id as source_id, i1.name as source_name, i1.file_path as source_path, "
            cypher += "i2.id as target_id, i2.name as target_name, i2.file_path as target_path, "
            cypher += f"'{relationship_type}' as relationship_type"
        else:
            # If no specifics, return all relationships of the specified type
            relationship_type = query.relationship_type or "CALLS"
            cypher = f"MATCH (i1:Implementation)-[r:{relationship_type}]->(i2:Implementation) "
            cypher += "RETURN i1.id as source_id, i1.name as source_name, i1.file_path as source_path, "
            cypher += "i2.id as target_id, i2.name as target_name, i2.file_path as target_path, "
            cypher += f"'{relationship_type}' as relationship_type"
            
        # Add pagination
        cypher += f" SKIP {query.skip} LIMIT {query.limit}"
        
        result = self.client.execute_query(cypher, params)
        
        # Process results
        data = []
        nodes = []
        relationships = []
        node_ids = set()
        
        for record in result:
            data.append({
                "source_id": record.get("source_id"),
                "source_name": record.get("source_name"),
                "source_path": record.get("source_path"),
                "target_id": record.get("target_id"),
                "target_name": record.get("target_name"),
                "target_path": record.get("target_path"),
                "relationship_type": record.get("relationship_type")
            })
            
            # Create node objects for unique nodes
            if record.get("source_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("source_id"),
                    name=record.get("source_name"),
                    file_path=record.get("source_path"),
                    type="Implementation",
                    properties={}
                ))
                node_ids.add(record.get("source_id"))
                
            if record.get("target_id") not in node_ids:
                nodes.append(NodeType(
                    id=record.get("target_id"),
                    name=record.get("target_name"),
                    file_path=record.get("target_path"),
                    type="Implementation",
                    properties={}
                ))
                node_ids.add(record.get("target_id"))
                
            # Create relationship objects
            relationship_id = f"{record.get('source_id')}_{record.get('relationship_type')}_{record.get('target_id')}"
            relationships.append(RelationshipType(
                id=relationship_id,
                type=record.get("relationship_type"),
                source_id=record.get("source_id"),
                target_id=record.get("target_id"),
                properties={}
            ))
                
        return QueryResult(
            items=data,
            nodes=nodes,
            relationships=relationships,
            metadata={
                "query_type": str(query.query_type),
                "result_count": len(data),
                "cypher": cypher
            },
            query=cypher
        )
        
    def _execute_custom_query(self, query: CustomQuery) -> QueryResult:
        """Execute a custom Cypher query.
        
        Allows executing arbitrary Cypher queries with parameters.
        """
        result = self.client.execute_query(query.cypher_query, query.parameters)
        
        # Process results
        items_data = []
        
        for record in result:
            # Convert record to dictionary
            items_data.append(dict(record))
                
        return QueryResult(
            items=items_data,
            nodes=[],
            relationships=[],
            metadata={
                "query_type": str(query.query_type),
                "result_count": len(items_data),
                "cypher": query.cypher_query
            },
            query=query.cypher_query
        ) 