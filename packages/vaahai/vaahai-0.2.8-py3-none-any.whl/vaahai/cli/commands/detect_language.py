"""
Detect Language Command

Command to detect programming languages, versions, and features in code files.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from vaahai.core.agents.factory import AgentFactory

app = typer.Typer(help="Detect programming languages, versions, and features in code files.")
console = Console()


def find_standalone_script():
    """Find the standalone detect-language script in various possible locations."""
    # Check common locations for the standalone script
    possible_locations = [
        # Local development environment
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "bin", "vaahai-detect-language-script"),
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


def display_table_results(result):
    """Display language detection results in a table format."""
    console.print(f"[bold blue]Language Detection Results[/bold blue]")
    console.print(f"Analyzed {result['file_count']} files")
    
    # Display language distribution
    console.print("\n[bold]Project Language Distribution:[/bold]")
    dist_table = Table(show_header=True)
    dist_table.add_column("Language")
    dist_table.add_column("Files")
    dist_table.add_column("Percentage")
    
    for lang, count in result["language_distribution"].items():
        percentage = (count / result["file_count"]) * 100
        dist_table.add_row(
            lang,
            str(count),
            f"{percentage:.1f}%"
        )
    
    console.print(dist_table)
    
    # Display file analysis results
    console.print("\n[bold]File Analysis:[/bold]")
    file_table = Table(show_header=True)
    file_table.add_column("File")
    file_table.add_column("Language")
    file_table.add_column("Confidence")
    file_table.add_column("Version")
    file_table.add_column("Frameworks")
    
    for file_path, analysis in result["file_analyses"].items():
        frameworks = ", ".join([f["name"] for f in analysis.get("frameworks", [])])
        version = analysis.get("version", {}).get("detected", "unknown")
        confidence = analysis.get("confidence", 0)
        confidence_str = f"{confidence * 100:.1f}%" if isinstance(confidence, float) else str(confidence)
        
        file_table.add_row(
            str(file_path),
            analysis.get("language", "unknown"),
            confidence_str,
            version,
            frameworks
        )
    
    console.print(file_table)


def display_markdown_results(result):
    """Display language detection results in markdown format."""
    md_output = "# Language Detection Results\n\n"
    md_output += f"Analyzed {result['file_count']} files\n\n"
    
    # Language distribution
    md_output += "## Project Language Distribution\n\n"
    md_output += "| Language | Files | Percentage |\n"
    md_output += "|----------|-------|------------|\n"
    
    for lang, count in result["language_distribution"].items():
        percentage = (count / result["file_count"]) * 100
        md_output += f"| {lang} | {count} | {percentage:.1f}% |\n"
    
    md_output += "\n## File Analysis\n\n"
    md_output += "| File | Language | Confidence | Version | Frameworks |\n"
    md_output += "|------|----------|------------|---------|------------|\n"
    
    for file_path, analysis in result["file_analyses"].items():
        frameworks = ", ".join([f["name"] for f in analysis.get("frameworks", [])])
        version = analysis.get("version", {}).get("detected", "unknown")
        confidence = analysis.get("confidence", 0)
        confidence_str = f"{confidence * 100:.1f}%" if isinstance(confidence, float) else str(confidence)
        
        md_output += f"| {file_path} | {analysis.get('language', 'unknown')} | {confidence_str} | {version} | {frameworks} |\n"
    
    console.print(md_output)


@app.callback(invoke_without_command=True)
def main(
    path: Optional[List[str]] = typer.Option(
        None, "--path", "-p", help="Paths to files or directories to analyze"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, markdown)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="OpenAI API key for LLM analysis (overrides global config)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Model to use for LLM analysis (overrides global config)"
    ),
    temperature: Optional[float] = typer.Option(
        None, "--temperature", help="Temperature for model generation (overrides global config)"
    ),
    no_llm: bool = typer.Option(
        False, "--no-llm", help="Disable LLM-based analysis, use only heuristic detection"
    ),
    save_config: bool = typer.Option(
        False, "--save-config", "-s", help="Save provided parameters to global configuration"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Enable debug mode with detailed error tracebacks"
    ),
):
    """
    Detect programming languages, versions, and features in code files.
    
    This command analyzes code files to identify programming languages, versions,
    and frameworks used. It can analyze a single file or an entire directory.
    """
    if not path:
        return
    
    # Try to find and use the standalone script first
    script_path = find_standalone_script()
    if script_path:
        # Build command arguments
        cmd = [script_path]
        
        # Add paths
        for p in path:
            cmd.append(p)
        
        # Add options
        if output_format and output_format != "table":
            cmd.extend(["--format", output_format])
        
        if api_key:
            cmd.extend(["--api-key", api_key])
        
        if model:
            cmd.extend(["--model", model])
        
        if temperature is not None:
            cmd.extend(["--temperature", str(temperature)])
        
        if no_llm:
            cmd.append("--no-llm")
        
        if save_config:
            cmd.append("--save-config")
            
        if debug:
            cmd.append("--debug")
        
        # Run the standalone script
        try:
            result = subprocess.run(cmd, check=True)
            return result.returncode
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Error running standalone detect-language script: {e}[/bold red]")
            return e.returncode
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            if debug:
                import traceback
                console.print(traceback.format_exc())
            return 1
    
    # Fallback to integrated implementation if standalone script not found
    console.print("[bold yellow]Warning: Standalone detect-language script not found.[/bold yellow]")
    console.print("[bold yellow]Using integrated implementation (may have Typer CLI issues).[/bold yellow]")
    console.print("[bold yellow]To install the standalone script, run:[/bold yellow]")
    console.print("  ./bin/install-detect-language.sh --local")
    
    try:
        # Process file paths
        file_paths = []
        file_contents = []
        
        for path_item in path:
            file_path = Path(path_item)
            if file_path.is_dir():
                # Process all files in directory
                for item in file_path.glob("**/*"):
                    if item.is_file() and not item.name.startswith("."):
                        try:
                            content = item.read_text(errors="replace")
                            file_paths.append(str(item))
                            file_contents.append(content)
                        except Exception as e:
                            console.print(f"[bold yellow]Warning: Could not read {item}: {str(e)}[/bold yellow]")
            else:
                # Process single file
                try:
                    content = file_path.read_text(errors="replace")
                    file_paths.append(str(file_path))
                    file_contents.append(content)
                except Exception as e:
                    console.print(f"[bold red]Error: Could not read {file_path}: {str(e)}[/bold red]")
                    return 1
        
        if not file_paths:
            console.print("[bold yellow]No valid files found to analyze.[/bold yellow]")
            return 1
        
        # Create configuration
        config = {}
        if api_key:
            config["api_key"] = api_key
        if model:
            config["model"] = model
        if temperature is not None:
            config["temperature"] = temperature
        
        # Create and run the agent
        agent = AgentFactory.create_agent("language_detector", config)
        result = asyncio.run(agent.run(file_paths, file_contents, use_llm=not no_llm))
        
        # Display results based on output format
        if output_format == "json":
            console.print(json.dumps(result, indent=2))
        elif output_format == "markdown":
            display_markdown_results(result)
        else:  # Default to table
            display_table_results(result)
        
        return 0
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        if debug:
            import traceback
            console.print(traceback.format_exc())
        return 1
