import hashlib
import os
import shutil
import signal
from pathlib import Path

import click

from ..logger import logger
from ..pending import remove_pending


@click.command()
@click.argument("path", type=str)
def delete(path: str) -> None:
    """Force delete a pending item immediately."""
    full_path = os.path.abspath(path)
    dswell_path = Path.home() / ".dswell"
    file_hash = hashlib.md5(str(full_path).encode()).hexdigest()
    pidfile_path = dswell_path / f"daemon_{file_hash}.pid"

    # 1. Kill the daemon process
    if pidfile_path.exists():
        try:
            with open(pidfile_path, "r") as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
            logger.debug(f"Sent SIGTERM to process {pid} for {full_path}")
        except (IOError, ValueError, ProcessLookupError) as e:
            logger.warning(f"Could not stop daemon for {full_path}: {e}")
            if pidfile_path.exists():
                pidfile_path.unlink()
    else:
        logger.warning(f"No active daemon found for {full_path}.")

    # 2. Perform the deletion
    try:
        if os.path.islink(full_path):
            os.remove(full_path)
            click.echo(f"Successfully deleted symlink: {full_path}")
        elif os.path.isfile(full_path):
            os.remove(full_path)
            click.echo(f"Successfully deleted file: {full_path}")
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            click.echo(f"Successfully deleted directory: {full_path}")
        else:
            click.echo(f"Path not found, it may have been deleted already: {full_path}")
    except OSError as e:
        logger.error(f"Failed to delete {full_path}: {e}")
        raise click.ClickException(str(e)) from e

    # 3. Clean up pending entry
    remove_pending(full_path)
