"""
Progress display utilities for the CLI framework.

This module provides utilities for displaying progress bars and spinners in the CLI.
"""
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Union

from rich.progress import (
    Progress as RichProgress,
    SpinnerColumn,
    BarColumn, 
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


class Progress:
    """
    Progress display for CLI commands.
    
    Wraps Rich's Progress class to provide a simplified interface for
    displaying progress bars and spinners in the CLI.
    """
    
    def __init__(
        self,
        total: Optional[int] = None,
        description: str = "Processing",
        show_spinner: bool = True,
        show_bar: bool = True,
        show_time: bool = True,
        transient: bool = True,
    ):
        """
        Initialize a new Progress display.
        
        Args:
            total: Total number of steps (default: None)
            description: Progress description (default: "Processing")
            show_spinner: Whether to show a spinner (default: True)
            show_bar: Whether to show a progress bar (default: True)
            show_time: Whether to show elapsed and remaining time (default: True)
            transient: Whether to remove the progress bar when complete (default: True)
        """
        self.total = total
        self.description = description
        self.show_spinner = show_spinner
        self.show_bar = show_bar
        self.show_time = show_time
        self.transient = transient
        self.task_id = None
        
        # Configure columns based on options
        columns = []
        
        if show_spinner:
            columns.append(SpinnerColumn())
            
        columns.append(TextColumn("[bold blue]{task.description}"))
        
        if show_bar and total is not None:
            columns.append(BarColumn())
            columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))
            
        if show_time:
            columns.append(TimeElapsedColumn())
            if total is not None:
                columns.append(TimeRemainingColumn())
        
        # Create Rich Progress instance
        self.progress = RichProgress(*columns, transient=transient)
        
    def start(self) -> None:
        """Start the progress display."""
        self.progress.start()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        
    def update(self, advance: Optional[int] = None, total: Optional[int] = None) -> None:
        """
        Update the progress display.
        
        Args:
            advance: Number of steps to advance (default: None)
            total: New total number of steps (default: None)
        """
        if self.task_id is None:
            raise RuntimeError("Progress display not started")
            
        update_kwargs = {}
        
        if advance is not None:
            update_kwargs["advance"] = advance
            
        if total is not None:
            update_kwargs["total"] = total
            
        self.progress.update(self.task_id, **update_kwargs)
        
    def stop(self) -> None:
        """Stop the progress display."""
        if self.progress.live.is_started:
            self.progress.stop()


@contextmanager
def create_progress(
    total: Optional[int] = None,
    description: str = "Processing",
    show_spinner: bool = True,
    show_bar: bool = True,
    show_time: bool = True,
    transient: bool = True,
) -> Iterator[Progress]:
    """
    Create a progress display as a context manager.
    
    Args:
        total: Total number of steps (default: None)
        description: Progress description (default: "Processing")
        show_spinner: Whether to show a spinner (default: True)
        show_bar: Whether to show a progress bar (default: True)
        show_time: Whether to show elapsed and remaining time (default: True)
        transient: Whether to remove the progress bar when complete (default: True)
        
    Yields:
        Progress instance
    """
    progress = Progress(
        total=total,
        description=description,
        show_spinner=show_spinner,
        show_bar=show_bar,
        show_time=show_time,
        transient=transient,
    )
    
    try:
        progress.start()
        yield progress
    finally:
        progress.stop()
