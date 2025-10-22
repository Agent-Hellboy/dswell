"""Watcher subcommand for managing the pending deletion monitor."""

import click

from ..watcher import start_watcher, status_watcher, stop_watcher


@click.group()
def watcher():
    """Manage the pending deletion file watcher."""
    pass


@watcher.command()
def start():
    """Start the file watcher daemon."""
    click.echo("Starting pending deletion watcher...")
    start_watcher()


@watcher.command()
def stop():
    """Stop the file watcher daemon."""
    click.echo("Stopping pending deletion watcher...")
    stop_watcher()


@watcher.command()
def status():
    """Check the status of the file watcher daemon."""
    status_watcher()
