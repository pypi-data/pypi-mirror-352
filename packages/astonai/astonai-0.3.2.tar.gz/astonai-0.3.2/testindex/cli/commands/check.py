"""
TestIndex check command.

This module implements the `aston check` command that verifies the environment
has all the required dependencies.
"""
import click

from testindex.core.cli.runner import common_options
from testindex.cli.utils.env_check import check_env

@click.command('check', help='Check environment for required dependencies')
@click.option('--test', is_flag=True, help='Check dependencies for test command')
@click.option('--coverage', is_flag=True, help='Check dependencies for coverage command')
@click.option('--init', is_flag=True, help='Check dependencies for init command')
@common_options
def check_command(test, coverage, init, **kwargs):
    """Check environment for required dependencies.
    
    This command:
    1. Checks if all required dependencies are installed
    2. Suggests how to install missing dependencies
    
    Exit codes:
    - 0: All checks passed or only optional dependencies missing
    - 1: Missing mandatory dependencies
    """
    # If no specific command selected, check all
    if not (test or coverage or init):
        test = coverage = init = True
    
    all_passed = True
    
    # Check each requested command
    if test:
        print("Checking dependencies for 'aston test'...")
        if not check_env('test'):
            all_passed = False
            
    if coverage:
        print("Checking dependencies for 'aston coverage'...")
        if not check_env('coverage'):
            all_passed = False
            
    if init:
        print("Checking dependencies for 'aston init'...")
        if not check_env('init'):
            all_passed = False
    
    if all_passed:
        return 0
    return 1 