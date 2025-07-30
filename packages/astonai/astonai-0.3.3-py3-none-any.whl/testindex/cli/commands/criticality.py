"""
Criticality CLI commands for TestIndex.

This module provides CLI commands for analyzing code criticality and 
tuning criticality weights.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver
from testindex.analysis.criticality_scorer import CriticalityScorer, CriticalityWeights, CriticalityError

logger = get_logger(__name__)


@click.group()
def criticality():
    """Analyze code criticality and manage criticality weights."""
    pass


@criticality.command()
@click.option('--top', '-n', default=10, help='Number of top critical nodes to show')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
@click.option('--nodes-file', type=click.Path(exists=True), 
              help='Path to nodes.json file (default: .testindex/knowledge_graph/nodes.json)')
@click.option('--edges-file', type=click.Path(exists=True), 
              help='Path to edges.json file (default: .testindex/knowledge_graph/edges.json)')
@click.option('--config', type=click.Path(exists=True), 
              help='Path to criticality weights config file')
@click.option('--verbose', is_flag=True, help='Show detailed scoring information')
def analyze(top: int, output_format: str, nodes_file: Optional[str], 
           edges_file: Optional[str], config: Optional[str], verbose: bool):
    """Analyze repository criticality and show top critical nodes."""
    console = Console()
    
    try:
        # Initialize scorer with config
        if config:
            scorer = CriticalityScorer.from_config_file(Path(config))
        else:
            scorer = CriticalityScorer()
        
        # Use default paths if not provided
        if nodes_file is None:
            nodes_file = str(PathResolver.nodes_file())
        if edges_file is None:
            edges_file = str(PathResolver.edges_file())
        
        nodes_path = Path(nodes_file)
        edges_path = Path(edges_file)
        
        if not nodes_path.exists():
            console.print(f"[red]Error:[/red] Nodes file not found: {nodes_path}")
            console.print("[yellow]Tip:[/yellow] Run 'aston graph build' to generate knowledge graph files")
            raise click.Abort()
        
        if not edges_path.exists():
            console.print(f"[red]Error:[/red] Edges file not found: {edges_path}")
            console.print("[yellow]Tip:[/yellow] Run 'aston graph build' to generate knowledge graph files")
            raise click.Abort()
        
        # Load data
        with console.status("[cyan]Loading knowledge graph data..."):
            with open(nodes_path, 'r') as f:
                nodes_data = json.load(f)
            
            with open(edges_path, 'r') as f:
                edges_data = json.load(f)
            
            # Handle both direct list and object with fields formats
            if isinstance(nodes_data, dict) and "nodes" in nodes_data:
                nodes = nodes_data["nodes"]
            else:
                nodes = nodes_data
                
            if isinstance(edges_data, dict) and "edges" in edges_data:
                edges = edges_data["edges"]
            else:
                edges = edges_data
        
        if verbose:
            scorer.weights.verbose_logging = True
            scorer.weights.export_intermediate_data = True
        
        # Calculate criticality scores
        with console.status("[cyan]Calculating criticality scores..."):
            start_time = time.time()
            top_critical_nodes = scorer.get_top_critical_nodes(nodes, edges, top_k=top)
            duration = time.time() - start_time
        
        # Display results
        if output_format == 'json':
            result = {
                "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "calculation_duration": round(duration, 2),
                "top_critical_nodes": top_critical_nodes,
                "weights": {
                    "centrality_weight": scorer.weights.centrality_weight,
                    "depth_weight": scorer.weights.depth_weight
                },
                "cache_stats": scorer.get_cache_stats()
            }
            console.print(json.dumps(result, indent=2))
        else:
            # Display as rich table
            _display_criticality_table(console, top_critical_nodes, duration, scorer)
        
    except CriticalityError as e:
        console.print(f"[red]Criticality analysis error:[/red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        logger.error(f"Failed to analyze criticality: {e}")
        raise click.Abort()


@criticality.command()
@click.option('--output', '-o', type=click.Path(), 
              help='Output file for criticality scores (default: stdout)')
@click.option('--nodes-file', type=click.Path(exists=True), 
              help='Path to nodes.json file')
@click.option('--edges-file', type=click.Path(exists=True), 
              help='Path to edges.json file')
@click.option('--config', type=click.Path(exists=True), 
              help='Path to criticality weights config file')
def export(output: Optional[str], nodes_file: Optional[str], 
          edges_file: Optional[str], config: Optional[str]):
    """Export criticality scores to JSON file."""
    console = Console()
    
    try:
        # Initialize scorer
        if config:
            scorer = CriticalityScorer.from_config_file(Path(config))
        else:
            scorer = CriticalityScorer()
        
        # Use default paths
        if nodes_file is None:
            nodes_file = str(PathResolver.nodes_file())
        if edges_file is None:
            edges_file = str(PathResolver.edges_file())
        
        # Load data
        with console.status("[cyan]Loading knowledge graph data..."):
            with open(nodes_file, 'r') as f:
                nodes = json.load(f)
            with open(edges_file, 'r') as f:
                edges = json.load(f)
        
        # Calculate scores
        with console.status("[cyan]Calculating criticality scores..."):
            scores = scorer.calculate_criticality_scores(nodes, edges)
        
        # Prepare export data
        export_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "weights": {
                "centrality_weight": scorer.weights.centrality_weight,
                "depth_weight": scorer.weights.depth_weight,
                "entry_point_patterns": scorer.weights.entry_point_patterns
            },
            "scores": scores,
            "statistics": {
                "total_nodes": len(scores),
                "max_score": max(scores.values()) if scores else 0.0,
                "avg_score": sum(scores.values()) / len(scores) if scores else 0.0
            }
        }
        
        # Write output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            console.print(f"[green]Criticality scores exported to:[/green] {output_path}")
        else:
            console.print(json.dumps(export_data, indent=2))
        
    except Exception as e:
        console.print(f"[red]Export failed:[/red] {e}")
        logger.error(f"Failed to export criticality scores: {e}")
        raise click.Abort()


@criticality.command()
@click.option('--output', '-o', default='criticality_weights.yaml', 
              help='Output file for tuned weights')
@click.option('--nodes-file', type=click.Path(exists=True), 
              help='Path to nodes.json file')
@click.option('--edges-file', type=click.Path(exists=True), 
              help='Path to edges.json file')
@click.option('--test-correlation', is_flag=True, 
              help='Tune weights based on test correlation')
def tune(output: str, nodes_file: Optional[str], edges_file: Optional[str], 
         test_correlation: bool):
    """Tune criticality weights for optimal results."""
    console = Console()
    
    try:
        # For now, provide a basic tuning approach
        # Future versions could implement more sophisticated optimization
        
        console.print("[yellow]Weight tuning is currently basic.[/yellow]")
        console.print("Consider these guidelines for manual tuning:")
        
        guidelines = [
            ("centrality_weight", "0.7", "Good for highly interconnected codebases"),
            ("depth_weight", "0.3", "Good for deep call hierarchies"),
            ("centrality_weight", "0.5", "Balanced for mixed architectures"),
            ("depth_weight", "0.5", "Balanced for mixed architectures")
        ]
        
        table = Table(title="Weight Tuning Guidelines")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Best For", style="white")
        
        for param, value, description in guidelines:
            table.add_row(param, value, description)
        
        console.print(table)
        
        # Create a sample tuned config
        tuned_config = {
            "centrality_weight": 0.6,
            "depth_weight": 0.4,
            "entry_point_patterns": [
                "main", "test_*", "*_handler", "*_endpoint", 
                "*_view", "handle_*", "*_main", "run_*"
            ],
            "normalization": {
                "max_call_depth": 25,
                "min_graph_size": 5
            },
            "performance": {
                "enable_caching": True,
                "auto_invalidate_cache": True,
                "max_batch_size": 1000
            },
            "debug": {
                "verbose_logging": False,
                "export_intermediate_data": False
            }
        }
        
        # Write tuned config
        import yaml
        output_path = Path(output)
        with open(output_path, 'w') as f:
            yaml.dump(tuned_config, f, default_flow_style=False, indent=2)
        
        console.print(f"\n[green]Sample tuned configuration written to:[/green] {output_path}")
        console.print("[yellow]Review and adjust weights based on your codebase characteristics.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Tuning failed:[/red] {e}")
        logger.error(f"Failed to tune weights: {e}")
        raise click.Abort()


def _display_criticality_table(console: Console, top_nodes: List[Dict[str, Any]], 
                              duration: float, scorer: CriticalityScorer) -> None:
    """Display criticality results in a rich table."""
    
    # Create summary panel
    summary_text = f"""
