"""
CLI runner for the Test Intelligence Engine.

This module provides utilities for creating and running CLI commands.
"""
import os
import sys
from typing import Any, Callable, Dict, List, Optional

import click

from testindex.core.exceptions import CLIError
from testindex import __version__


def create_cli(name: str, help_text: str) -> click.Group:
    """
    Create a new CLI command group.
    
    Args:
        name: Name of the CLI command group
        help_text: Help text for the CLI command group
        
    Returns:
        A new CLI command group
    """
    @click.group(name=name, help=help_text)
    @click.version_option(version=__version__)
    def cli() -> None:
        """CLI entry point."""
        pass
    
    return cli


def run_cli(cli: click.Group, args: Optional[List[str]] = None) -> None:
    """
    Run a CLI command group.
    
    Args:
        cli: CLI command group to run
        args: Command-line arguments (default: sys.argv[1:])
        
    Raises:
        CLIError: If the CLI command fails
    """
    try:
        cli(args=args)
    except click.ClickException as e:
        # Click already handles these exceptions well
        raise
    except Exception as e:
        # Wrap other exceptions in CLIError for consistent error handling
        raise CLIError(str(e))


def common_options(f: Callable) -> Callable:
    """
    Add common options to a CLI command.
    
    Args:
        f: CLI command function
        
    Returns:
        Decorated CLI command function
    """
    options = [
        click.option(
            "--config",
            "-c",
            type=click.Path(exists=True, file_okay=True, dir_okay=False),
            help="Path to configuration file",
        ),
        click.option(
            "--verbose",
            "-v",
            is_flag=True,
            help="Enable verbose output",
        ),
        click.option(
            "--quiet",
            "-q",
            is_flag=True,
            help="Suppress output",
        ),
        click.option(
            "--output",
            "-o",
            type=click.Choice(["text", "json", "table"]),
            default="text",
            help="Output format",
        ),
    ]
    
    for option in reversed(options):
        f = option(f)
    
    return f
