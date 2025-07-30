"""
Path resolution utilities for TestIndex.

This module provides centralized path handling to ensure consistent path resolution
across the entire application, preventing path mismatches that can cause issues with
coverage detection.
"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

from testindex.core.logging import get_logger

# Set up logger
logger = get_logger(__name__)


class PathResolver:
    """Centralized path resolution utilities to prevent path mismatches."""
    
    @staticmethod
    def repo_root() -> Path:
        """Get the repository root path.
        
        This method attempts to find the repository root by checking for common
        repository indicators like .git or .hg directories. If none are found,
        it falls back to the current working directory.
        
        Returns:
            Path: The repository root path
        """
        # Start from current directory
        current_dir = Path.cwd()
        
        # Check for Git repository
        git_dir = current_dir / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return current_dir
        
        # Check for Mercurial repository
        hg_dir = current_dir / ".hg"
        if hg_dir.exists() and hg_dir.is_dir():
            return current_dir
        
        # Fallback to current directory if no repository is found
        logger.warning("No Git or Mercurial repository found, using current directory")
        return current_dir
    
    @staticmethod
    def testindex_dir() -> Path:
        """Get the .testindex directory path.
        
        Returns:
            Path: The .testindex directory path
        """
        return PathResolver.repo_root() / ".testindex"
    
    @staticmethod
    def knowledge_graph_dir() -> Path:
        """Get the knowledge graph directory path.
        
        Returns:
            Path: The knowledge graph directory path
        """
        return PathResolver.testindex_dir() / "knowledge_graph"
    
    @staticmethod
    def config_file() -> Path:
        """Get the config file path.
        
        Returns:
            Path: The config file path
        """
        return PathResolver.testindex_dir() / "config.yml"
    
    @staticmethod
    def nodes_file() -> Path:
        """Get the knowledge graph nodes file path.
        
        Returns:
            Path: The knowledge graph nodes file path
        """
        return PathResolver.knowledge_graph_dir() / "nodes.json"
    
    @staticmethod
    def edges_file() -> Path:
        """Get the knowledge graph edges file path.
        
        Returns:
            Path: The knowledge graph edges file path
        """
        return PathResolver.knowledge_graph_dir() / "edges.json"
    
    @staticmethod
    def to_repo_relative(path: Union[str, Path]) -> str:
        """Convert an absolute path to a repository-relative path.
        
        Args:
            path: The path to convert
            
        Returns:
            str: The repository-relative path
        """
        if isinstance(path, str):
            path = Path(path)
        
        try:
            # Get the repository root path
            repo_root = PathResolver.repo_root()
            
            # Check if the path is absolute and within the repo root
            if path.is_absolute():
                try:
                    # Try to make it relative to the repo root
                    return str(path.relative_to(repo_root))
                except ValueError:
                    # Path is outside the repository root, return the full path
                    logger.debug(f"Path {path} is outside the repository root, returning full path")
                    return str(path)
            else:
                # Path is already relative, just convert to string
                return str(path)
        except Exception as e:
            # Log the error and return the path as a string
            logger.error(f"Error converting path to repo-relative: {e}")
            return str(path)
    
    @staticmethod
    def to_absolute(path: Union[str, Path]) -> Path:
        """Convert a repository-relative path to an absolute path.
        
        Args:
            path: The path to convert
            
        Returns:
            Path: The absolute path
        """
        if isinstance(path, str):
            path = Path(path)
        
        if path.is_absolute():
            return path
        
        return PathResolver.repo_root() / path
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> str:
        """Normalize a path for consistent comparison.
        
        Normalization includes:
        - Converting to lowercase
        - Replacing backslashes with forward slashes
        - Removing leading './'
        
        For absolute paths, the path is preserved but normalized.
        
        Args:
            path: The path to normalize
            
        Returns:
            str: The normalized path
        """
        path_str = str(path).lower().replace('\\', '/').strip()
        
        # Remove trailing whitespace and new lines
        path_str = path_str.rstrip()
        
        # Remove leading "./" which can cause inconsistencies
        while path_str.startswith('./'):
            path_str = path_str[2:]
            
        return path_str
    
    @staticmethod
    def find_coverage_file() -> Optional[Path]:
        """Find the coverage.xml file in the repository.
        
        Returns:
            Optional[Path]: The coverage file path if found, None otherwise
        """
        root = PathResolver.repo_root()
        
        # Check common locations
        candidates = [
            root / "coverage.xml",
            root / ".coverage.xml",
            root / "htmlcov" / "coverage.xml",
            root / "reports" / "coverage.xml",
            root / "cov" / "coverage.xml",
            root / "test" / "coverage.xml",
            root / "tests" / "coverage.xml"
        ]
        
        for candidate in candidates:
            if candidate.exists():
                logger.info(f"Found coverage file at {candidate}")
                return candidate
        
        # Fallback to broader search if not found in common locations
        logger.debug("Coverage file not found in common locations, performing broader search")
        for path in root.glob("**/coverage.xml"):
            logger.info(f"Found coverage file at {path}")
            return path
        
        logger.warning("No coverage file found in repository")
        return None
    
    @staticmethod
    def match_coverage_path(file_path: str, coverage_paths: List[str]) -> Optional[str]:
        """Match a file path against coverage paths using multiple strategies.
        
        Args:
            file_path: The file path to match
            coverage_paths: The list of coverage paths to match against
            
        Returns:
            Optional[str]: The matched coverage path if found, None otherwise
        """
        # Strategy 1: Direct match
        if file_path in coverage_paths:
            logger.debug(f"Direct match for {file_path}")
            return file_path
        
        # Strategy 2: Normalized match
        norm_file_path = PathResolver.normalize_path(file_path)
        for cov_path in coverage_paths:
            norm_cov_path = PathResolver.normalize_path(cov_path)
            if norm_cov_path == norm_file_path:
                logger.debug(f"Normalized match: {cov_path} == {file_path}")
                return cov_path
        
        # Strategy 3: Suffix match
        for cov_path in coverage_paths:
            norm_cov_path = PathResolver.normalize_path(cov_path)
            if norm_file_path.endswith(norm_cov_path) or norm_cov_path.endswith(norm_file_path):
                logger.debug(f"Suffix match: {cov_path} with {file_path}")
                return cov_path
        
        # Strategy 4: Basename match
        basename = os.path.basename(file_path)
        for cov_path in coverage_paths:
            if os.path.basename(cov_path) == basename:
                logger.debug(f"Basename match: {cov_path} with {file_path}")
                return cov_path
        
        logger.debug(f"No match found for {file_path}")
        return None 