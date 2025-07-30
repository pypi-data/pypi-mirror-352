"""
Aston AI package.

This module provides aliasing to allow imports like `import aston` 
to work correctly even though the internal structure uses `testindex`.
"""

import importlib
import sys

# Alias the testindex module as aston for future-proof imports
sys.modules["aston"] = importlib.import_module("testindex")

# Re-export key components for cleaner imports
from testindex import __version__

__all__ = ["__version__"] 