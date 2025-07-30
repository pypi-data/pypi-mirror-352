"""Coverage models for test-to-implementation mapping.

This module defines the data structures for representing test coverage.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime


@dataclass
class CoverageModel:
    """Model for function/method coverage.

    Represents the coverage status of a specific implementation function or method.
    """

    implementation_id: str
    implementation_name: str
    implementation_path: str
    is_covered: bool = False
    covering_tests: List[Dict[str, str]] = field(default_factory=list)

    def add_test(self, test_id: str, test_name: str, test_path: str) -> None:
        """Add a test that covers this implementation.

        Args:
            test_id: Unique identifier for the test
            test_name: Name of the test function/method
            test_path: File path of the test
        """
        self.covering_tests.append({
            "id": test_id,
            "name": test_name,
            "path": test_path
        })
        self.is_covered = True

    @property
    def test_count(self) -> int:
        """Get the number of tests covering this implementation.

        Returns:
            Number of covering tests
        """
        return len(self.covering_tests)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation of the coverage model
        """
        return {
            "implementation_id": self.implementation_id,
            "implementation_name": self.implementation_name,
            "implementation_path": self.implementation_path,
            "is_covered": self.is_covered,
            "test_count": self.test_count,
            "covering_tests": self.covering_tests
        }


@dataclass
class ModuleCoverageModel:
    """Model for module-level coverage.

    Represents the coverage status of an implementation module.
    """

    module_id: str
    module_path: str
    functions: Dict[str, CoverageModel] = field(default_factory=dict)

    def add_function(self, coverage_model: CoverageModel) -> None:
        """Add a function's coverage information to this module.

        Args:
            coverage_model: Coverage model for a function
        """
        self.functions[coverage_model.implementation_id] = coverage_model

    @property
    def function_count(self) -> int:
        """Get the total number of functions in this module.

        Returns:
            Total function count
        """
        return len(self.functions)

    @property
    def covered_function_count(self) -> int:
        """Get the number of covered functions in this module.

        Returns:
            Number of covered functions
        """
        return sum(1 for func in self.functions.values() if func.is_covered)

    @property
    def coverage_percentage(self) -> float:
        """Get the percentage of functions covered by tests.

        Returns:
            Percentage of functions covered (0-100)
        """
        if self.function_count == 0:
            return 0.0
        return (self.covered_function_count / self.function_count) * 100

    def to_dict(self) -> Dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary representation of the module coverage model
        """
        return {
            "module_id": self.module_id,
            "module_path": self.module_path,
            "function_count": self.function_count,
            "covered_function_count": self.covered_function_count,
            "coverage_percentage": self.coverage_percentage,
            "functions": {func_id: func.to_dict() for func_id, func in self.functions.items()}
        }


@dataclass
class CoverageGap:
    """Model for code coverage gaps.
    
    Represents an implementation with no test coverage (a gap).
    """
    
    implementation_id: str
    path: str
    line_start: int
    line_end: int
    coverage: float
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "v1"
    
    @classmethod
    def from_implementation(cls, implementation: Dict[str, any]) -> 'CoverageGap':
        """Create a CoverageGap from an implementation dictionary.
        
        Args:
            implementation: Dictionary containing implementation data
                Must include: id, path, line_start, line_end, coverage
                
        Returns:
            CoverageGap: New coverage gap object
        """
        return cls(
            implementation_id=implementation['id'],
            path=implementation['path'],
            line_start=implementation['line_start'],
            line_end=implementation['line_end'],
            coverage=implementation['coverage']
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the coverage gap
        """
        return {
            "implementation_id": self.implementation_id,
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "coverage": self.coverage,
            "detected_at": self.detected_at,
            "version": self.version
        }
    
    def to_neo4j_properties(self) -> Dict:
        """Convert to Neo4j node properties.
        
        Returns:
            Dictionary of properties for Neo4j node creation
        """
        return {
            "id": self.implementation_id,
            "path": self.path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "coverage": self.coverage,
            "detected_at": self.detected_at,
            "version": self.version
        } 