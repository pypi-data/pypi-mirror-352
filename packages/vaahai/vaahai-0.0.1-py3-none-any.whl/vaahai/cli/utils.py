"""
Utility functions for the Vaahai CLI.

This module provides common utilities used across CLI commands.
"""

import os
from pathlib import Path
from typing import List, Set, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def resolve_path(path: Path) -> Path:
    """
    Resolve a path to its absolute form.
    
    Args:
        path: The path to resolve
        
    Returns:
        The absolute path
    """
    return path.absolute()

def is_supported_file(file_path: Path, supported_extensions: Optional[Set[str]] = None) -> bool:
    """
    Check if a file is supported for processing.
    
    Args:
        file_path: Path to the file
        supported_extensions: Set of supported file extensions (e.g., {'.py', '.js'})
                             If None, all files are considered supported
    
    Returns:
        True if the file is supported, False otherwise
    """
    if supported_extensions is None:
        return True
    
    return file_path.suffix.lower() in supported_extensions

def collect_files(
    path: Path, 
    include_patterns: List[str] = None, 
    exclude_patterns: List[str] = None,
    supported_extensions: Optional[Set[str]] = None
) -> List[Path]:
    """
    Collect files for processing based on include/exclude patterns.
    
    Args:
        path: Path to file or directory
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        supported_extensions: Set of supported file extensions
        
    Returns:
        List of file paths to process
    """
    # Placeholder implementation
    # In a real implementation, this would use pathspec or similar to handle glob patterns
    
    result = []
    
    if path.is_file():
        if is_supported_file(path, supported_extensions):
            result.append(path)
    else:  # Directory
        for root, _, files in os.walk(path):
            root_path = Path(root)
            for file in files:
                file_path = root_path / file
                if is_supported_file(file_path, supported_extensions):
                    result.append(file_path)
    
    return result

def create_spinner(text: str) -> Progress:
    """
    Create a spinner with the given text.
    
    Args:
        text: Text to display next to the spinner
        
    Returns:
        Progress object with spinner
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        console=console,
        transient=True,
    )
    progress.add_task(text, total=None)
    return progress
