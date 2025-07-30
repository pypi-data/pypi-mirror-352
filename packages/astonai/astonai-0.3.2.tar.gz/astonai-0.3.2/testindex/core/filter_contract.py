"""
Filter Contract for TestIndex.

Ensures consistent filtering across all commands by generating and validating
filter manifests. This helps track what filters were used to generate artifacts.
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from testindex.core.filtering import FileFilter
from testindex.core.path_resolution import PathResolver
from testindex.core.logging import get_logger

logger = get_logger(__name__)


class FilterConstants:
    """Filter system constants."""
    # Filter manifest version
    MANIFEST_VERSION = "1.0"
    
    # Manifest file name
    MANIFEST_FILE = "filter_manifest.json"
    
    # Default patterns
    DEFAULT_PYTHON_EXTENSIONS = ['.py']
    DEFAULT_EXCLUDE_DIRS = ['venv*', '.git', '__pycache__']
    
    # Manifest fields
    FIELD_VERSION = "version"
    FIELD_PATTERNS = "patterns"
    FIELD_FILE_HASHES = "file_hashes"
    FIELD_TIMESTAMP = "timestamp"
    FIELD_FILE_COUNT = "file_count"
    FIELD_TOTAL_LINES = "total_lines"


class FilterContract:
    """Ensures consistent filtering across all commands."""
    
    def __init__(self, file_filter: FileFilter):
        """Initialize the filter contract.
        
        Args:
            file_filter: Configured FileFilter instance
        """
        self.file_filter = file_filter
        self._manifest = None
        self._file_list_cache = None
    
    def generate_manifest(self, file_extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a manifest of what will be processed.
        
        Args:
            file_extensions: List of file extensions to include
            
        Returns:
            Dictionary containing manifest data
        """
        if file_extensions is None:
            file_extensions = FilterConstants.DEFAULT_PYTHON_EXTENSIONS
        
        # Get filtered files
        files = self.file_filter.discover_files(file_extensions)
        self._file_list_cache = files
        
        # Calculate file hashes and stats
        file_hashes = {}
        total_lines = 0
        
        for file_path in files:
            try:
                # Calculate file hash
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()[:16]
                
                # Count lines
                with open(file_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                relative_path = file_path.relative_to(self.file_filter.repo_root)
                file_hashes[str(relative_path)] = {
                    "hash": file_hash,
                    "lines": line_count
                }
                total_lines += line_count
                
            except Exception as e:
                logger.warning(f"Error processing {file_path} for manifest: {e}")
        
        # Build manifest
        manifest = {
            FilterConstants.FIELD_VERSION: FilterConstants.MANIFEST_VERSION,
            FilterConstants.FIELD_TIMESTAMP: datetime.now().isoformat(),
            FilterConstants.FIELD_PATTERNS: self.file_filter.get_pattern_summary(),
            FilterConstants.FIELD_FILE_COUNT: len(files),
            FilterConstants.FIELD_TOTAL_LINES: total_lines,
            FilterConstants.FIELD_FILE_HASHES: file_hashes
        }
        
        self._manifest = manifest
        return manifest
    
    def save_manifest(self, output_dir: Path) -> Path:
        """Save the manifest to a file.
        
        Args:
            output_dir: Directory to save the manifest
            
        Returns:
            Path to the saved manifest file
        """
        if self._manifest is None:
            self.generate_manifest()
        
        manifest_path = output_dir / FilterConstants.MANIFEST_FILE
        
        with open(manifest_path, 'w') as f:
            json.dump(self._manifest, f, indent=2)
        
        logger.info(f"Saved filter manifest to {manifest_path}")
        return manifest_path
    
    def load_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Load a manifest from file.
        
        Args:
            manifest_path: Path to the manifest file
            
        Returns:
            Manifest dictionary
        """
        with open(manifest_path, 'r') as f:
            return json.load(f)
    
    def validate_manifest(self, stored_manifest: Dict[str, Any]) -> bool:
        """Check if current filter matches stored manifest.
        
        Args:
            stored_manifest: Previously saved manifest
            
        Returns:
            True if filters match, False otherwise
        """
        # Generate current manifest
        current = self.generate_manifest()
        
        # Compare patterns
        return self._compare_manifests(current, stored_manifest)
    
    def _compare_manifests(self, manifest1: Dict[str, Any], manifest2: Dict[str, Any]) -> bool:
        """Compare two manifests for compatibility.
        
        Args:
            manifest1: First manifest
            manifest2: Second manifest
            
        Returns:
            True if manifests are compatible
        """
        # Check version compatibility
        if manifest1.get(FilterConstants.FIELD_VERSION) != manifest2.get(FilterConstants.FIELD_VERSION):
            logger.warning("Manifest version mismatch")
            return False
        
        # Compare patterns
        patterns1 = manifest1.get(FilterConstants.FIELD_PATTERNS, {})
        patterns2 = manifest2.get(FilterConstants.FIELD_PATTERNS, {})
        
        # Extract pattern strings for comparison
        include1 = {p['pattern'] for p in patterns1.get('include_patterns', [])}
        include2 = {p['pattern'] for p in patterns2.get('include_patterns', [])}
        
        exclude1 = {p['pattern'] for p in patterns1.get('exclude_patterns', [])}
        exclude2 = {p['pattern'] for p in patterns2.get('exclude_patterns', [])}
        
        if include1 != include2 or exclude1 != exclude2:
            logger.info("Filter patterns have changed")
            return False
        
        return True
    
    def get_changed_files(self, stored_manifest: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get files that have changed since the stored manifest.
        
        Args:
            stored_manifest: Previously saved manifest
            
        Returns:
            Dictionary with 'added', 'removed', and 'modified' file lists
        """
        current = self.generate_manifest()
        
        stored_files = stored_manifest.get(FilterConstants.FIELD_FILE_HASHES, {})
        current_files = current.get(FilterConstants.FIELD_FILE_HASHES, {})
        
        # Find changes
        added = []
        removed = []
        modified = []
        
        # Check for removed and modified files
        for file_path, file_info in stored_files.items():
            if file_path not in current_files:
                removed.append(file_path)
            elif current_files[file_path]['hash'] != file_info['hash']:
                modified.append(file_path)
        
        # Check for added files
        for file_path in current_files:
            if file_path not in stored_files:
                added.append(file_path)
        
        return {
            'added': added,
            'removed': removed,
            'modified': modified
        }
    
    def requires_rechunk(self, stored_manifest_path: Path) -> bool:
        """Check if rechunking is required based on filter changes.
        
        Args:
            stored_manifest_path: Path to the stored manifest
            
        Returns:
            True if rechunking is required
        """
        if not stored_manifest_path.exists():
            logger.info("No manifest found, rechunking required")
            return True
        
        try:
            stored_manifest = self.load_manifest(stored_manifest_path)
            
            # Check if filters have changed
            if not self.validate_manifest(stored_manifest):
                logger.info("Filter patterns have changed, rechunking required")
                return True
            
            # Check if any files have changed
            changes = self.get_changed_files(stored_manifest)
            total_changes = len(changes['added']) + len(changes['removed']) + len(changes['modified'])
            
            if total_changes > 0:
                logger.info(f"Found {total_changes} file changes, rechunking required")
                return True
                
            logger.info("No changes detected, rechunking not required")
            return False
            
        except Exception as e:
            logger.error(f"Error checking manifest: {e}")
            return True
    
    def get_files_to_process(self) -> List[Path]:
        """Get the list of files that will be processed.
        
        Returns:
            List of file paths
        """
        if self._file_list_cache is None:
            self._file_list_cache = self.file_filter.discover_files(
                FilterConstants.DEFAULT_PYTHON_EXTENSIONS
            )
        
        return self._file_list_cache 