"""
TestIndex CLI commands.

This module provides the command-line interface for TestIndex.
"""

from testindex.cli.commands.init import init_command
from testindex.cli.commands.coverage import coverage_command
from testindex.cli.commands.test import test_command
from testindex.cli.commands.graph import graph_command
from testindex.cli.commands.check import check_command
from testindex.cli.commands.ingest_coverage import ingest_coverage_command
from testindex.cli.commands.test_suggest import test_suggest_command
from testindex.cli.commands.regression_guard import regression_guard_command

# List of commands to register with CLI
commands = [
    init_command,
    test_command,
    coverage_command,
    graph_command,
    check_command,
    ingest_coverage_command,
    test_suggest_command,
    regression_guard_command,
] 