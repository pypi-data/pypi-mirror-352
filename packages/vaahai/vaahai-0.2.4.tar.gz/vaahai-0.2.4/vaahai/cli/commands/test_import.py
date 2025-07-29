"""
Simple test script to verify that the CLI modules can be imported.
"""

print("Importing modules...")

try:
    import typer
    print("✅ Successfully imported typer")
except ImportError:
    print("❌ Failed to import typer")

try:
    from rich.console import Console
    print("✅ Successfully imported rich")
except ImportError:
    print("❌ Failed to import rich")

print("\nTesting CLI module imports...")

try:
    from vaahai.cli.commands import review
    print("✅ Successfully imported review command")
except ImportError as e:
    print(f"❌ Failed to import review command: {e}")

try:
    from vaahai.cli.commands import analyze
    print("✅ Successfully imported analyze command")
except ImportError as e:
    print(f"❌ Failed to import analyze command: {e}")

try:
    from vaahai.cli.commands import config
    print("✅ Successfully imported config command")
except ImportError as e:
    print(f"❌ Failed to import config command: {e}")

try:
    from vaahai.cli.commands import explain
    print("✅ Successfully imported explain command")
except ImportError as e:
    print(f"❌ Failed to import explain command: {e}")

try:
    from vaahai.cli.commands import document
    print("✅ Successfully imported document command")
except ImportError as e:
    print(f"❌ Failed to import document command: {e}")

print("\nTesting main CLI import...")

try:
    from vaahai.__main__ import app
    print("✅ Successfully imported main CLI application")
except ImportError as e:
    print(f"❌ Failed to import main CLI application: {e}")

print("\nTest complete!")
