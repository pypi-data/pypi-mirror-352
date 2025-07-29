"""
Main entry point for the Vaahai CLI application.

This module initializes the Typer application and registers all commands.
"""

import typer
from rich.console import Console
from typing import Optional
import sys

from vaahai import __version__
from vaahai.cli.commands import review, analyze, config, explain, document

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
app.add_typer(review.app, name="review", help="Review code with AI assistance")
app.add_typer(analyze.app, name="analyze", help="Run static analysis on code")
app.add_typer(config.app, name="config", help="Manage configuration")
app.add_typer(explain.app, name="explain", help="Generate code explanations")
app.add_typer(document.app, name="document", help="Generate code documentation")

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
