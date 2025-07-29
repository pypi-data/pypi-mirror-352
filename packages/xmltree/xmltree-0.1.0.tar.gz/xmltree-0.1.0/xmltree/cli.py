#!/usr/bin/env python3
"""CLI interface for xmltree."""

import sys
from pathlib import Path

import typer
from rich import print as rich_print

from .core import directory_to_xml, format_xml
from .logger import get_logger

logger = get_logger(__name__)
app = typer.Typer()


@app.command()
def convert(
    path: Path = typer.Argument(
        Path("."),
        help="Directory path to convert (default: current directory)",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output file path (default: stdout)"
    ),
    ignore: list[str] = typer.Option(
        [], "--ignore", "-i", help="Patterns to ignore (can be used multiple times)"
    ),
    include: list[str] = typer.Option(
        [],
        "--include",
        "-I",
        help="Only include files matching these patterns (can be used multiple times)",
    ),
    no_gitignore: bool = typer.Option(
        False, "--no-gitignore", help="Don't respect .gitignore files"
    ),
    compact: bool = typer.Option(
        False, "--compact", "-c", help="Compact output (no pretty printing)"
    ),
    name: str | None = typer.Option(
        None, "--name", "-n", help="Name for the root directory element (default: directory name)"
    ),
    full_paths: bool = typer.Option(
        False, "--full-paths", "-f", help="Show absolute paths instead of relative paths"
    ),
):
    """Convert directory structures to XML format.

    By default, respects .gitignore files and outputs pretty-printed XML.

    Examples:
        # Convert current directory to XML
        dtx

        # Convert specific directory and save to file
        dtx /path/to/project -o project.xml

        # Ignore additional patterns
        dtx -i "*.log" -i "temp/*" -i "build/"

        # Only include specific file types
        dtx -I "*.py" -I "*.js" -I "*.md"

        # Compact output without respecting .gitignore
        dtx --no-gitignore --compact
    """
    assert sys.version_info >= (3, 12), "Requires Python 3.12+"

    logger.debug(f"Converting directory: {path}")

    # Convert directory to XML
    try:
        xml_root = directory_to_xml(
            path=path,
            ignore_patterns=list(ignore) if ignore else None,
            include_patterns=list(include) if include else None,
            respect_gitignore=not no_gitignore,
            root_name=name,
            full_paths=full_paths,
        )
    except AssertionError as e:
        logger.error(f"Assertion failed: {e}")
        raise typer.Exit(1) from e
    except Exception as e:
        logger.error(f"Failed to convert directory: {e}")
        raise typer.Exit(1) from e

    # Format XML
    xml_output = format_xml(xml_root, pretty=not compact)

    # Output
    if output:
        try:
            output.write_text(xml_output, encoding="utf-8")
            rich_print(f"[green]✓[/green] Written to {output}")
        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            raise typer.Exit(1) from e
    else:
        rich_print(xml_output)


@app.callback()
def callback():
    """Convert directory structures to XML format."""
    pass


if __name__ == "__main__":
    app()
