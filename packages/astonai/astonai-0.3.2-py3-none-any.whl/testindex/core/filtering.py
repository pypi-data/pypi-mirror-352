"""
Advanced file filtering system for TestIndex.

This module provides comprehensive file filtering capabilities including:
- Glob and regex pattern matching
- .astonignore file support
- Preset filter configurations
- Environment variable support
- Pattern validation and dry-run mode
"""
import os
import re
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from testindex.core.logging import get_logger

logger = get_logger(__name__)


class PatternType(Enum):
    """Types of patterns supported."""
    GLOB = "glob"
    REGEX = "regex"


@dataclass
class FilterPattern:
    """Represents a filter pattern with its type and metadata."""
    pattern: str
    pattern_type: PatternType
    description: Optional[str] = None
    source: Optional[str] = None  # Where the pattern came from (file, preset, etc.)


class FilterPresets:
    """Predefined filter configurations for common use cases."""
    
    PYTHON_ONLY = {
        "name": "python-only",
        "description": "Include only Python source files, exclude tests and common artifacts",
        "include": ["**/*.py"],
        "exclude": [
            "**/test_*.py",
            "**/tests/**",
            "**/*_test.py",
            "**/conftest.py",
            "**/setup.py",
            "**/manage.py"
        ]
    }
    
    NO_TESTS = {
        "name": "no-tests", 
        "description": "Exclude all test files and directories",
        "include": [],
        "exclude": [
            "**/test_*.py",
            "**/tests/**",
            "**/*_test.py",
            "**/conftest.py",
            "**/pytest.ini",
            "**/tox.ini",
            "**/.pytest_cache/**"
        ]
    }
    
    SOURCE_ONLY = {
        "name": "source-only",
        "description": "Include only source code, exclude docs, configs, and build artifacts",
        "include": ["**/*.py", "**/*.js", "**/*.ts", "**/*.java", "**/*.cpp", "**/*.c", "**/*.h"],
        "exclude": [
            "**/docs/**",
            "**/documentation/**",
            "**/*.md",
            "**/*.rst",
            "**/*.txt",
            "**/README*",
            "**/LICENSE*",
            "**/CHANGELOG*",
            "**/*.json",
            "**/*.yaml",
            "**/*.yml",
            "**/*.toml",
            "**/*.ini",
            "**/*.cfg"
        ]
    }
    
    MINIMAL = {
        "name": "minimal",
        "description": "Very restrictive filtering for core functionality only",
        "include": ["src/**/*.py", "lib/**/*.py", "core/**/*.py"],
        "exclude": [
            "**/test*/**",
            "**/*test*",
            "**/example*/**",
            "**/demo*/**",
            "**/sample*/**"
        ]
    }
    
    @classmethod
    def get_preset(cls, name: str) -> Optional[Dict]:
        """Get a preset configuration by name."""
        presets = {
            "python-only": cls.PYTHON_ONLY,
            "no-tests": cls.NO_TESTS,
            "source-only": cls.SOURCE_ONLY,
            "minimal": cls.MINIMAL
        }
        return presets.get(name)
    
    @classmethod
    def list_presets(cls) -> List[Dict]:
        """List all available presets."""
        return [cls.PYTHON_ONLY, cls.NO_TESTS, cls.SOURCE_ONLY, cls.MINIMAL]


