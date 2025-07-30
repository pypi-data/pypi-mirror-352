"""
Configuration management system for the Test Intelligence Engine.

This module provides utilities for:
- Loading configuration from YAML/JSON files
- Environment variable overrides
- Default configuration values
- Type validation using Pydantic
- Basic error handling for invalid configurations
"""
import os
import json
import yaml
from typing import Any, Dict, Optional, Type, TypeVar, Union
from pathlib import Path

from pydantic import BaseModel, ValidationError

from testindex.core.exceptions import ConfigurationError


T = TypeVar('T', bound=BaseModel)

# Define ConfigModel for use in other modules
class ConfigModel:
    """Base class for configuration models."""
    
    def __init__(self, **kwargs):
        """Initialize a configuration model with keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary."""
        return {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigModel":
        """Create a configuration model from a dictionary."""
        return cls(**data)
    
    @classmethod
    def with_defaults(cls):
        """Create an instance with default values."""
        return cls()
    
    def __repr__(self) -> str:
        """Get a string representation of the configuration."""
        items = ", ".join(f"{key}={value!r}" for key, value in self.to_dict().items())
        return f"{self.__class__.__name__}({items})"


class ConfigLoader:
    """
    Configuration loader that supports multiple file formats and environment overrides.
    
    Handles loading configuration from YAML or JSON files with support for environment
    variable overrides and default values. Uses Pydantic for validation.
    """
    
    def __init__(self):
        """Initialize the ConfigLoader."""
        self._config = {}
    
    def load_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Load configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration data
        """
        self._config = config_dict
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the loaded configuration.
        
        Returns:
            Dictionary containing the loaded configuration
        """
        return self._config
    
    @staticmethod
    def load_config(
        config_class: Type[T],
        config_path: Optional[Union[str, Path]] = None,
        env_prefix: str = "TI_",
        default_values: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Load and validate configuration from file and/or environment variables.
        
        Args:
            config_class: Pydantic model class for the configuration
            config_path: Path to the configuration file (YAML or JSON)
            env_prefix: Prefix for environment variables to override config
            default_values: Default values for configuration
            
        Returns:
            An instance of the provided config_class
            
        Raises:
            ConfigurationError: If configuration cannot be loaded or validated
        """
        try:
            # Start with default values or empty dict
            config_data = default_values or {}
            
            # Load from file if provided
            if config_path:
                file_data = ConfigLoader._load_from_file(config_path)
                config_data.update(file_data)
            
            # Override with environment variables
            env_data = ConfigLoader._load_from_env(config_class, env_prefix)
            ConfigLoader._deep_update(config_data, env_data)
            
            # Validate and create config object using Pydantic
            return config_class(**config_data)
            
        except ValidationError as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    @staticmethod
    def _load_from_file(config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from a YAML or JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ConfigurationError: If the file cannot be loaded
        """
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ('.yaml', '.yml'):
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {path.suffix}"
                    )
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigurationError(f"Error parsing configuration file {path}: {str(e)}")
    
    @staticmethod
    def _load_from_env(config_class: Type[BaseModel], env_prefix: str) -> Dict[str, Any]:
        """
        Extract configuration values from environment variables.
        
        Environment variables are expected to follow the pattern:
        ENV_PREFIX_VARIABLE_NAME
        
        For nested configurations, use double underscores:
        ENV_PREFIX_SECTION__VARIABLE_NAME
        
        Args:
            config_class: Pydantic model class for the configuration
            env_prefix: Prefix for environment variables
            
        Returns:
            Dictionary containing configuration data from environment variables
        """
        env_config = {}
        
        # Process environment variables
        for env_var, env_val in os.environ.items():
            # Only process variables with the specified prefix
            if not env_var.startswith(env_prefix):
                continue
            
            # Remove prefix and convert to lowercase to match Pydantic model fields
            key = env_var[len(env_prefix):].lower()
            
            # Parse the value based on content
            try:
                # Try to parse as JSON if it looks like a JSON value
                if env_val.startswith('{') or env_val.startswith('['):
                    value = json.loads(env_val)
                # Try to convert to int if it's numeric
                elif env_val.isdigit():
                    value = int(env_val)
                # Try to convert to float if it has a decimal point
                elif env_val.replace('.', '', 1).isdigit() and env_val.count('.') == 1:
                    value = float(env_val)
                # Convert to boolean for "true"/"false" values
                elif env_val.lower() in ('true', 'false'):
                    value = env_val.lower() == 'true'
                # Otherwise, keep as string
                else:
                    value = env_val
            except (json.JSONDecodeError, ValueError):
                # If any parsing fails, use the original string value
                value = env_val
                
            # Handle nested configurations (separated by double underscore)
            if '__' in key:
                parts = key.split('__')
                current = env_config
                
                # Build nested dictionary structure
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
                current[parts[-1]] = value
            else:
                env_config[key] = value
        
        return env_config
        
    @staticmethod
    def _deep_update(target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a nested dictionary with values from another dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update nested dictionaries
                ConfigLoader._deep_update(target[key], value)
            else:
                # Update or add the value
                target[key] = value


# Example usage:
# 
# from pydantic import BaseModel
# 
# class DatabaseConfig(BaseModel):
#     host: str
#     port: int
#     username: str
#     password: str
#     database: str
#
# class AppConfig(ConfigModel):
#     debug: bool = False
#     log_level: str = "INFO"
#     database: DatabaseConfig
#
# # Load configuration
# config_loader = ConfigLoader()
# app_config = config_loader.load_config(
#     AppConfig,
#     config_path="config.yaml",
#     env_prefix="MYAPP_"
# )

class EmbeddingConfig(ConfigModel):
    """Configuration for embedding services."""
    openai_api_key: Optional[str] = None
    openai_organization: Optional[str] = None
    openai_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    batch_size: int = 100
    retry_attempts: int = 3
    
class PineconeConfig(ConfigModel):
    """Configuration for Pinecone vector database."""
    api_key: Optional[str] = None
    environment: Optional[str] = None
    index_name: str = "code-embeddings"
    namespace: str = "testindex"
    
# Avoid the conflicting redefinition of ConfigModel
class PydanticConfigWrapper(BaseModel):
    """Pydantic wrapper for configuration classes."""
    
    # Add new sections
    embedding: Optional[Dict[str, Any]] = None
    pinecone: Optional[Dict[str, Any]] = None
    
    @classmethod
    def with_defaults(cls):
        """Create an instance with default configurations."""
        return cls(
            embedding=EmbeddingConfig().to_dict(),
            pinecone=PineconeConfig().to_dict()
        )
