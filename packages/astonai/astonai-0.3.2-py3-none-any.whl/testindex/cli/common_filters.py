"""
Common filter options and utilities for CLI commands.

Provides a decorator to add standard filter options to any command,
ensuring consistent filtering behavior across the codebase.
"""
import click
from typing import Optional, List, Callable
from pathlib import Path

from testindex.core.filtering import FileFilter, PatternType, FilterPresets
from testindex.core.path_resolution import PathResolver
from testindex.core.logging import get_logger

logger = get_logger(__name__)


def add_filter_options(func: Callable) -> Callable:
    """Decorator to add standard filter options to any command.
    
    Adds the following options:
    - --include/-i: Include glob patterns
    - --exclude/-e: Exclude glob patterns  
    - --include-regex: Include regex patterns
    - --exclude-regex: Exclude regex patterns
    - --preset: Apply preset configurations
    - --dry-run: Preview file selection
    - --show-patterns: Show active patterns
    
    Args:
        func: The click command function to decorate
        
    Returns:
        Decorated function with filter options
    """
    options = [
        click.option(
            '--include', '-i',
            multiple=True, 
            help='Include only files matching these glob patterns. Can be used multiple times.'
        ),
        click.option(
            '--exclude', '-e',
            multiple=True, 
            help='Exclude files matching these glob patterns (in addition to defaults). Can be used multiple times.'
        ),
        click.option(
            '--include-regex',
            multiple=True,
            help='Include only files matching these regex patterns. Can be used multiple times.'
        ),
        click.option(
            '--exclude-regex',
            multiple=True,
            help='Exclude files matching these regex patterns. Can be used multiple times.'
        ),
        click.option(
            '--preset',
            type=click.Choice(['python-only', 'no-tests', 'source-only', 'minimal']),
            help='Apply a preset filter configuration'
        ),
        click.option(
            '--dry-run',
            is_flag=True,
            help='Show which files would be processed without actually processing them'
        ),
        click.option(
            '--show-patterns',
            is_flag=True,
            help='Show all active filter patterns and exit'
        ),
    ]
    
    # Apply options in reverse order so they appear in correct order in help
    for option in reversed(options):
        func = option(func)
    
    return func


def create_file_filter(repo_root: Optional[Path] = None,
                      include: Optional[List[str]] = None,
                      exclude: Optional[List[str]] = None,
                      include_regex: Optional[List[str]] = None,
                      exclude_regex: Optional[List[str]] = None,
                      preset: Optional[str] = None) -> FileFilter:
    """Create a configured FileFilter instance.
    
    Args:
        repo_root: Repository root path (defaults to current repo)
        include: Glob patterns to include
        exclude: Glob patterns to exclude
        include_regex: Regex patterns to include
        exclude_regex: Regex patterns to exclude
        preset: Preset configuration name
        
    Returns:
        Configured FileFilter instance
    """
    if repo_root is None:
        repo_root = PathResolver.repo_root()
    
    file_filter = FileFilter(repo_root)
    
    # Apply preset if specified
    if preset:
        try:
            file_filter.apply_preset(preset)
        except ValueError as e:
            logger.error(f"Invalid preset: {e}")
            raise
    
    # Add manual patterns
    if include:
        file_filter.add_include_patterns(list(include), source="command-line")
    if exclude:
        file_filter.add_exclude_patterns(list(exclude), source="command-line")
    if include_regex:
        file_filter.add_include_patterns(list(include_regex), PatternType.REGEX, source="command-line")
    if exclude_regex:
        file_filter.add_exclude_patterns(list(exclude_regex), PatternType.REGEX, source="command-line")
    
    return file_filter


def handle_filter_display(file_filter: FileFilter, 
                         show_patterns: bool,
                         dry_run: bool,
                         verbose: bool = False) -> bool:
    """Handle filter pattern display and dry run.
    
    Args:
        file_filter: Configured FileFilter instance
        show_patterns: Whether to show active patterns
        dry_run: Whether to perform dry run
        verbose: Whether to show verbose output
        
    Returns:
        True if command should exit after display, False otherwise
    """
    # Show patterns if requested
    if show_patterns:
        pattern_summary = file_filter.get_pattern_summary()
        
        click.echo("📋 Active Filter Patterns:")
        click.echo()
        
        if pattern_summary["include_patterns"]:
            click.echo("Include patterns:")
            for p in pattern_summary["include_patterns"]:
                click.echo(f"  {p['type']:5} | {p['pattern']:30} | {p['source']}")
        else:
            click.echo("Include patterns: (none - all files included by default)")
        
        click.echo()
        click.echo("Exclude patterns:")
        for p in pattern_summary["exclude_patterns"]:
            click.echo(f"  {p['type']:5} | {p['pattern']:30} | {p['source']}")
        
        return True
    
    # Perform dry run if requested
    if dry_run:
        click.echo("🔍 Dry run - showing files that would be processed:")
        click.echo()
        
        dry_run_result = file_filter.dry_run(limit=50)
        
        # Show summary
        summary = dry_run_result["summary"]
        click.echo(f"📊 Summary:")
        click.echo(f"  Total files found: {summary['total_found']}")
        click.echo(f"  Would include: {summary['total_included']}")
        click.echo(f"  Would exclude: {summary['total_excluded']}")
        click.echo()
        
        # Show included files
        if dry_run_result["included"]:
            click.echo(f"✅ Files to include (showing {summary['showing_included']}):")
            for file_info in dry_run_result["included"]:
                click.echo(f"  ✓ {file_info['path']}")
            if summary['total_included'] > summary['showing_included']:
                click.echo(f"  ... and {summary['total_included'] - summary['showing_included']} more")
            click.echo()
        
        # Show excluded files
        if dry_run_result["excluded"]:
            click.echo(f"❌ Files to exclude (showing {summary['showing_excluded']}):")
            for file_info in dry_run_result["excluded"][:10]:  # Limit excluded display
                click.echo(f"  ✗ {file_info['path']} ({file_info['reason']})")
            if summary['total_excluded'] > 10:
                click.echo(f"  ... and {summary['total_excluded'] - 10} more")
        
        return True
    
    # Log filter info if verbose
    if verbose:
        patterns = file_filter.get_pattern_summary()
        if patterns["include_patterns"]:
            include_list = [p["pattern"] for p in patterns["include_patterns"]]
            click.echo(f"📋 Include patterns: {', '.join(include_list)}")
        if len(patterns["exclude_patterns"]) > len(FileFilter.DEFAULT_EXCLUDES):
            # Only show non-default excludes
            exclude_list = [p["pattern"] for p in patterns["exclude_patterns"] 
                          if p["source"] != "default"]
            if exclude_list:
                click.echo(f"🚫 Additional exclude patterns: {', '.join(exclude_list)}")
    
    return False


def get_filtered_python_files(file_filter: FileFilter) -> List[Path]:
    """Get Python files using the file filter.
    
    Args:
        file_filter: Configured FileFilter instance
        
    Returns:
        List of Python file paths to process
        
    Raises:
        click.ClickException: If no files found
    """
    python_files = file_filter.discover_files(['.py'])
    
    if not python_files:
        raise click.ClickException(
            "No Python files found to process. Check your filter patterns or use --dry-run to debug."
        )
    
    return python_files 