#!/usr/bin/env python3
"""
Command-line interface for DaLog.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .app import DaLogApp


def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(__version__)
    ctx.exit()


@click.command()
@click.argument(
    "log_file",
    required=True,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, readable=True),
    help="Path to configuration file",
)
@click.option(
    "--search",
    "-s",
    type=str,
    help="Initial search term to filter logs",
)
@click.option(
    "--tail",
    "-t",
    type=int,
    help="Load only last N lines of the file",
)
@click.option(
    "--no-live-reload",
    is_flag=True,
    help="Disable live reload feature",
)
@click.option(
    "--theme",
    type=str,
    help="Set the Textual theme (e.g., nord, gruvbox, tokyo-night, textual-dark)",
)
@click.option(
    "--version",
    "-V",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
)
def main(
    log_file: str,
    config: Optional[str],
    search: Optional[str],
    tail: Optional[int],
    no_live_reload: bool,
    theme: Optional[str],
) -> None:
    """
    DaLog - Advanced Terminal Log Viewer
    
    View and search a log file with a modern terminal interface.
    
    Examples:
    
        dalog app.log
        
        dalog --search ERROR app.log
        
        dalog --tail 1000 large-app.log
        
        dalog --config ~/.config/dalog/custom.toml app.log
    """
    # Convert path to string
    log_file_path = str(Path(log_file).resolve())
    
    # Create and run the application
    try:
        app = DaLogApp(
            log_file=log_file_path,
            config_path=config,
            initial_search=search,
            tail_lines=tail,
            theme=theme,
            live_reload=not no_live_reload,
        )
        
        # Run the app
        app.run()
        
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main() 