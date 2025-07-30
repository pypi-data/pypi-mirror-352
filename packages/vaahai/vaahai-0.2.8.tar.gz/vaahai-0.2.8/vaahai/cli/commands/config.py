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
from vaahai.core.config.models import CURRENT_SCHEMA_VERSION
import tomli_w
import os

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
        # Handle special values
        if value.lower() in ("none", "null", ""):
            value = None
        # Handle enum values
        elif key.endswith(".depth"):
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
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-n",
        help="Use default values without prompting",
    ),
    skip_api_key: bool = typer.Option(
        False,
        "--skip-api-key",
        help="Skip API key input in interactive mode",
    ),
    api_key: str = typer.Option(
        None,
        "--api-key",
        help="Set OpenAI API key (will be stored in config file)",
    ),
    llm_model: str = typer.Option(
        None,
        "--llm-model",
        help="Set default LLM model",
    ),
    llm_temperature: float = typer.Option(
        None,
        "--llm-temperature",
        help="Set LLM temperature (0.0-1.0)",
    ),
    autogen_enabled: bool = typer.Option(
        None,
        "--autogen-enabled/--no-autogen-enabled",
        help="Enable or disable Autogen",
    ),
    autogen_model: str = typer.Option(
        None,
        "--autogen-model",
        help="Set default Autogen model",
    ),
    autogen_temperature: float = typer.Option(
        None,
        "--autogen-temperature",
        help="Set Autogen temperature (0.0-1.0)",
    ),
    use_docker: bool = typer.Option(
        None,
        "--use-docker/--no-use-docker",
        help="Enable or disable Docker for Autogen",
    ),
) -> None:
    """
    Initialize configuration file.
    
    Creates a configuration file with default or user-provided values.
    In interactive mode, prompts for key configuration values.
    
    Configuration can be set via command-line arguments, interactive prompts,
    or using default values with --non-interactive.
    """
    console.print("[bold]Initializing configuration file[/bold]")
    
    if force:
        console.print("[bold yellow]Force flag set, will overwrite existing configuration.[/bold yellow]")
    
    # Check if file exists first
    config_path = Path(os.getcwd()) / ".vaahai.toml"
    if config_path.exists() and not force:
        console.print("[bold red]Configuration file already exists[/bold red]")
        console.print("Use [bold]--force[/bold] flag to overwrite")
        raise typer.Exit(1)
    
    # Check if we should run in interactive mode
    interactive = not non_interactive
    
    # Default configuration values
    config = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.7,
        },
        "autogen": {
            "enabled": True,
            "default_model": "gpt-3.5-turbo",
            "temperature": 0,
            "use_docker": False,
        },
        "review": {
            "depth": "standard",
            "focus": "all",
            "output_format": "terminal",
        },
    }
    
    # Apply command-line arguments if provided
    if api_key is not None:
        config["llm"]["api_key"] = api_key
        interactive = False  # Skip interactive mode if explicit values are provided
    
    if llm_model is not None:
        config["llm"]["model"] = llm_model
        interactive = False
    
    if llm_temperature is not None:
        config["llm"]["temperature"] = llm_temperature
        interactive = False
    
    if autogen_enabled is not None:
        config["autogen"]["enabled"] = autogen_enabled
        interactive = False
    
    if autogen_model is not None:
        config["autogen"]["default_model"] = autogen_model
        interactive = False
    
    if autogen_temperature is not None:
        config["autogen"]["temperature"] = autogen_temperature
        interactive = False
    
    if use_docker is not None:
        config["autogen"]["use_docker"] = use_docker
        interactive = False
    
    # Check for API key in environment variable
    env_api_key = os.environ.get("OPENAI_API_KEY")
    if env_api_key and "api_key" not in config["llm"]:
        config["llm"]["api_key"] = env_api_key
        console.print("[green]Using API key from OPENAI_API_KEY environment variable.[/green]")
    
    if interactive:
        console.print("\n[bold]Interactive Configuration Setup[/bold]")
        console.print("Please provide values for the following configuration settings:")
        console.print("(Press Enter to accept default values shown in brackets)\n")
        
        # LLM Configuration
        console.print("[bold]LLM Configuration[/bold]")
        
        # API Key input - only if not skipped
        if not skip_api_key:
            # Check for environment variable first
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                console.print("[yellow]Note: For security, consider setting the OPENAI_API_KEY environment variable instead.[/yellow]")
                console.print("[yellow]You can also set it later with: vaahai config set llm.api_key YOUR_API_KEY --global[/yellow]\n")
                
                # Use regular visible input with a warning
                try:
                    api_key = typer.prompt(
                        "OpenAI API Key (will be visible)",
                        default="",
                        show_default=False
                    )
                except (KeyboardInterrupt, EOFError):
                    console.print("\n[bold yellow]API key input skipped.[/bold yellow]")
                    api_key = ""
            
            if api_key:
                config["llm"]["api_key"] = api_key
                console.print("[green]API key set successfully.[/green]")
            else:
                console.print("[yellow]No API key provided. You can set it later with:[/yellow]")
                console.print("[yellow]vaahai config set llm.api_key YOUR_API_KEY --global[/yellow]")
        
        # LLM Model
        try:
            llm_model = typer.prompt(
                "Default LLM Model", 
                default=config["llm"]["model"]
            )
            config["llm"]["model"] = llm_model
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Using default LLM model.[/bold yellow]")
        
        # LLM Temperature
        try:
            llm_temp = typer.prompt(
                "LLM Temperature (0.0-1.0)", 
                default=str(config["llm"]["temperature"])
            )
            try:
                config["llm"]["temperature"] = float(llm_temp)
            except ValueError:
                console.print("[bold yellow]Invalid temperature value, using default.[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Using default LLM temperature.[/bold yellow]")
        
        # Autogen Configuration
        console.print("\n[bold]Autogen Configuration[/bold]")
        
        # Enable Autogen
        try:
            autogen_enabled = typer.prompt(
                "Enable Autogen", 
                default="Yes" if config["autogen"]["enabled"] else "No"
            )
            config["autogen"]["enabled"] = autogen_enabled.lower() in ("yes", "y", "true", "1")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Using default Autogen setting.[/bold yellow]")
        
        if config["autogen"]["enabled"]:
            # Autogen Model
            try:
                autogen_model = typer.prompt(
                    "Autogen Default Model", 
                    default=config["autogen"]["default_model"]
                )
                config["autogen"]["default_model"] = autogen_model
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Using default Autogen model.[/bold yellow]")
            
            # Autogen Temperature
            try:
                autogen_temp = typer.prompt(
                    "Autogen Temperature (0.0-1.0)", 
                    default=str(config["autogen"]["temperature"])
                )
                try:
                    config["autogen"]["temperature"] = float(autogen_temp)
                except ValueError:
                    console.print("[bold yellow]Invalid temperature value, using default.[/bold yellow]")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Using default Autogen temperature.[/bold yellow]")
            
            # Use Docker
            try:
                use_docker = typer.prompt(
                    "Use Docker for Autogen", 
                    default="Yes" if config["autogen"]["use_docker"] else "No"
                )
                config["autogen"]["use_docker"] = use_docker.lower() in ("yes", "y", "true", "1")
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold yellow]Using default Docker setting.[/bold yellow]")
    
    # Clean up None values before writing to TOML
    def clean_config(config_dict):
        result = {}
        for k, v in config_dict.items():
            if isinstance(v, dict):
                cleaned = clean_config(v)
                if cleaned:  # Only add non-empty dicts
                    result[k] = cleaned
            elif v is not None:
                result[k] = v
        return result
    
    cleaned_config = clean_config(config)
    
    # Write the configuration file
    try:
        with open(config_path, "wb") as f:
            tomli_w.dump(cleaned_config, f)
        
        console.print("\n[bold green]Configuration file created successfully[/bold green]")
        console.print(f"Created [bold].vaahai.toml[/bold] in the current directory")
        
        # Display configuration summary
        console.print("\n[bold]Configuration Summary:[/bold]")
        table = Table()
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("LLM Provider", config["llm"].get("provider", "openai"))
        table.add_row("LLM Model", config["llm"].get("model", "Not set"))
        table.add_row("API Key", "Set" if config["llm"].get("api_key") else "Not set")
        table.add_row("LLM Temperature", str(config["llm"].get("temperature", "Not set")))
        
        table.add_row("Autogen Enabled", "Yes" if config["autogen"].get("enabled", False) else "No")
        if config["autogen"].get("enabled", False):
            table.add_row("Autogen Model", config["autogen"].get("default_model", "Not set"))
            table.add_row("Autogen Temperature", str(config["autogen"].get("temperature", "Not set")))
            table.add_row("Use Docker", "Yes" if config["autogen"].get("use_docker", False) else "No")
        
        console.print(table)
        
        # Display next steps
        console.print("\n[bold]Next Steps:[/bold]")
        if not config["llm"].get("api_key"):
            console.print("- Set your OpenAI API key: [bold]vaahai config set llm.api_key YOUR_API_KEY --global[/bold]")
        console.print("- Try the Hello World agent: [bold]vaahai helloworld[/bold]")
        console.print("- Edit configuration: [bold]vaahai config set <key> <value> --global[/bold]")
        
        return True
    except Exception as e:
        console.print(f"[bold red]Error creating configuration file: {str(e)}[/bold red]")
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
