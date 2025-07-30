"""
Test Quality Analyzer

Provides analysis capabilities for evaluating test quality.
"""
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import ast
import os
import re

from testindex.analysis.test_quality.metrics import QualityMetrics, calculate_complexity, calculate_flakiness
# from testindex.core.models import CodeNode, TestResultNode  # These classes don't exist
# from testindex.knowledge.graph import KnowledgeGraph  # Temporarily commented out
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.knowledge.schema.nodes import NodeSchema, ImplementationNode
from testindex.core.logging import get_logger

logger = get_logger(__name__)

class TestQualityAnalyzer:
    """Analyzer for measuring and tracking test quality metrics."""
    
    def __init__(self, knowledge_graph = None):  # Optional[KnowledgeGraph] = None):
        """
        Initialize the test quality analyzer.
        
        Args:
            knowledge_graph: The knowledge graph containing test and code nodes
        """
        self.knowledge_graph = knowledge_graph
        
    def analyze_test(self, test_node: NodeSchema) -> QualityMetrics:
        """
        Analyze a single test and generate quality metrics.
        
        Args:
            test_node: The test node to analyze
            
        Returns:
            QualityMetrics: Metrics for the individual test
        """
        metrics = QualityMetrics()
        metrics.total_tests = 1
        
        # Set basic test status metrics
        if hasattr(test_node, 'status'):
            if test_node.status == 'pass':
                metrics.passing_tests = 1
            elif test_node.status == 'fail':
                metrics.failing_tests = 1
            elif test_node.status == 'skip':
                metrics.skipped_tests = 1
        
        # Calculate execution time if available
        if hasattr(test_node, 'execution_time'):
            metrics.avg_execution_time = test_node.execution_time
            metrics.total_execution_time = test_node.execution_time
        
        # Calculate complexity if source code is available
        if hasattr(test_node, 'source') and test_node.source:
            try:
                tree = ast.parse(test_node.source)
                complexity = calculate_complexity(tree)
                metrics.avg_test_complexity = complexity
                metrics.max_test_complexity = complexity
            except SyntaxError:
                # Handle invalid python code
                pass
        
        # Calculate coverage for this specific test if available
        if self.knowledge_graph and hasattr(test_node, 'id'):
            covered_nodes = self._get_covered_code_nodes(test_node.id)
            if covered_nodes is not None:
                # Simple coverage calculation - can be enhanced later
                metrics.code_coverage_percentage = len(covered_nodes) * 5.0
        
        # Set timestamp
        metrics.last_update = datetime.now().isoformat()
        
        return metrics
    
    def analyze_test_suite(self, test_nodes: List[NodeSchema]) -> QualityMetrics:
        """
        Analyze an entire test suite and generate aggregated quality metrics.
        
        Args:
            test_nodes: List of test nodes to analyze
            
        Returns:
            QualityMetrics: Aggregated metrics for the test suite
        """
        if not test_nodes:
            return QualityMetrics(last_update=datetime.now().isoformat())
        
        aggregated_metrics = QualityMetrics()
        
        # Count basic test statistics
        aggregated_metrics.total_tests = len(test_nodes)
        aggregated_metrics.passing_tests = sum(1 for t in test_nodes if hasattr(t, 'status') and t.status == 'pass')
        aggregated_metrics.failing_tests = sum(1 for t in test_nodes if hasattr(t, 'status') and t.status == 'fail')
        aggregated_metrics.skipped_tests = sum(1 for t in test_nodes if hasattr(t, 'status') and t.status == 'skip')
        
        # Calculate execution time statistics
        execution_times = [t.execution_time for t in test_nodes if hasattr(t, 'execution_time')]
        if execution_times:
            aggregated_metrics.avg_execution_time = sum(execution_times) / len(execution_times)
            aggregated_metrics.total_execution_time = sum(execution_times)
        
        # Calculate complexity statistics
        complexities = []
        for test in test_nodes:
            if hasattr(test, 'source') and test.source:
                try:
                    tree = ast.parse(test.source)
                    complexity = calculate_complexity(tree)
                    complexities.append(complexity)
                except SyntaxError:
                    # Handle invalid python code
                    pass
        
        if complexities:
            aggregated_metrics.avg_test_complexity = sum(complexities) / len(complexities)
            aggregated_metrics.max_test_complexity = max(complexities)
        
        # Calculate flakiness if test history is available
        if self.knowledge_graph:
            flakiness_scores = []
            for test in test_nodes:
                if hasattr(test, 'id'):
                    history = self._get_test_history(test.id)
                    if history:
                        flakiness = calculate_flakiness(history)
                        flakiness_scores.append(flakiness)
            
            if flakiness_scores:
                aggregated_metrics.flakiness_score = sum(flakiness_scores) / len(flakiness_scores)
        
        # Calculate overall code coverage
        if self.knowledge_graph:
            covered_nodes, total_nodes = self._calculate_total_coverage(test_nodes)
            if total_nodes > 0:
                aggregated_metrics.code_coverage_percentage = (covered_nodes / total_nodes) * 100
        
        # Set timestamp
        aggregated_metrics.last_update = datetime.now().isoformat()
        
        return aggregated_metrics
    
    def _get_test_history(self, test_id: str) -> List[bool]:
        """
        Retrieve test execution history for flakiness calculation.
        
        Args:
            test_id: The identifier of the test
            
        Returns:
            List[bool]: History of test passes (True) and failures (False)
        """
        if not self.knowledge_graph:
            return []
            
        # This is a placeholder - actual implementation would query the knowledge graph
        # for test result history
        test_results = []
        
        # Example query to find test results for a specific test
        # results = self.knowledge_graph.query(
        #     f"""
        #     MATCH (t:Test {{id: '{test_id}'}})-[:HAS_RESULT]->(r:TestResult)
        #     RETURN r ORDER BY r.timestamp
        #     """
        # )
        
        # for result in results:
        #     test_results.append(result['status'] == 'pass')
            
        return test_results
    
    def _get_covered_code_nodes(self, test_id: str) -> Optional[Set[str]]:
        """
        Get the set of code nodes covered by a test.
        
        Args:
            test_id: The identifier of the test
            
        Returns:
            Optional[Set[str]]: Set of code node identifiers covered by the test
        """
        if not self.knowledge_graph:
            return None
            
        # This is a placeholder - actual implementation would query the knowledge graph
        covered_nodes = set()
        
        # Example query to find code nodes covered by a test
        # results = self.knowledge_graph.query(
        #     f"""
        #     MATCH (t:Test {{id: '{test_id}'}})-[:COVERS]->(c:Code)
        #     RETURN c.id
        #     """
        # )
        
        # for result in results:
        #     covered_nodes.add(result['c.id'])
            
        return covered_nodes
    
    def _calculate_total_coverage(self, test_nodes: List[NodeSchema]) -> Tuple[int, int]:
        """
        Calculate total code coverage for a set of tests.
        
        Args:
            test_nodes: List of test nodes
            
        Returns:
            Tuple[int, int]: (covered_nodes_count, total_nodes_count)
        """
        if not self.knowledge_graph:
            return 0, 1
            
        # Placeholder for actual implementation
        covered_nodes_set = set()
        
        for test in test_nodes:
            if hasattr(test, 'id'):
                nodes = self._get_covered_code_nodes(test.id)
                if nodes:
                    covered_nodes_set.update(nodes)
        
        # Get total code nodes count - placeholder
        total_nodes = 100  # This would come from the knowledge graph
        
        return len(covered_nodes_set), total_nodes 