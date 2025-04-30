import click

from ..pending import get_pending_deletions
from ..utils import format_time


@click.command()
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
