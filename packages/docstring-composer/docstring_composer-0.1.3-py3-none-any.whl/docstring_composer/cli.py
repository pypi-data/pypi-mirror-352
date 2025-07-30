"""
Command-line interface for docstring-composer.
"""

import sys
import json
import click
from typing import Dict, Any, Optional, TextIO, List

from docstring_composer.composer import DocstringComposer
from docstring_composer.formatters import SUPPORTED_LANGUAGES, list_supported_formats
from docstring_composer.schema import load_schema


@click.group()
@click.version_option()
def cli():
    """
    Docstring Composer: Convert schema-based docstrings to different language formats.
    """
    pass


@cli.command()
@click.option(
    "--schema",
    type=click.File("r"),
    help="Path to the docstring schema file (JSON format).",
)
@click.option(
    "--language",
    type=click.Choice(list(SUPPORTED_LANGUAGES.keys())),
    required=True,
    help="Target programming language.",
)
@click.option(
    "--style",
    type=str,
    help="Docstring style for the target language.",
)
@click.option(
    "--output",
    type=click.File("w"),
    default="-",
    help="Output file path. If not specified, output will be written to stdout.",
)
def convert(schema, language: str, style: Optional[str], output):
    """
    Convert a docstring schema to a specific language format.
    """
    # Read the schema from stdin if not provided as a file
    if schema is None:
        if not sys.stdin.isatty():
            schema_str = sys.stdin.read()
            try:
                schema_data = json.loads(schema_str)
            except json.JSONDecodeError as e:
                click.echo(f"Error parsing schema JSON: {e}", err=True)
                sys.exit(1)
        else:
            click.echo("Error: No schema provided. Use --schema or pipe JSON input.", err=True)
            sys.exit(1)
    else:
        try:
            schema_data = json.load(schema)
        except json.JSONDecodeError as e:
            click.echo(f"Error parsing schema JSON: {e}", err=True)
            sys.exit(1)

    # Validate the style if provided
    if style is not None:
        if style not in SUPPORTED_LANGUAGES[language]["styles"]:
            click.echo(
                f"Error: Unsupported style '{style}' for language '{language}'. "
                f"Supported styles are: {', '.join(SUPPORTED_LANGUAGES[language]['styles'])}",
                err=True,
            )
            sys.exit(1)

    # Convert the schema
    composer = DocstringComposer()
    try:
        docstring = composer.convert(schema=schema_data, language=language, style=style)
    except Exception as e:
        click.echo(f"Error converting schema: {e}", err=True)
        sys.exit(1)

    # Write the output
    output.write(docstring)


@cli.command()
def list_formats():
    """
    List supported languages and styles.
    """
    click.echo("Supported languages and styles:")
    for language, info in SUPPORTED_LANGUAGES.items():
        click.echo(f"  {language}:")
        click.echo(f"    Default style: {info['default_style']}")
        click.echo(f"    Supported styles: {', '.join(info['styles'])}")


def main():
    """
    Main entry point for the CLI.
    """
    cli()
