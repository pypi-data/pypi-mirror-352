# Aston AI

Aston is a code intelligence system for parsing, analyzing, and finding test coverage gaps in your code.

> **Latest**: v0.2.5 achieves 100% test pass rate (321 passed, 4 warnings) with enhanced test suggestions and critical refactoring stability improvements.

# Explain
aston init → creates chunks + nodes
aston graph build → uses those to create edges

## Installation

```bash
# Install from PyPI
pip install astonai

# For LLM-powered features (optional)
pip install "astonai[llm]"
```

## Quick Start

```bash
# Initialize your repository
aston init --offline

# Generate knowledge graph relationships
aston graph build

# View knowledge graph statistics
aston graph stats

# Smart incremental updates (recommended for ongoing development)
aston refresh

# Find critical paths and generate test suggestions
aston coverage --critical-path
aston test-suggest core/auth.py --k 3
aston test-suggest user/models.py --prompt --yaml context.yaml
```

## Core Commands

### Repository Initialization

```bash
# Initialize repository and create knowledge graph
aston init [--offline] [--preset PRESET] [--include PATTERN] [--exclude PATTERN]

# Incremental rechunk - fast updates for changed files only
aston init --rechunk [--offline]

# Force full rebuild
aston init --force [--offline]
```

**Advanced Filtering Options:**
- `--preset`: Apply preset configurations (`python-only`, `no-tests`, `source-only`, `minimal`)
- `--include`, `-i`: Include only files matching these glob patterns (can be used multiple times)
- `--exclude`, `-e`: Exclude files matching these glob patterns in addition to defaults (can be used multiple times)
- `--include-regex`: Include only files matching these regex patterns (can be used multiple times)
- `--exclude-regex`: Exclude files matching these regex patterns (can be used multiple times)
- `--dry-run`: Show which files would be processed without actually processing them
- `--show-patterns`: Display all active filter patterns and exit
- `--create-astonignore`: Create a template .astonignore file for persistent filtering

**Incremental Updates:**
- `--rechunk`: Process only files that have changed since last run (fast incremental updates)
- `--force`: Force complete rebuild even if knowledge graph exists

**Default Excludes**: Common directories are automatically excluded:
- `venv*/**`, `.venv*/**`, `env/**`, `.env/**`
- `node_modules/**`, `.git/**`, `.svn/**`, `.hg/**`
- `__pycache__/**`, `*.pyc`, `.pytest_cache/**`
- `build/**`, `dist/**`, `*.egg-info/**`
- `.idea/**`, `.vscode/**`, and more

**Examples:**
```bash
# Use preset configurations
aston init --preset python-only --offline
aston init --preset no-tests --offline

# Incremental rechunk for fast updates
aston init --rechunk --offline

# Custom filtering with patterns
aston init --include "src/**/*.py" --include "lib/**/*.py" --offline
aston init --exclude "legacy/**" --exclude "deprecated/**" --offline

# Use regex patterns for advanced filtering
aston init --include-regex ".*/(core|utils)/.*\.py$" --offline

# Preview what would be processed
aston init --preset minimal --dry-run

# Create .astonignore template for persistent rules
aston init --create-astonignore
```

**Environment Variables:**
- `ASTON_INCLUDE_PATTERNS`: Comma-separated include patterns
- `ASTON_EXCLUDE_PATTERNS`: Comma-separated exclude patterns

### Intelligent Refresh

```bash
# Smart incremental updates with change analysis
aston refresh [--strategy auto|incremental|full] [--force-full] [--dry-run]
```

The `refresh` command provides intelligent updates:
- **Auto Strategy**: Automatically chooses between incremental and full refresh based on changes
- **Change Detection**: Uses file hashes to detect actual modifications
- **Dry Run**: Preview what would be updated without making changes
- **Force Full**: Override auto-detection and force complete rebuild

**Examples:**
```bash
# Smart refresh (recommended)
aston refresh

# Preview changes without applying
aston refresh --dry-run

# Force full refresh
aston refresh --force-full

# Use specific strategy
aston refresh --strategy incremental
```

### Test Coverage

```bash
# Run tests with coverage
aston test

# Find testing gaps
aston coverage [--threshold 80] [--json results.json] [--exit-on-gap]

# Identify critical implementation nodes
aston coverage --critical-path [--n 50] [--weight loc]
```

Options:
- `--threshold`: Minimum coverage percentage (default: 0)
- `--json`: Output results in JSON format
- `--exit-on-gap`: Return code 1 if gaps found (useful for CI)
- `--coverage-file`: Specify custom coverage file location
- `--critical-path`: Identify critical code paths that need testing
- `--n`: Number of critical nodes to return (default: 50)
- `--weight`: Weight function for critical path (loc, calls, churn)

### Knowledge Graph

