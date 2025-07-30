"""
Git utilities for TestIndex.

This module provides utilities for working with Git repositories 
and extracting information from them.
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import os

from testindex.core.logging import get_logger
from testindex.core.path_resolution import PathResolver

# Set up logger
logger = get_logger(__name__)


class GitUtilError(Exception):
    """Base exception for git utility operations."""
    pass


class GitManager:
    """Manages git repository operations for diff analysis."""
    
    def __init__(self):
        """Initialize the GitManager."""
        self.repo_root = PathResolver.repo_root()
        self.logger = get_logger("git-manager")
        
    def get_changed_files(self, since: str, until: str = "HEAD") -> List[Path]:
        """Get a list of files changed between two git references.
        
        Args:
            since: The git reference to compare from (e.g., "HEAD~1")
            until: The git reference to compare to (default: "HEAD")
            
        Returns:
            List[Path]: A list of paths to changed files
            
        Raises:
            GitUtilError: If the git command fails
        """
        try:
            self.logger.info(f"Getting changed files from {since} to {until}")
            
            # Handle special case for comparing working tree changes
            command = ["git", "diff", "--name-only", "--diff-filter=ACMR"]
            
            # Different command format depending on if we're comparing to working tree
            if until == "":
                # Compare HEAD to working tree (unstaged and staged changes)
                command.append(since)
            else:
                # Compare two references
                command.append(f"{since}..{until}")
                
            # Run git diff command to get changed files
            result = subprocess.run(
                command,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the output
            changed_files = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
            self.logger.info(f"Found {len(changed_files)} changed files")
            
            return changed_files
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to get changed files: {e}"
            if e.stderr:
                error_msg += f"\nError details: {e.stderr}"
            self.logger.error(error_msg)
            raise GitUtilError(error_msg)
    
    def get_file_diff(self, file_path: Union[str, Path], since: str, until: str = "HEAD") -> Dict[str, List[int]]:
        """Get line-level diff information for a specific file.
        
        Args:
            file_path: Path to the file (repository-relative)
            since: The git reference to compare from
            until: The git reference to compare to (default: "HEAD")
            
        Returns:
            Dict[str, List[int]]: Dictionary with keys 'added', 'modified', 'deleted'
                and values as lists of line numbers
                
        Raises:
            GitUtilError: If the git command fails
        """
        try:
            file_path_str = str(file_path)
            self.logger.info(f"Getting diff for file {file_path_str}")
            
            # Run git diff with unified format and extract line numbers
            result = subprocess.run(
                ["git", "diff", "-U0", f"{since}..{until}", "--", file_path_str],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the diff output to extract line numbers
            diff_lines = result.stdout.splitlines()
            added_lines = []
            modified_lines = []
            deleted_lines = []
            
            current_line = 0
            for line in diff_lines:
                # Look for hunk headers (e.g., @@ -15,7 +15,8 @@)
                if line.startswith("@@"):
                    # Parse hunk header to get line numbers
                    parts = line.split()
                    if len(parts) >= 3:
                        # Parse the target line number (+15,8)
                        target_part = parts[2].lstrip("+")
                        if "," in target_part:
                            start, count = map(int, target_part.split(","))
                        else:
                            start = int(target_part)
                            count = 1
                        
                        current_line = start
                
                # Process added/modified lines
                elif line.startswith("+") and not line.startswith("+++"):
                    if current_line > 0:
                        added_lines.append(current_line)
                        current_line += 1
                
                # Process deleted lines
                elif line.startswith("-") and not line.startswith("---"):
                    deleted_lines.append(current_line)
            
            return {
                "added": added_lines,
                "modified": modified_lines,
                "deleted": deleted_lines
            }
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to get file diff: {e}"
            if e.stderr:
                error_msg += f"\nError details: {e.stderr}"
            self.logger.error(error_msg)
            raise GitUtilError(error_msg)
    
    def is_git_repository(self) -> bool:
        """Check if the current directory is a git repository.
        
        Returns:
            bool: True if the directory is a git repository, False otherwise
        """
        try:
            # Check if .git directory exists
            git_dir = self.repo_root / ".git"
            if git_dir.exists() and git_dir.is_dir():
                return True
            
            # Try git command as fallback
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False


# Create a global memoization cache for expensive git operations
_git_cache = {}

def memoize_repo(func):
    """Decorator to memoize function results based on repo path and args.
    
    This decorator is used to cache expensive git operations
    to improve performance on repeated calls.
    """
    def wrapper(*args, **kwargs):
        # Create a cache key from repo path and function arguments
        repo_path = str(PathResolver.repo_root())
        args_str = str(args) + str(kwargs)
        cache_key = f"{repo_path}:{func.__name__}:{args_str}"
        
        # Check if result is in cache
        if cache_key in _git_cache:
            logger.debug(f"Using cached result for {func.__name__}")
            return _git_cache[cache_key]
        
        # Call function and cache result
        result = func(*args, **kwargs)
        _git_cache[cache_key] = result
        return result
    
    return wrapper 