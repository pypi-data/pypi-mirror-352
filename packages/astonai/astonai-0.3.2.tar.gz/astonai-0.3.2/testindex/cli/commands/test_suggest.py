"""
TestIndex test-suggest command.

This module implements the `testindex test-suggest` command that generates test suggestions
for implementation nodes.
"""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from testindex.core.cli.runner import common_options
from testindex.core.logging import get_logger, LogLevel
from testindex.core.path_resolution import PathResolver
from testindex.cli.utils.env_check import needs_env
from testindex.analysis.test_suggest import SuggestionError, SuggestionEngine

# Set up logger - will be configured further down if debug is true
logger = get_logger(__name__)

# Create rich console instance
console = Console()

# Fallback import for older versions of TestIndex, not used by core logic but might be imported by plugins.
# This can be removed after a deprecation period.
try:
    from testindex.analysis.test_suggest import SuggestionEngine
except ImportError:
    logger.debug("Legacy TestSuggestionEngine not found, assuming new version.")
    SuggestionEngine = None # Or a placeholder if needed for type hinting in stubs


def _write_yaml_output(suggestions: List[Dict[str, Any]], yaml_path: str) -> None:
    """Write suggestions to YAML format."""
    try:
        import yaml
        
        yaml_data = {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "suggestions": suggestions
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, indent=2)
            
        logger.info(f"YAML output written to: {yaml_path}")
    except ImportError:
        logger.error("PyYAML not available. Install with: pip install PyYAML")
        console.print("[red]Error:[/red] PyYAML required for YAML output. Install with: pip install PyYAML")
    except Exception as e:
        logger.error(f"Failed to write YAML output: {e}")
        console.print(f"[red]Error:[/red] Failed to write YAML output: {e}")


