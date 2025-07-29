"""
Config command for Vaahai CLI.

This module implements the 'config' command, which manages configuration settings.
"""

from pathlib import Path
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table

from vaahai.core.config import config_manager, ReviewDepth, ReviewFocus, OutputFormat

console = Console()

# Create the command app
app = typer.Typer(help="Manage configuration")

@app.command()
def get(
    key: str = typer.Argument(..., help="Configuration key to get"),
) -> None:
    """
    Get a configuration value.
    
    Retrieves the value for a specific configuration key.
    Keys use dot notation (e.g., 'llm.provider').
    """
    console.print(f"[bold]Getting configuration value for:[/bold] {key}")
    
    value = config_manager.get(key)
    if value is None:
        console.print(f"[bold red]Error:[/bold red] Configuration key '{key}' not found")
        raise typer.Exit(1)
    
    source = config_manager.get_source(key)
    console.print(f"[bold green]{key}[/bold green] = {value} [dim](source: {source})[/dim]")

@app.command()
def set(
    key: str = typer.Argument(..., help="Configuration key to set"),
    value: str = typer.Argument(..., help="Value to set"),
    global_config: bool = typer.Option(
        False, "--global", "-g", help="Save to global user configuration"
    ),
) -> None:
    """
    Set a configuration value.
    
    Sets the value for a specific configuration key.
    Keys use dot notation (e.g., 'llm.provider').
    """
    console.print(f"[bold]Setting configuration:[/bold] {key} = {value}")
    
    try:
        # Handle enum values
        if key.endswith(".depth"):
            value = ReviewDepth(value)
        elif key.endswith(".focus"):
            value = ReviewFocus(value)
        elif key.endswith(".output_format"):
            value = OutputFormat(value)
        elif key.endswith(".interactive") or key.endswith(".save_history") or key.endswith(".private"):
            value = value.lower() in ("true", "yes", "1", "y")
        
        # Set the value and save if global
        config_manager.set(key, value, save=global_config)
        
        if global_config:
            console.print(f"[bold green]Configuration saved to user config file[/bold green]")
        else:
            console.print(f"[bold yellow]Configuration set for current session only[/bold yellow]")
            console.print("Use [bold]--global[/bold] flag to save permanently")
    
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def list() -> None:
    """
    List all configuration values.
    
    Displays all current configuration settings in a table.
    """
    console.print("[bold]Current configuration:[/bold]")
    
    # Create a table for output
    table = Table(show_header=True, header_style="bold")
    table.add_column("Key")
    table.add_column("Value")
    table.add_column("Source")
    
    # Get all config values with sources
    all_config = config_manager.get_all_with_sources()
    
    # Add rows to table
    for key, info in sorted(all_config.items()):
        value = str(info["value"])
        source = info["source"]
        table.add_row(key, value, source)
    
    console.print(table)

@app.command()
def init(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration file",
    ),
) -> None:
    """
    Initialize configuration file.
    
    Creates a default configuration file in the current directory.
    """
    console.print("[bold]Initializing configuration file[/bold]")
    
    if force:
        console.print("[bold yellow]Force flag set, will overwrite existing configuration.[/bold yellow]")
    
    success = config_manager.init_project_config(force=force)
    
    if success:
        console.print("[bold green]Configuration file created successfully[/bold green]")
        console.print(f"Created [bold].vaahai.toml[/bold] in the current directory")
    else:
        console.print("[bold red]Configuration file already exists[/bold red]")
        console.print("Use [bold]--force[/bold] flag to overwrite")
        raise typer.Exit(1)

@app.command()
def validate() -> None:
    """
    Validate configuration.
    
    Checks if the current configuration is valid according to the schema.
    Reports any validation errors found.
    """
    console.print("[bold]Validating configuration...[/bold]")
    
    # Load configuration if not already loaded
    if not hasattr(config_manager, "_loaded") or not config_manager._loaded:
        config_manager.load()
    
    # Validate the configuration
    errors = config_manager.validate_config()
    
    if not errors:
        console.print("[bold green]Configuration is valid![/bold green]")
    else:
        console.print("[bold red]Configuration validation failed with the following errors:[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)
