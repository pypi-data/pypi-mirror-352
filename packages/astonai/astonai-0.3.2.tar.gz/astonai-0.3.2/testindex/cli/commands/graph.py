"""
TestIndex graph command.

This module implements the `testindex graph` command that generates edges for the knowledge graph.
"""
import os
import sys
import json
import webbrowser
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

import click
from rich.console import Console
from rich.table import Table

from testindex.core.cli.runner import common_options
from testindex.core.config import ConfigModel
from testindex.core.exceptions import CLIError
from testindex.core.path_resolution import PathResolver
from testindex.core.utils import ensure_directory
from testindex.core.logging import get_logger
from testindex.core.filtering import FileFilter, FilterPresets, PatternType
from testindex.preprocessing.edge_extractor import EdgeExtractor
from testindex.visualization.dot_exporter import DotExporter
from testindex.visualization.viewer_packager import ViewerPackager
from testindex.cli.utils.env_check import needs_env
from testindex.cli.common_filters import add_filter_options, create_file_filter, handle_filter_display
from testindex.core.filter_contract import FilterContract

# Set up logger
logger = get_logger(__name__)

# Constants
DEFAULT_CONFIG_DIR = ".testindex"
DEFAULT_CONFIG_FILE = "config.yml"


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment variables.
    
    Fallback order: 
    1. .testindex/config.yml 
    2. environment variables 
    3. defaults
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    
    Raises:
        CLIError: If configuration cannot be loaded
    """
    try:
        # 1. Try to load from .testindex/config.yml
        config_path = Path(DEFAULT_CONFIG_DIR) / DEFAULT_CONFIG_FILE
        if config_path.exists():
            logger.info(f"Loading config from {config_path}")
            import yaml
            
            # Parse YAML
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
                
                # Add default values if missing
                if 'offline_mode' not in config_data:
                    config_data['offline_mode'] = True
                if 'knowledge_graph_dir' not in config_data:
                    config_data['knowledge_graph_dir'] = str(Path(DEFAULT_CONFIG_DIR) / "knowledge_graph")

                logger.info(f"Parsed config data: {config_data}")
                return config_data
        
        # 2. Use defaults (offline mode)
        logger.info("Using default offline configuration")
        return {
            "offline_mode": True,
            "knowledge_graph_dir": Path(DEFAULT_CONFIG_DIR) / "knowledge_graph"
        }
    
    except Exception as e:
        error_msg = f"Failed to load configuration: {e}"
        logger.error(error_msg)
        raise CLIError(error_msg)


def check_prerequisites() -> bool:
    """Check if prerequisites for edge extraction are available.
    
    Returns:
        bool: True if prerequisites are met, False otherwise
    """
    try:
        # Check if edge extractor requirements are met
        if not EdgeExtractor.check_requirements():
            logger.error("Edge extraction requirements not met")
            return False
            
        # Check if chunks.json and nodes.json exist
        kg_dir = PathResolver.knowledge_graph_dir()
        chunks_file = kg_dir / "chunks.json"
        nodes_file = kg_dir / "nodes.json"
        
        if not chunks_file.exists():
            logger.error(f"Required file not found: {chunks_file}")
            return False
            
        if not nodes_file.exists():
            logger.error(f"Required file not found: {nodes_file}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error checking prerequisites: {e}")
        return False


def extract_edges(config: Dict[str, Any], verbose: bool = False,
                  include_patterns: Optional[List[str]] = None,
                  exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Extract edges from code chunks.
    
    Args:
        config: Configuration dictionary
        verbose: Whether to display verbose output
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        
    Returns:
        Dict with edge extraction statistics
        
    Raises:
        CLIError: If edge extraction fails
    """
    try:
        # Create config model from config dict
        config_model = ConfigModel(**config) if config else ConfigModel()
        
        # Initialize edge extractor
        extractor = EdgeExtractor(
            config=config_model,
            repo_path=PathResolver.repo_root(),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Get paths
        kg_dir = PathResolver.knowledge_graph_dir()
        chunks_file = kg_dir / "chunks.json"
        nodes_file = kg_dir / "nodes.json"
        edges_file = PathResolver.edges_file()
        
        if verbose:
            logger.info(f"Using chunks file: {chunks_file}")
            logger.info(f"Using nodes file: {nodes_file}")
            logger.info(f"Output will be written to: {edges_file}")
            if include_patterns:
                logger.info(f"Include patterns: {include_patterns}")
            if exclude_patterns:
                logger.info(f"Exclude patterns: {exclude_patterns}")
        
        # Extract edges
        result = extractor.extract_edges(
            chunks_file=chunks_file,
            nodes_file=nodes_file,
            output_file=edges_file
        )
        
        return result
    
    except Exception as e:
        error_msg = f"Failed to extract edges: {e}"
        logger.error(error_msg)
        raise CLIError(error_msg)


def get_graph_stats() -> Dict[str, Any]:
    """Get statistics about the knowledge graph.
    
    Returns:
        Dict with graph statistics
    
    Raises:
        CLIError: If files cannot be read
    """
    try:
        # Get paths
        kg_dir = PathResolver.knowledge_graph_dir()
        nodes_file = kg_dir / "nodes.json"
        edges_file = kg_dir / "edges.json"
        chunks_file = kg_dir / "chunks.json"
        
        stats = {}
        
        # Count nodes by type
        if nodes_file.exists():
            with open(nodes_file, 'r') as f:
                nodes = json.load(f)
                
            stats['total_nodes'] = len(nodes)
            
            # Count by type
            node_types = {}
            for node in nodes:
                node_type = node.get('type', 'Unknown')
                node_types[node_type] = node_types.get(node_type, 0) + 1
                
            stats['node_types'] = node_types
        else:
            stats['total_nodes'] = 0
            stats['node_types'] = {}
            
        # Count edges by type
        if edges_file.exists():
            with open(edges_file, 'r') as f:
                edges_data = json.load(f)
                edges = edges_data.get('edges', [])
                
            stats['total_edges'] = len(edges)
            
            # Count by type
            edge_types = {}
            for edge in edges:
                edge_type = edge.get('type', 'Unknown')
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                
            stats['edge_types'] = edge_types
            
            # Get generation timestamp
            stats['generated_at'] = edges_data.get('generated_at', 'Unknown')
        else:
            stats['total_edges'] = 0
            stats['edge_types'] = {}
            stats['generated_at'] = None
            
        # Get file sizes
        if nodes_file.exists():
            stats['nodes_file_size'] = nodes_file.stat().st_size / (1024 * 1024)  # MB
        if edges_file.exists():
            stats['edges_file_size'] = edges_file.stat().st_size / (1024 * 1024)  # MB
        if chunks_file.exists():
            stats['chunks_file_size'] = chunks_file.stat().st_size / (1024 * 1024)  # MB
            
        return stats
    
    except Exception as e:
        error_msg = f"Failed to get graph statistics: {e}"
        logger.error(error_msg)
        raise CLIError(error_msg)


def output_summary(stats: Dict[str, Any]) -> None:
    """Output edge extraction summary to console.
    
    Args:
        stats: Edge extraction statistics
    """
    console = Console()
    
    # Create table
    table = Table(title="Edge Extraction Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # Add rows
    table.add_row("Total Edges", str(stats.get('total', 0)))
    table.add_row("CALLS Edges", str(stats.get('CALLS', 0)))
    table.add_row("IMPORTS Edges", str(stats.get('IMPORTS', 0)))
    if 'processed_files' in stats:
        table.add_row("Files Processed", str(stats.get('processed_files', 0)))
    if 'skipped_files' in stats:
        table.add_row("Files Skipped", str(stats.get('skipped_files', 0)))
    table.add_row("Duration", f"{stats.get('duration', 0):.2f}s")
    
    # Output table
    console.print(table)


def output_graph_stats(stats: Dict[str, Any]) -> None:
    """Output graph statistics to console.
    
    Args:
        stats: Graph statistics
    """
    console = Console()
    
    # Create table
    table = Table(title="Knowledge Graph Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # Add rows for node stats
    table.add_row("Total Nodes", str(stats.get('total_nodes', 0)))
    
    # Add rows for node types
    node_types = stats.get('node_types', {})
    for node_type, count in node_types.items():
        table.add_row(f"Nodes: {node_type}", str(count))
        
    # Add empty row as separator
    table.add_row("", "")
    
    # Add rows for edge stats
    table.add_row("Total Edges", str(stats.get('total_edges', 0)))
    
    # Add rows for edge types
    edge_types = stats.get('edge_types', {})
    for edge_type, count in edge_types.items():
        table.add_row(f"Edges: {edge_type}", str(count))
        
    # Add empty row as separator
    table.add_row("", "")
    
    # Add file size information
    if 'nodes_file_size' in stats:
        table.add_row("nodes.json Size", f"{stats['nodes_file_size']:.2f} MB")
    if 'edges_file_size' in stats:
        table.add_row("edges.json Size", f"{stats['edges_file_size']:.2f} MB")
    if 'chunks_file_size' in stats:
        table.add_row("chunks.json Size", f"{stats['chunks_file_size']:.2f} MB")
        
    # Add generated timestamp if available
    if stats.get('generated_at'):
        table.add_row("Generated At", stats['generated_at'])
    
    # Output table
    console.print(table)


def extract_edges_with_filter(config: Dict[str, Any], file_filter: FileFilter, verbose: bool = False) -> Dict[str, Any]:
    """Extract edges using the file filter.
    
    Args:
        config: Configuration dictionary
        file_filter: FileFilter instance with configured patterns
        verbose: Whether to display verbose output
        
    Returns:
        Dict with edge extraction statistics
        
    Raises:
        CLIError: If edge extraction fails
    """
    try:
        # Get filtered file list
        python_files = file_filter.discover_files(['.py'])
        
        if not python_files:
            raise CLIError("No Python files found to process. Check your filter patterns or use --dry-run to debug.")
        
        # Convert file paths to relative paths for pattern matching
        repo_root = PathResolver.repo_root()
        include_patterns = []
        exclude_patterns = []
        
        # Build patterns from the file filter for EdgeExtractor compatibility
        for pattern in file_filter.include_patterns:
            if pattern.pattern_type == PatternType.GLOB:
                include_patterns.append(pattern.pattern)
        
        for pattern in file_filter.exclude_patterns:
            if pattern.pattern_type == PatternType.GLOB:
                exclude_patterns.append(pattern.pattern)
        
        # Initialize edge extractor with patterns
        config_model = ConfigModel(**config) if config else ConfigModel()
        extractor = EdgeExtractor(
            config=config_model,
            repo_path=repo_root,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns
        )
        
        # Extract edges
        result = extractor.extract_edges()
        
        return result
        
    except Exception as e:
        logger.error(f"Error extracting edges: {e}")
        raise CLIError(f"Failed to extract edges: {str(e)}")


def display_edge_results(result: Dict[str, Any], verbose: bool = False):
    """Display edge extraction results.
    
    Args:
        result: Results dictionary from edge extraction
        verbose: Whether to show verbose output
    """
    console = Console()
    
    # Create summary table
    table = Table(title="Edge Extraction Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Edges", str(result.get("total", 0)))
    table.add_row("CALLS Edges", str(result.get("CALLS", 0)))
    table.add_row("IMPORTS Edges", str(result.get("IMPORTS", 0)))
    table.add_row("Files Processed", str(result.get("processed_files", 0)))
    table.add_row("Files Skipped", str(result.get("skipped_files", 0)))
    table.add_row("Duration", f"{result.get('duration', 0):.2f}s")
    
    console.print(table)
    
    # Show parsing statistics if available
    parsing_stats = result.get("parsing_stats")
    if parsing_stats and any(parsing_stats.values()):
        console.print()
        stats_table = Table(title="Parsing Statistics")
        stats_table.add_column("Parser", style="cyan")
        stats_table.add_column("Count", style="green")
        
        stats_table.add_row("Standard AST", str(parsing_stats.get("ast", 0)))
        stats_table.add_row("Parso (fallback)", str(parsing_stats.get("parso", 0)))
        stats_table.add_row("LibCST (fallback)", str(parsing_stats.get("libcst", 0)))
        stats_table.add_row("Regex (fallback)", str(parsing_stats.get("regex", 0)))
        stats_table.add_row("Failed", str(parsing_stats.get("failed", 0)))
        
        console.print(stats_table)
    
    # Success message
    total_edges = result.get("total", 0)
    console.print(f"[bold green]Success![/] Generated edges.json with {total_edges} relationships")


@click.group('graph', help='Knowledge graph operations')
@common_options
def graph_command(**kwargs):
    """Knowledge graph operations.
    
    This command provides subcommands for working with the knowledge graph:
    - build: Generate edges.json from code chunks
    - stats: Display statistics about the knowledge graph
    - export: Export graph to DOT format
    - view: Open graph in interactive viewer
    """
    pass


@graph_command.command('build', help='Extract function calls and module imports')
@add_filter_options
@common_options
def build_command(include, exclude, include_regex, exclude_regex, preset, dry_run, show_patterns, verbose, **kwargs):
    """Generate edges.json from code chunks.
    
    This command analyzes code chunks to extract relationships between functions and modules.
    It creates CALLS edges for function calls and IMPORTS edges for module imports.
    
    Advanced filtering options:
    - Use --preset for common configurations (python-only, no-tests, source-only, minimal)
    - Use --include/--exclude for glob patterns
    - Use --include-regex/--exclude-regex for regex patterns
    - Use .astonignore file for persistent patterns
    - Use --dry-run to preview file selection
    
    Examples:
        # Build with default filtering
        aston graph build
        
        # Use a preset configuration
        aston graph build --preset no-tests
        
        # Include only specific directories
        aston graph build --include "src/**/*.py" --include "lib/**/*.py"
        
        # Use regex patterns
        aston graph build --include-regex ".*/(core|utils)/.*\\.py$"
        
        # Dry run to see what would be processed
        aston graph build --dry-run --preset python-only
    """
    try:
        # Create and configure file filter
        repo_root = PathResolver.repo_root()
        file_filter = create_file_filter(
            repo_root=repo_root,
            include=include,
            exclude=exclude,
            include_regex=include_regex,
            exclude_regex=exclude_regex,
            preset=preset
        )
        
        # Handle display options (show patterns or dry run)
        if handle_filter_display(file_filter, show_patterns, dry_run, verbose):
            return
        
        # Check filter manifest compatibility
        filter_contract = FilterContract(file_filter)
        
        kg_dir = PathResolver.knowledge_graph_dir()
        manifest_path = kg_dir / "filter_manifest.json"
        
        if manifest_path.exists():
            try:
                stored_manifest = filter_contract.load_manifest(manifest_path)
                if not filter_contract.validate_manifest(stored_manifest):
                    click.echo("⚠️  Warning: Filter patterns have changed since last init!")
                    click.echo("   The graph may not match the current filter settings.")
                    click.echo("   Run 'aston init --force' to regenerate with new filters.")
                    click.echo()
            except Exception as e:
                logger.warning(f"Could not validate filter manifest: {e}")
        
        # Load config
        config = load_config()
        
        # Extract edges with filtering
        result = extract_edges_with_filter(config, file_filter, verbose)
        
        # Display results
        display_edge_results(result, verbose)
        
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        raise CLIError(f"Failed to build graph: {str(e)}")


@graph_command.command('stats', help='Display knowledge graph statistics')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@needs_env('graph')
def stats_command(no_env_check: bool = False):
    """Display statistics about the knowledge graph.
    
    This command displays information about the knowledge graph,
    including node and edge counts, types, and file sizes.
    """
    console = Console()
    
    try:
        # Get graph statistics
        stats = get_graph_stats()
        
        # Output statistics
        output_graph_stats(stats)
        
    except CLIError as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {str(e)}")
        sys.exit(1)


@graph_command.command('export', help='Export graph to DOT format')
@click.option('--output', '-o', type=click.Path(), default="graph.dot",
              help='Output file path (default: graph.dot)')
@click.option('--format', '-f', type=click.Choice(['dot']), default='dot',
              help='Output format (currently only DOT supported)')
@click.option('--filter', '-t', multiple=True,
              type=click.Choice(['CALLS', 'IMPORTS']),
              help='Edge types to include (can be used multiple times)')
@click.option('--open', is_flag=True, help='Open viewer after export')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@needs_env('graph')
def export_command(output, format, filter, open, no_env_check: bool = False):
    """Export knowledge graph to DOT format.
    
    This command exports the knowledge graph to Graphviz DOT format,
    which can be used with external visualization tools or our built-in viewer.
    """
    console = Console()
    
    try:
        # Create exporter with edge filter
        edge_filter = list(filter) if filter else None
        exporter = DotExporter(edge_filter=edge_filter)
        
        # Get output path
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = PathResolver.repo_root() / output_path
            
        # Export graph
        console.print(f"[bold]Exporting graph to {output_path}...[/]")
        exporter.export_dot(output_path)
        
        # Open viewer if requested
        if open:
            viewer_dir = PathResolver.knowledge_graph_dir().parent / "viewer"
            ViewerPackager.ensure_viewer_assets(viewer_dir)
            
            # Copy DOT file to viewer directory
            shutil.copy2(output_path, viewer_dir / "graph.dot")
            
            # Open viewer
            viewer_path = viewer_dir / "index.html"
            webbrowser.open(f"file://{viewer_path}")
            
        console.print(f"[bold green]Success![/] Graph exported to {output_path}")
        
    except CLIError as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {str(e)}")
        sys.exit(1)


@graph_command.command('view', help='Open graph in interactive viewer')
@click.option('--filter', '-t', multiple=True,
              type=click.Choice(['CALLS', 'IMPORTS']),
              help='Edge types to include (can be used multiple times)')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@needs_env('graph')
def view_command(filter, no_env_check: bool = False):
    """Open knowledge graph in interactive viewer.
    
    This command exports the graph and opens it in our built-in
    D3-force based interactive viewer.
    """
    console = Console()
    
    try:
        # Create viewer directory
        viewer_dir = PathResolver.knowledge_graph_dir().parent / "viewer"
        ensure_directory(viewer_dir)
        
        # Export graph with filter
        edge_filter = list(filter) if filter else None
        exporter = DotExporter(edge_filter=edge_filter)
        exporter.export_dot(viewer_dir / "graph.dot")
        
        # Create viewer assets
        ViewerPackager.ensure_viewer_assets(viewer_dir)
        
        # Open viewer
        viewer_path = viewer_dir / "index.html"
        webbrowser.open(f"file://{viewer_path}")
        
        console.print("[bold green]Success![/] Opening graph viewer in browser")
        
    except CLIError as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {str(e)}")
        sys.exit(1) 