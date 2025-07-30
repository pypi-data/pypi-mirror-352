"""Mapping functions for test-to-implementation coverage analysis.

This module provides functions to map tests to implementations and calculate coverage metrics.
"""

from typing import Dict, List, Optional, Set, Tuple, Any

from testindex.core.config import ConfigModel
from testindex.core.exceptions import AstonError
from testindex.core.logging import get_logger
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode
from testindex.analysis.coverage.models import CoverageModel, ModuleCoverageModel


logger = get_logger("analysis.coverage")


class CoverageAnalysisError(AstonError):
    """Custom exception for errors during coverage analysis."""
    error_code = "COV001"
    default_message = "An error occurred during coverage analysis."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, file_path: Optional[str] = None):
        final_message = message or self.default_message
        if file_path:
            final_message = f"{final_message} in file {file_path}"

        super().__init__(
            message=final_message,
            error_code=error_code or self.error_code,
            context=context
        )
        self.file_path = file_path


class CoverageConfig(ConfigModel):
    """Configuration for coverage analysis."""
    query_timeout: int = 30  # Seconds
    cache_results: bool = True
    include_uncovered: bool = True


def get_neo4j_client(config: Optional[CoverageConfig] = None) -> Neo4jClient:
    """Get a configured Neo4j client.

    Args:
        config: Optional configuration for the client

    Returns:
        Configured Neo4j client
    """
    if config is None:
        config = CoverageConfig.with_defaults()
    return Neo4jClient(config)


def get_coverage_for_function(function_id: str, config: Optional[CoverageConfig] = None) -> CoverageModel:
    """Return coverage information for a specific function/method.

    Args:
        function_id: ID of the implementation function/method
        config: Optional configuration for coverage analysis

    Returns:
        Coverage model for the function

    Raises:
        CoverageAnalysisError: If the function could not be found or another error occurs
    """
    client = get_neo4j_client(config)
    
    # Get the implementation details
    impl_query = """
    MATCH (i:Implementation {id: $impl_id})
    RETURN i.id, i.name, i.file_path
    """
    
    try:
        impl_result = client.execute_query(impl_query, {"impl_id": function_id})
        if not impl_result or len(impl_result) == 0:
            raise CoverageAnalysisError(f"Implementation with ID {function_id} not found")
        
        impl_row = impl_result[0]
        coverage_model = CoverageModel(
            implementation_id=impl_row["i.id"],
            implementation_name=impl_row["i.name"],
            implementation_path=impl_row["i.file_path"]
        )
        
        # Get tests covering the implementation
        test_query = """
        MATCH (t:Test)-[:TESTS]->(i:Implementation {id: $impl_id})
        RETURN t.id, t.name, t.file_path
        """
        
        test_result = client.execute_query(test_query, {"impl_id": function_id})
        for test_row in test_result:
            coverage_model.add_test(
                test_id=test_row["t.id"],
                test_name=test_row["t.name"],
                test_path=test_row["t.file_path"]
            )
            
        return coverage_model
    
    except Exception as e:
        if isinstance(e, CoverageAnalysisError):
            raise
        logger.error(f"Error getting coverage for function {function_id}: {str(e)}")
        raise CoverageAnalysisError(f"Error analyzing coverage for function {function_id}: {str(e)}")


def get_coverage_for_module(module_id: str, config: Optional[CoverageConfig] = None) -> ModuleCoverageModel:
    """Return coverage information for a specific module.

    Args:
        module_id: ID of the implementation module
        config: Optional configuration for coverage analysis

    Returns:
        Module coverage model

    Raises:
        CoverageAnalysisError: If the module could not be found or another error occurs
    """
    client = get_neo4j_client(config)
    
    # Get the module details
    module_query = """
    MATCH (m:Module {id: $module_id})
    RETURN m.id, m.file_path
    """
    
    try:
        module_result = client.execute_query(module_query, {"module_id": module_id})
        if not module_result or len(module_result) == 0:
            raise CoverageAnalysisError(f"Module with ID {module_id} not found")
        
        module_row = module_result[0]
        module_coverage = ModuleCoverageModel(
            module_id=module_row["m.id"],
            module_path=module_row["m.file_path"]
        )
        
        # Get all implementations in the module
        impl_query = """
        MATCH (i:Implementation)-[:CONTAINED_IN]->(:Module {id: $module_id})
        RETURN i.id, i.name, i.file_path
        """
        
        impl_result = client.execute_query(impl_query, {"module_id": module_id})
        for impl_row in impl_result:
            impl_id = impl_row["i.id"]
            coverage = get_coverage_for_function(impl_id, config)
            module_coverage.add_function(coverage)
            
        return module_coverage
    
    except Exception as e:
        if isinstance(e, CoverageAnalysisError):
            raise
        logger.error(f"Error getting coverage for module {module_id}: {str(e)}")
        raise CoverageAnalysisError(f"Error analyzing coverage for module {module_id}: {str(e)}")


def get_uncovered_implementations(config: Optional[CoverageConfig] = None) -> List[Dict]:
    """Get a list of implementations that are not covered by any tests.

    Args:
        config: Optional configuration for coverage analysis

    Returns:
        List of dictionaries with uncovered implementation information
    """
    client = get_neo4j_client(config)
    
    query = """
    MATCH (i:Implementation)
    WHERE NOT ((:Test)-[:TESTS]->(i))
    RETURN i.id, i.name, i.file_path
    """
    
    try:
        result = client.execute_query(query)
        return [
            {
                "id": row["i.id"],
                "name": row["i.name"],
                "path": row["i.file_path"]
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Error getting uncovered implementations: {str(e)}")
        raise CoverageAnalysisError(f"Error finding uncovered implementations: {str(e)}")


def calculate_overall_coverage(config: Optional[CoverageConfig] = None) -> Dict:
    """Calculate overall coverage metrics for the entire codebase.

    Args:
        config: Optional configuration for coverage analysis

    Returns:
        Dictionary with overall coverage metrics
    """
    client = get_neo4j_client(config)
    
    try:
        # Get total implementation count
        total_query = """
        MATCH (i:Implementation)
        RETURN count(i) as total
        """
        total_result = client.execute_query(total_query)
        total_count = total_result[0]["total"] if total_result else 0
        
        # Get covered implementation count
        covered_query = """
        MATCH (i:Implementation)<-[:TESTS]-(:Test)
        RETURN count(DISTINCT i) as covered
        """
        covered_result = client.execute_query(covered_query)
        covered_count = covered_result[0]["covered"] if covered_result else 0
        
        # Calculate percentages
        coverage_percentage = (covered_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_implementations": total_count,
            "covered_implementations": covered_count,
            "uncovered_implementations": total_count - covered_count,
            "coverage_percentage": coverage_percentage
        }
    
    except Exception as e:
        logger.error(f"Error calculating overall coverage: {str(e)}")
        raise CoverageAnalysisError(f"Error calculating overall coverage metrics: {str(e)}") 