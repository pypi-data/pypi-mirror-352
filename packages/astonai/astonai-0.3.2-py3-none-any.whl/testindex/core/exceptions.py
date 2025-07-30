"""
Exception handling framework for the Test Intelligence Engine.

This module defines a hierarchy of custom exceptions used throughout the application.
Each exception type includes an error code and standardized message format to
provide consistent error reporting and handling.
"""
from typing import Any, Dict, Optional


# Top-level base exception for the entire Test Intelligence system
class AstonError(Exception):
    """Base exception for all Test Intelligence errors.
    
    Attributes:
        message: Error message
        error_code: Unique error code (e.g., E001)
        context: Additional context for the error
    """
    error_code: Optional[str] = None
    default_message: str = "An unspecified error occurred in the Test Intelligence system."

    def __init__(self, message: Optional[str] = None, error_code: Optional[str] = None, context: Optional[Dict[str, Any]] = None, details: Optional[Dict[str, Any]] = None):
        # Initialize a new AstonError with backward compatibility for 'details' parameter
        self.message = message or self.default_message
        if error_code: # Allow overriding class-level error_code
            self.error_code = error_code
        # Support both 'context' and 'details' for backward compatibility
        self.context = context or details or {}
        
        # Format message with error code
        msg_prefix = f"[{self.error_code}] " if self.error_code else ""
        super().__init__(f"{msg_prefix}{self.message}")

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}" if self.error_code else self.message


class BaseException(AstonError):
    """Generic base exception for more specific error categories."""
    # This class seems redundant if AstonError is the top-level one.
    # Consider removing or merging if appropriate after reviewing all usages.
    # For now, just update inheritance.
    pass


class ConfigurationError(AstonError):
    """Error related to configuration issues."""
    error_code = "CONFIG001"
    default_message = "Configuration error."


class StorageError(AstonError):
    """Error related to data storage operations."""
    error_code = "STORAGE001"
    default_message = "Storage error."


class CLIError(AstonError):
    """Error related to command-line interface operations."""
    error_code = "CLI001"
    default_message = "CLI error."


class LoggingError(AstonError):
    """Error related to logging operations."""
    error_code = "LOGGING001"
    default_message = "Logging error."


class ValidationError(AstonError):
    """Error related to data validation failures."""
    error_code = "VALIDATE001"
    default_message = "Validation error."