def _generate_rich_context(engine, target: str, suggestions: List[Dict[str, Any]]) -> str:
    """Generate rich context for developers/AI agents."""
    from testindex.analysis.test_suggest import TestSuggestionEngine
    
    context_blocks = []
    
    # Get target nodes
    target_nodes = engine._identify_target_nodes(target, os.path.exists(target))
    
    for i, target_node in enumerate(target_nodes[:3]):  # Limit to top 3 nodes
        target_file = target_node.get("file_path", "")
        target_name = target_node.get("name", "")
        
        # Get source code
        source_code = ""
        function_source = ""
        try:
            source_path = engine._resolve_source_file(target_file)
            if source_path:
                with open(source_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                    
                # Extract just the function
                import ast
                try:
                    tree = ast.parse(source_code)
                    node_ast = engine._find_node_ast(tree, target_name)
                    if node_ast:
                        function_source = ast.unparse(node_ast)
                except:
                    function_source = source_code  # Fallback to full file
        except Exception as e:
            logger.warning(f"Failed to read source file: {e}")
        
        # Extract metadata
        properties = target_node.get("properties", {})
        metadata = {
            "file_path": target_file,
            "function_name": target_name,
            "coverage": properties.get("coverage", 0),
            "complexity": properties.get("complexity", "unknown"),
            "type": target_node.get("type", "Unknown"),
            "line_start": properties.get("line_start", "?"),
            "line_end": properties.get("line_end", "?"),
        }
        
        # Extract parameters
        params, type_hints = engine._extract_params_from_node(target_node, source_code)
        
        # Extract dependencies
        dependencies = engine._extract_dependencies(target_node)
        
        # Generate context block
        context_block = f"""
## Function: {metadata['function_name']} (Node {i+1})

**File**: `{metadata['file_path']}`
**Type**: {metadata['type']}
**Lines**: {metadata['line_start']}-{metadata['line_end']}
**Coverage**: {metadata['coverage']}%
**Complexity**: {metadata['complexity']}

### Source Code:
```python
{function_source if function_source else 'Source code not available'}
```

### Parameters:
{_format_parameters(params, type_hints)}

### Dependencies:
{_format_dependencies(dependencies)}

### Recommended Test Patterns:
- **Boundary Value Testing**: Test edge cases for parameters
- **Error Handling**: Test invalid inputs and exception conditions
- **Integration Testing**: Test interactions with dependencies
- **Performance Testing**: Test with large/complex inputs if applicable

### Suggested Test Cases:
1. **Happy Path**: Test with valid, typical inputs
2. **Boundary Conditions**: Test with empty, null, minimum, maximum values
3. **Error Conditions**: Test with invalid inputs that should raise exceptions
4. **Edge Cases**: Test specific business logic edge cases

### Test Implementation Guide:
```python
import pytest
from {metadata['file_path'].replace('.py', '').replace('/', '.')} import {metadata['function_name']}

class Test{metadata['function_name'].title()}:
    def test_{metadata['function_name']}_happy_path(self):
        # Test with valid inputs
        pass
        
    def test_{metadata['function_name']}_boundary_conditions(self):
        # Test edge cases
        pass
        
    def test_{metadata['function_name']}_error_handling(self):
        # Test error conditions
        pass
```
        """
        context_blocks.append(context_block)
    
    # Add general guidance
    general_guidance = """
## Test Writing Guidelines

### Best Practices:
1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: Test names should clearly describe what is being tested
3. **Test One Thing**: Each test should focus on one specific behavior
4. **Use Fixtures**: Create reusable test data and setup
5. **Mock Dependencies**: Isolate the unit under test

### Coverage Goals:
- Aim for 100% line coverage
- Focus on critical paths and error conditions
- Test all public interfaces
- Consider edge cases and boundary conditions

### Tools and Frameworks:
- **pytest**: Primary testing framework
- **pytest-mock**: For mocking dependencies
- **pytest-cov**: For coverage measurement
- **hypothesis**: For property-based testing (advanced cases)
    """
    
    full_context = "\n---\n".join(context_blocks) + "\n---\n" + general_guidance
    
    return full_context


def _format_parameters(params: List[str], type_hints: Dict[str, str]) -> str:
    """Format parameters for display."""
    if not params:
        return "No parameters"
    
    param_lines = []
    for param in params:
        hint = type_hints.get(param, "unknown")
        param_lines.append(f"- `{param}`: {hint}")
    
    return "\n".join(param_lines)


def _format_dependencies(dependencies: List[str]) -> str:
    """Format dependencies for display."""
    if not dependencies:
        return "No external dependencies detected"
    
    dep_lines = []
    for dep in dependencies:
        dep_lines.append(f"- {dep}")
    
    return "\n".join(dep_lines)


@click.command('test-suggest', help='Generate test suggestions for functions')
@click.argument('target', type=str, required=True)
@click.option('--k', type=int, default=5,
              help='Maximum number of suggestions to generate (default: 5)')
@click.option('--yaml', 'yaml_output', type=click.Path(),
              help='Path to write YAML output')
@click.option('--json', 'json_output', type=click.Path(),
              help='Path to write JSON output')
@click.option('--llm', is_flag=True,
              help='Use LLM fallback if heuristics fail')
@click.option('--model', type=str, default="gpt-4o",
              help='LLM model to use (default: gpt-4o)')
@click.option('--budget', type=float, default=0.03,
              help='Maximum cost per suggestion in dollars (default: 0.03)')
@click.option('--prompt', '-p', is_flag=True,
              help='Generate rich context for developers/AI agents to write tests instead of direct test suggestions')
@click.option('--debug', is_flag=True, help='Enable detailed debugging output')
@click.option('--no-env-check', is_flag=True, help='Skip environment dependency check')
@common_options
@needs_env('test-suggest')
def test_suggest_command(
    target: str,
    k: int,
    yaml_output: Optional[str],
    json_output: Optional[str],
    llm: bool,
    model: str,
    budget: float,
    prompt: bool,
    debug: bool,
    verbose: bool,
    no_env_check: bool,
    **kwargs
):
    """Generate test suggestions for implementation nodes.
    
    TARGET: Path to file or fully-qualified node name (e.g., 'src/module.py' or 'src.module.MyClass.my_method')
    """
    
    # Configure logger level based on debug flag
    if debug:
        logger.level = LogLevel.DEBUG # Assuming LogLevel is available or use string "DEBUG"
        logger.debug("Debug mode enabled for test-suggest command")
    else:
        logger.level = LogLevel.INFO # Assuming LogLevel is available or use string "INFO"

    logger.info(f"Test suggest called with target: {target}, k={k}, llm={llm}, prompt={prompt}")
    
    try:
        # Removed: Set debug mode if requested (now handled by logger.level)
        
        # Import for TestSuggestionEngine is already updated to SuggestionEngine
        
        # Get the repository root
        repo_root = PathResolver.repo_root()
        cwd = Path.cwd()
        
        # Check if target exists or resolve common target patterns
        target_exists = os.path.exists(target)
        if not target_exists and '/' not in target and '::' not in target:
            # Try various paths for the target
            possible_paths = [
                target,
                os.path.join('src', target),
                os.path.join('testindex', target),
                os.path.join('django', target),
            ]
            
            # Also try repo-root based paths
            possible_paths.extend([
                os.path.join(repo_root, target),
                os.path.join(repo_root, 'src', target),
                os.path.join(repo_root, 'testindex', target),
                os.path.join(repo_root, 'django', target),
            ])
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    target = path
                    found = True
                    if debug:
                        logger.debug(f"Resolved target to '{path}'")
                    break
                    
            if not found:
                if debug:
                    logger.debug(f"Target '{target}' not found in any of these paths: {possible_paths}")
                console.print(f"[yellow]Warning:[/yellow] Target '{target}' does not exist as a file. " +
                              "Treating as a node name.")
        elif debug and target_exists:
            logger.debug(f"Target '{target}' exists as a file")
        
        # Check if repo has django subdirectory
        django_dir = cwd / "django"
        has_django_dir = django_dir.exists() and django_dir.is_dir()
        if has_django_dir and debug:
            logger.debug(f"Found Django directory at {django_dir}")
            
            # Special case for django paths
            if target.startswith("django/") and not os.path.exists(target):
                alt_target = target.replace("django/", "")
                django_relative_path = django_dir / alt_target
                if django_relative_path.exists():
                    target = str(django_relative_path)
                    if debug:
                        logger.debug(f"Resolved Django-relative path to {target}")
        
        # Initialize the engine
        console.print(f"Generating test suggestions for [bold]{target}[/bold]...")
        if llm and not prompt:
            # Check if the OpenAI API key is set
            if not os.environ.get("OPENAI_API_KEY"):
                console.print("[red]Error:[/red] OPENAI_API_KEY environment variable not set.")
                console.print("Set it or use without --llm flag.")
                sys.exit(2)
                
            console.print(f"Using LLM fallback with model [bold]{model}[/bold] (budget: ${budget})...")
        
        if prompt:
            console.print("[bold blue]Generating test context in prompt mode[/bold blue]")
            
        # Instantiate the suggestion engine
        # Ensure that the correct class is instantiated based on availability
        # This handles the case where the old name might still be around during transition
        # but prefers the new name if available.
        current_engine_class = SuggestionEngine
        if current_engine_class is None and 'TestSuggestionEngine' in globals():
             # This case should ideally not happen if imports are correct
             logger.warning("Fallback to TestSuggestionEngine due to import issue. Please check imports.")
             current_engine_class = globals().get('TestSuggestionEngine')
        
        if current_engine_class is None:
            # Critical error if neither can be found.
            logger.error("SuggestionEngine class not found. AstonAI might be improperly installed or corrupted.")
            console.print("[red]Error:[/red] SuggestionEngine not found. Please reinstall AstonAI.")
            raise click.Abort()

        engine = current_engine_class(llm_enabled=llm, model=model, budget=budget)
        
        # Generate suggestions
        output_file = None
        if json_output:
            output_file = json_output
        
        suggestions = engine.generate_suggestions(
            target=target,
            k=k,
            output_file=output_file
        )
        
        # Write YAML output if requested
        if yaml_output:
            _write_yaml_output(suggestions, yaml_output)
        
        if not suggestions:
            console.print("[yellow]No test suggestions generated.[/yellow] " +
                          "This could be due to:")
            console.print("• No matching nodes found in the knowledge graph")
            console.print("• No function parameters to generate tests for")
            console.print("• Source file not found or parse error")
            
            if not llm and not prompt:
                console.print("\nTry using [bold]--llm[/bold] flag for more advanced suggestions.")
            
            sys.exit(1)
        
        # In prompt mode, generate rich context instead of test suggestions
        if prompt:
            rich_context = _generate_rich_context(engine, target, suggestions)
            console.print(rich_context)
            return 0
        
        # Display suggestions (non-prompt mode)
        console.print(f"\n[bold green]Generated {len(suggestions)} test suggestions:[/bold green]\n")
        
        for i, suggestion in enumerate(suggestions, 1):
            test_name = suggestion.get("test_name", "")
            target_node = suggestion.get("target_node", "")
            skeleton = suggestion.get("skeleton", "")
            
            # Create a syntax-highlighted panel for the skeleton
            syntax = Syntax(skeleton, "python", theme="monokai", line_numbers=True)
            
            # Determine source of suggestion
            source = "[bold blue]Heuristic[/bold blue]"
            if suggestion.get("llm", False):
                model_name = suggestion.get("model", "LLM")
                source = f"[bold magenta]{model_name}[/bold magenta]"
            
            panel = Panel(
                syntax,
                title=f"[{i}] {test_name}",
                subtitle=f"Target: {target_node} | Source: {source}"
            )
            
            console.print(panel)
            console.print()
        
        # Output file paths
        output_files = []
        if not json_output and not yaml_output:
            output_file = PathResolver.knowledge_graph_dir() / "test_suggestions.json"
            output_files.append(str(output_file))
        else:
            if json_output:
                output_files.append(json_output)
            if yaml_output:
                output_files.append(yaml_output)
        
        if output_files:
            files_str = ", ".join(f"[bold]{f}[/bold]" for f in output_files)
            console.print(f"Suggestions written to: {files_str}")
            
        console.print("\nTo run these tests, create a test file with the suggested functions.")
        
    except SuggestionError as e:
        logger.error(f"Failed to generate test suggestions: {str(e)}")
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        if verbose:
            logger.error(traceback.format_exc())
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(2) 