"""
TestIndex regression guard command.

This module implements the `testindex regression-guard` command that analyzes
git changes to detect potential regressions and provide actionable recommendations.
"""
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.utils.git import GitManager
from testindex.analysis.regression_guard import RegressionGuard, RegressionThreshold, RegressionGuardError
from testindex.cli.utils.env_check import needs_env

# Set up logger
logger = get_logger(__name__)


def output_summary_table(result: Dict[str, Any]) -> None:
    """Output regression analysis summary as a rich table.
    
    Args:
        result: Regression analysis result dictionary
    """
    console = Console()
    
    # Create summary table
    table = Table(title="Regression Risk Assessment")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Status", style="green")
    
    # Risk assessment
    risk_assessment = result.get("risk_assessment", {})
    risk_level = risk_assessment.get("risk_level", "UNKNOWN")
    risk_score = risk_assessment.get("score", 0.0)
    
    # Status styling
    if risk_level == "LOW":
        status_style = "[green]✓ Safe[/green]"
    elif risk_level == "MEDIUM":
        status_style = "[yellow]⚠ Review[/yellow]"
    else:  # HIGH
        status_style = "[red]🚨 Risk[/red]"
    
    table.add_row("Risk Level", risk_level, status_style)
    table.add_row("Risk Score", f"{risk_score:.2f}", f"{risk_score:.2f}/1.0")
    table.add_row("Impacted Nodes", str(result.get("impacted_nodes_count", 0)), "")
    table.add_row("Critical Nodes", str(risk_assessment.get("critical_nodes", 0)), "")
    table.add_row("Test Coverage", f"{(1.0 - risk_assessment.get('uncovered_nodes', 0) / max(result.get('impacted_nodes_count', 1), 1)):.1%}", "")
    
    # Blocking status
    should_block = result.get("should_block", False)
    block_status = "[red]🚫 BLOCKED[/red]" if should_block else "[green]✅ SAFE[/green]"
    table.add_row("Merge Status", "BLOCKED" if should_block else "SAFE", block_status)
    
    console.print()
    console.print(table)
    console.print()


def output_recommendations(result: Dict[str, Any]) -> None:
    """Output actionable recommendations.
    
    Args:
        result: Regression analysis result dictionary
    """
    console = Console()
    recommendations = result.get("recommendations", [])
    
    if not recommendations:
        return
    
    # Create recommendations panel
    rec_text = "\n".join(recommendations)
    
    if result.get("should_block", False):
        panel_style = "red"
        title = "🚨 Regression Risk Detected"
    else:
        panel_style = "green" 
        title = "✅ Recommendations"
    
    panel = Panel(rec_text, title=title, border_style=panel_style)
    console.print(panel)
    console.print()


def output_violations(result: Dict[str, Any]) -> None:
    """Output threshold violations if any.
    
    Args:
        result: Regression analysis result dictionary
    """
    console = Console()
    violations = result.get("threshold_violations", [])
    
    if not violations:
        return
    
    # Create violations table
    table = Table(title="Threshold Violations", border_style="red")
    table.add_column("Violation", style="red")
    
    for violation in violations:
        table.add_row(violation)
    
    console.print(table)
    console.print()


def output_test_plan(result: Dict[str, Any]) -> None:
    """Output test execution plan.
    
    Args:
        result: Regression analysis result dictionary
    """
    console = Console()
    test_plan = result.get("test_execution_plan", [])
    
    if not test_plan:
        console.print("[yellow]No automated tests found for impacted code.[/yellow]\n")
        return
    
    # Create test plan table
    table = Table(title="Prioritized Test Execution Plan")
    table.add_column("Priority", style="cyan", justify="center")
    table.add_column("Test File", style="green")
    
    for i, test_file in enumerate(test_plan[:10], 1):  # Show top 10
        table.add_row(str(i), test_file)
    
    console.print()
    console.print(table)
    
    if len(test_plan) > 10:
        console.print(f"\n[dim]... and {len(test_plan) - 10} more tests[/dim]")
    
    console.print()


def output_json(result: Dict[str, Any], output_path: str) -> None:
    """Output regression analysis as JSON to a file.
    
    Args:
        result: Regression analysis result dictionary
        output_path: Path to write JSON output
    """
    try:
        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        logger.info(f"Wrote regression analysis to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write JSON output: {e}")
        raise click.ClickException(f"Failed to write JSON output: {e}")


