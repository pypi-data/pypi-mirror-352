"""
Schema versioning system for the Knowledge Graph.

This module provides utilities for managing schema versions,
including migration between versions and compatibility checking.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Type

from testindex.core.exceptions import ValidationError
from testindex.core.logging import get_logger
from testindex.knowledge.schema.base import SchemaItem, SchemaVersionMismatchError

logger = get_logger(__name__)


class SchemaVersion:
    """Represents a schema version with version number and compatibility info."""
    
    def __init__(
        self,
        version: str,
        release_date: datetime,
        description: str,
        compatible_with: Optional[List[str]] = None,
        migration_notes: Optional[str] = None,
    ):
        """Initialize a schema version.
        
        Args:
            version: Semantic version number (x.y.z)
            release_date: When this version was released
            description: Brief description of this version
            compatible_with: List of other versions this is compatible with
            migration_notes: Notes on migrating to/from this version
        """
        self.version = version
        self.release_date = release_date
        self.description = description
        self.compatible_with = compatible_with or []
        self.migration_notes = migration_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the schema version to a dictionary."""
        return {
            "version": self.version,
            "release_date": self.release_date.isoformat(),
            "description": self.description,
            "compatible_with": self.compatible_with,
            "migration_notes": self.migration_notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SchemaVersion":
        """Create a schema version from a dictionary."""
        return cls(
            version=data["version"],
            release_date=datetime.fromisoformat(data["release_date"]),
            description=data["description"],
            compatible_with=data.get("compatible_with", []),
            migration_notes=data.get("migration_notes"),
        )


class SchemaRegistry:
    """Registry of all schema versions and their compatibility."""
    
    _instance = None
    _versions: Dict[str, SchemaVersion] = {}
    _migrations: Dict[Tuple[str, str], callable] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one registry exists."""
        if cls._instance is None:
            cls._instance = super(SchemaRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the registry with built-in versions."""
        # Register initial schema version
        self.register_version(
            SchemaVersion(
                version="1.0.0",
                release_date=datetime(2023, 6, 1),
                description="Initial schema version",
                compatible_with=[],
                migration_notes="Initial version, no migration needed.",
            )
        )
    
    def register_version(self, version: SchemaVersion) -> None:
        """Register a new schema version in the registry.
        
        Args:
            version: The schema version to register
        """
        self._versions[version.version] = version
        logger.info(f"Registered schema version {version.version}")
    
    def register_migration(
        self, from_version: str, to_version: str, migration_func: callable
    ) -> None:
        """Register a migration function between two schema versions.
        
        Args:
            from_version: Source schema version
            to_version: Target schema version
            migration_func: Function that performs the migration
        """
        if from_version not in self._versions:
            raise ValueError(f"Unknown source version: {from_version}")
        if to_version not in self._versions:
            raise ValueError(f"Unknown target version: {to_version}")
        
        self._migrations[(from_version, to_version)] = migration_func
        logger.info(f"Registered migration from {from_version} to {to_version}")
    
    def get_version(self, version: str) -> SchemaVersion:
        """Get a schema version by version number.
        
        Args:
            version: Version number to retrieve
            
        Returns:
            SchemaVersion: The requested schema version
            
        Raises:
            ValueError: If the version is not found
        """
        if version not in self._versions:
            raise ValueError(f"Unknown schema version: {version}")
        return self._versions[version]
    
    def list_versions(self) -> List[SchemaVersion]:
        """List all registered schema versions.
        
        Returns:
            List[SchemaVersion]: All registered versions
        """
        return list(self._versions.values())
    
    def are_compatible(self, version1: str, version2: str) -> bool:
        """Check if two schema versions are compatible.
        
        Args:
            version1: First version to check
            version2: Second version to check
            
        Returns:
            bool: True if the versions are compatible
        """
        # Exact same version is always compatible
        if version1 == version2:
            return True
        
        # Check if either version lists the other as compatible
        v1 = self.get_version(version1)
        v2 = self.get_version(version2)
        
        return (
            version2 in v1.compatible_with or
            version1 in v2.compatible_with
        )
    
    def migrate(
        self, data: Dict[str, Any], from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """Migrate data from one schema version to another.
        
        Args:
            data: The data to migrate
            from_version: Source schema version
            to_version: Target schema version
            
        Returns:
            Dict[str, Any]: The migrated data
            
        Raises:
            ValueError: If no migration path exists
        """
        # No migration needed if versions are the same
        if from_version == to_version:
            return data
        
        # Check if direct migration exists
        migration_key = (from_version, to_version)
        if migration_key in self._migrations:
            logger.info(f"Migrating from {from_version} to {to_version}")
            return self._migrations[migration_key](data)
        
        # Try to find a path through intermediate versions
        # This is a simplified approach; a real implementation would use a graph algorithm
        for intermediate in self._versions:
            if (from_version, intermediate) in self._migrations and \
               (intermediate, to_version) in self._migrations:
                logger.info(f"Migrating from {from_version} to {intermediate} to {to_version}")
                intermediate_data = self._migrations[(from_version, intermediate)](data)
                return self._migrations[(intermediate, to_version)](intermediate_data)
        
        raise ValueError(f"No migration path from {from_version} to {to_version}")


def migrate_schema_item(item: SchemaItem, to_version: str) -> SchemaItem:
    """Migrate a schema item to a different version.
    
    Args:
        item: The schema item to migrate
        to_version: Target schema version
        
    Returns:
        SchemaItem: The migrated schema item
        
    Raises:
        SchemaVersionMismatchError: If migration fails
    """
    from_version = item._schema_version
    
    if from_version == to_version:
        return item
    
    try:
        # Convert to dictionary for migration
        data = item.to_dict()
        
        # Migrate the data
        registry = SchemaRegistry()
        migrated_data = registry.migrate(data, from_version, to_version)
        
        # Create a new instance with the migrated data
        # We need to use the appropriate class for the item
        item_class = type(item)
        migrated_item = item_class.from_dict(migrated_data)
        
        # Update the schema version
        migrated_item._schema_version = to_version
        
        return migrated_item
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise SchemaVersionMismatchError(
            f"Failed to migrate from {from_version} to {to_version}: {str(e)}"
        )


def save_schema_registry(path: str) -> None:
    """Save the schema registry to a file.
    
    Args:
        path: Path to save the registry to
    """
    registry = SchemaRegistry()
    versions = {
        version.version: version.to_dict()
        for version in registry.list_versions()
    }
    
    with open(path, "w") as f:
        json.dump(versions, f, indent=2)


def load_schema_registry(path: str) -> None:
    """Load the schema registry from a file.
    
    Args:
        path: Path to load the registry from
    """
    if not os.path.exists(path):
        logger.warning(f"Schema registry file not found: {path}")
        return
    
    with open(path, "r") as f:
        data = json.load(f)
    
    registry = SchemaRegistry()
    for version_data in data.values():
        version = SchemaVersion.from_dict(version_data)
        registry.register_version(version) 