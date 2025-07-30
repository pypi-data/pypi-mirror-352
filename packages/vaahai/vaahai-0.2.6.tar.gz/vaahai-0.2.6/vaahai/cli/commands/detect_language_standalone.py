#!/usr/bin/env python3
"""
Standalone Language Detector CLI Command

Command to detect programming languages, versions, and features in code files.
This is a standalone version that can be run directly without Typer integration.
"""

import asyncio
import json
import sys
import traceback
from pathlib import Path

from rich.console import Console
from rich.table import Table

from vaahai.core.agents.factory import AgentFactory
from vaahai.core.config import config_manager

# Create console for rich output
console = Console()


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


def detect_language(path, output_format="table", no_llm=False, api_key=None, model=None, temperature=None, save_config=False, debug=False):
    """
    Detect programming languages, versions, and features in code files.
    
    Args:
        path: Path to file or directory to analyze
        output_format: Output format (table, json, markdown)
        no_llm: Disable LLM-based analysis, use only heuristic detection
        api_key: OpenAI API key for LLM analysis
        model: Model to use for LLM analysis
        temperature: Temperature for model generation
        save_config: Save provided parameters to global configuration
        debug: Enable debug mode with detailed error tracebacks
    """
    try:
        # Process file paths
        file_paths = []
        file_contents = []
        
        file_path = Path(path)
        if file_path.is_dir():
            # Process all files in directory
            for path_item in file_path.glob("**/*"):
                if path_item.is_file() and not path_item.name.startswith("."):
                    try:
                        content = path_item.read_text(errors="replace")
                        file_paths.append(str(path_item))
                        file_contents.append(content)
                    except Exception as e:
                        console.print(f"[bold yellow]Warning: Could not read {path_item}: {str(e)}[/bold yellow]")
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
        
        # Save to global config if requested
        if save_config:
            if api_key:
                config_manager.set("llm.api_key", api_key, save=True)
                console.print("[bold green]Saved API key to global configuration[/bold green]")
            if model:
                config_manager.set("autogen.default_model", model, save=True)
                console.print(f"[bold green]Saved model '{model}' to global configuration[/bold green]")
            if temperature is not None:
                config_manager.set("autogen.temperature", temperature, save=True)
                console.print(f"[bold green]Saved temperature {temperature} to global configuration[/bold green]")
        
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
        if debug:
            console.print("[bold red]Error with traceback:[/bold red]")
            console.print(traceback.format_exc())
        else:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            console.print("[bold yellow]Tip:[/bold yellow] Use --debug flag for detailed error traceback")
        return 1


def print_help():
    """Print help message."""
    console.print("[bold blue]Vaahai Language Detector[/bold blue]")
    console.print("\nDetect programming languages, versions, and features in code files.")
    console.print("\n[bold]Usage:[/bold]")
    console.print("  vaahai-detect-language PATH [OPTIONS]")
    console.print("\n[bold]Arguments:[/bold]")
    console.print("  PATH                  Path to file or directory to analyze")
    console.print("\n[bold]Options:[/bold]")
    console.print("  --format, -f FORMAT   Output format: table, json, or markdown [default: table]")
    console.print("  --api-key KEY         OpenAI API key for LLM analysis")
    console.print("  --model MODEL         Model to use for LLM analysis")
    console.print("  --temperature TEMP    Temperature for model generation")
    console.print("  --no-llm              Disable LLM-based analysis, use only heuristic detection")
    console.print("  --save-config, -s     Save provided parameters to global configuration")
    console.print("  --debug               Enable debug mode with detailed error tracebacks")
    console.print("  --help, -h            Show this help message and exit")
    console.print("\n[bold]Examples:[/bold]")
    console.print("  vaahai-detect-language app.py")
    console.print("  vaahai-detect-language src/ --format json")
    console.print("  vaahai-detect-language file.js --no-llm")
    console.print("  vaahai-detect-language src/ --debug")


def main():
    """Main entry point for the standalone detect-language command."""
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print_help()
        return 0
    
    # Extract path (first non-option argument)
    path = None
    output_format = "table"
    no_llm = False
    api_key = None
    model = None
    temperature = None
    save_config = False
    debug = False
    
    i = 0
    while i < len(args):
        if args[i].startswith("-"):
            if args[i] in ["--format", "-f"]:
                if i + 1 < len(args):
                    output_format = args[i + 1]
                    i += 2
                else:
                    console.print("[bold red]Error: Missing value for --format option[/bold red]")
                    return 1
            elif args[i] == "--api-key":
                if i + 1 < len(args):
                    api_key = args[i + 1]
                    i += 2
                else:
                    console.print("[bold red]Error: Missing value for --api-key option[/bold red]")
                    return 1
            elif args[i] == "--model":
                if i + 1 < len(args):
                    model = args[i + 1]
                    i += 2
                else:
                    console.print("[bold red]Error: Missing value for --model option[/bold red]")
                    return 1
            elif args[i] == "--temperature":
                if i + 1 < len(args):
                    try:
                        temperature = float(args[i + 1])
                        i += 2
                    except ValueError:
                        console.print("[bold red]Error: Temperature must be a float[/bold red]")
                        return 1
                else:
                    console.print("[bold red]Error: Missing value for --temperature option[/bold red]")
                    return 1
            elif args[i] == "--no-llm":
                no_llm = True
                i += 1
            elif args[i] in ["--save-config", "-s"]:
                save_config = True
                i += 1
            elif args[i] == "--debug":
                debug = True
                i += 1
            else:
                console.print(f"[bold red]Error: Unknown option {args[i]}[/bold red]")
                return 1
        else:
            if path is None:
                path = args[i]
                i += 1
            else:
                console.print("[bold red]Error: Multiple paths specified[/bold red]")
                return 1
    
    if path is None:
        console.print("[bold red]Error: No path specified[/bold red]")
        return 1
    
    return detect_language(path, output_format, no_llm, api_key, model, temperature, save_config, debug)


def main_cli():
    """Entry point for the standalone detect-language script when installed as a package."""
    return main()


if __name__ == "__main__":
    sys.exit(main_cli())