[cyan]Analysis completed in {duration:.2f}s[/cyan]
[yellow]Weights:[/yellow] centrality={scorer.weights.centrality_weight}, depth={scorer.weights.depth_weight}
[green]Found {len(top_nodes)} critical nodes[/green]
    """
    
    console.print(Panel(summary_text.strip(), title="Criticality Analysis Summary"))
    
    # Create main results table
    table = Table(title=f"Top {len(top_nodes)} Critical Nodes")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Node ID", style="blue", width=20)
    table.add_column("Name", style="green", width=25)
    table.add_column("File", style="white", width=30)
    table.add_column("Criticality", style="red", width=12)
    table.add_column("Type", style="yellow", width=12)
    
    for i, node in enumerate(top_nodes, 1):
        criticality_score = node.get('criticality_score', 0.0)
        node_id = node.get('id', 'N/A')[:18] + '...' if len(node.get('id', '')) > 20 else node.get('id', 'N/A')
        name = node.get('name', 'N/A')[:23] + '...' if len(node.get('name', '')) > 25 else node.get('name', 'N/A')
        file_path = node.get('file_path', 'N/A')
        if len(file_path) > 28:
            file_path = '...' + file_path[-25:]
        node_type = node.get('type', 'N/A')
        
        # Color-code criticality score
        if criticality_score >= 0.7:
            criticality_style = "red bold"
        elif criticality_score >= 0.4:
            criticality_style = "yellow"
        else:
            criticality_style = "green"
        
        table.add_row(
            str(i),
            node_id,
            name,
            file_path,
            f"[{criticality_style}]{criticality_score:.3f}[/{criticality_style}]",
            node_type
        )
    
    console.print(table)
    
    # Show cache stats if available
    cache_stats = scorer.get_cache_stats()
    if cache_stats.get('cache_enabled'):
        console.print(f"\n[dim]Cache: {cache_stats.get('cached_scores', 0)} scores cached[/dim]") 