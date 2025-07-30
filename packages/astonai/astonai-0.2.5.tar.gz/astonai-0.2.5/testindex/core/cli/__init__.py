"""
CLI framework for the Test Intelligence Engine.

This package provides a command-line interface framework for the application,
without any business logic.
"""

__version__ = "0.1.12"

# Re-export key classes and functions for easier imports
from testindex.core.cli.runner import create_cli, run_cli
from testindex.core.cli.formatting import format_output
from testindex.core.cli.progress import Progress, create_progress
