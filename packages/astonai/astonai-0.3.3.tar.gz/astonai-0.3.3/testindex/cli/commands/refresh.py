"""
TestIndex refresh command.

This module implements the `testindex refresh` command that intelligently updates
the knowledge graph with minimal processing by detecting changes since last run.
"""
import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from testindex.core.cli.runner import common_options
from testindex.core.exceptions import CLIError
from testindex.core.path_resolution import PathResolver
from testindex.core.utils import ensure_directory
from testindex.core.logging import get_logger
from testindex.core.filter_contract import FilterContract
from testindex.cli.common_filters import (
    add_filter_options, 
    create_file_filter, 
    handle_filter_display
)
from testindex.cli.commands.init import run_ingest_pipeline_with_files, write_config
from testindex.preprocessing.chunking.code_chunker import PythonCodeChunker
from testindex.core.config import ConfigModel
from testindex.cli.utils.env_check import needs_env

# Set up logger
logger = get_logger(__name__)

# Constants
DEFAULT_CONFIG_DIR = ".testindex"
DEFAULT_CONFIG_FILE = "config.yml"


class RefreshStrategy:
    """Strategies for refreshing the knowledge graph."""
    
    INCREMENTAL = "incremental"  # Only process changed files
    SMART = "smart"             # Incremental + dependency analysis
    FULL = "full"               # Full rebuild (same as init --force)


