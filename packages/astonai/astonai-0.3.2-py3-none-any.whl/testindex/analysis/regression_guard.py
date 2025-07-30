"""
Regression Guard for TestIndex.

This module implements regression detection and prevention mechanisms
based on change impact analysis and historical test data.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.analysis.diff_analyzer import DiffAnalyzer, DiffAnalyzerError

logger = get_logger(__name__)


@dataclass
class RegressionThreshold:
    """Configuration for regression detection thresholds."""
    max_risk_score: float = 0.7
    max_impacted_nodes: int = 50
    min_test_coverage: float = 0.8
    max_critical_nodes: int = 10


class RegressionGuardError(Exception):
    """Raised when there's an error during regression analysis."""
    pass


class RegressionGuard:
    """Detects potential regressions from code changes."""
    
    def __init__(self, thresholds: Optional[RegressionThreshold] = None, depth: int = 2):
        """Initialize regression guard with configurable thresholds.
        
        Args:
            thresholds: Custom threshold configuration
            depth: Depth of call graph traversal for impact analysis
        """
        self.thresholds = thresholds or RegressionThreshold()
        self.diff_analyzer = DiffAnalyzer(depth=depth)  # Deeper analysis for regression detection
        
    def evaluate_change_risk(self, 
                           since: str, 
                           until: str = "HEAD",
                           nodes_file: Optional[Path] = None,
                           edges_file: Optional[Path] = None,
                           output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Evaluate regression risk for a change.
        
        Args:
            since: Git reference to compare from
            until: Git reference to compare to
            nodes_file: Path to nodes.json file (optional)
            edges_file: Path to edges.json file (optional)
            output_file: Optional path to write detailed results
            
        Returns:
            Dict containing risk assessment and recommendations
            
        Raises:
            RegressionGuardError: If analysis fails
        """
        start_time = time.time()
        
        try:
            # Run impact analysis using enhanced DiffAnalyzer
            impacted_nodes = self.diff_analyzer.analyze(
                since=since, 
                until=until,
                nodes_file=nodes_file,
                edges_file=edges_file
            )
            
            # Calculate risk metrics using Step 1 enhanced functionality
            risk_metrics = self.diff_analyzer.calculate_risk_score(impacted_nodes)
            
            # Generate test execution plan using Step 1 enhanced functionality
            test_plan = self.diff_analyzer.find_test_execution_plan(impacted_nodes)
            
            # Check against regression thresholds
            violations = self._check_thresholds(risk_metrics, impacted_nodes)
            
            # Generate actionable recommendations
            recommendations = self._generate_recommendations(risk_metrics, violations, test_plan)
            
            # Calculate additional regression-specific metrics
            regression_metrics = self._calculate_regression_metrics(impacted_nodes, risk_metrics)
            
            # Build comprehensive result
            result = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "git_range": f"{since}..{until}",
                "risk_assessment": risk_metrics,
                "regression_metrics": regression_metrics,
                "impacted_nodes_count": len(impacted_nodes),
                "test_execution_plan": test_plan,
                "threshold_violations": violations,
                "recommendations": recommendations,
                "should_block": len(violations) > 0,
                "analysis_duration": round(time.time() - start_time, 2),
                "thresholds_applied": {
                    "max_risk_score": self.thresholds.max_risk_score,
                    "max_impacted_nodes": self.thresholds.max_impacted_nodes,
                    "min_test_coverage": self.thresholds.min_test_coverage,
                    "max_critical_nodes": self.thresholds.max_critical_nodes
                }
            }
            
            # Write detailed output if requested
            if output_file:
                self._write_detailed_output(result, impacted_nodes, output_file)
                
            logger.info(f"Regression analysis completed in {result['analysis_duration']}s")
            logger.info(f"Risk level: {risk_metrics['risk_level']}, Should block: {result['should_block']}")
            
            return result
            
        except DiffAnalyzerError as e:
            raise RegressionGuardError(f"Impact analysis failed: {str(e)}")
        except Exception as e:
            raise RegressionGuardError(f"Regression analysis failed: {str(e)}")
    
    def _check_thresholds(self, risk_metrics: Dict[str, Any], impacted_nodes: List[Dict[str, Any]]) -> List[str]:
        """Check if change exceeds regression thresholds.
        
        Args:
            risk_metrics: Risk assessment from enhanced DiffAnalyzer
            impacted_nodes: List of impacted nodes
            
        Returns:
            List of threshold violation messages
        """
        violations = []
        
        # Check risk score threshold
        if risk_metrics["score"] > self.thresholds.max_risk_score:
            violations.append(f"Risk score too high: {risk_metrics['score']:.2f} > {self.thresholds.max_risk_score}")
        
        # Check impact scope threshold
        if len(impacted_nodes) > self.thresholds.max_impacted_nodes:
            violations.append(f"Too many impacted nodes: {len(impacted_nodes)} > {self.thresholds.max_impacted_nodes}")
        
        # Check critical nodes threshold
        critical_count = risk_metrics.get("critical_nodes", 0)
        if critical_count > self.thresholds.max_critical_nodes:
            violations.append(f"Too many critical nodes affected: {critical_count} > {self.thresholds.max_critical_nodes}")
        
        # Check test coverage threshold
        uncovered_count = risk_metrics.get("uncovered_nodes", 0)
        total_nodes = len(impacted_nodes)
        if total_nodes > 0:
            coverage_ratio = 1.0 - (uncovered_count / total_nodes)
            if coverage_ratio < self.thresholds.min_test_coverage:
                violations.append(f"Insufficient test coverage: {coverage_ratio:.2f} < {self.thresholds.min_test_coverage}")
        
        return violations
    
    def _calculate_regression_metrics(self, impacted_nodes: List[Dict[str, Any]], risk_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional regression-specific metrics.
        
        Args:
            impacted_nodes: List of impacted nodes
            risk_metrics: Basic risk metrics from DiffAnalyzer
            
        Returns:
            Dict containing regression-specific metrics
        """
        if not impacted_nodes:
            return {
                "avg_connectivity": 0.0,
                "max_connectivity": 0,
                "test_coverage_ratio": 1.0,
                "file_diversity": 0,
                "change_complexity": "LOW"
            }
        
        # Calculate connectivity metrics
        connectivities = [node.get("calls_in", 0) + node.get("calls_out", 0) for node in impacted_nodes]
        avg_connectivity = sum(connectivities) / len(connectivities)
        max_connectivity = max(connectivities) if connectivities else 0
        
        # Calculate test coverage ratio
        tested_nodes = len([node for node in impacted_nodes if node.get("tests")])
        test_coverage_ratio = tested_nodes / len(impacted_nodes)
        
        # Calculate file diversity (number of unique files affected)
        unique_files = len(set(node.get("file", "") for node in impacted_nodes if node.get("file")))
        
        # Determine change complexity
        if len(impacted_nodes) > 30 or max_connectivity > 20:
            complexity = "HIGH"
        elif len(impacted_nodes) > 10 or max_connectivity > 10:
            complexity = "MEDIUM"
        else:
            complexity = "LOW"
        
        return {
            "avg_connectivity": round(avg_connectivity, 2),
            "max_connectivity": max_connectivity,
            "test_coverage_ratio": round(test_coverage_ratio, 2),
            "file_diversity": unique_files,
            "change_complexity": complexity
        }
    
    def _generate_recommendations(self, 
                                risk_metrics: Dict[str, Any], 
                                violations: List[str], 
                                test_plan: List[str]) -> List[str]:
        """Generate actionable recommendations based on analysis.
        
        Args:
            risk_metrics: Risk assessment metrics
            violations: List of threshold violations
            test_plan: Prioritized test execution plan
            
        Returns:
            List of actionable recommendation strings
        """
        recommendations = []
        
        if violations:
            recommendations.append("🚨 REGRESSION RISK DETECTED - Consider the following actions:")
            
            # High-level recommendations based on risk level
            if risk_metrics["score"] > 0.7:
                recommendations.append("• Break this change into smaller, more focused commits")
                recommendations.append("• Consider feature flags to reduce blast radius")
                recommendations.append("• Add comprehensive tests before merging")
                recommendations.append("• Perform thorough manual testing")
            elif risk_metrics["score"] > 0.4:
                recommendations.append("• Review the change carefully before merging")
                recommendations.append("• Consider adding more tests for critical paths")
                
            # Specific recommendations based on violations
            for violation in violations:
                if "Risk score too high" in violation:
                    recommendations.append("• Reduce change scope or improve test coverage")
                elif "Too many impacted nodes" in violation:
                    recommendations.append("• Split change into multiple smaller PRs")
                elif "Too many critical nodes" in violation:
                    recommendations.append("• Focus testing on high-connectivity components")
                elif "Insufficient test coverage" in violation:
                    recommendations.append("• Add tests for uncovered impacted nodes")
            
            # Test execution recommendations
            if test_plan:
                if len(test_plan) <= 5:
                    recommendations.append(f"• Run these {len(test_plan)} critical tests:")
                    for i, test in enumerate(test_plan):
                        recommendations.append(f"  {i+1}. {test}")
                else:
                    recommendations.append(f"• Run these {min(5, len(test_plan))} highest priority tests first:")
                    for i, test in enumerate(test_plan[:5]):
                        recommendations.append(f"  {i+1}. {test}")
                    if len(test_plan) > 5:
                        recommendations.append(f"  ... and {len(test_plan) - 5} more tests")
            else:
                recommendations.append("• No automated tests found - manual testing required")
                
        else:
            recommendations.append("✅ Change appears safe to merge")
            recommendations.append(f"• Risk level: {risk_metrics['risk_level']} (score: {risk_metrics['score']:.2f})")
            
            if test_plan:
                if len(test_plan) <= 3:
                    recommendations.append(f"• Consider running these {len(test_plan)} related tests as validation:")
                    for test in test_plan:
                        recommendations.append(f"  • {test}")
                else:
                    recommendations.append(f"• Consider running {len(test_plan)} related tests as validation")
                    recommendations.append(f"• Start with: {', '.join(test_plan[:3])}")
        
        return recommendations
    
    def _write_detailed_output(self, 
                             result: Dict[str, Any], 
                             impacted_nodes: List[Dict[str, Any]], 
                             output_file: Path) -> None:
        """Write detailed regression analysis to file.
        
        Args:
            result: Analysis result dictionary
            impacted_nodes: List of impacted nodes with detailed information
            output_file: Path to write detailed results
        """
        detailed_result = {
            **result,
            "detailed_impact": impacted_nodes,
            "metadata": {
                "analysis_version": "D3.2-Step2",
                "analyzer_depth": self.diff_analyzer.depth,
                "total_violations": len(result["threshold_violations"]),
                "total_recommendations": len(result["recommendations"])
            }
        }
        
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(detailed_result, f, indent=2)
            logger.info(f"Wrote detailed regression analysis to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write detailed output: {e}")
            raise RegressionGuardError(f"Failed to write detailed output: {str(e)}")
    
    def check_blocking_conditions(self, analysis_result: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check if change should be blocked based on analysis results.
        
        Args:
            analysis_result: Result from evaluate_change_risk()
            
        Returns:
            Tuple of (should_block, blocking_reasons)
        """
        should_block = analysis_result.get("should_block", False)
        violations = analysis_result.get("threshold_violations", [])
        
        blocking_reasons = []
        if should_block:
            blocking_reasons.append("Threshold violations detected:")
            blocking_reasons.extend([f"  • {violation}" for violation in violations])
            
        return should_block, blocking_reasons
    
    def get_safe_merge_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate a safe merge score from 0.0 (unsafe) to 1.0 (safe).
        
        Args:
            analysis_result: Result from evaluate_change_risk()
            
        Returns:
            Float score representing merge safety
        """
        risk_score = analysis_result.get("risk_assessment", {}).get("score", 1.0)
        violation_count = len(analysis_result.get("threshold_violations", []))
        
        # Base safety is inverse of risk (1.0 - risk_score)
        base_safety = max(0.0, 1.0 - risk_score)
        
        # Reduce safety for each violation
        violation_penalty = min(0.8, violation_count * 0.2)
        
        # Ensure minimum safety for zero-risk changes
        final_safety = max(0.1, base_safety - violation_penalty)
        
        return round(final_safety, 2)