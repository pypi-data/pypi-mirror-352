"""
Utility functions for the Test Intelligence Engine.

This module provides small, framework-agnostic helper functions used throughout the application.
"""
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable


def generate_unique_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        A unique identifier string
    """
    return str(uuid.uuid4())


def hash_content(content: Union[str, bytes]) -> str:
    """
    Generate a hash for the given content.
    
    Args:
        content: Content to hash
        
    Returns:
        SHA-256 hash of the content
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
        
    return hashlib.sha256(content).hexdigest()


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object for the directory
        
    Raises:
        OSError: If the directory cannot be created
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_valid_path(path: Union[str, Path]) -> bool:
    """
    Check if a path is valid and exists.
    
    Args:
        path: Path to check
        
    Returns:
        True if the path is valid and exists, False otherwise
    """
    try:
        return Path(path).exists()
    except (TypeError, ValueError):
        return False


def format_timestamp() -> str:
    """Returns the current UTC timestamp in ISO format."""
    timestamp = datetime.now(timezone.utc)
    return timestamp.isoformat() + "Z"


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Format a timestamp in ISO 8601 format.
    
    Args:
        timestamp: Timestamp to format (default: current time)
        
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
        
    return dt.isoformat() + "Z"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely load a JSON string.
    
    Args:
        json_str: JSON string to load
        default: Default value to return if loading fails (default: None)
        
    Returns:
        Parsed JSON object or default value if loading fails
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def parse_size_string(size_str: str) -> int:
    """
    Parse a human-readable size string (e.g., '10MB', '1GB') to bytes.
    
    Args:
        size_str: Size string to parse
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If the size string is invalid
    """
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4
    }
    
    pattern = r"^(\d+(?:\.\d+)?)\s*([A-Za-z]+)$"
    match = re.match(pattern, size_str.strip())
    
    if not match:
        raise ValueError(f"Invalid size string: {size_str}")
    
    value, unit = match.groups()
    unit = unit.upper()
    
    if unit not in units:
        raise ValueError(f"Invalid unit: {unit}")
    
    return int(float(value) * units[unit])


def flatten_dict(nested_dict: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        nested_dict: Nested dictionary to flatten
        separator: Separator for nested keys (default: '.')
        
    Returns:
        Flattened dictionary
    """
    result = {}
    
    def _flatten(d: Dict[str, Any], prefix: str = "") -> None:
        for key, value in d.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                _flatten(value, new_key)
            else:
                result[new_key] = value
    
    _flatten(nested_dict)
    return result
