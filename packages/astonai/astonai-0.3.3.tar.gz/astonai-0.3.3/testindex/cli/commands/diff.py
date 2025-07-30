"""
TestIndex diff command.

This module implements the `testindex diff` command that analyzes git diffs
to identify impacted implementation nodes and related tests.
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

import click
from rich.console import Console
from rich.table import Table

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.utils.git import GitManager
from testindex.analysis.diff_analyzer import DiffAnalyzer
from testindex.cli.utils.env_check import needs_env

# Set up logger
logger = get_logger(__name__)


def validate_git_reference(ctx, param, value):
    """Validate that a string is a valid git reference.
    
    Args:
        ctx: Click context
        param: Parameter being validated
        value: The value to validate
        
    Returns:
        The validated value
    
    Raises:
        click.BadParameter: If the value is not a valid git reference
    """
    if not value:
        return value
        
    try:
        # Check if we're in a git repository
        git_manager = GitManager()
        if not git_manager.is_git_repository():
            raise click.BadParameter(f"Not a git repository")
            
        # Test if it's a valid git reference
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{value}^{{commit}}"],
            cwd=git_manager.repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
        
        if result.returncode != 0:
            raise click.BadParameter(f"'{value}' is not a valid git reference")
            
        return value
    except Exception as e:
        if isinstance(e, click.BadParameter):
            raise e
        raise click.BadParameter(str(e))


def output_table(impacted_nodes: List[Dict[str, Any]]) -> None:
    """Output impacted nodes as a rich table.
    
    Args:
        impacted_nodes: List of impacted node dictionaries
    """
    console = Console()
    
    # Create table
    table = Table(title="Impacted Implementation Nodes")
    table.add_column("File", style="cyan")
    table.add_column("Change", style="magenta")
    table.add_column("Calls In", style="green", justify="right")
    table.add_column("Calls Out", style="green", justify="right")
    table.add_column("Tests", style="yellow")
    
    # Add rows
    for node in impacted_nodes:
        file_path = node.get("file", "")
        change = node.get("change", "unknown")
        calls_in = str(node.get("calls_in", 0))
        calls_out = str(node.get("calls_out", 0))
        tests = ", ".join(node.get("tests", []))
        if len(tests) > 60:
            tests = tests[:57] + "..."
            
        # Style the change type
        change_style = ""
        if change == "added":
            change_style = "[green]added[/green]"
        elif change == "modified":
            change_style = "[yellow]modified[/yellow]"
        else:
            change_style = change
            
        table.add_row(file_path, change_style, calls_in, calls_out, tests)
    
    # Output summary if no nodes found
    if not impacted_nodes:
        console.print("\n[yellow]No impacted implementation nodes found.[/yellow]\n")
        return
        
    # Output table
    console.print()
    console.print(table)
    console.print()
    console.print(f"Found [bold]{len(impacted_nodes)}[/bold] impacted implementation nodes.")
    

def output_json(impacted_nodes: List[Dict[str, Any]], output_path: str) -> None:
    """Output impacted nodes as JSON to a file.
    
    Args:
        impacted_nodes: List of impacted node dictionaries
        output_path: Path to write JSON output
    """
    try:
        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Build output structure
        output = {
            "version": "0.3.0",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "nodes": impacted_nodes
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
            
        logger.info(f"Wrote {len(impacted_nodes)} impacted nodes to {output_file}")
    except Exception as e:
        logger.error(f"Failed to write JSON output: {e}")
        raise click.ClickException(f"Failed to write JSON output: {e}")


@click.command('diff', help='Show implementation nodes impacted by git diff')
@click.option('--since', required=True, 
              help='Git reference to diff from (e.g., HEAD~1, a commit hash, or a tag)')
@click.option('--until', default="HEAD", show_default=True,
              help='Git reference to diff to')
@click.option('--depth', default=1, show_default=True, type=int,
              help='Depth of call graph traversal')
@click.option('--json', 'json_output', type=click.Path(),
              help='Path to write JSON output')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@common_options
@needs_env('diff')
def diff_command(since, until, depth, json_output, verbose: bool = False, 
                 summary_only: bool = False, no_env_check: bool = False, **kwargs):
    """Analyze git diff to show implementation nodes and tests impacted by changes.
    
    Args:
        since: Git reference to diff from
        until: Git reference to diff to
        depth: Depth of call graph traversal
        json_output: Path to write JSON output
        verbose: Whether to show verbose output
        summary_only: Whether to only show summary
        no_env_check: Whether to skip environment checks
        kwargs: Additional arguments
    """
    # Time the operation
    start_time = time.time()
    
    console = Console()
    
    try:
        # Check if running in a git repository
        git_manager = GitManager()
        if not git_manager.is_git_repository():
            console.print("[bold red]Error:[/bold red] Not a git repository")
            sys.exit(1)
            
        # Initialize diff analyzer
        analyzer = DiffAnalyzer(depth=depth)
        
        # Run analysis
        impacted_nodes = analyzer.analyze(since=since, until=until)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Output results
        output_table(impacted_nodes)
        
        # Write JSON output if requested
        if json_output:
            output_json(impacted_nodes, json_output)
        
        # Output timing
        console.print(f"⚡ Diff analyzed in {duration:.2f} s")
        
        # Exit with success
        sys.exit(0)
    except Exception as e:
        # Log error
        logger.error(f"Error in diff command: {e}")
        
        # Print error to console
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        
        # Exit with error
        sys.exit(1) 