# Repository Management Module

This module provides tools for managing Git repositories and running code in isolated Docker environments.

## Features

### Git Manager (`git_manager.py`)

The GitManager class provides a wrapper around GitPython to manage Git repositories:

- Repository cloning with branch/tag/commit selection
- Repository updates (pulling latest changes)
- Checkout of specific references (branches, tags, commits)
- Repository metadata extraction
- Change detection and status reporting

### Docker Environment (`docker_env.py`)

The DockerEnvironment class provides containerized execution environments for code:

- Container creation and lifecycle management
- Code volume mounting for read-only or read-write access
- Resource limits for CPU and memory
- Command execution in containers
- Container status reporting and management

## Usage

### Git Manager Example

```python
from pathlib import Path
from testindex.preprocessing.cloning.git_manager import GitManager
from testindex.core.config import ConfigModel

# Create configuration
config = ConfigModel()

# Initialize Git manager
git_manager = GitManager(config)

# Clone a repository
repo = git_manager.clone_repository(
    url="https://github.com/example/repo.git",
    target_dir=Path("/path/to/target"),
    branch="main"
)

# Update an existing repository
git_manager.update_repository(Path("/path/to/repo"))

# Get latest commit information
commit_info = git_manager.get_latest_commit(repo)
print(f"Latest commit: {commit_info['hash']} by {commit_info['author']}")
```

### Docker Environment Example

```python
from pathlib import Path
from testindex.preprocessing.cloning.docker_env import DockerEnvironment, ResourceLimits
from testindex.core.config import ConfigModel

# Create configuration
config = ConfigModel()

# Initialize Docker environment
docker_env = DockerEnvironment(config)

# Set resource limits
limits = ResourceLimits(cpu_count=1.0, memory_limit="512m")

# Create container
container = docker_env.create_container(
    name="test-container",
    image="python:3.9-slim",
    code_dir=Path("/path/to/code"),
    working_dir="/code",
    resource_limits=limits
)

# Start container
docker_env.start_container("test-container")

# Execute command
result = docker_env.execute_command(
    container_name="test-container",
    command=["python", "-m", "pytest", "tests/"]
)

print(f"Exit code: {result['exit_code']}")
print(f"Output: {result['output']}")

# Clean up
docker_env.stop_container("test-container")
docker_env.remove_container("test-container")
```

## Error Handling

Both components use the Core exception hierarchy for robust error handling:

- `GitError`: Base exception for Git operations
- `CloneError`: Raised when cloning fails
- `UpdateError`: Raised when repository update fails
- `CheckoutError`: Raised when reference checkout fails
- `DockerError`: Base exception for Docker operations
- `ContainerCreationError`: Raised when container creation fails
- `ContainerStartError`: Raised when container start fails
- `ContainerStopError`: Raised when container stop fails
- `CommandExecutionError`: Raised when command execution fails

All exceptions include details and proper error codes for tracking and debugging.

## Dependencies

- GitPython: For Git operations
- Docker: For Docker operations
- Core components: For configuration, logging, and exceptions 