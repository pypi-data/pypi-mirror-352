# TestIndex CLI

Command-line interface for the TestIndex Knowledge v1 system.

## Installation

```bash
# Install from the repository
pip install -e .
```

## Commands

### Initialize Repository

The `init` command initializes a knowledge graph for a repository:

```bash
# Use current directory
testindex init

# Use a specific local repository
testindex init --path /path/to/repo

# Clone a remote repository
testindex init --url https://github.com/user/repo.git

# Force rebuild of an existing graph
testindex init --force

# Run in offline mode (without Neo4j)
testindex init --offline
```

## Behavior

### Repository Support

The `init` command supports multiple repository types:

1. **Git Repositories**
   - Detected by `.git` directory
   - URLs ending in `.git` or containing `github.com`
   - Uses Git commands for cloning and updates

2. **Mercurial Repositories**
   - Detected by `.hg` directory
   - URLs starting with `hg+` or containing `hg`
   - Uses `hg` command for cloning and updates

3. **Subversion Repositories**
   - Detected by `.svn` directory
   - URLs starting with `svn+` or containing `svn`
   - Uses `svn` command for cloning and updates

4. **Plain Directories**
   - Used when no VCS is detected
   - Simple file copying for "cloning"
   - No update mechanism

### Local Repository

When running `testindex init` in a local repository:

1. Detects the repository type (Git, Mercurial, SVN, or plain directory)
2. Runs the ingest pipeline on the repository code
3. Creates a Knowledge graph in Neo4j (or local files in offline mode)
4. Writes configuration to `.testindex/config.yml`

Example output:
```
📂 Using Git repository at /path/to/repo
📊 Analyzing repository...
📖 Parsing 1.3M LOC...
✅ Parsed 39081 code chunks
🔄 Building knowledge graph...
✅ Created 39081 nodes and 52143 relationships in knowledge graph
📝 Configuration written to .testindex/config.yml
🚀 Knowledge graph ready (neo4j://localhost:7687)
✨ Processed 39081 chunks into 39081 nodes in 10.5s
```

### Remote Repository

When running `testindex init` with a remote repository URL:

1. Detects repository type from URL
2. Clones the repository to `.testindex/cache/<repo-name>`
3. Follows the same steps as for a local repository

Example output:
```
🌐 Cloning Mercurial repository from hg+https://hg.example.com/repo...
📂 Repository cloned to .testindex/cache/repo
...
```

### Offline Mode

When running `testindex init` with the `--offline` flag:

1. Processes repository code without requiring Neo4j
2. Stores chunks and nodes as JSON files in `.testindex/knowledge_graph/`
3. Writes configuration to `.testindex/config.yml`

Example output:
```
📂 Using Mercurial repository at /path/to/repo
📊 Analyzing repository...
📖 Parsing 1.3M LOC...
✅ Parsed 39081 code chunks
🔄 Building knowledge graph...
💾 Saved 39081 chunks to .testindex/knowledge_graph/chunks.json
💾 Saved 39081 nodes to .testindex/knowledge_graph/nodes.json
📝 Configuration written to .testindex/config.yml
🚀 Knowledge graph ready (neo4j://localhost:7687)
✨ Processed 39081 chunks into 39081 nodes in 10.5s
```

### Display Coverage Gaps

The `coverage` command displays test coverage gaps:

```bash
# Display coverage gaps as a table
testindex coverage

# Output to JSON file
testindex coverage --json gaps.json

# Exit with code 1 if gaps exist (for CI)
testindex coverage --exit-on-gap

# Specify custom threshold (default is 0%)
testindex coverage --threshold 50
```

Example output:
```
┌────────────────────────────┬────────────┬──────┐
│ File                       │ Function   │ %Cov │
├────────────────────────────┼────────────┼──────┤
│ src/orders.py              │ calc       │ 0    │
│ src/utils/math.py          │ add        │ 0    │
└────────────────────────────┴────────────┴──────┘
Gaps: 2 / 123 implementations (1.6%)
```

## Troubleshooting

### VCS Tool Requirements

The `init` command requires the appropriate VCS tools to be installed:

1. **Git**
   - Required for Git repositories
   - Install: `brew install git` (macOS) or `apt-get install git` (Linux)

2. **Mercurial**
   - Required for Mercurial repositories
   - Install: `brew install mercurial` (macOS) or `apt-get install mercurial` (Linux)

3. **Subversion**
   - Required for SVN repositories
   - Install: `brew install subversion` (macOS) or `apt-get install subversion` (Linux)

If a required tool is missing, you'll see an error like:
```
Error: Mercurial (hg) command not found. Please install Mercurial.
```

### Neo4j Connection Issues

If you encounter Neo4j connection issues, you have several options:

1. Run in offline mode using the `--offline` flag:
   ```
   testindex init --offline
   ```

2. Ensure Neo4j is running and accessible:
   ```
   docker ps --filter "name=neo4j"
   ```

3. Set Neo4j environment variables correctly:
   ```
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USERNAME="neo4j"
   export NEO4J_PASSWORD="testindexdev"
   ```

### Syntax Error in Repository Files

The tool may find syntax errors in some repository files. These are typically ignored, and processing continues on the valid files. If you see errors like:

```
[ERROR] Syntax error in tests_syntax_error.py: invalid decimal literal
```

This is normal and expected for repositories with test files that intentionally contain syntax errors.

## Configuration

The command uses the following configuration settings:

- Neo4j connection: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASS` environment variables
- Default values:
  - Neo4j URI: `bolt://localhost:7687`
  - Vector store: `demo_output/vectors.sqlite`
  - Schema version: `K1`

## Generated Configuration

The `.testindex/config.yml` file contains:

```yaml
neo4j_uri: bolt://localhost:7687
vector_store: demo_output/vectors.sqlite
schema_version: K1
``` 