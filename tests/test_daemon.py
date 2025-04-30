"""Tests for the daemon implementation."""

import os
from pathlib import Path


def test_daemon_initialization(daemon):
    """Test daemon initialization with basic parameters."""
    assert daemon.rtime == 10
    assert daemon.name == "test.txt"
    assert Path(daemon.pidfile).name == "test.pid"
    assert daemon.pidfile_timeout == 5


def test_daemon_creation(daemon):
    """Test daemon creation with basic parameters."""
    assert daemon is not None


# TODO: Add this test after adding is_running method
# def test_daemon_run(daemon, mock_os):
#     """Test daemon run method."""
#     daemon.run()
#     assert daemon.is_running()


# TODO: Add this test after adding is_running method
# def test_daemon_cleanup(daemon):
#     """Test daemon cleanup method."""
#     daemon.cleanup()
#     assert not daemon.is_running()


def test__write_pidfile(daemon):
    """Test write_pidfile method."""
    daemon._write_pidfile()
    assert os.path.exists(daemon.pidfile)
    assert os.path.isfile(daemon.pidfile)
    assert os.path.getsize(daemon.pidfile) > 0
