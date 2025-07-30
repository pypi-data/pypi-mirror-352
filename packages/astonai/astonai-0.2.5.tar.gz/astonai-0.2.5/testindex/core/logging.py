"""
Structured logging framework for the Test Intelligence Engine.

This module provides utilities for:
- Structured logging with JSON output
- Multiple output destinations (console, file)
- Log levels and filtering
- Context enrichment
- Performance optimizations
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.logging import RichHandler

from testindex.core.exceptions import LoggingError


class LogLevel(str, Enum):
    """Log levels supported by the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output formats supported by the application."""
    TEXT = "text"
    JSON = "json"
    RICH = "rich"


class LogDestination(str, Enum):
    """Log output destinations supported by the application."""
    CONSOLE = "console"
    FILE = "file"
    BOTH = "both"


class StructuredLogger:
    """
    Structured logger for the Test Intelligence Engine.
    
    Provides structured logging with support for JSON output, multiple
    destinations, context enrichment, and various log levels.
    """
    
    def __init__(
        self,
        name: str,
        level: Union[str, LogLevel] = LogLevel.INFO,
        format: Union[str, LogFormat] = LogFormat.TEXT,
        destination: Union[str, LogDestination] = LogDestination.CONSOLE,
        log_file: Optional[Union[str, Path]] = None,
        add_timestamp: bool = True,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new structured logger.
        
        Args:
            name: Logger name
            level: Log level (default: INFO)
            format: Log format (default: TEXT)
            destination: Log destination (default: CONSOLE)
            log_file: Path to log file (required if destination includes FILE)
            add_timestamp: Whether to add timestamps to log messages (default: True)
            context: Global context to include in all log messages (default: None)
            
        Raises:
            LoggingError: If the logger cannot be initialized
        """
        self.name = name
        self.level = level if isinstance(level, LogLevel) else LogLevel(level.upper())
        self.format = format if isinstance(format, LogFormat) else LogFormat(format.lower())
        self.destination = destination if isinstance(destination, LogDestination) else LogDestination(destination.lower())
        self.log_file = Path(log_file) if log_file else None
        self.add_timestamp = add_timestamp
        self.context = context or {}
        
        # Validate log file path if file destination is specified
        if self.destination in (LogDestination.FILE, LogDestination.BOTH) and not self.log_file:
            raise LoggingError(
                "Log file path must be specified when using file destination",
                error_code="E401"
            )
            
        # Ensure log directory exists if file destination is specified
        if self.log_file:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise LoggingError(
                    f"Failed to create log directory: {str(e)}",
                    error_code="E402"
                )
        
        try:
            # Create and configure logger
            self.logger = logging.getLogger(name)
            self.logger.setLevel(getattr(logging, self.level.value))
            self.logger.handlers = []  # Remove any existing handlers
            
            # Add handlers based on destination
            if self.destination in (LogDestination.CONSOLE, LogDestination.BOTH):
                self._add_console_handler()
                
            if self.destination in (LogDestination.FILE, LogDestination.BOTH):
                self._add_file_handler()
                
        except Exception as e:
            raise LoggingError(
                f"Failed to initialize logger: {str(e)}",
                error_code="E400"
            )
    
    def _add_console_handler(self) -> None:
        """Add a console handler to the logger."""
        if self.format == LogFormat.RICH:
            # Use Rich for pretty console output
            console = Console()
            handler = RichHandler(console=console, rich_tracebacks=True)
            formatter = logging.Formatter("%(message)s")
        else:
            # Use standard console handler
            handler = logging.StreamHandler(sys.stdout)
            
            if self.format == LogFormat.JSON:
                formatter = logging.Formatter("%(message)s")
            else:
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _add_file_handler(self) -> None:
        """Add a file handler to the logger."""
        assert self.log_file is not None, "Log file path cannot be None"
        
        handler = logging.FileHandler(str(self.log_file))
        
        if self.format == LogFormat.JSON:
            formatter = logging.Formatter("%(message)s")
        else:
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _log(
        self,
        level: LogLevel,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a message with the specified level and context.
        
        Args:
            level: Log level
            message: Log message
            context: Additional context to include in the log message
        """
        log_level = getattr(logging, level.value)
        
        # Skip if log level is below the configured level
        if not self.logger.isEnabledFor(log_level):
            return
        
        # Combine global and local context
        combined_context = {**self.context}
        if context:
            combined_context.update(context)
            
        # Add timestamp if enabled
        if self.add_timestamp:
            now_utc = datetime.now(timezone.utc)
            combined_context["timestamp"] = now_utc.isoformat()
            
        # Format message based on the configured format
        if self.format == LogFormat.JSON:
            log_data = {
                "message": message,
                "level": level.value,
                "logger": self.name,
                **combined_context
            }
            log_message = json.dumps(log_data)
        else:
            log_message = message
            
        # Log the message
        getattr(self.logger, level.value.lower())(log_message)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message.
        
        Args:
            message: Log message
            context: Additional context to include in the log message
        """
        self._log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an info message.
        
        Args:
            message: Log message
            context: Additional context to include in the log message
        """
        self._log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning message.
        
        Args:
            message: Log message
            context: Additional context to include in the log message
        """
        self._log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: Log message
            context: Additional context to include in the log message
        """
        self._log(LogLevel.ERROR, message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a critical message.
        
        Args:
            message: Log message
            context: Additional context to include in the log message
        """
        self._log(LogLevel.CRITICAL, message, context)
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        Set the global context for all log messages.
        
        Args:
            context: Global context to include in all log messages
        """
        self.context = context
    
    def update_context(self, context: Dict[str, Any]) -> None:
        """
        Update the global context for all log messages.
        
        Args:
            context: Global context to include in all log messages
        """
        self.context.update(context)


# Factory function to create a logger with default settings
def get_logger(
    name: str,
    level: Union[str, LogLevel] = LogLevel.INFO,
    format: Union[str, LogFormat] = LogFormat.TEXT,
    destination: Union[str, LogDestination] = LogDestination.CONSOLE,
    log_file: Optional[Union[str, Path]] = None,
    context: Optional[Dict[str, Any]] = None
) -> StructuredLogger:
    """
    Create a new structured logger with the specified settings.
    
    Args:
        name: Logger name
        level: Log level (default: INFO)
        format: Log format (default: TEXT)
        destination: Log destination (default: CONSOLE)
        log_file: Path to log file (required if destination includes FILE)
        context: Global context to include in all log messages (default: None)
        
    Returns:
        A new structured logger instance
        
    Raises:
        LoggingError: If the logger cannot be initialized
    """
    return StructuredLogger(
        name=name,
        level=level,
        format=format,
        destination=destination,
        log_file=log_file,
        context=context
    )
