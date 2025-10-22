import click

from .subcmds.create import create
from .subcmds.delete import delete
from .subcmds.list import list
from .subcmds.snapshot import snapshot


@click.group()
def cli() -> None:
    """dswell: A tool to schedule file and directory deletions."""
    pass


cli.add_command(create)
cli.add_command(list)
cli.add_command(delete)
cli.add_command(snapshot)


if __name__ == "__main__":
    cli()
