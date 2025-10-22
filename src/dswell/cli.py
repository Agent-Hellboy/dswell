import click

from .subcmds.create import create
from .subcmds.list import list
from .subcmds.watcher import watcher


@click.group()
def cli():
    """dswell - Delayed file deletion utility"""
    pass


# Add subcommands
cli.add_command(create)
cli.add_command(list)
cli.add_command(watcher)


if __name__ == "__main__":
    cli()
