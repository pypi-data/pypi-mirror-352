from pathlib import Path
from typing import Dict, Optional, List, Any, Union
import os
import docker
from docker.models.containers import Container
from docker.errors import DockerException, ImageNotFound, ContainerError
from testindex.core.config import ConfigModel
from testindex.core.logging import get_logger
from testindex.core.exceptions import BaseException

class DockerError(BaseException):
    """Base exception for docker operations."""
    error_code_prefix = "DOCK"
    
class ContainerCreationError(DockerError):
    """Exception raised when container creation fails."""
    error_code = "DOCK001"
    
class ContainerStartError(DockerError):
    """Exception raised when container start fails."""
    error_code = "DOCK002"
    
class ContainerStopError(DockerError):
    """Exception raised when container stop fails."""
    error_code = "DOCK003"
    
class VolumeError(DockerError):
    """Exception raised when volume operations fail."""
    error_code = "DOCK004"
    
class CommandExecutionError(DockerError):
    """Exception raised when command execution fails."""
    error_code = "DOCK005"

class ResourceLimits:
    """Configuration for container resource limits."""
    
    def __init__(
        self,
        cpu_count: Optional[float] = None,
        memory_limit: Optional[str] = None,
        memory_swap: Optional[str] = None,
        memory_reservation: Optional[str] = None
    ):
        """Initialize resource limits for Docker containers.
        
        Args:
            cpu_count: Number of CPUs to limit (can be fractional)
            memory_limit: Memory limit (e.g., "512m", "2g")
            memory_swap: Total memory limit (memory + swap)
            memory_reservation: Soft limit for memory
        """
        self.cpu_count = cpu_count
        self.memory_limit = memory_limit
        self.memory_swap = memory_swap
        self.memory_reservation = memory_reservation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource limits to Docker-compatible dictionary.
        
        Returns:
            Dict: Resource constraints for Docker API
        """
        resources: Dict[str, Any] = {}
        
        if self.cpu_count is not None:
            resources['cpu_quota'] = int(self.cpu_count * 100000)
            resources['cpu_period'] = 100000
            
        if self.memory_limit is not None:
            resources['mem_limit'] = self.memory_limit
            
        if self.memory_swap is not None:
            resources['memswap_limit'] = self.memory_swap
            
        if self.memory_reservation is not None:
            resources['mem_reservation'] = self.memory_reservation
            
        return resources

class DockerEnvironment:
    """Manages Docker-based isolated environments for code execution."""
    
    def __init__(self, config: ConfigModel):
        """Initialize the Docker environment manager.
        
        Args:
            config: Configuration object containing Docker settings
        """
        self.logger = get_logger("docker-env")
        self.config = config
        self.client = None
        self.containers: Dict[str, Container] = {}
        
        self._initialize_client()
        
    def _initialize_client(self) -> None:
        """Initialize the Docker client."""
        try:
            self.client = docker.from_env()
            self.logger.info("Docker client initialized")
        except DockerException as e:
            self.logger.error(f"Failed to initialize Docker client: {e}")
            raise DockerError(f"Failed to initialize Docker client: {e}")
    
    def create_container(
        self,
        name: str,
        image: str,
        code_dir: Path,
        working_dir: str = "/code",
        command: Optional[Union[str, List[str]]] = None,
        environment: Optional[Dict[str, str]] = None,
        resource_limits: Optional[ResourceLimits] = None,
        network_disabled: bool = True,
        detach: bool = True
    ) -> Container:
        """Create a Docker container for code execution.
        
        Args:
            name: Container name
            image: Docker image to use
            code_dir: Directory containing code to mount
            working_dir: Working directory inside container
            command: Command to run (if any)
            environment: Environment variables
            resource_limits: Container resource limits
            network_disabled: Whether to disable networking
            detach: Whether to run container in background
            
        Returns:
            Container: The created Docker container
            
        Raises:
            ContainerCreationError: If container creation fails
        """
        if self.client is None:
            self._initialize_client()
            
        self.logger.info(f"Creating container '{name}' from image '{image}'")
        
        try:
            # Prepare volume mount
            code_dir_abs = code_dir.absolute()
            volumes = {
                str(code_dir_abs): {
                    'bind': working_dir,
                    'mode': 'ro'  # Read-only by default
                }
            }
            
            # Prepare resource limits
            host_config = {}
            if resource_limits:
                host_config.update(resource_limits.to_dict())
                
            # Create container
            container = self.client.containers.create(
                image=image,
                name=name,
                command=command,
                volumes=volumes,
                working_dir=working_dir,
                environment=environment,
                network_disabled=network_disabled,
                detach=detach,
                **host_config
            )
            
            self.containers[name] = container
            self.logger.info(f"Container '{name}' created successfully")
            return container
            
        except ImageNotFound as e:
            error_msg = f"Docker image '{image}' not found: {e}"
            self.logger.error(error_msg)
            raise ContainerCreationError(error_msg, details={
                "image": image,
                "name": name
            })
        except DockerException as e:
            error_msg = f"Failed to create container '{name}': {e}"
            self.logger.error(error_msg)
            raise ContainerCreationError(error_msg, details={
                "image": image,
                "name": name
            })
    
    def start_container(self, container_name: str) -> Container:
        """Start a Docker container.
        
        Args:
            container_name: Name of the container to start
            
        Returns:
            Container: The started container
            
        Raises:
            ContainerStartError: If container start fails
        """
        try:
            container = self._get_container(container_name)
            container.start()
            self.logger.info(f"Container '{container_name}' started")
            return container
        except DockerException as e:
            error_msg = f"Failed to start container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise ContainerStartError(error_msg, details={"name": container_name})
    
    def stop_container(self, container_name: str, timeout: int = 10) -> None:
        """Stop a Docker container.
        
        Args:
            container_name: Name of the container to stop
            timeout: Timeout before container is killed
            
        Raises:
            ContainerStopError: If container stop fails
        """
        try:
            container = self._get_container(container_name)
            container.stop(timeout=timeout)
            self.logger.info(f"Container '{container_name}' stopped")
        except DockerException as e:
            error_msg = f"Failed to stop container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise ContainerStopError(error_msg, details={"name": container_name})
    
    def remove_container(self, container_name: str, force: bool = False) -> None:
        """Remove a Docker container.
        
        Args:
            container_name: Name of the container to remove
            force: Whether to force remove the container
            
        Raises:
            DockerError: If container removal fails
        """
        try:
            container = self._get_container(container_name)
            container.remove(force=force)
            if container_name in self.containers:
                del self.containers[container_name]
            self.logger.info(f"Container '{container_name}' removed")
        except DockerException as e:
            error_msg = f"Failed to remove container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise DockerError(error_msg, details={"name": container_name})
    
    def execute_command(
        self,
        container_name: str,
        command: Union[str, List[str]],
        working_dir: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a command in a running container.
        
        Args:
            container_name: Name of the container to execute in
            command: Command to execute
            working_dir: Working directory for command execution
            environment: Environment variables for command
            user: User to run the command as
            
        Returns:
            Dict: Command execution results with exit_code, output, and error
            
        Raises:
            CommandExecutionError: If command execution fails
        """
        try:
            container = self._get_container(container_name)
            
            # Check if container is running
            container.reload()
            if container.status != 'running':
                self.start_container(container_name)
            
            # Execute command
            exec_kwargs = {
                'cmd': command,
                'workdir': working_dir,
                'environment': environment,
                'user': user
            }
            # Remove None values
            exec_kwargs = {k: v for k, v in exec_kwargs.items() if v is not None}
            
            # Execute command
            exec_result = container.exec_run(**exec_kwargs)
            exit_code = exec_result.exit_code
            output = exec_result.output.decode('utf-8') if exec_result.output else ""
            
            if exit_code != 0:
                self.logger.warning(f"Command '{command}' in container '{container_name}' "
                                  f"exited with code {exit_code}: {output}")
            else:
                self.logger.info(f"Command executed successfully in container '{container_name}'")
                
            return {
                "exit_code": exit_code,
                "output": output,
                "error": output if exit_code != 0 else None
            }
            
        except ContainerError as e:
            error_msg = f"Command execution error in container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise CommandExecutionError(error_msg, details={
                "name": container_name,
                "command": command,
                "exit_code": getattr(e, 'exit_code', None),
                "stderr": getattr(e, 'stderr', None)
            })
        except DockerException as e:
            error_msg = f"Failed to execute command in container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise CommandExecutionError(error_msg, details={
                "name": container_name,
                "command": command
            })
    
    def _get_container(self, container_name: str) -> Container:
        """Get a container by name.
        
        Args:
            container_name: Name of the container
            
        Returns:
            Container: The Docker container
            
        Raises:
            DockerError: If container not found
        """
        if container_name in self.containers:
            return self.containers[container_name]
            
        if self.client is None:
            self._initialize_client()
            
        try:
            container = self.client.containers.get(container_name)
            self.containers[container_name] = container
            return container
        except DockerException as e:
            error_msg = f"Container '{container_name}' not found: {e}"
            self.logger.error(error_msg)
            raise DockerError(error_msg, details={"name": container_name})
    
    def get_container_status(self, container_name: str) -> str:
        """Get the status of a container.
        
        Args:
            container_name: Name of the container
            
        Returns:
            str: Container status
            
        Raises:
            DockerError: If container status cannot be retrieved
        """
        try:
            container = self._get_container(container_name)
            container.reload()
            return container.status
        except DockerException as e:
            error_msg = f"Failed to get status for container '{container_name}': {e}"
            self.logger.error(error_msg)
            raise DockerError(error_msg, details={"name": container_name})
    
    def list_containers(self, all_containers: bool = True) -> List[Dict[str, Any]]:
        """List all containers managed by this environment.
        
        Args:
            all_containers: Whether to include stopped containers
            
        Returns:
            List[Dict]: List of container information
        """
        if self.client is None:
            self._initialize_client()
            
        try:
            containers = self.client.containers.list(all=all_containers)
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else c.image.id,
                    "created": c.attrs.get("Created", "")
                }
                for c in containers
            ]
        except DockerException as e:
            self.logger.error(f"Failed to list containers: {e}")
            return []
