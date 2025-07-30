"""
Core Foundation package for the Test Intelligence Engine.

This package provides the essential infrastructure that all other pods depend on,
including configuration management, logging, exception handling, and utility functions.
"""

__version__ = "0.1.12"

# Re-export key classes and functions for easier imports
from testindex.core.config import ConfigLoader
from testindex.core.exceptions import (
    AstonError,
    ConfigurationError,
    StorageError,
    CLIError,
    LoggingError,
    ValidationError,
)
from testindex.core.logging import (
    LogLevel,
    LogFormat,
    LogDestination,
    StructuredLogger,
    get_logger,
)
from testindex.core.utils import (
    generate_unique_id,
    hash_content,
    ensure_directory,
    is_valid_path,
    format_timestamp,
    safe_json_loads,
    parse_size_string,
    flatten_dict,
)

__all__ = [
    "AppConfig",
    "ConfigModel",
    "ConfigLoader",
    "load_config",
    "AstonError",
    "BaseException",
    "ConfigurationError",
    "StorageError",
    "CLIError",
    "LoggingError",
    "ValidationError",
]
