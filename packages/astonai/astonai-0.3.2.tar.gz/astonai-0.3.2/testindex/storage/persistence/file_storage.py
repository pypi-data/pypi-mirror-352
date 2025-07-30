"""
File-based storage implementation for the Test Intelligence Engine.

This module provides utilities for storing and retrieving data from files.
"""
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from testindex.core.exceptions import StorageError


class FileStorage:
    """
    File-based storage for the Test Intelligence Engine.
    
    This class provides utilities for storing and retrieving data from files
    in various formats (JSON, YAML, binary).
    """
    
    def __init__(self, base_dir: Union[str, Path]):
        """
        Initialize a new file storage.
        
        Args:
            base_dir: Base directory for storing files
            
        Raises:
            StorageError: If the base directory cannot be created
        """
        self.base_dir = Path(base_dir)
        
        try:
            # Create base directory if it doesn't exist
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Failed to create base directory: {str(e)}")
    
    def _get_path(self, key: str) -> Path:
        """
        Get the path for a storage key.
        
        Args:
            key: Storage key
            
        Returns:
            Path object for the storage key
        """
        # Replace path separators with underscores to avoid directory traversal
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self.base_dir / safe_key
    
    def save_json(self, key: str, data: Any) -> None:
        """
        Save data as JSON.
        
        Args:
            key: Storage key
            data: Data to save
            
        Raises:
            StorageError: If the data cannot be saved
        """
        path = self._get_path(f"{key}.json")
        
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save JSON data: {str(e)}")
    
    def load_json(self, key: str, default: Any = None) -> Any:
        """
        Load data from JSON.
        
        Args:
            key: Storage key
            default: Default value to return if the file doesn't exist (default: None)
            
        Returns:
            Loaded data or default if the file doesn't exist
            
        Raises:
            StorageError: If the data cannot be loaded
        """
        path = self._get_path(f"{key}.json")
        
        if not path.exists():
            return default
        
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            raise StorageError(f"Failed to load JSON data: {str(e)}")
    
    def save_yaml(self, key: str, data: Any) -> None:
        """
        Save data as YAML.
        
        Args:
            key: Storage key
            data: Data to save
            
        Raises:
            StorageError: If the data cannot be saved
        """
        path = self._get_path(f"{key}.yaml")
        
        try:
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        except Exception as e:
            raise StorageError(f"Failed to save YAML data: {str(e)}")
    
    def load_yaml(self, key: str, default: Any = None) -> Any:
        """
        Load data from YAML.
        
        Args:
            key: Storage key
            default: Default value to return if the file doesn't exist (default: None)
            
        Returns:
            Loaded data or default if the file doesn't exist
            
        Raises:
            StorageError: If the data cannot be loaded
        """
        path = self._get_path(f"{key}.yaml")
        
        if not path.exists():
            return default
        
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise StorageError(f"Failed to load YAML data: {str(e)}")
    
    def save_binary(self, key: str, data: bytes) -> None:
        """
        Save binary data.
        
        Args:
            key: Storage key
            data: Binary data to save
            
        Raises:
            StorageError: If the data cannot be saved
        """
        path = self._get_path(f"{key}.bin")
        
        try:
            with open(path, "wb") as f:
                f.write(data)
        except Exception as e:
            raise StorageError(f"Failed to save binary data: {str(e)}")
    
    def load_binary(self, key: str, default: Any = None) -> Optional[bytes]:
        """
        Load binary data.
        
        Args:
            key: Storage key
            default: Default value to return if the file doesn't exist (default: None)
            
        Returns:
            Loaded binary data or default if the file doesn't exist
            
        Raises:
            StorageError: If the data cannot be loaded
        """
        path = self._get_path(f"{key}.bin")
        
        if not path.exists():
            return default
        
        try:
            with open(path, "rb") as f:
                return f.read()
        except Exception as e:
            raise StorageError(f"Failed to load binary data: {str(e)}")
    
    def delete(self, key: str) -> bool:
        """
        Delete a stored item.
        
        Args:
            key: Storage key
            
        Returns:
            True if the item was deleted, False if it didn't exist
            
        Raises:
            StorageError: If the item cannot be deleted
        """
        # Try to delete the item with each possible extension
        for ext in [".json", ".yaml", ".bin"]:
            path = self._get_path(f"{key}{ext}")
            
            if path.exists():
                try:
                    path.unlink()
                    return True
                except Exception as e:
                    raise StorageError(f"Failed to delete item: {str(e)}")
        
        return False
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all storage keys.
        
        Args:
            prefix: Optional prefix to filter keys (default: None)
            
        Returns:
            List of storage keys
            
        Raises:
            StorageError: If the keys cannot be listed
        """
        try:
            # Get all files in the base directory
            files = [p.name for p in self.base_dir.glob("*") if p.is_file()]
            
            # Extract keys by removing extensions
            keys = []
            for file in files:
                key, _ = os.path.splitext(file)
                if prefix is None or key.startswith(prefix):
                    keys.append(key)
            
            return list(set(keys))  # Remove duplicates
        except Exception as e:
            raise StorageError(f"Failed to list keys: {str(e)}")
    
    def clear(self) -> None:
        """
        Clear all stored items.
        
        Raises:
            StorageError: If the items cannot be cleared
        """
        try:
            # Remove all files in the base directory
            for path in self.base_dir.glob("*"):
                if path.is_file():
                    path.unlink()
        except Exception as e:
            raise StorageError(f"Failed to clear storage: {str(e)}")
    
    def ensure_directory(self, directory: Union[str, Path]) -> Path:
        """
        Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path
            
        Returns:
            Path object for the directory
            
        Raises:
            StorageError: If the directory cannot be created
        """
        path = self.base_dir / directory
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            raise StorageError(f"Failed to create directory: {str(e)}")

    def exists(self, key: str) -> bool:
        """
        Check if a stored item exists.
        
        Args:
            key: Storage key
            
        Returns:
            True if the item exists, False otherwise
        """
        # Check if the item exists with any possible extension
        for ext in [".json", ".yaml", ".bin"]:
            path = self._get_path(f"{key}{ext}")
            
            if path.exists():
                return True
        
        return False 