"""Test configuration and fixtures."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

from dswell.daemon import FileDswellDaemon  # noqa: E402


@pytest.fixture
def daemon(tmp_path):
    rtime = 10
    name = "test.txt"
    pidfile = str(tmp_path / "test.pid")
    return FileDswellDaemon(rtime, name, pidfile)


@pytest.fixture
def mock_os():
    """Mock os module functions used in daemon."""
    with patch("os.fork") as mock_fork, patch("os.setsid") as mock_setsid, patch(
        "os.chdir"
    ) as mock_chdir, patch("os.umask") as mock_umask, patch(
        "os.open"
    ) as mock_open, patch(
        "os.dup2"
    ) as mock_dup2, patch(
        "os.close"
    ) as mock_close:

        # Configure fork to simulate parent and child processes
        mock_fork.side_effect = [0, 0]  # Child process both times
        yield {
            "fork": mock_fork,
            "setsid": mock_setsid,
            "chdir": mock_chdir,
            "umask": mock_umask,
            "open": mock_open,
            "dup2": mock_dup2,
            "close": mock_close,
        }
