import click

from .subcmds.create import create
from .subcmds.list import list


@click.group()
def cli():
    """dswell - Delayed file deletion utility"""
    pass


# Add subcommands
cli.add_command(create)
cli.add_command(list)


if __name__ == "__main__":
    cli()
