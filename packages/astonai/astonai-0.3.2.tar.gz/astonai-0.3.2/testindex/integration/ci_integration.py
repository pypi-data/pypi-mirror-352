"""
CI/CD Integration for TestIndex Regression Guard.

This module provides utilities for integrating regression guard analysis
into CI/CD pipelines with support for various CI systems.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

from testindex.core.logging import get_logger
from testindex.analysis.regression_guard import RegressionGuard, RegressionThreshold, RegressionGuardError

logger = get_logger(__name__)


@dataclass
class CIConfig:
    """Configuration for CI/CD integration."""
    max_risk_score: float = 0.7
    max_impacted_nodes: int = 50
    min_test_coverage: float = 0.8
    max_critical_nodes: int = 10
    depth: int = 2
    block_on_high_risk: bool = True
    require_manual_approval: bool = False
    output_format: str = "both"  # "json", "text", "both"
    detailed_output_path: Optional[str] = None
    json_output_path: Optional[str] = None


class CIIntegration:
    """Provides CI/CD integration capabilities for regression guard."""
    
    def __init__(self, config: Optional[CIConfig] = None):
        """Initialize CI integration with configuration.
        
        Args:
            config: CI configuration settings
        """
        self.config = config or CIConfig()
        
    @classmethod
    def from_env(cls) -> 'CIIntegration':
        """Create CI integration from environment variables.
        
        Environment variables:
            TESTINDEX_MAX_RISK_SCORE: Maximum allowed risk score (0.0-1.0)
            TESTINDEX_MAX_IMPACTED_NODES: Maximum allowed impacted nodes
            TESTINDEX_MIN_TEST_COVERAGE: Minimum required test coverage
            TESTINDEX_MAX_CRITICAL_NODES: Maximum allowed critical nodes
            TESTINDEX_ANALYSIS_DEPTH: Analysis depth
            TESTINDEX_BLOCK_ON_HIGH_RISK: Whether to block on high risk
            TESTINDEX_OUTPUT_FORMAT: Output format (json/text/both)
            TESTINDEX_DETAILED_OUTPUT: Path for detailed output
            TESTINDEX_JSON_OUTPUT: Path for JSON output
            
        Returns:
            CIIntegration configured from environment
        """
        config = CIConfig()
        
        # Load configuration from environment
        if os.getenv('TESTINDEX_MAX_RISK_SCORE'):
            config.max_risk_score = float(os.getenv('TESTINDEX_MAX_RISK_SCORE'))
        if os.getenv('TESTINDEX_MAX_IMPACTED_NODES'):
            config.max_impacted_nodes = int(os.getenv('TESTINDEX_MAX_IMPACTED_NODES'))
        if os.getenv('TESTINDEX_MIN_TEST_COVERAGE'):
            config.min_test_coverage = float(os.getenv('TESTINDEX_MIN_TEST_COVERAGE'))
        if os.getenv('TESTINDEX_MAX_CRITICAL_NODES'):
            config.max_critical_nodes = int(os.getenv('TESTINDEX_MAX_CRITICAL_NODES'))
        if os.getenv('TESTINDEX_ANALYSIS_DEPTH'):
            config.depth = int(os.getenv('TESTINDEX_ANALYSIS_DEPTH'))
        if os.getenv('TESTINDEX_BLOCK_ON_HIGH_RISK'):
            config.block_on_high_risk = os.getenv('TESTINDEX_BLOCK_ON_HIGH_RISK').lower() == 'true'
        if os.getenv('TESTINDEX_OUTPUT_FORMAT'):
            config.output_format = os.getenv('TESTINDEX_OUTPUT_FORMAT')
        if os.getenv('TESTINDEX_DETAILED_OUTPUT'):
            config.detailed_output_path = os.getenv('TESTINDEX_DETAILED_OUTPUT')
        if os.getenv('TESTINDEX_JSON_OUTPUT'):
            config.json_output_path = os.getenv('TESTINDEX_JSON_OUTPUT')
            
        return cls(config)
    
    def analyze_pr_changes(self, 
                          base_ref: str, 
                          head_ref: str = "HEAD",
                          pr_number: Optional[str] = None) -> Dict[str, Any]:
        """Analyze changes in a pull request for regression risk.
        
        Args:
            base_ref: Base branch reference (e.g., 'main', 'develop')
            head_ref: Head reference to analyze (default: 'HEAD')
            pr_number: Pull request number for metadata
            
        Returns:
            Dict containing analysis results and CI recommendations
            
        Raises:
            RegressionGuardError: If analysis fails
        """
        logger.info(f"Analyzing PR changes from {base_ref} to {head_ref}")
        
        try:
            # Create regression guard with CI thresholds
            thresholds = RegressionThreshold(
                max_risk_score=self.config.max_risk_score,
                max_impacted_nodes=self.config.max_impacted_nodes,
                min_test_coverage=self.config.min_test_coverage,
                max_critical_nodes=self.config.max_critical_nodes
            )
            
            guard = RegressionGuard(thresholds=thresholds, depth=self.config.depth)
            
            # Determine output paths
            detailed_output = None
            if self.config.detailed_output_path:
                detailed_output = Path(self.config.detailed_output_path)
            
            # Run regression analysis
            result = guard.evaluate_change_risk(
                since=base_ref,
                until=head_ref,
                output_file=detailed_output
            )
            
            # Add CI-specific metadata
            ci_result = {
                **result,
                "ci_metadata": {
                    "pr_number": pr_number,
                    "base_ref": base_ref,
                    "head_ref": head_ref,
                    "ci_config": asdict(self.config),
                    "environment": self._get_ci_environment()
                },
                "ci_actions": self._generate_ci_actions(result)
            }
            
            # Write JSON output if configured
            if self.config.json_output_path:
                self._write_json_output(ci_result, self.config.json_output_path)
            
            logger.info(f"PR analysis completed: {result['risk_assessment']['risk_level']} risk")
            return ci_result
            
        except Exception as e:
            logger.error(f"Failed to analyze PR changes: {e}")
            raise RegressionGuardError(f"PR analysis failed: {str(e)}")
    
    def should_block_merge(self, analysis_result: Dict[str, Any]) -> bool:
        """Determine if merge should be blocked based on analysis.
        
        Args:
            analysis_result: Result from analyze_pr_changes()
            
        Returns:
            True if merge should be blocked
        """
        if not self.config.block_on_high_risk:
            return False
            
        should_block = analysis_result.get("should_block", False)
        risk_level = analysis_result.get("risk_assessment", {}).get("risk_level", "LOW")
        
        # Additional CI-specific blocking logic
        if risk_level == "HIGH" and self.config.block_on_high_risk:
            return True
            
        return should_block
    
    def generate_pr_comment(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a pull request comment with analysis results.
        
        Args:
            analysis_result: Result from analyze_pr_changes()
            
        Returns:
            Formatted comment text for pull request
        """
        risk_assessment = analysis_result.get("risk_assessment", {})
        risk_level = risk_assessment.get("risk_level", "UNKNOWN")
        risk_score = risk_assessment.get("score", 0.0)
        should_block = analysis_result.get("should_block", False)
        recommendations = analysis_result.get("recommendations", [])
        test_plan = analysis_result.get("test_execution_plan", [])
        
        # Choose emoji and color based on risk level
        if risk_level == "LOW":
            emoji = "✅"
            status = "Safe to merge"
        elif risk_level == "MEDIUM":
            emoji = "⚠️"
            status = "Review recommended"
        else:  # HIGH
            emoji = "🚨"
            status = "High risk detected"
        
        comment_lines = [
            f"## {emoji} Regression Guard Analysis",
            "",
            f"**Risk Level:** {risk_level} (score: {risk_score:.2f}/1.0)",
            f"**Status:** {status}",
            f"**Impacted Nodes:** {analysis_result.get('impacted_nodes_count', 0)}",
            ""
        ]
        
        # Add blocking notice if applicable
        if should_block:
            comment_lines.extend([
                "🚫 **MERGE BLOCKED** - This change exceeds safety thresholds.",
                ""
            ])
        
        # Add recommendations
        if recommendations:
            comment_lines.append("### Recommendations")
            for rec in recommendations:
                comment_lines.append(f"- {rec}")
            comment_lines.append("")
        
        # Add test execution plan
        if test_plan:
            comment_lines.append("### Suggested Test Execution")
            if len(test_plan) <= 5:
                for i, test in enumerate(test_plan, 1):
                    comment_lines.append(f"{i}. `{test}`")
            else:
                for i, test in enumerate(test_plan[:5], 1):
                    comment_lines.append(f"{i}. `{test}`")
                comment_lines.append(f"... and {len(test_plan) - 5} more tests")
            comment_lines.append("")
        
        # Add metadata
        ci_metadata = analysis_result.get("ci_metadata", {})
        if ci_metadata.get("environment"):
            comment_lines.extend([
                "<details><summary>Analysis Details</summary>",
                "",
                f"- **Environment:** {ci_metadata['environment']}",
                f"- **Analysis Depth:** {ci_metadata.get('ci_config', {}).get('depth', 'N/A')}",
                f"- **Duration:** {analysis_result.get('analysis_duration', 'N/A')}s",
                "",
                "</details>"
            ])
        
        return "\n".join(comment_lines)
    
    def generate_github_actions_workflow(self) -> str:
        """Generate a GitHub Actions workflow for regression guard.
        
        Returns:
            YAML content for GitHub Actions workflow
        """
        workflow = f"""name: Regression Guard

on:
  pull_request:
    branches: [main, develop]

jobs:
  regression-analysis:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Need full history for analysis
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install TestIndex
      run: |
        pip install -e .
        aston init --offline
    
    - name: Run Regression Guard
      env:
        TESTINDEX_MAX_RISK_SCORE: "{self.config.max_risk_score}"
        TESTINDEX_MAX_IMPACTED_NODES: "{self.config.max_impacted_nodes}"
        TESTINDEX_MIN_TEST_COVERAGE: "{self.config.min_test_coverage}"
        TESTINDEX_MAX_CRITICAL_NODES: "{self.config.max_critical_nodes}"
        TESTINDEX_JSON_OUTPUT: "regression-analysis.json"
      run: |
        aston regression-guard \\
          --since origin/${{{{ github.base_ref }}}} \\
          --until HEAD \\
          --json regression-analysis.json \\
          --exit-code
    
    - name: Upload Analysis Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: regression-analysis
        path: regression-analysis.json
        
    - name: Comment PR
      uses: actions/github-script@v6
      if: always()
      with:
        script: |
          const fs = require('fs');
          const analysis = JSON.parse(fs.readFileSync('regression-analysis.json', 'utf8'));
          
          // Generate comment (would need to implement comment generation in JS or call Python script)
          const comment = `## Regression Guard Analysis
          
          **Risk Level:** ${{analysis.risk_assessment.risk_level}}
          **Score:** ${{analysis.risk_assessment.score.toFixed(2)}}
          **Should Block:** ${{analysis.should_block ? '🚫 Yes' : '✅ No'}}
          `;
          
          github.rest.issues.createComment({{
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          }});
"""
        
        return workflow
    
    def generate_jenkins_pipeline(self) -> str:
        """Generate a Jenkins pipeline for regression guard.
        
        Returns:
            Jenkinsfile content
        """
        pipeline = f"""pipeline {{
    agent any
    
    environment {{
        TESTINDEX_MAX_RISK_SCORE = '{self.config.max_risk_score}'
        TESTINDEX_MAX_IMPACTED_NODES = '{self.config.max_impacted_nodes}'
        TESTINDEX_MIN_TEST_COVERAGE = '{self.config.min_test_coverage}'
        TESTINDEX_MAX_CRITICAL_NODES = '{self.config.max_critical_nodes}'
        TESTINDEX_JSON_OUTPUT = 'regression-analysis.json'
    }}
    
    stages {{
        stage('Setup') {{
            steps {{
                sh 'pip install -e .'
                sh 'aston init --offline'
            }}
        }}
        
        stage('Regression Analysis') {{
            steps {{
                script {{
                    def baseRef = env.CHANGE_TARGET ?: 'main'
                    sh \"\"\"
                        aston regression-guard \\
                            --since origin/${{baseRef}} \\
                            --until HEAD \\
                            --json regression-analysis.json \\
                            --exit-code
                    \"\"\"
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'regression-analysis.json', fingerprint: true
                    
                    script {{
                        def analysis = readJSON file: 'regression-analysis.json'
                        def riskLevel = analysis.risk_assessment.risk_level
                        def shouldBlock = analysis.should_block
                        
                        if (shouldBlock) {{
                            error("Merge blocked due to high regression risk: ${{riskLevel}}")
                        }}
                        
                        echo "Regression analysis complete: ${{riskLevel}} risk"
                    }}
                }}
            }}
        }}
    }}
}}"""
        
        return pipeline
    
    def _get_ci_environment(self) -> str:
        """Detect the current CI environment.
        
        Returns:
            String identifying the CI environment
        """
        if os.getenv('GITHUB_ACTIONS'):
            return 'GitHub Actions'
        elif os.getenv('JENKINS_URL'):
            return 'Jenkins'
        elif os.getenv('GITLAB_CI'):
            return 'GitLab CI'
        elif os.getenv('CIRCLECI'):
            return 'CircleCI'
        elif os.getenv('TRAVIS'):
            return 'Travis CI'
        elif os.getenv('BUILDKITE'):
            return 'Buildkite'
        else:
            return 'Unknown'
    
    def _generate_ci_actions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate CI-specific action recommendations.
        
        Args:
            analysis_result: Regression analysis result
            
        Returns:
            List of CI action recommendations
        """
        actions = []
        should_block = analysis_result.get("should_block", False)
        risk_level = analysis_result.get("risk_assessment", {}).get("risk_level", "LOW")
        
        if should_block:
            actions.append("BLOCK_MERGE: Prevent merge due to high regression risk")
            actions.append("REQUIRE_APPROVAL: Request manual review from senior developer")
            
        if risk_level == "MEDIUM":
            actions.append("REQUEST_REVIEW: Recommend additional code review")
            actions.append("RUN_EXTENDED_TESTS: Execute full test suite")
            
        test_plan = analysis_result.get("test_execution_plan", [])
        if test_plan:
            actions.append(f"RUN_TARGETED_TESTS: Execute {len(test_plan)} prioritized tests")
            
        return actions
    
    def _write_json_output(self, result: Dict[str, Any], output_path: str) -> None:
        """Write analysis result to JSON file.
        
        Args:
            result: Analysis result to write
            output_path: Path to write JSON file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
                
            logger.info(f"Wrote CI analysis result to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write JSON output: {e}")
            raise 