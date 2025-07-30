"""
Test Quality Metrics

Defines the data structures for representing test quality metrics.
"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field


@dataclass
class QualityMetrics:
    """Container for test quality metrics.
    
    Holds various metrics related to test quality, including counts,
    coverage, complexity, performance, and reliability indicators.
    """
    # Test counts
    total_tests: int = 0
    passing_tests: int = 0
    failing_tests: int = 0
    skipped_tests: int = 0
    
    # Coverage metrics
    code_coverage_percentage: float = 0.0
    covered_lines: int = 0
    total_lines: int = 0
    
    # Complexity metrics
    avg_test_complexity: float = 0.0
    max_test_complexity: float = 0.0
    
    # Performance metrics
    avg_execution_time: float = 0.0
    total_execution_time: float = 0.0
    
    # Reliability metrics
    flakiness_score: float = 0.0  # Higher score means more flaky
    
    # Overall quality score (0-100)
    health_score: float = 0.0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def pass_rate(self) -> float:
        """Calculate the pass rate as a percentage of passing tests.
        
        Returns:
            float: Percentage of passing tests (0-100)
        """
        if self.total_tests == 0:
            return 0.0
        return (self.passing_tests / self.total_tests) * 100.0
    
    @property
    def failure_rate(self) -> float:
        """Calculate the failure rate as a percentage of failing tests.
        
        Returns:
            float: Percentage of failing tests (0-100)
        """
        if self.total_tests == 0:
            return 0.0
        return (self.failing_tests / self.total_tests) * 100.0
    
    @property
    def skip_rate(self) -> float:
        """Calculate the skip rate as a percentage of skipped tests.
        
        Returns:
            float: Percentage of skipped tests (0-100)
        """
        if self.total_tests == 0:
            return 0.0
        return (self.skipped_tests / self.total_tests) * 100.0
    
    def calculate_health_score(self) -> float:
        """Calculate an overall test health score based on all metrics.
        
        Returns:
            float: Test health score (0-100)
        """
        # Weights for different components (sum to 1.0)
        weights = {
            "pass_rate": 0.4,
            "coverage": 0.3,
            "flakiness": 0.2,
            "complexity": 0.1
        }
        
        # Calculate individual component scores (0-100)
        pass_rate_score = self.pass_rate
        coverage_score = self.code_coverage_percentage
        
        # Flakiness score (0 is good, convert to 0-100 scale where 100 is good)
        # Assume flakiness > 1.0 is very bad
        flakiness_score = max(0, 100 - (self.flakiness_score * 100))
        
        # Complexity score (lower is better, convert to 0-100 scale)
        # Assume complexity > 10 is very complex
        if self.avg_test_complexity > 0:
            complexity_factor = min(self.avg_test_complexity / 10.0, 1.0)
            complexity_score = 100 - (complexity_factor * 100)
        else:
            complexity_score = 100.0
        
        # Calculate weighted score
        health_score = (
            weights["pass_rate"] * pass_rate_score +
            weights["coverage"] * coverage_score +
            weights["flakiness"] * flakiness_score +
            weights["complexity"] * complexity_score
        )
        
        # Update the health_score property
        self.health_score = health_score
        
        return health_score
    
    @classmethod
    def merge(cls, metrics_list: List["QualityMetrics"]) -> "QualityMetrics":
        """Merge multiple QualityMetrics instances into a single aggregate.
        
        Args:
            metrics_list: List of QualityMetrics instances to merge
            
        Returns:
            QualityMetrics: A new instance with merged values
        """
        if not metrics_list:
            return cls()
        
        result = cls()
        
        # Sum up counts
        result.total_tests = sum(m.total_tests for m in metrics_list)
        result.passing_tests = sum(m.passing_tests for m in metrics_list)
        result.failing_tests = sum(m.failing_tests for m in metrics_list)
        result.skipped_tests = sum(m.skipped_tests for m in metrics_list)
        
        # Weighted average for percentages
        if result.total_tests > 0:
            # Coverage (weighted by total tests)
            coverage_weighted_sum = sum(m.code_coverage_percentage * m.total_tests for m in metrics_list)
            result.code_coverage_percentage = coverage_weighted_sum / result.total_tests
        
        # Sum up line counts
        result.covered_lines = sum(m.covered_lines for m in metrics_list)
        result.total_lines = sum(m.total_lines for m in metrics_list)
        
        # Recalculate coverage from merged line counts
        if result.total_lines > 0:
            result.code_coverage_percentage = (result.covered_lines / result.total_lines) * 100.0
        
        # Complexity metrics (max of maxes, weighted avg of avgs)
        result.max_test_complexity = max(m.max_test_complexity for m in metrics_list)
        
        if result.total_tests > 0:
            complexity_weighted_sum = sum(m.avg_test_complexity * m.total_tests for m in metrics_list)
            result.avg_test_complexity = complexity_weighted_sum / result.total_tests
        
        # Performance metrics
        total_time = sum(m.total_execution_time for m in metrics_list)
        result.total_execution_time = total_time
        
        if result.total_tests > 0:
            result.avg_execution_time = total_time / result.total_tests
        
        # Flakiness (weighted average)
        if result.total_tests > 0:
            flakiness_weighted_sum = sum(m.flakiness_score * m.total_tests for m in metrics_list)
            result.flakiness_score = flakiness_weighted_sum / result.total_tests
        
        # Recalculate the health score
        result.calculate_health_score()
        
        # Merge metadata
        for m in metrics_list:
            result.metadata.update(m.metadata)
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metrics to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of all metrics
        """
        return {
            "test_counts": {
                "total": self.total_tests,
                "passing": self.passing_tests,
                "failing": self.failing_tests,
                "skipped": self.skipped_tests,
                "pass_rate": self.pass_rate,
                "failure_rate": self.failure_rate,
                "skip_rate": self.skip_rate,
            },
            "coverage": {
                "percentage": self.code_coverage_percentage,
                "covered_lines": self.covered_lines,
                "total_lines": self.total_lines,
            },
            "complexity": {
                "average": self.avg_test_complexity,
                "maximum": self.max_test_complexity,
            },
            "performance": {
                "average_execution_time": self.avg_execution_time,
                "total_execution_time": self.total_execution_time,
            },
            "reliability": {
                "flakiness_score": self.flakiness_score,
            },
            "quality": {
                "health_score": self.health_score,
            },
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualityMetrics":
        """Create a QualityMetrics instance from a dictionary.
        
        Args:
            data: Dictionary containing test quality metrics
            
        Returns:
            QualityMetrics: New instance with values from the dictionary
        """
        metrics = cls()
        
        test_counts = data.get("test_counts", {})
        metrics.total_tests = test_counts.get("total", 0)
        metrics.passing_tests = test_counts.get("passing", 0)
        metrics.failing_tests = test_counts.get("failing", 0)
        metrics.skipped_tests = test_counts.get("skipped", 0)
        
        coverage = data.get("coverage", {})
        metrics.code_coverage_percentage = coverage.get("percentage", 0.0)
        metrics.covered_lines = coverage.get("covered_lines", 0)
        metrics.total_lines = coverage.get("total_lines", 0)
        
        complexity = data.get("complexity", {})
        metrics.avg_test_complexity = complexity.get("average", 0.0)
        metrics.max_test_complexity = complexity.get("maximum", 0.0)
        
        performance = data.get("performance", {})
        metrics.avg_execution_time = performance.get("average_execution_time", 0.0)
        metrics.total_execution_time = performance.get("total_execution_time", 0.0)
        
        reliability = data.get("reliability", {})
        metrics.flakiness_score = reliability.get("flakiness_score", 0.0)
        
        quality = data.get("quality", {})
        metrics.health_score = quality.get("health_score", 0.0)
        
        metrics.metadata = data.get("metadata", {})
        
        return metrics


def calculate_complexity(ast_node) -> int:
    """
    Calculate cyclomatic complexity of a test function.
    This is a placeholder for actual implementation.
    
    Args:
        ast_node: The AST node representing the test function
        
    Returns:
        int: The calculated complexity score
    """
    # Placeholder - to be implemented with actual AST analysis
    return 1


def calculate_flakiness(test_history: List[bool]) -> float:
    """
    Calculate the flakiness score based on test history.
    
    Args:
        test_history: A list of boolean values representing test results
                     over time (True for pass, False for fail)
                     
    Returns:
        float: A value between 0 and 1, where 0 means not flaky and 1 means extremely flaky
    """
    if not test_history:
        return 0.0
        
    # If the test has only been run once, it can't be considered flaky
    if len(test_history) == 1:
        return 0.0
        
    # Count transitions between pass and fail
    transitions = sum(1 for i in range(1, len(test_history)) 
                     if test_history[i] != test_history[i-1])
    
    # Calculate flakiness score
    max_possible_transitions = len(test_history) - 1
    flakiness = transitions / max_possible_transitions if max_possible_transitions > 0 else 0
    
    return flakiness 