@click.command('regression-guard', help='Analyze changes for regression risk and provide recommendations')
@click.option('--since', required=True, 
              help='Git reference to analyze changes from (e.g., HEAD~1, main, commit hash)')
@click.option('--until', default="HEAD", show_default=True,
              help='Git reference to analyze changes to')
@click.option('--max-risk-score', type=float, default=0.7, show_default=True,
              help='Maximum allowed risk score (0.0-1.0)')
@click.option('--max-impacted-nodes', type=int, default=50, show_default=True,
              help='Maximum allowed impacted nodes')
@click.option('--min-test-coverage', type=float, default=0.8, show_default=True,
              help='Minimum required test coverage ratio (0.0-1.0)')
@click.option('--max-critical-nodes', type=int, default=10, show_default=True,
              help='Maximum allowed critical nodes')
@click.option('--depth', default=2, show_default=True, type=int,
              help='Depth of call graph traversal for impact analysis')
@click.option('--json', 'json_output', type=click.Path(),
              help='Path to write detailed JSON analysis')
@click.option('--detailed-output', type=click.Path(),
              help='Path to write comprehensive analysis with impacted nodes details')
@click.option('--exit-code', is_flag=True,
              help='Exit with non-zero code if change should be blocked')
@click.option('--summary-only', is_flag=True,
              help='Only show summary table, skip detailed output')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@common_options
@needs_env('regression-guard')
def regression_guard_command(since, until, max_risk_score, max_impacted_nodes, 
                            min_test_coverage, max_critical_nodes, depth,
                            json_output, detailed_output, exit_code, summary_only,
                            verbose: bool = False, no_env_check: bool = False, **kwargs):
    """Analyze git changes for regression risk and provide actionable recommendations.
    
    This command evaluates code changes against configurable thresholds to detect
    potential regressions before they reach production. It provides risk assessment,
    threshold violation analysis, and prioritized test execution plans.
    
    Args:
        since: Git reference to analyze changes from
        until: Git reference to analyze changes to
        max_risk_score: Maximum allowed risk score (0.0-1.0)
        max_impacted_nodes: Maximum allowed impacted nodes
        min_test_coverage: Minimum required test coverage ratio
        max_critical_nodes: Maximum allowed critical nodes
        depth: Depth of call graph traversal
        json_output: Path to write JSON analysis
        detailed_output: Path to write detailed analysis
        exit_code: Whether to exit with error code for blocking conditions
        summary_only: Whether to show only summary
        verbose: Whether to show verbose output
        no_env_check: Whether to skip environment checks
        kwargs: Additional arguments
    """
    start_time = time.time()
    console = Console()
    
    try:
        # Check if running in a git repository
        git_manager = GitManager()
        if not git_manager.is_git_repository():
            console.print("[bold red]Error:[/bold red] Not a git repository")
            sys.exit(1)
        
        # Create custom thresholds
        thresholds = RegressionThreshold(
            max_risk_score=max_risk_score,
            max_impacted_nodes=max_impacted_nodes,
            min_test_coverage=min_test_coverage,
            max_critical_nodes=max_critical_nodes
        )
        
        # Initialize regression guard
        guard = RegressionGuard(thresholds=thresholds, depth=depth)
        
        # Run regression analysis
        with console.status("[bold blue]Analyzing changes for regression risk..."):
            result = guard.evaluate_change_risk(
                since=since,
                until=until,
                output_file=Path(detailed_output) if detailed_output else None
            )
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Output results based on flags
        if not summary_only:
            output_summary_table(result)
            output_violations(result)
            output_recommendations(result)
            output_test_plan(result)
        else:
            output_summary_table(result)
        
        # Write JSON output if requested
        if json_output:
            output_json(result, json_output)
        
        # Output timing and summary
        console.print(f"⚡ Regression analysis completed in {duration:.2f}s")
        
        # Show quick summary line
        risk_level = result.get("risk_assessment", {}).get("risk_level", "UNKNOWN")
        should_block = result.get("should_block", False)
        nodes_count = result.get("impacted_nodes_count", 0)
        
        if should_block:
            console.print(f"[red]🚫 BLOCKED: {risk_level} risk detected ({nodes_count} nodes impacted)[/red]")
        else:
            console.print(f"[green]✅ SAFE: {risk_level} risk assessment ({nodes_count} nodes impacted)[/green]")
        
        # Exit with appropriate code
        if exit_code and should_block:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except RegressionGuardError as e:
        logger.error(f"Regression analysis failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in regression guard: {e}")
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        sys.exit(1) 