class FileFilter:
    """Advanced file filtering with multiple pattern types and configuration sources."""
    
    # Default exclude patterns (same as before but now centralized)
    DEFAULT_EXCLUDES = [
        "venv*/**",
        ".venv*/**", 
        "env/**",
        ".env/**",
        "node_modules/**",
        ".git/**",
        ".svn/**",
        ".hg/**",
        "__pycache__/**",
        "*.pyc",
        ".pytest_cache/**",
        ".coverage/**",
        "htmlcov/**",
        "build/**",
        "dist/**",
        "*.egg-info/**",
        ".tox/**",
        ".mypy_cache/**",
        ".idea/**",
        ".vscode/**",
        "*.min.js",
        "*.bundle.js",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize the file filter.
        
        Args:
            repo_root: Repository root directory
        """
        self.repo_root = Path(repo_root)
        self.include_patterns: List[FilterPattern] = []
        self.exclude_patterns: List[FilterPattern] = []
        self._compiled_regex_cache: Dict[str, re.Pattern] = {}
        
        # Load default excludes
        self._add_default_excludes()
        
        # Load from .astonignore if it exists
        self._load_astonignore()
        
        # Load from environment variables
        self._load_from_environment()
    
    def _add_default_excludes(self):
        """Add default exclude patterns."""
        for pattern in self.DEFAULT_EXCLUDES:
            self.exclude_patterns.append(FilterPattern(
                pattern=pattern,
                pattern_type=PatternType.GLOB,
                description="Default exclude",
                source="default"
            ))
    
    def _load_astonignore(self):
        """Load patterns from .astonignore file."""
        astonignore_file = self.repo_root / ".astonignore"
        if not astonignore_file.exists():
            return
        
        try:
            with open(astonignore_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse pattern type prefix
                pattern_type = PatternType.GLOB
                pattern = line
                
                if line.startswith('regex:'):
                    pattern_type = PatternType.REGEX
                    pattern = line[6:].strip()
                elif line.startswith('glob:'):
                    pattern_type = PatternType.GLOB
                    pattern = line[5:].strip()
                
                # Validate pattern
                if self._validate_pattern(pattern, pattern_type):
                    self.exclude_patterns.append(FilterPattern(
                        pattern=pattern,
                        pattern_type=pattern_type,
                        description=f"From .astonignore line {line_num}",
                        source=".astonignore"
                    ))
                else:
                    logger.warning(f"Invalid pattern in .astonignore line {line_num}: {pattern}")
                    
        except Exception as e:
            logger.warning(f"Error reading .astonignore: {e}")
    
    def _load_from_environment(self):
        """Load patterns from environment variables."""
        # ASTON_INCLUDE_PATTERNS: comma-separated include patterns
        include_env = os.environ.get('ASTON_INCLUDE_PATTERNS')
        if include_env:
            patterns = [p.strip() for p in include_env.split(',') if p.strip()]
            for pattern in patterns:
                if self._validate_pattern(pattern, PatternType.GLOB):
                    self.include_patterns.append(FilterPattern(
                        pattern=pattern,
                        pattern_type=PatternType.GLOB,
                        description="From ASTON_INCLUDE_PATTERNS",
                        source="environment"
                    ))
        
        # ASTON_EXCLUDE_PATTERNS: comma-separated exclude patterns
        exclude_env = os.environ.get('ASTON_EXCLUDE_PATTERNS')
        if exclude_env:
            patterns = [p.strip() for p in exclude_env.split(',') if p.strip()]
            for pattern in patterns:
                if self._validate_pattern(pattern, PatternType.GLOB):
                    self.exclude_patterns.append(FilterPattern(
                        pattern=pattern,
                        pattern_type=PatternType.GLOB,
                        description="From ASTON_EXCLUDE_PATTERNS",
                        source="environment"
                    ))
    
    def add_include_patterns(self, patterns: List[str], pattern_type: PatternType = PatternType.GLOB, source: str = "manual"):
        """Add include patterns.
        
        Args:
            patterns: List of pattern strings
            pattern_type: Type of patterns (glob or regex)
            source: Source description for the patterns
        """
        for pattern in patterns:
            if self._validate_pattern(pattern, pattern_type):
                self.include_patterns.append(FilterPattern(
                    pattern=pattern,
                    pattern_type=pattern_type,
                    description=f"Manual {pattern_type.value} pattern",
                    source=source
                ))
            else:
                logger.warning(f"Invalid {pattern_type.value} pattern: {pattern}")
    
    def add_exclude_patterns(self, patterns: List[str], pattern_type: PatternType = PatternType.GLOB, source: str = "manual"):
        """Add exclude patterns.
        
        Args:
            patterns: List of pattern strings
            pattern_type: Type of patterns (glob or regex)
            source: Source description for the patterns
        """
        for pattern in patterns:
            if self._validate_pattern(pattern, pattern_type):
                self.exclude_patterns.append(FilterPattern(
                    pattern=pattern,
                    pattern_type=pattern_type,
                    description=f"Manual {pattern_type.value} pattern",
                    source=source
                ))
            else:
                logger.warning(f"Invalid {pattern_type.value} pattern: {pattern}")
    
    def apply_preset(self, preset_name: str):
        """Apply a preset configuration.
        
        Args:
            preset_name: Name of the preset to apply
        """
        preset = FilterPresets.get_preset(preset_name)
        if not preset:
            available = [p["name"] for p in FilterPresets.list_presets()]
            raise ValueError(f"Unknown preset '{preset_name}'. Available presets: {available}")
        
        # Add preset patterns
        if preset.get("include"):
            self.add_include_patterns(preset["include"], source=f"preset:{preset_name}")
        
        if preset.get("exclude"):
            self.add_exclude_patterns(preset["exclude"], source=f"preset:{preset_name}")
        
        logger.info(f"Applied preset '{preset_name}': {preset['description']}")
    
    def should_process_file(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Determine if a file should be processed.
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Tuple of (should_process, reason)
        """
        # Convert to relative path for pattern matching
        try:
            relative_path = file_path.relative_to(self.repo_root)
            relative_path_str = str(relative_path)
        except ValueError:
            return False, "File is not under repository root"
        
        # Check exclude patterns first
        for pattern in self.exclude_patterns:
            if self._match_pattern(relative_path_str, pattern):
                return False, f"Excluded by {pattern.source}: {pattern.pattern}"
        
        # If no include patterns, include all files that passed exclude filters
        if not self.include_patterns:
            return True, "No include patterns specified"
        
        # Check include patterns
        for pattern in self.include_patterns:
            if self._match_pattern(relative_path_str, pattern):
                return True, f"Included by {pattern.source}: {pattern.pattern}"
        
        return False, "No include pattern matched"
    
    def discover_files(self, file_extensions: Optional[List[str]] = None) -> List[Path]:
        """Discover files in the repository with filtering.
        
        Args:
            file_extensions: List of file extensions to include (e.g., ['.py', '.js'])
            
        Returns:
            List of file paths to process
        """
        files = []
        total_found = 0
        
        # Default to Python files if no extensions specified
        if file_extensions is None:
            file_extensions = ['.py']
        
        # Find all files with specified extensions
        for ext in file_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    total_found += 1
                    should_process, reason = self.should_process_file(file_path)
                    if should_process:
                        files.append(file_path)
        
        logger.info(f"Discovered {len(files)} files to process (filtered from {total_found} total)")
        return files
    
    def dry_run(self, file_extensions: Optional[List[str]] = None, limit: int = 100) -> Dict[str, List[Dict]]:
        """Perform a dry run to show which files would be processed.
        
        Args:
            file_extensions: List of file extensions to check
            limit: Maximum number of files to show in each category
            
        Returns:
            Dictionary with 'included', 'excluded', and 'summary' keys
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        included = []
        excluded = []
        total_found = 0
        
        # Find all files with specified extensions
        for ext in file_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    total_found += 1
                    relative_path = file_path.relative_to(self.repo_root)
                    should_process, reason = self.should_process_file(file_path)
                    
                    file_info = {
                        "path": str(relative_path),
                        "reason": reason
                    }
                    
                    if should_process:
                        if len(included) < limit:
                            included.append(file_info)
                    else:
                        if len(excluded) < limit:
                            excluded.append(file_info)
        
        return {
            "included": included,
            "excluded": excluded,
            "summary": {
                "total_found": total_found,
                "total_included": len([f for f in self._get_all_files(file_extensions) if self.should_process_file(f)[0]]),
                "total_excluded": total_found - len([f for f in self._get_all_files(file_extensions) if self.should_process_file(f)[0]]),
                "showing_included": len(included),
                "showing_excluded": len(excluded)
            }
        }
    
    def get_pattern_summary(self) -> Dict[str, List[Dict]]:
        """Get a summary of all active patterns.
        
        Returns:
            Dictionary with pattern information
        """
        include_summary = []
        for pattern in self.include_patterns:
            include_summary.append({
                "pattern": pattern.pattern,
                "type": pattern.pattern_type.value,
                "source": pattern.source,
                "description": pattern.description
            })
        
        exclude_summary = []
        for pattern in self.exclude_patterns:
            exclude_summary.append({
                "pattern": pattern.pattern,
                "type": pattern.pattern_type.value,
                "source": pattern.source,
                "description": pattern.description
            })
        
        return {
            "include_patterns": include_summary,
            "exclude_patterns": exclude_summary
        }
    
    def _get_all_files(self, file_extensions: List[str]) -> List[Path]:
        """Get all files with specified extensions (for dry run calculations)."""
        files = []
        for ext in file_extensions:
            pattern = f"**/*{ext}"
            for file_path in self.repo_root.glob(pattern):
                if file_path.is_file():
                    files.append(file_path)
        return files
    
    def _match_pattern(self, file_path: str, pattern: FilterPattern) -> bool:
        """Check if a file path matches a pattern.
        
        Args:
            file_path: Relative file path to check
            pattern: Pattern to match against
            
        Returns:
            True if the pattern matches
        """
        if pattern.pattern_type == PatternType.GLOB:
            return fnmatch.fnmatch(file_path, pattern.pattern)
        elif pattern.pattern_type == PatternType.REGEX:
            regex = self._get_compiled_regex(pattern.pattern)
            return bool(regex.search(file_path))
        
        return False
    
    def _get_compiled_regex(self, pattern: str) -> re.Pattern:
        """Get a compiled regex pattern, using cache.
        
        Args:
            pattern: Regex pattern string
            
        Returns:
            Compiled regex pattern
        """
        if pattern not in self._compiled_regex_cache:
            try:
                self._compiled_regex_cache[pattern] = re.compile(pattern)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                # Return a pattern that never matches
                self._compiled_regex_cache[pattern] = re.compile(r'(?!.*)')
        
        return self._compiled_regex_cache[pattern]
    
    def _validate_pattern(self, pattern: str, pattern_type: PatternType) -> bool:
        """Validate a pattern.
        
        Args:
            pattern: Pattern string to validate
            pattern_type: Type of pattern
            
        Returns:
            True if the pattern is valid
        """
        if not pattern or not pattern.strip():
            return False
        
        if pattern_type == PatternType.REGEX:
            try:
                re.compile(pattern)
                return True
            except re.error:
                return False
        elif pattern_type == PatternType.GLOB:
            # Basic validation for glob patterns
            try:
                # Test the pattern with fnmatch
                fnmatch.fnmatch("test", pattern)
                return True
            except Exception:
                return False
        
        return False


def create_astonignore_template(repo_root: Path) -> None:
    """Create a template .astonignore file.
    
    Args:
        repo_root: Repository root directory
    """
    astonignore_file = repo_root / ".astonignore"
    
    if astonignore_file.exists():
        logger.info(f".astonignore already exists at {astonignore_file}")
        return
    
    template_content = """# Aston AI ignore patterns
# Lines starting with # are comments
# Patterns can be glob (default) or regex (prefix with 'regex:')
# Examples:
#   tests/**           # Exclude all files in tests directory
#   **/test_*.py       # Exclude test files
#   regex:.*\\.tmp$    # Exclude .tmp files using regex

# Additional test exclusions
**/pytest.ini
**/tox.ini
**/conftest.py

# Documentation
docs/**
documentation/**
*.md
*.rst

# Configuration files
*.json
*.yaml
*.yml
*.toml
*.ini
*.cfg

# Temporary files
*.tmp
*.temp
*.bak
*.swp
*~

# IDE files
.vscode/**
.idea/**
*.sublime-*

# OS files
.DS_Store
Thumbs.db
"""
    
    try:
        with open(astonignore_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        logger.info(f"Created .astonignore template at {astonignore_file}")
    except Exception as e:
        logger.error(f"Failed to create .astonignore template: {e}") 