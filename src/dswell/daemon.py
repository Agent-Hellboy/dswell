import hashlib
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

from .logger import logger
from .pending import add_pending, remove_pending


class DswellDaemon:
    """A custom daemon implementation for background file deletion."""

    def __init__(self, rtime: int, name: str, pidfile: str):
        """Initialize the daemon.

        Args:
            rtime: Time in seconds to wait before deletion
            name: Path to the file/directory to delete
            pidfile: Path to the PID file
        """
        self.rtime = rtime
        self.name = name
        self.pidfile = pidfile
        self.pidfile_timeout = 5
        logger.debug(
            f"Initialized daemon for {name} with deletion time {rtime} seconds"
        )

    def daemonize(self) -> None:
        """Convert the current process into a daemon following standard steps."""
        ### DISCLAIMER: Followed https://www.youtube.com/watch?v=6t982BjaMko
        ### I hope it works , Sorry if it doesn't
        # STEP 1: First fork() and leave parent
        try:
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                sys.exit(0)
        except OSError as e:
            logger.error(f"Fork #1 failed: {e}")
            sys.exit(1)

        # STEP 2: Create new session
        os.setsid()

        # STEP 3: Ignore signals
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        # We still handle SIGTERM and SIGINT for clean shutdown
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        # STEP 4: Second fork so that PID != SID
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError as e:
            logger.error(f"Fork #2 failed: {e}")
            sys.exit(1)

        # STEP 5: Set umask for file permissions
        os.umask(0o022)  # Set default permissions to 644 for files, 755 for dirs

        # STEP 6: Change to root directory
        os.chdir("/")

        # STEP 7: Close all open file descriptors
        # Get maximum number of file descriptors
        import resource

        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            maxfd = 1024

        # Close all file descriptors
        for fd in range(maxfd):
            try:
                os.close(fd)
            except OSError:
                pass

        # Redirect standard file descriptors to /dev/null
        os.open(os.devnull, os.O_RDWR)  # stdin
        os.dup2(0, 1)  # stdout
        os.dup2(0, 2)  # stderr

        # STEP 8: Setup logging (already done via logger import)
        logger.debug("Daemon process successfully created")

        # Write PID file
        self._write_pidfile()

    def _write_pidfile(self) -> None:
        """Write the PID file."""
        pid = str(os.getpid())
        try:
            with open(self.pidfile, "w+") as f:
                f.write(f"{pid}\n")
            # Set proper permissions for PID file
            os.chmod(self.pidfile, 0o644)
        except OSError as e:
            logger.error(f"Failed to write PID file: {e}")
            sys.exit(1)

    def _handle_signal(self, signum: int, frame: Optional[object]) -> None:
        """Handle termination signals."""
        logger.debug(f"Received signal {signum}")
        self.cleanup()
        sys.exit(0)

    def cleanup(self) -> None:
        """Clean up resources before exit."""
        if os.path.exists(self.pidfile):
            try:
                os.remove(self.pidfile)
            except OSError as e:
                logger.error(f"Failed to remove PID file: {e}")

    def run(self) -> None:
        """Run the daemon process."""
        try:
            # Add to pending deletions
            add_pending(self.name, self.rtime)

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
            # Remove from pending deletions
            remove_pending(self.name)
            self.cleanup()


def start_daemon(file_path: str, deletion_time: int) -> None:
    """Start a daemon process for file deletion.

    Args:
        file_path: Path to the file/directory to delete
        deletion_time: Time in seconds to wait before deletion
    """
    dswell_path = Path.home() / ".dswell"
    dswell_path.mkdir(exist_ok=True, mode=0o755)  # Set proper directory permissions

    # Create a unique PID file name based on the file path
    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
    pidfile = dswell_path / f"daemon_{file_hash}.pid"
    logger.debug(f"Starting daemon for {file_path} with PID file: {pidfile}")

    # Create and start the daemon
    daemon = DswellDaemon(deletion_time, file_path, pidfile=str(pidfile))
    daemon.daemonize()
    daemon.run()
