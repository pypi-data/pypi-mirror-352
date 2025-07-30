"""
Main entry point for the Vaahai CLI application.

This module initializes the Typer application and registers all commands.
"""

import typer
from rich.console import Console
from typing import Optional
import sys
from pathlib import Path
from typing import List
import asyncio
import json
import os
import subprocess

from vaahai import __version__
from vaahai.cli.commands import review, analyze, config, explain, document, helloworld

# Create console for rich output
console = Console()

# Create the main Typer application
app = typer.Typer(
    name="vaahai",
    help="AI-augmented code review CLI tool",
    add_completion=False,
)

def version_callback(value: bool) -> None:
    """Print the version and exit."""
    if value:
        console.print(f"[bold]Vaahai[/bold] version: [bold green]{__version__}[/bold green]")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """
    Vaahai: AI-augmented code review CLI tool.
    
    Combines static analysis with LLM capabilities to provide comprehensive
    code reviews, suggestions, and automated fixes.
    """
    pass

# Register commands
# Replace the review Typer app with a direct command
@app.command(name="review", help="Review code with AI assistance")
def review_command(
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
):
    """Review code with AI assistance."""
    # Call the review function from the review module
    review.review(
        path=path,
        depth=depth,
        focus=focus,
        output=output,
        output_file=output_file,
        interactive=interactive,
        include=include,
        exclude=exclude,
        config=config,
        save_history=save_history,
        private=private,
        max_file_size=max_file_size,
    )

# Register other command apps
app.add_typer(analyze.app, name="analyze", help="Run static analysis on code")
app.add_typer(config.app, name="config", help="Manage configuration")
app.add_typer(explain.app, name="explain", help="Generate code explanations")
app.add_typer(document.app, name="document", help="Generate code documentation")
app.add_typer(helloworld.app, name="helloworld", help="Run a simple Hello World agent")

def find_standalone_script():
    """Find the standalone detect-language script in various possible locations."""
    possible_locations = [
        # Local development environment
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "vaahai-detect-language-script"),
        # System-wide installation
        "/usr/local/bin/vaahai-detect-language-script",
        # User local installation
        os.path.expanduser("~/.local/bin/vaahai-detect-language-script"),
        # Project local installation
        os.path.join(os.getcwd(), "local", "bin", "vaahai-detect-language-script"),
        # Current directory (for testing)
        os.path.join(os.getcwd(), "vaahai-detect-language-script"),
    ]
    
    for location in possible_locations:
        if os.path.isfile(location) and os.access(location, os.X_OK):
            return location
    
    return None

if __name__ == "__main__":
    try:
        # Special handling for detect-language command to bypass Typer CLI issues
        if len(sys.argv) > 1 and sys.argv[1] == "detect-language":
            # Find the standalone script
            script_path = find_standalone_script()
            
            if not script_path:
                console.print("[bold red]Error: Standalone detect-language script not found.[/bold red]")
                console.print("[bold yellow]To install the standalone script, run:[/bold yellow]")
                console.print("  ./bin/install-detect-language.sh --local")
                console.print("  export PATH=\"$PWD/local/bin:$PATH\"")
                sys.exit(1)
            
            # Pass all arguments to the standalone script
            cmd = [script_path] + sys.argv[2:]
            
            try:
                # Run the standalone script with the original arguments
                result = subprocess.run(cmd, check=True)
                sys.exit(result.returncode)
            except subprocess.CalledProcessError as e:
                sys.exit(e.returncode)
            except Exception as e:
                console.print(f"[bold red]Error: {str(e)}[/bold red]")
                sys.exit(1)
        else:
            # Normal Typer CLI handling for other commands
            app()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