```bash
# Build edge relationships between nodes with advanced filtering
aston graph build [--preset PRESET] [--include PATTERN] [--exclude PATTERN]

# View statistics about the knowledge graph
aston graph stats

# Export graph to DOT format
aston graph export [--output graph.dot] [--filter CALLS,IMPORTS] [--open]

# Open interactive graph viewer in browser
aston graph view [--filter CALLS,IMPORTS]
```


**Advanced Filtering for Graph Build:**
- `--preset`: Apply preset configurations (`python-only`, `no-tests`, `source-only`, `minimal`)
- `--include`, `-i`: Include only files matching these glob patterns (can be used multiple times)
- `--exclude`, `-e`: Exclude files matching these glob patterns in addition to defaults (can be used multiple times)
- `--include-regex`: Include only files matching these regex patterns (can be used multiple times)
- `--exclude-regex`: Exclude files matching these regex patterns (can be used multiple times)
- `--dry-run`: Show which files would be processed without actually processing them
- `--show-patterns`: Display all active filter patterns and exit

**Examples:**
```bash
# Build with preset filtering
aston graph build --preset no-tests

# Include only specific directories
aston graph build --include "src/**/*.py" --include "lib/**/*.py"

# Use regex patterns for advanced filtering
aston graph build --include-regex ".*/(core|utils)/.*\.py$"

# Preview what would be processed
aston graph build --preset python-only --dry-run
```

The graph command provides:
- `build`: Analyzes your codebase to extract CALLS and IMPORTS edges with advanced filtering
- `stats`: Displays node and edge statistics
- `export`: Exports to Graphviz DOT format for external visualization
- `view`: Opens interactive D3-force based viewer in browser

### Test Suggestions

```bash
# Generate test suggestions for a file or function
aston test-suggest <file_or_node> [--k 5] [--llm] [--model gpt-4o]

# Generate rich context for developers or AI agents
aston test-suggest <file_or_node> --prompt [--json context.json]

# Output in multiple formats
aston test-suggest core/auth.py --yaml tests.yaml --json tests.json

# Use LLM with budget control
aston test-suggest api/endpoints.py --llm --budget 0.01 --model gpt-4o

# Debug path resolution issues
aston test-suggest <file_or_node> --debug
```

**Intelligent Test Generation:**
- **Heuristic Mode**: Lightning-fast pytest skeleton generation (≤1.2s)
- **Boundary Value Testing**: Automatic edge cases for int/float, string, list, dict, bool types
- **Happy Path Coverage**: Valid input test cases for comprehensive coverage
- **Error Condition Testing**: Invalid input handling and exception testing

**LLM Integration (Optional):**
- **Fallback Strategy**: Uses LLM when heuristics can't generate suggestions
- **Cost Control**: Built-in budget tracking and enforcement
- **Model Selection**: Support for GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **Performance Guarantee**: ≤6s latency for LLM-generated suggestions

**Rich Context Mode:**
- **Developer Guidance**: Comprehensive test implementation guides
- **Parameter Analysis**: Detailed function signature and dependency analysis
- **Best Practices**: pytest patterns and testing recommendations
- **AI-Agent Ready**: Structured context for automated test generation

Options:
- `--k`: Number of suggestions to generate (default: 5)
- `--llm`: Use LLM fallback if heuristics fail (requires OPENAI_API_KEY)
- `--model`: LLM model to use (default: gpt-4o)
- `--budget`: Maximum cost per suggestion in dollars (default: $0.03)
- `--prompt`, `-p`: Generate rich context for manual test development
- `--debug`: Enable detailed debugging output for path resolution
- `--json`/`--yaml`: Output results in structured format for automation
- `--no-env-check`: Skip environment dependency check

**Examples:**
```bash
# Quick heuristic suggestions
aston test-suggest src/calculator.py --k 3

# Rich context for manual test writing
aston test-suggest user/models.py --prompt --yaml context.yaml

# LLM-powered suggestions with cost control
aston test-suggest complex/algorithm.py --llm --budget 0.005

# Target specific function
aston test-suggest "auth/login.py::authenticate_user" --debug
```

### Environment Check

```bash
# Check if all required dependencies are installed
aston check
```

Options:
- `--no-env-check`: Skip environment dependency check (also works with any command)

## Repository-Centric Design

Aston follows a repository-centric approach:
- All operations are relative to the repository root (current directory)
- Data is stored in `.testindex` directory at the repository root
- Path resolution is normalized for consistent matching
- Works with both offline and Neo4j storage

## Environment Variables

```
DEBUG=1                      # Enable debug logging
NEO4J_URI=bolt://localhost:7687  # Optional Neo4j connection
NEO4J_USER=neo4j            # Optional Neo4j username
NEO4J_PASS=password         # Optional Neo4j password
ASTON_NO_ENV_CHECK=1        # Skip environment dependency check
OPENAI_API_KEY=sk-...       # Required for --llm features
```

