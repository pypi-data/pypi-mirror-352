"""
TestIndex test command.

This module implements the `testindex test` command that runs tests with coverage.
"""
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger
from testindex.core.exceptions import CLIError
from testindex.cli.utils.env_check import needs_env

# Set up logger
logger = get_logger(__name__)


@click.command('test', help='Run tests with coverage')
@click.option('--pytest-args', type=str, help='Additional arguments to pass to pytest')
@click.option('--no-cov', is_flag=True, help='Run tests without coverage')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@common_options
@needs_env('test')
def test_command(pytest_args: Optional[str], no_cov: bool = False, no_env_check: bool = False, **kwargs):
    """Run tests with coverage.
    
    This command:
    1. Runs pytest with coverage
    2. Generates coverage.xml file in the repository root
    
    Exit codes:
    - 0: Tests passed
    - 1: Tests failed
    - 2: Other error occurred
    """
    try:
        console = Console()
        
        # Use the repository root (current directory) for coverage output
        output_dir = Path.cwd()
        
        # Run pytest with or without coverage
        if no_cov:
            cmd = ["pytest"]
        else:
            cmd = [
                "pytest",
                "--cov", ".",
                "--cov-report", f"xml:{output_dir / 'coverage.xml'}",
            ]
        
        # Add user-provided pytest args if specified
        if pytest_args:
            cmd.extend(pytest_args.split())
        
        console.print(f"Running: [green]{' '.join(cmd)}[/]")
        
        # Run the pytest command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        console.print(result.stdout)
        if result.stderr:
            console.print("[yellow]STDERR:[/]")
            console.print(result.stderr)
            
            # Check for common errors in stderr
            if "ModuleNotFoundError: No module named 'pytest_cov" in result.stderr:
                console.print("[bold red]Error:[/] pytest-cov plugin missing")
                console.print("[bold green]Solution:[/] Run 'pip install pytest-cov' or add --no-cov flag.")
        
        # Return appropriate exit code
        return result.returncode
        
    except Exception as e:
        console = Console()
        console.print(f"[red]Error running tests:[/] {e}")
        return 2

def run_pytest_command():
    """Run pytest with coverage reporting."""
    try:
        # Try direct pytest command first
        subprocess.run(["pytest", "-q", "--cov", ".", "--cov-report", f"xml:{coverage_file}"], check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        try:
            # Try python -m pytest as fallback
            subprocess.run(["python", "-m", "pytest", "-q", "--cov", ".", "--cov-report", f"xml:{coverage_file}"], check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            console.print("[bold red]Error:[/] Could not run pytest. Please install pytest and pytest-cov:")
            console.print("    pip install pytest pytest-cov")
            sys.exit(1) 