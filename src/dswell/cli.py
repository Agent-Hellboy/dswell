import os
from pathlib import Path

import click

from .daemon import start_daemon
from .logger import logger
from .pending import get_pending_deletions
from .utils import format_time, parse_time


def touch_file(filepath):
    """Create an empty file if it doesn't exist."""
    Path(filepath).touch()


@click.group()
def cli():
    """dswell - Delayed file deletion utility"""
    pass


@cli.command()
@click.option(
    "--dir",
    is_flag=True,
    default=False,
    help="Create a directory instead of a file",
)
@click.argument("name")
@click.option(
    "--time",
    help="Time till deletion (e.g., '1h3m2s', '1h', '30m', '45s')",
    required=True,
)
def create(dir: bool, name: str, time: str) -> None:
    """Create a file or directory and schedule it for deletion.

    NAME is the name of the file or directory to create.
    """
    try:
        # Parse the time string into seconds
        seconds = parse_time(time)
        logger.debug(
            f"Create command called with options: dir={dir}, name={name}, "
            f"time={time} ({seconds} seconds)"
        )

        # Create the file or directory
        if dir:
            os.makedirs(name, exist_ok=True)
            name = str(Path(name).absolute())
            logger.debug(f"Created directory: {name}")
            click.echo(
                f"Created directory: {name} and scheduled for deletion "
                f"after {format_time(seconds)}"
            )
        else:
            touch_file(name)
            name = str(Path(name).absolute())
            logger.debug(f"Created file: {name}")
            click.echo(
                f"Created file: {name} and scheduled for deletion "
                f"after {format_time(seconds)}"
            )

        # Schedule for deletion
        start_daemon(name, seconds)

    except ValueError as e:
        logger.error(f"Invalid time format: {str(e)}")
        raise click.ClickException(str(e)) from e
    except Exception as e:
        logger.error(f"Error in create command: {str(e)}")
        raise click.ClickException(str(e)) from e


@cli.command()
def list():
    """List all pending file/directory deletions."""
    pending = get_pending_deletions()

    if not pending:
        click.echo("No pending deletions")
        return

    # Print header
    click.echo("\nPending Deletions:")
    click.echo("-" * 80)
    click.echo(f"{'Path':<50} {'Created At':<20} {'Time Left':<10}")
    click.echo("-" * 80)

    # Print each pending deletion
    for item in pending:
        path = item["path"]
        created_at = item["created_at"].split("T")[1].split(".")[0]  # Format: HH:MM:SS
        time_left = format_time(item["time_left"])

        # Truncate path if too long
        if len(path) > 47:
            path = "..." + path[-44:]

        click.echo(f"{path:<50} {created_at:<20} {time_left:<10}")

    click.echo("-" * 80)


if __name__ == "__main__":
    cli()
