"""File system watcher for monitoring pending deletions.

This module provides functionality to monitor files/directories scheduled
for deletion and automatically clean up pending.json when they are manually
deleted before their scheduled deletion time.
"""

import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .logger import logger
from .pending import PENDING_FILE, get_pending_deletions, remove_pending


class PendingFileHandler(FileSystemEventHandler):
    """Handler for file system events on pending deletion paths."""

    def __init__(self):
        """Initialize the handler with a set of monitored paths."""
        super().__init__()
        self.monitored_paths: Set[str] = set()
        self._update_monitored_paths()

    def _update_monitored_paths(self) -> None:
        """Update the set of monitored paths from pending.json."""
        try:
            pending = get_pending_deletions()
            self.monitored_paths = {item["path"] for item in pending}
            logger.debug(f"Monitoring {len(self.monitored_paths)} paths")
        except Exception as e:
            logger.error(f"Failed to update monitored paths: {e}")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle deletion events.

        Args:
            event: The file system event
        """
        if event.src_path in self.monitored_paths:
            logger.info(f"Detected manual deletion of {event.src_path}")
            remove_pending(event.src_path)
            self.monitored_paths.discard(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle move/rename events.

        Args:
            event: The file system event
        """
        if event.src_path in self.monitored_paths:
            logger.info(f"Detected move/rename of {event.src_path}")
            remove_pending(event.src_path)
            self.monitored_paths.discard(event.src_path)


class PendingWatcher:
    """Watcher daemon for monitoring pending deletions."""

    def __init__(self, pidfile: str = None):
        """Initialize the watcher.

        Args:
            pidfile: Path to the PID file for the watcher daemon
        """
        self.pidfile = pidfile or str(Path.home() / ".dswell" / "watcher.pid")
        self.observer: Observer = None
        self.event_handler = PendingFileHandler()
        self.running = False
        self.watched_paths: Set[str] = set()  # Track watched paths internally

        # Only setup signal handlers if not in test environment
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            # Setup signal handlers
            signal.signal(signal.SIGTERM, self._handle_signal)
            signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum: int, frame) -> None:
        """Handle termination signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, stopping watcher")
        self.stop()
        sys.exit(0)

    def _write_pidfile(self) -> None:
        """Write the PID file."""
        pid = str(os.getpid())
        try:
            pidfile_path = Path(self.pidfile)
            pidfile_path.parent.mkdir(exist_ok=True)
            with open(self.pidfile, "w") as f:
                f.write(f"{pid}\n")
            os.chmod(self.pidfile, 0o644)
            logger.debug(f"Created PID file: {self.pidfile}")
        except OSError as e:
            logger.error(f"Failed to write PID file: {e}")
            sys.exit(1)

    def _remove_pidfile(self) -> None:
        """Remove the PID file."""
        try:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
                logger.debug(f"Removed PID file: {self.pidfile}")
        except OSError as e:
            logger.error(f"Failed to remove PID file: {e}")

    def _get_watch_paths(self) -> Set[str]:
        """Get unique parent directories to watch.

        Returns:
            Set of parent directory paths to monitor
        """
        pending = get_pending_deletions()
        watch_paths = set()

        for item in pending:
            path = Path(item["path"])
            # Watch the parent directory
            parent = path.parent
            if parent.exists():
                watch_paths.add(str(parent.resolve()))
            else:
                logger.warning(
                    f"Parent directory {parent} does not exist for pending file {path}"
                )

        return watch_paths

    def start(self) -> None:
        """Start the watcher daemon."""
        logger.info("Starting pending deletion watcher...")
        self._write_pidfile()

        self.observer = Observer()
        self.running = True

        try:
            while self.running:
                # Get current watch paths
                watch_paths = self._get_watch_paths()

                # Update monitored paths in event handler
                self.event_handler._update_monitored_paths()

                # Schedule observers for all parent directories
                for watch_path in watch_paths:
                    try:
                        # Check if already watching this path using our internal set
                        if watch_path not in self.watched_paths:
                            self.observer.schedule(
                                self.event_handler, watch_path, recursive=False
                            )
                            self.watched_paths.add(watch_path)
                            logger.debug(f"Started watching: {watch_path}")
                    except Exception as e:
                        logger.error(f"Failed to watch {watch_path}: {e}")

                # Start observer if not already started
                if not self.observer.is_alive():
                    self.observer.start()
                    logger.info("Watcher observer started")

                # Sleep for a bit before checking for new paths
                time.sleep(10)  # Check every 10 seconds for new pending files

        except KeyboardInterrupt:
            logger.info("Watcher interrupted by user")
        except Exception as e:
            logger.error(f"Watcher error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the watcher daemon."""
        logger.info("Stopping watcher...")
        self.running = False

        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Observer stopped")

        self._remove_pidfile()

    def is_running(self) -> bool:
        """Check if the watcher daemon is running.

        Returns:
            True if the daemon is running, False otherwise
        """
        if not os.path.exists(self.pidfile):
            return False

        try:
            with open(self.pidfile, "r") as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            # Process doesn't exist or invalid PID
            self._remove_pidfile()
            return False


def start_watcher() -> None:
    """Start the watcher daemon in the foreground."""
    watcher = PendingWatcher()

    if watcher.is_running():
        logger.warning("Watcher is already running")
        return

    watcher.start()


def stop_watcher() -> None:
    """Stop the watcher daemon."""
    watcher = PendingWatcher()

    if not watcher.is_running():
        logger.warning("Watcher is not running")
        return

    try:
        with open(watcher.pidfile, "r") as f:
            pid = int(f.read().strip())

        os.kill(pid, signal.SIGTERM)
        logger.info(f"Sent SIGTERM to watcher process {pid}")

        # Wait for process to exit
        timeout = 5
        while timeout > 0 and watcher.is_running():
            time.sleep(0.5)
            timeout -= 0.5

        if watcher.is_running():
            logger.warning("Watcher did not stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)

    except (OSError, ValueError) as e:
        logger.error(f"Failed to stop watcher: {e}")


def status_watcher() -> bool:
    """Check the status of the watcher daemon.

    Returns:
        True if the watcher is running, False otherwise
    """
    watcher = PendingWatcher()
    is_running = watcher.is_running()

    if is_running:
        try:
            with open(watcher.pidfile, "r") as f:
                pid = int(f.read().strip())
            logger.info(f"Watcher is running (PID: {pid})")
        except (OSError, ValueError):
            logger.info("Watcher is running (PID unknown)")
    else:
        logger.info("Watcher is not running")

    return is_running