def analyze_changes(filter_contract: FilterContract, 
                   manifest_path: Path) -> Dict[str, Any]:
    """Analyze what has changed since the last manifest.
    
    Args:
        filter_contract: FilterContract instance
        manifest_path: Path to the stored manifest
        
    Returns:
        Dictionary with change analysis
    """
    if not manifest_path.exists():
        return {
            "status": "no_manifest",
            "message": "No previous manifest found - full refresh required",
            "requires_full_refresh": True,
            "file_changes": {"added": [], "removed": [], "modified": []},
            "filter_changes": False
        }
    
    try:
        # Load stored manifest
        stored_manifest = filter_contract.load_manifest(manifest_path)
        
        # Check filter compatibility
        filter_compatible = filter_contract.validate_manifest(stored_manifest)
        
        # Get file changes
        file_changes = filter_contract.get_changed_files(stored_manifest)
        
        total_changes = (len(file_changes["added"]) + 
                        len(file_changes["removed"]) + 
                        len(file_changes["modified"]))
        
        # Determine if full refresh is needed
        requires_full_refresh = (
            not filter_compatible or 
            len(file_changes["removed"]) > 0  # File deletions require full rebuild
        )
        
        return {
            "status": "analyzed",
            "filter_compatible": filter_compatible,
            "file_changes": file_changes,
            "total_changes": total_changes,
            "requires_full_refresh": requires_full_refresh,
            "message": f"Found {total_changes} file changes"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing changes: {e}")
        return {
            "status": "error",
            "message": f"Error analyzing changes: {e}",
            "requires_full_refresh": True,
            "file_changes": {"added": [], "removed": [], "modified": []},
            "filter_changes": False
        }


def display_change_summary(analysis: Dict[str, Any]) -> None:
    """Display a summary of changes to the user.
    
    Args:
        analysis: Change analysis from analyze_changes()
    """
    console = Console()
    
    if analysis["status"] == "no_manifest":
        console.print("📋 No previous manifest found - full refresh required")
        return
    
    if analysis["status"] == "error":
        console.print(f"⚠️  {analysis['message']}")
        return
    
    # Create change summary table
    table = Table(title="Change Summary")
    table.add_column("Change Type", style="cyan")
    table.add_column("Count", style="green", justify="right")
    table.add_column("Examples", style="yellow")
    
    changes = analysis["file_changes"]
    
    # Added files
    added_examples = ", ".join(changes["added"][:3])
    if len(changes["added"]) > 3:
        added_examples += f" (+{len(changes['added']) - 3} more)"
    table.add_row("Added", str(len(changes["added"])), added_examples)
    
    # Modified files
    modified_examples = ", ".join(changes["modified"][:3])
    if len(changes["modified"]) > 3:
        modified_examples += f" (+{len(changes['modified']) - 3} more)"
    table.add_row("Modified", str(len(changes["modified"])), modified_examples)
    
    # Removed files
    removed_examples = ", ".join(changes["removed"][:3])
    if len(changes["removed"]) > 3:
        removed_examples += f" (+{len(changes['removed']) - 3} more)"
    table.add_row("Removed", str(len(changes["removed"])), removed_examples)
    
    console.print(table)
    
    # Filter compatibility
    if not analysis.get("filter_compatible", True):
        console.print("⚠️  [yellow]Filter patterns have changed since last run[/yellow]")
    
    # Refresh strategy recommendation
    if analysis["requires_full_refresh"]:
        console.print("🔄 [bold]Recommendation:[/bold] Full refresh required")
        if len(changes["removed"]) > 0:
            console.print("   (File deletions require full rebuild)")
    else:
        console.print("⚡ [bold]Recommendation:[/bold] Incremental refresh possible")


def incremental_refresh(repo_path: Path, config_path: Path, 
                       changed_files: List[Path], 
                       offline: bool = False) -> Tuple[int, int]:
    """Perform incremental refresh by processing only changed files.
    
    Args:
        repo_path: Repository root path
        config_path: Configuration directory path
        changed_files: List of files that have changed
        offline: Whether to run in offline mode
        
    Returns:
        Tuple of (chunks_processed, nodes_updated)
    """
    if not changed_files:
        return 0, 0
    
    console = Console()
    console.print(f"🔄 Processing {len(changed_files)} changed files...")
    
    # Load existing data
    kg_dir = config_path / "knowledge_graph"
    chunks_file = kg_dir / "chunks.json"
    nodes_file = kg_dir / "nodes.json"
    
    existing_chunks = []
    existing_nodes = []
    
    if chunks_file.exists():
        with open(chunks_file, 'r') as f:
            existing_chunks = json.load(f)
    
    if nodes_file.exists():
        with open(nodes_file, 'r') as f:
            existing_nodes = json.load(f)
    
    # Create chunker
    config = ConfigModel()
    chunker = PythonCodeChunker(config)
    
    # Process changed files
    new_chunks = []
    processed_files = set()
    
    with Progress() as progress:
        task = progress.add_task("Processing files", total=len(changed_files))
        
        for file_path in changed_files:
            try:
                rel_path = file_path.relative_to(repo_path)
                chunks = chunker.chunk_file(file_path)
                
                # Remove old chunks for this file
                existing_chunks = [c for c in existing_chunks 
                                 if c.get("file_path") != str(rel_path)]
                
                # Add new chunks
                for chunk in chunks:
                    chunk_dict = chunk.to_dict()
                    new_chunks.append(chunk_dict)
                    existing_chunks.append(chunk_dict)
                
                processed_files.add(str(rel_path))
                progress.update(task, advance=1, description=f"Processing {rel_path}")
                
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")
                progress.update(task, advance=1)
    
    # Update chunks file
    with open(chunks_file, 'w') as f:
        json.dump(existing_chunks, f, indent=2)
    
    # Update nodes (simplified - in practice would need more sophisticated merging)
    # For now, we'll regenerate nodes from all chunks
    from testindex.preprocessing.integration.chunk_graph_adapter import ChunkGraphAdapter
    
    adapter = ChunkGraphAdapter(neo4j_client=None)
    all_nodes = []
    
    for chunk_dict in existing_chunks:
        try:
            # Convert dict back to chunk object for processing
            # This is simplified - real implementation would need proper deserialization
            node_dict = {
                "id": chunk_dict.get("id"),
                "type": chunk_dict.get("type", "Implementation"),
                "name": chunk_dict.get("name"),
                "file_path": chunk_dict.get("file_path"),
                "start_line": chunk_dict.get("start_line"),
                "end_line": chunk_dict.get("end_line"),
                "content": chunk_dict.get("content")
            }
            all_nodes.append(node_dict)
        except Exception as e:
            logger.warning(f"Error converting chunk to node: {e}")
    
    # Save updated nodes
    with open(nodes_file, 'w') as f:
        json.dump(all_nodes, f, indent=2)
    
    console.print(f"✅ Updated {len(new_chunks)} chunks and {len(all_nodes)} nodes")
    return len(new_chunks), len(all_nodes)


@click.command('refresh', help='Intelligently refresh the knowledge graph')
@click.option('--strategy', 
              type=click.Choice([RefreshStrategy.INCREMENTAL, RefreshStrategy.SMART, RefreshStrategy.FULL]),
              default=RefreshStrategy.SMART,
              help='Refresh strategy to use')
@click.option('--force-full', is_flag=True, 
              help='Force full refresh even if incremental is possible')
@click.option('--dry-run', is_flag=True,
              help='Show what would be refreshed without actually doing it')
@click.option('--config-dir', type=str, default=DEFAULT_CONFIG_DIR, 
              help='Configuration directory')
@click.option('--offline', is_flag=True, 
              help='Run in offline mode without Neo4j')
@add_filter_options
@common_options
@needs_env('refresh')
def refresh_command(strategy, force_full, dry_run, config_dir, offline,
                   include, exclude, include_regex, exclude_regex, preset, show_patterns,
                   verbose, **kwargs):
    """Intelligently refresh the knowledge graph with minimal processing.
    
    This command analyzes what has changed since the last run and updates
    only the necessary parts of the knowledge graph.
    
    Refresh strategies:
    - incremental: Only process files that have changed
    - smart: Incremental + analyze dependencies of changed files  
    - full: Complete rebuild (equivalent to init --force)
    
    The command automatically detects:
    - New, modified, and deleted files
    - Changes to filter patterns
    - Whether incremental refresh is safe
    
    Examples:
        # Smart refresh (recommended)
        aston refresh
        
        # Force full refresh
        aston refresh --force-full
        
        # Dry run to see what would be processed
        aston refresh --dry-run
        
        # Incremental refresh only
        aston refresh --strategy incremental
        
        # Change filter patterns and refresh
        aston refresh --preset no-tests
    """
    try:
        start_time = time.time()
        console = Console()
        
        # Get repository root
        repo_root = PathResolver.repo_root()
        config_path = repo_root / config_dir
        
        # Check if knowledge graph exists
        kg_dir = config_path / "knowledge_graph"
        if not kg_dir.exists():
            console.print("❌ No knowledge graph found. Run 'aston init' first.")
            sys.exit(1)
        
        # Create file filter
        file_filter = create_file_filter(
            repo_root=repo_root,
            include=include,
            exclude=exclude,
            include_regex=include_regex,
            exclude_regex=exclude_regex,
            preset=preset
        )
        
        # Handle display options (only show patterns, not dry-run yet)
        if handle_filter_display(file_filter, show_patterns, False, verbose):
            return
        
        # Create filter contract
        filter_contract = FilterContract(file_filter)
        manifest_path = kg_dir / "filter_manifest.json"
        
        # Analyze changes
        console.print("🔍 Analyzing changes since last run...")
        analysis = analyze_changes(filter_contract, manifest_path)
        
        # Display change summary
        display_change_summary(analysis)
        
        # Determine refresh strategy
        if force_full or strategy == RefreshStrategy.FULL or analysis["requires_full_refresh"]:
            console.print("\n🔄 Performing full refresh...")
            if dry_run:
                console.print("   [dry-run] Would rebuild entire knowledge graph")
                return
            
            # Full refresh - delegate to init command
            from testindex.cli.commands.init import init_command
            ctx = click.get_current_context()
            ctx.invoke(init_command, 
                      path=str(repo_root),
                      force=True,
                      config_dir=config_dir,
                      offline=offline,
                      include=include,
                      exclude=exclude,
                      include_regex=include_regex,
                      exclude_regex=exclude_regex,
                      preset=preset,
                      verbose=verbose)
            return
        
        # Incremental refresh
        if analysis["total_changes"] == 0:
            console.print("✅ No changes detected - knowledge graph is up to date")
            return
        
        if dry_run:
            console.print(f"\n[dry-run] Would incrementally process {analysis['total_changes']} changed files:")
            file_changes = analysis["file_changes"]
            for file_path in file_changes["added"] + file_changes["modified"]:
                console.print(f"  📝 {file_path}")
            return
        
        # Get changed files that need processing
        file_changes = analysis["file_changes"]
        changed_file_paths = []
        
        # Convert relative paths back to absolute paths
        for rel_path in file_changes["added"] + file_changes["modified"]:
            abs_path = repo_root / rel_path
            if abs_path.exists() and abs_path.suffix == '.py':
                changed_file_paths.append(abs_path)
        
        if not changed_file_paths:
            console.print("✅ No Python files to process")
            return
        
        # Perform incremental refresh
        chunks_processed, nodes_updated = incremental_refresh(
            repo_root, config_path, changed_file_paths, offline
        )
        
        # Update manifest
        new_manifest = filter_contract.generate_manifest()
        filter_contract.save_manifest(kg_dir)
        
        # Update config if needed
        config_file = config_path / DEFAULT_CONFIG_FILE
        if config_file.exists():
            # Config already exists, no need to update
            pass
        else:
            # Write new config
            neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            vector_store_path = str(config_path / "vectors.sqlite")
            write_config(config_file, neo4j_uri, vector_store_path)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Success message
        console.print(f"✨ Refresh completed in {duration:.1f}s")
        console.print(f"   Processed {chunks_processed} chunks, updated {nodes_updated} nodes")
        
        # Suggest next steps
        if strategy == RefreshStrategy.INCREMENTAL:
            console.print("\n💡 Tip: Run 'aston graph build' to update relationships")
        
    except Exception as e:
        logger.error(f"Error in refresh command: {e}")
        raise CLIError(f"Refresh failed: {str(e)}") 