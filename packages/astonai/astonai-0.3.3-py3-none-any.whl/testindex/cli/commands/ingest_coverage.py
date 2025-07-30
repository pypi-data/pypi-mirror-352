"""
TestIndex ingest-coverage command.

This module implements the `testindex ingest-coverage` command that ingests coverage data
into the knowledge graph.
"""
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import click
from rich.console import Console

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger
from testindex.core.exceptions import CLIError
from testindex.analysis.coverage.ingest import ingest_coverage

# Set up logger
logger = get_logger(__name__)

# Constants
DEFAULT_CONFIG_DIR = ".testindex"
DEFAULT_CONFIG_FILE = "config.yml"


@click.command('ingest-coverage', help='Ingest coverage data into the knowledge graph')
@click.option('--coverage-file', type=click.Path(exists=True), required=True,
              help='Path to coverage.xml file to ingest')
@click.option('--kg-dir', type=click.Path(), default=f"{DEFAULT_CONFIG_DIR}/knowledge_graph",
              help='Path to knowledge graph directory')
@common_options
def ingest_coverage_command(coverage_file, kg_dir, **kwargs):
    """Ingest coverage data into the knowledge graph.
    
    This command:
    1. Parses coverage data from a coverage.xml file
    2. Updates implementation nodes in the knowledge graph with coverage data
    
    Exit codes:
    - 0: Success
    - 1: Error occurred
    """
    try:
        console = Console()
        
        # Process paths
        kg_dir_path = Path(kg_dir)
        coverage_file_path = Path(coverage_file)
        
        # Check if knowledge graph directory exists
        if not kg_dir_path.exists():
            console.print(f"[red]Error:[/] Knowledge graph directory not found: {kg_dir_path}")
            console.print("Have you run `testindex init` first?")
            sys.exit(1)
            
        # Check if coverage file exists
        if not coverage_file_path.exists():
            console.print(f"[red]Error:[/] Coverage file not found: {coverage_file_path}")
            sys.exit(1)
            
        # Ingest coverage data
        console.print(f"Ingesting coverage data from [cyan]{coverage_file_path}[/] into knowledge graph...")
        updated, total = ingest_coverage(str(coverage_file_path), str(kg_dir_path))
        
        # Display results
        if updated > 0:
            console.print(f"[green]Success:[/] Updated {updated} of {total} implementation nodes with coverage data")
        else:
            console.print(f"[yellow]Warning:[/] No implementation nodes were updated with coverage data")
            console.print("Possible reasons:")
            console.print("- Coverage file format not recognized")
            console.print("- No matching function/method names found")
            console.print("- Coverage data already exists for all nodes")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise CLIError(f"{e}") 