"""Tests for the watcher module."""

import json
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from dswell.pending import PENDING_FILE, add_pending, ensure_pending_file
from dswell.watcher import (
    PendingFileHandler,
    PendingWatcher,
    start_watcher,
    status_watcher,
    stop_watcher,
)


@pytest.fixture
def temp_pending_file(tmp_path, monkeypatch):
    """Create a temporary pending.json file."""
    pending_file = tmp_path / "pending.json"
    monkeypatch.setattr("dswell.watcher.PENDING_FILE", pending_file)
    monkeypatch.setattr("dswell.pending.PENDING_FILE", pending_file)
    ensure_pending_file()
    return pending_file


@pytest.fixture
def temp_pidfile(tmp_path):
    """Create a temporary PID file path."""
    return str(tmp_path / "watcher.pid")


class TestPendingFileHandler:
    """Tests for PendingFileHandler class."""

    def test_init(self, temp_pending_file):
        """Test handler initialization."""
        handler = PendingFileHandler()
        assert isinstance(handler.monitored_paths, set)

    def test_on_deleted(self, temp_pending_file, tmp_path):
        """Test deletion event handling."""
        # Create a test file and add it to pending
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        add_pending(str(test_file), 3600)

        handler = PendingFileHandler()
        assert str(test_file) in handler.monitored_paths

        # Simulate deletion event
        event = MagicMock()
        event.src_path = str(test_file)
        handler.on_deleted(event)

        # Check that path was removed from monitored paths
        assert str(test_file) not in handler.monitored_paths

    def test_on_deleted_nonexistent_path(self, temp_pending_file, tmp_path):
        """Test that on_deleted does nothing when path is not in monitored_paths."""
        handler = PendingFileHandler()
        initial_paths = handler.monitored_paths.copy()
        
        # Simulate deletion event for a path not in monitored_paths
        event = MagicMock()
        event.src_path = str(tmp_path / "nonexistent.txt")
        handler.on_deleted(event)
        
        # monitored_paths should remain unchanged
        assert handler.monitored_paths == initial_paths

    def test_on_moved(self, temp_pending_file, tmp_path):
        """Test move event handling."""
        # Create a test file and add it to pending
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        add_pending(str(test_file), 3600)

        handler = PendingFileHandler()
        assert str(test_file) in handler.monitored_paths

        # Simulate move event
        event = MagicMock()
        event.src_path = str(test_file)
        handler.on_moved(event)

        # Check that path was removed from monitored paths
        assert str(test_file) not in handler.monitored_paths


class TestPendingWatcher:
    """Tests for PendingWatcher class."""

    def test_init(self, temp_pidfile):
        """Test watcher initialization."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        assert watcher.pidfile == temp_pidfile
        assert watcher.observer is None
        assert not watcher.running

    def test_write_pidfile(self, temp_pidfile):
        """Test PID file creation."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        watcher._write_pidfile()

        assert os.path.exists(temp_pidfile)
        with open(temp_pidfile, "r") as f:
            pid = int(f.read().strip())
        assert pid == os.getpid()

    def test_remove_pidfile(self, temp_pidfile):
        """Test PID file removal."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        watcher._write_pidfile()
        assert os.path.exists(temp_pidfile)

        watcher._remove_pidfile()
        assert not os.path.exists(temp_pidfile)

    def test_is_running_when_not_running(self, temp_pidfile):
        """Test is_running when watcher is not running."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        assert not watcher.is_running()

    def test_is_running_when_running(self, temp_pidfile):
        """Test is_running when watcher is running."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        watcher._write_pidfile()
        assert watcher.is_running()

    def test_is_running_with_invalid_pidfile(self, temp_pidfile):
        """Test is_running with invalid PID file contents."""
        # Write invalid (non-integer) data to the PID file
        with open(temp_pidfile, "w") as f:
            f.write("not_a_pid")
        watcher = PendingWatcher(pidfile=temp_pidfile)
        assert not watcher.is_running()
        # PID file should be removed after ValueError
        assert not os.path.exists(temp_pidfile)

    def test_get_watch_paths(self, temp_pending_file, tmp_path):
        """Test getting watch paths from pending deletions."""
        # Create test files in different directories
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        file1 = dir1 / "test1.txt"
        file2 = dir2 / "test2.txt"
        file1.write_text("test")
        file2.write_text("test")

        add_pending(str(file1), 3600)
        add_pending(str(file2), 3600)

        watcher = PendingWatcher()
        watch_paths = watcher._get_watch_paths()

        assert str(dir1.resolve()) in watch_paths
        assert str(dir2.resolve()) in watch_paths

    def test_stop(self, temp_pidfile):
        """Test watcher stop."""
        watcher = PendingWatcher(pidfile=temp_pidfile)
        watcher._write_pidfile()
        watcher.running = True

        # Mock observer
        watcher.observer = MagicMock()
        watcher.observer.is_alive.return_value = True

        watcher.stop()

        assert not watcher.running
        watcher.observer.stop.assert_called_once()
        watcher.observer.join.assert_called_once()
        assert not os.path.exists(temp_pidfile)


class TestWatcherFunctions:
    """Tests for module-level watcher functions."""

    @patch("dswell.watcher.PendingWatcher")
    def test_start_watcher_when_not_running(self, mock_watcher_class):
        """Test starting watcher when not already running."""
        mock_watcher = MagicMock()
        mock_watcher.is_running.return_value = False
        mock_watcher_class.return_value = mock_watcher

        start_watcher()

        mock_watcher.start.assert_called_once()

    @patch("dswell.watcher.PendingWatcher")
    def test_start_watcher_when_already_running(self, mock_watcher_class):
        """Test starting watcher when already running."""
        mock_watcher = MagicMock()
        mock_watcher.is_running.return_value = True
        mock_watcher_class.return_value = mock_watcher

        start_watcher()

        mock_watcher.start.assert_not_called()

    @patch("dswell.watcher.PendingWatcher")
    def test_stop_watcher_when_running(self, mock_watcher_class):
        """Test stopping watcher when running."""
        mock_watcher = MagicMock()
        mock_watcher.is_running.return_value = True
        mock_watcher.pidfile = "/tmp/test.pid"
        mock_watcher_class.return_value = mock_watcher

        with patch("dswell.watcher.open", create=True) as mock_open:
            with patch("os.kill") as mock_kill:
                mock_open.return_value.__enter__.return_value.read.return_value = (
                    "12345\n"
                )
                stop_watcher()

                mock_kill.assert_called()

    @patch("dswell.watcher.PendingWatcher")
    def test_stop_watcher_when_not_running(self, mock_watcher_class):
        """Test stopping watcher when not running."""
        mock_watcher = MagicMock()
        mock_watcher.is_running.return_value = False
        mock_watcher_class.return_value = mock_watcher

        with patch("os.kill") as mock_kill:
            stop_watcher()
            mock_kill.assert_not_called()

    @patch("dswell.watcher.PendingWatcher")
    def test_status_watcher(self, mock_watcher_class):
        """Test checking watcher status."""
        mock_watcher = MagicMock()
        mock_watcher.is_running.return_value = True
        mock_watcher.pidfile = "/tmp/test.pid"
        mock_watcher_class.return_value = mock_watcher

        with patch("dswell.watcher.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "12345\n"
            result = status_watcher()

            assert result is True
