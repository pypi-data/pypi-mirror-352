"""Command-line interface for the resume builder.

This module provides a command-line interface for building resumes from YAML files.
"""

import os
import shutil
import sys

import click

from yaml_resume_builder.builder import build_resume


@click.group()
def cli() -> None:
    """Resume Builder CLI.

    A tool to generate PDF resumes from YAML files using LaTeX templates.
    """
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the input YAML file.",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="Path to save the output PDF file.",
)
@click.option(
    "--debug",
    "-d",
    is_flag=True,
    help="Enable debug mode to save the intermediate .tex file alongside the PDF.",
)
@click.option(
    "--one-page",
    "-1",
    is_flag=True,
    help="Optimize the resume to fit on one page by adjusting font size, margins, and spacing.",
)
def build(input: str, output: str, debug: bool, one_page: bool) -> None:
    """Build a resume from a YAML file.

    Args:
        input (str): Path to the input YAML file.
        output (str): Path to save the output PDF file.
        debug (bool): Whether to save the intermediate .tex file.
        one_page (bool): Whether to optimize the resume to fit on one page.
    """
    try:
        output_path = build_resume(input, output, debug=debug, one_page=one_page)

        click.echo(f"Resume successfully built and saved to: {output_path}")

        if debug:
            # Generate the .tex file path based on the output PDF path
            tex_output = output.replace(".pdf", ".tex")
            click.echo(f"Debug mode: LaTeX source saved to: {tex_output}")
    except Exception as e:
        click.echo(f"Error building resume: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    required=False,
    default="sample_resume.yml",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    help="Path to save the sample YAML file.",
)
def init(output: str) -> None:
    """Create a sample YAML resume file.

    Args:
        output (str): Path to save the sample YAML file.
    """
    try:
        # Get the path to the sample resume file
        sample_path = os.path.join(os.path.dirname(__file__), "sample_resume.yml")

        # Copy the sample file to the output path
        shutil.copy(sample_path, output)

        click.echo(f"Sample resume file created at: {output}")
        click.echo(
            "Edit this file with your information and then use the 'build' command to generate your resume."
        )
    except Exception as e:
        click.echo(f"Error creating sample resume file: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()
