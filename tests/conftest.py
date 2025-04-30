"""Test configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, src_path)

from dswell.daemon import DswellDaemon  # noqa: E402


@pytest.fixture
def daemon():
    rtime = 10
    name = "test.txt"
    pidfile = "test.pid"
    return DswellDaemon(rtime, name, pidfile)
