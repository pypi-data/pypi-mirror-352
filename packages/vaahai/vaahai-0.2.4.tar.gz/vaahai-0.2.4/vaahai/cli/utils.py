"""
Utility functions for the Vaahai CLI.

This module provides common utilities used across CLI commands.
"""

import os
from pathlib import Path
from typing import List, Set, Optional, Union

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from vaahai.core.scanner import code_scanner, FileInfo
from vaahai.core.scanner.filters import LanguageFilter, PatternFilter, CompositeFilter

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
    # Reset the scanner to default settings
    code_scanner.reset()
    
    # Configure the scanner
    if supported_extensions:
        code_scanner.set_include_extensions(list(supported_extensions))
    
    if include_patterns:
        code_scanner.set_include_patterns(include_patterns)
    
    if exclude_patterns:
        code_scanner.set_exclude_patterns(exclude_patterns)
    
    # Scan the path
    file_infos = code_scanner.scan_path(str(path))
    
    # Convert FileInfo objects to Path objects for backward compatibility
    return [Path(file_info.path) for file_info in file_infos]

def file_infos_to_paths(file_infos: List[FileInfo]) -> List[Path]:
    """
    Convert a list of FileInfo objects to Path objects.
    
    Args:
        file_infos: List of FileInfo objects
        
    Returns:
        List of Path objects
    """
    return [Path(file_info.path) for file_info in file_infos]

def scan_files(
    path: Union[str, Path],
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
    supported_extensions: Optional[List[str]] = None,
    max_file_size: int = 1024 * 1024,  # 1MB default
    load_content: bool = False
) -> List[FileInfo]:
    """
    Scan files using the code scanner.
    
    Args:
        path: Path to file or directory
        include_patterns: List of glob patterns to include
        exclude_patterns: List of glob patterns to exclude
        supported_extensions: List of supported file extensions
        max_file_size: Maximum file size in bytes
        load_content: Whether to load file content
        
    Returns:
        List of FileInfo objects
    """
    # Reset the scanner to default settings
    code_scanner.reset()
    
    # Convert path to string if it's a Path object
    path_str = str(path)
    
    # Configure the scanner
    if supported_extensions:
        code_scanner.set_include_extensions(supported_extensions)
    
    if include_patterns:
        code_scanner.set_include_patterns(include_patterns)
    
    if exclude_patterns:
        code_scanner.set_exclude_patterns(exclude_patterns)
    
    code_scanner.set_max_file_size(max_file_size)
    
    # Scan the path
    try:
        if load_content:
            return code_scanner.scan_and_load_content([path_str])
        else:
            return code_scanner.scan_path(path_str)
    except Exception as e:
        console.print(f"[bold red]Error scanning path:[/bold red] {e}")
        return []

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
