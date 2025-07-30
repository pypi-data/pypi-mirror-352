"""Coverage report generators.

This module provides functions for generating test coverage reports in various formats.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import matplotlib.pyplot as plt

from testindex.core.config import ConfigModel
from testindex.core.logging import get_logger
from testindex.core.exceptions import AstonError
from testindex.knowledge.graph.neo4j_client import Neo4jClient
from testindex.analysis.coverage.mapping import (
    CoverageConfig,
    calculate_overall_coverage,
    get_coverage_for_module,
    get_uncovered_implementations,
)


logger = get_logger("analysis.coverage.reports")


class ReportConfig(CoverageConfig):
    """Configuration for coverage reports."""
    output_dir: str = "coverage_reports"
    show_uncovered: bool = True
    detailed_view: bool = False
    max_items_per_section: int = 50


def generate_console_report(repo_path: str, config: Optional[ReportConfig] = None) -> None:
    """Generate a console report for test coverage.

    Args:
        repo_path: Path to the repository
        config: Optional configuration for the report
    """
    if config is None:
        config = ReportConfig.with_defaults()
    
    # Get overall coverage metrics
    metrics = calculate_overall_coverage(config)
    
    print("\n====== TEST COVERAGE REPORT ======")
    print(f"Repository: {repo_path}")
    print(f"Total implementations: {metrics['total_implementations']}")
    print(f"Covered implementations: {metrics['covered_implementations']}")
    print(f"Coverage percentage: {metrics['coverage_percentage']:.2f}%")
    print("==================================\n")
    
    # Show uncovered implementations if requested
    if config.show_uncovered and metrics['uncovered_implementations'] > 0:
        uncovered = get_uncovered_implementations(config)
        
        print("\n-- UNCOVERED IMPLEMENTATIONS --")
        display_count = min(config.max_items_per_section, len(uncovered))
        for i, impl in enumerate(uncovered[:display_count]):
            print(f"{i+1}. {impl['name']} ({impl['path']})")
        
        if len(uncovered) > display_count:
            print(f"... and {len(uncovered) - display_count} more")
        print("-------------------------------\n")


def generate_json_report(repo_path: str, config: Optional[ReportConfig] = None) -> Dict:
    """Generate a JSON report for test coverage.

    Args:
        repo_path: Path to the repository
        config: Optional configuration for the report

    Returns:
        Dictionary containing the report data
    """
    if config is None:
        config = ReportConfig.with_defaults()
    
    # Get overall coverage metrics
    metrics = calculate_overall_coverage(config)
    
    report = {
        "repository": repo_path,
        "metrics": metrics,
        "timestamp": datetime.now().isoformat(),
    }
    
    # Add uncovered implementations if requested
    if config.show_uncovered and metrics['uncovered_implementations'] > 0:
        uncovered = get_uncovered_implementations(config)
        report["uncovered_implementations"] = uncovered
    
    return report


def save_json_report(repo_path: str, output_path: Optional[str] = None, config: Optional[ReportConfig] = None) -> str:
    """Generate and save a JSON report to a file.

    Args:
        repo_path: Path to the repository
        output_path: Path to save the report (default: repo_path/coverage_report.json)
        config: Optional configuration for the report

    Returns:
        Path to the saved report file
    """
    if config is None:
        config = ReportConfig.with_defaults()
    
    # Generate the report
    report = generate_json_report(repo_path, config)
    
    # Determine output path
    if output_path is None:
        output_dir = Path(repo_path) / config.output_dir
        output_dir.mkdir(exist_ok=True, parents=True)
        output_path = str(output_dir / "coverage_report.json")
    
    # Save the report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Coverage report saved to {output_path}")
    return output_path


def generate_coverage_report(
    repo_path: str, 
    output_format: str = 'console', 
    output_path: Optional[str] = None,
    config: Optional[ReportConfig] = None
) -> Union[None, Dict, str]:
    """Generate and output a coverage report for the specified repo.

    Args:
        repo_path: Path to the repository
        output_format: Format of the report ('console', 'json', or 'file')
        output_path: Path to save the report (only used if output_format is 'file')
        config: Optional configuration for the report

    Returns:
        None if console output, Dict if JSON output, or file path if file output

    Raises:
        ValueError: If an invalid output format is specified
    """
    if config is None:
        config = ReportConfig.with_defaults()
    
    if output_format == 'console':
        generate_console_report(repo_path, config)
        return None
    elif output_format == 'json':
        return generate_json_report(repo_path, config)
    elif output_format == 'file':
        return save_json_report(repo_path, output_path, config)
    else:
        raise ValueError(f"Invalid output format: {output_format}. Must be 'console', 'json', or 'file'.") 