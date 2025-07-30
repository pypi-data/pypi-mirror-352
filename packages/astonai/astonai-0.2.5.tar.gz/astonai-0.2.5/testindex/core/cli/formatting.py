"""
Output formatting utilities for the CLI framework.

This module provides utilities for formatting CLI output in different formats.
"""
import json
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.pretty import Pretty


class OutputFormat(str, Enum):
    """Output formats supported by the CLI framework."""
    TEXT = "text"
    JSON = "json"
    TABLE = "table"


def format_output(
    data: Any,
    format: Union[str, OutputFormat] = OutputFormat.TEXT,
    headers: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Format output data in the specified format.
    
    Args:
        data: Data to format
        format: Output format (default: TEXT)
        headers: Column headers for table output (default: None)
        title: Title for formatted output (default: None)
        
    Returns:
        Formatted output string
        
    Raises:
        ValueError: If the output format is invalid
    """
    format_enum = format if isinstance(format, OutputFormat) else OutputFormat(format.lower())
    
    if format_enum == OutputFormat.JSON:
        return _format_json(data)
    elif format_enum == OutputFormat.TABLE:
        return _format_table(data, headers, title)
    else:  # TEXT format
        return _format_text(data, title)


def _format_json(data: Any) -> str:
    """
    Format data as JSON.
    
    Args:
        data: Data to format
        
    Returns:
        JSON-formatted string
    """
    return json.dumps(data, indent=2, sort_keys=True)


def _format_table(
    data: Union[List[Dict[str, Any]], Dict[str, Any]],
    headers: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Format data as a table.
    
    Args:
        data: Data to format (list of dictionaries or dictionary)
        headers: Column headers (default: None)
        title: Table title (default: None)
        
    Returns:
        Table-formatted string
    """
    console = Console(width=100)
    table = Table(title=title)
    
    # Convert dictionary to list if necessary
    if isinstance(data, dict):
        data = [{"Key": k, "Value": v} for k, v in data.items()]
        headers = headers or ["Key", "Value"]
    
    # Determine headers if not provided
    if not headers and data:
        headers = list(data[0].keys())
    
    # Add columns
    for header in headers or []:
        table.add_column(header)
    
    # Add rows
    for row_data in data:
        row = [str(row_data.get(header, "")) for header in headers or []]
        table.add_row(*row)
    
    # Render table to string
    with console.capture() as capture:
        console.print(table)
    
    return capture.get()


def _format_text(data: Any, title: Optional[str] = None) -> str:
    """
    Format data as plain text.
    
    Args:
        data: Data to format
        title: Text title (default: None)
        
    Returns:
        Text-formatted string
    """
    console = Console(width=100)
    
    # Handle different data types
    if isinstance(data, (dict, list)):
        content = Pretty(data)
    else:
        content = str(data)
    
    # Add title if provided
    if title:
        content = Panel(content, title=title)
    
    # Render to string
    with console.capture() as capture:
        console.print(content)
    
    return capture.get()
