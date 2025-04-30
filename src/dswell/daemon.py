import hashlib
import os
import sys
import time
from pathlib import Path

from daemons.prefab import run

from .logger import logger


class DswellDaemon(run.RunDaemon):
    """A daemon to perform background action like deletion of file after required period."""

    def __init__(self, rtime, name, pidfile):
        super().__init__(pidfile=pidfile)
        self.rtime = rtime
        self.name = name
        self.pidfile_timeout = 5
        logger.debug(
            f"Initialized daemon for {name} with deletion time {rtime} seconds"
        )

    def run(self):
        try:
            logger.debug(
                f"Daemon started, waiting {self.rtime} seconds before deletion"
            )
            time.sleep(self.rtime)

            if os.path.isfile(self.name):
                os.remove(self.name)
                logger.debug(f"Successfully deleted file: {self.name}")
            elif os.path.isdir(self.name):
                os.rmdir(self.name)
                logger.debug(f"Successfully deleted directory: {self.name}")
            else:
                logger.warning(f"Path not found for deletion: {self.name}")

        except Exception as e:
            logger.error(f"Failed to delete {self.name}: {str(e)}")
        finally:
            # Clean up the PID file
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)


def start_daemon(file_path: str, deletion_time: int) -> None:
    """Start a daemon process for file deletion."""
    dswell_path = Path.home() / ".dswell"
    dswell_path.mkdir(exist_ok=True)

    # Create a unique PID file name based on the file path
    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
    pidfile = dswell_path / f"daemon_{file_hash}.pid"
    logger.debug(f"Starting daemon for {file_path} with PID file: {pidfile}")

    # Create a new daemon instance
    daemon = DswellDaemon(deletion_time, file_path, pidfile=str(pidfile))

    # Start the daemon and don't wait
    daemon.start()
    logger.debug(f"Daemon process started for {file_path}")

    # Exit immediately after starting the daemon
    sys.exit(0)
