"""
Review command for Vaahai CLI.

This module implements the 'review' command, which performs code reviews with AI assistance.
"""

from pathlib import Path
from typing import List, Optional
import os

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from vaahai.core.config import config_manager, ReviewDepth, ReviewFocus, OutputFormat
from vaahai.cli.utils import resolve_path, scan_files
from vaahai.core.scanner import FileInfo

console = Console()

# Create the command app
app = typer.Typer(help="Review code with AI assistance")

@app.command()
def review(
    path: Path = typer.Argument(
        ...,
        help="Path to file or directory to review",
        exists=True,
    ),
    depth: str = typer.Option(
        "standard",
        help="Review depth (quick, standard, thorough)",
    ),
    focus: str = typer.Option(
        "all",
        help="Review focus (all, security, performance, style)",
    ),
    output: str = typer.Option(
        "terminal",
        help="Output format (terminal, markdown, html)",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        help="Output file path",
    ),
    interactive: bool = typer.Option(
        False,
        help="Enable interactive fix application",
    ),
    include: List[str] = typer.Option(
        None,
        help="Patterns to include (can be used multiple times)",
    ),
    exclude: List[str] = typer.Option(
        None,
        help="Patterns to exclude (can be used multiple times)",
    ),
    config: Optional[Path] = typer.Option(
        None,
        help="Path to configuration file",
    ),
    save_history: bool = typer.Option(
        False,
        help="Save review results to history",
    ),
    private: bool = typer.Option(
        False,
        help="Use only local resources",
    ),
    max_file_size: int = typer.Option(
        1024 * 1024,  # 1MB default
        help="Maximum file size in bytes",
    ),
) -> None:
    """
    Review code with AI assistance.
    
    This command analyzes code files using static analysis tools and LLM
    capabilities to provide comprehensive feedback and suggestions for
    improvement.
    """
    # Load config with CLI args
    cli_args = {
        "review.depth": ReviewDepth(depth),
        "review.focus": ReviewFocus(focus),
        "review.output_format": OutputFormat(output),
        "review.interactive": interactive,
        "review.save_history": save_history,
        "review.private": private,
    }
    
    # If config file is specified, use it
    if config and config.exists():
        # In a real implementation, we would load this config file
        console.print(f"Using configuration from: {config}")
    
    # Load configuration with CLI args
    config_manager.load(cli_args)
    
    # Get effective configuration
    review_config = config_manager.config.review
    
    # Resolve path
    resolved_path = resolve_path(path)
    
    console.print(f"Reviewing: [bold]{resolved_path}[/bold]")
    console.print(f"Depth: [bold]{review_config.depth}[/bold]")
    console.print(f"Focus: [bold]{review_config.focus}[/bold]")
    
    with console.status("[bold green]Scanning files...[/bold green]"):
        # Use the new code scanner to scan files
        files = scan_files(
            path=resolved_path,
            include_patterns=include,
            exclude_patterns=exclude,
            max_file_size=max_file_size
        )
    
    # Display results
    if files:
        console.print(f"Found [bold green]{len(files)}[/bold green] files to review")
        
        # Create a table to display file information
        table = Table(box=box.SIMPLE)
        table.add_column("File", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Language", style="yellow")
        
        # Add rows for each file
        for file_info in files:
            size_str = f"{file_info.size / 1024:.1f} KB" if file_info.size >= 1024 else f"{file_info.size} bytes"
            rel_path = os.path.relpath(file_info.path, str(resolved_path)) if resolved_path.is_dir() else file_info.filename
            table.add_row(
                rel_path,
                size_str,
                file_info.language or "Unknown"
            )
        
        console.print(table)
    else:
        console.print("[bold red]No files found matching the criteria[/bold red]")
    
    # Placeholder for actual implementation
    console.print("[yellow]This is a skeleton implementation. Actual review functionality will be implemented in future tasks.[/yellow]")
