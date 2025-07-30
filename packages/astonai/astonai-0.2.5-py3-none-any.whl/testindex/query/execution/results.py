from typing import Dict, List, Optional, Any, Union
import json
from testindex.query.model.base import QueryResult, NodeType, RelationshipType


class ResultFormatter:
    """Utility class for formatting and processing query results."""
    
    @staticmethod
    def to_dict(result: QueryResult) -> Dict[str, Any]:
        """Convert a QueryResult to a dictionary.
        
        Args:
            result: The query result to convert.
            
        Returns:
            Dict[str, Any]: Dictionary representation of the query result.
        """
        return result.model_dump(exclude={"query"})
    
    @staticmethod
    def to_json(result: QueryResult, indent: int = None) -> str:
        """Convert a QueryResult to a JSON string.
        
        Args:
            result: The query result to convert.
            indent: Number of spaces for indentation in the JSON output.
            
        Returns:
            str: JSON string representation of the query result.
        """
        result_dict = ResultFormatter.to_dict(result)
        return json.dumps(result_dict, indent=indent, default=str)
    
    @staticmethod
    def extract_nodes(result: QueryResult, node_type: Optional[str] = None) -> List[NodeType]:
        """Extract nodes from a query result, optionally filtering by type.
        
        Args:
            result: The query result to extract nodes from.
            node_type: Optional node type to filter by.
            
        Returns:
            List[NodeType]: List of nodes matching the criteria.
        """
        if node_type is None:
            return result.nodes
        
        return [node for node in result.nodes if node.type == node_type]
    
    @staticmethod
    def extract_relationships(
        result: QueryResult, 
        relationship_type: Optional[str] = None
    ) -> List[RelationshipType]:
        """Extract relationships from a query result, optionally filtering by type.
        
        Args:
            result: The query result to extract relationships from.
            relationship_type: Optional relationship type to filter by.
            
        Returns:
            List[RelationshipType]: List of relationships matching the criteria.
        """
        if result.relationships is None:
            return []
            
        if relationship_type is None:
            return result.relationships
        
        return [rel for rel in result.relationships if rel.type == relationship_type]
    
    @staticmethod
    def format_coverage_result(result: QueryResult) -> Dict[str, Any]:
        """Format a test coverage query result for easier consumption.
        
        Args:
            result: The test coverage query result to format.
            
        Returns:
            Dict[str, Any]: Formatted result with implementations and their covering tests.
        """
        # Group results by implementation
        implementations = {}
        
        for item in result.items:
            impl_id = item.get("implementation_id")
            if not impl_id:
                continue
                
            if impl_id not in implementations:
                implementations[impl_id] = {
                    "id": impl_id,
                    "name": item.get("implementation_name"),
                    "file_path": item.get("implementation_path"),
                    "tests": []
                }
                
            implementations[impl_id]["tests"].append({
                "id": item.get("test_id"),
                "name": item.get("test_name"),
                "file_path": item.get("test_path")
            })
            
        return {
            "implementations": list(implementations.values()),
            "coverage_count": len(implementations),
            "test_count": len(set(item.get("test_id") for item in result.items if item.get("test_id")))
        }
    
    @staticmethod
    def format_test_relationship_result(result: QueryResult) -> Dict[str, Any]:
        """Format a test relationship query result for easier consumption.
        
        Args:
            result: The test relationship query result to format.
            
        Returns:
            Dict[str, Any]: Formatted result with tests and their related entities.
        """
        # Group results by test
        tests = {}
        
        for item in result.items:
            test_id = item.get("test_id")
            if not test_id:
                continue
                
            if test_id not in tests:
                tests[test_id] = {
                    "id": test_id,
                    "name": item.get("test_name"),
                    "file_path": item.get("test_path"),
                    "fixtures": []
                }
                
            # Add fixture information if available
            if item.get("fixture_id"):
                tests[test_id]["fixtures"].append({
                    "id": item.get("fixture_id"),
                    "name": item.get("fixture_name"),
                    "file_path": item.get("fixture_path")
                })
            
        return {
            "tests": list(tests.values()),
            "test_count": len(tests),
            "fixture_count": len(set(item.get("fixture_id") for item in result.items if item.get("fixture_id")))
        }
    
    @staticmethod
    def format_implementation_relationship_result(result: QueryResult) -> Dict[str, Any]:
        """Format an implementation relationship query result for easier consumption.
        
        Args:
            result: The implementation relationship query result to format.
            
        Returns:
            Dict[str, Any]: Formatted result with implementations and their relationships.
        """
        # Group results by source implementation
        implementations = {}
        relationship_type = None
        
        for item in result.items:
            source_id = item.get("source_id")
            if not source_id:
                continue
                
            relationship_type = item.get("relationship_type")
                
            if source_id not in implementations:
                implementations[source_id] = {
                    "id": source_id,
                    "name": item.get("source_name"),
                    "file_path": item.get("source_path"),
                    "related_implementations": []
                }
                
            # Add target implementation information
            if item.get("target_id"):
                implementations[source_id]["related_implementations"].append({
                    "id": item.get("target_id"),
                    "name": item.get("target_name"),
                    "file_path": item.get("target_path"),
                    "relationship_type": relationship_type
                })
            
        return {
            "implementations": list(implementations.values()),
            "implementation_count": len(implementations),
            "relationship_count": len(result.items),
            "relationship_type": relationship_type
        } 