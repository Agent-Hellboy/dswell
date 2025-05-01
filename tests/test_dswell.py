import pytest

from dswell.daemon import DirectoryDswellDaemon, FileDswellDaemon
from dswell.utils import format_time, parse_time


def test_parse_time():
    """Test time string parsing."""
    assert parse_time("1h") == 3600
    assert parse_time("30m") == 1800
    assert parse_time("45s") == 45
    assert parse_time("1h30m45s") == 5445

    with pytest.raises(ValueError):
        parse_time("invalid")
    with pytest.raises(ValueError):
        parse_time("")
    with pytest.raises(ValueError):
        parse_time("0s")


def test_format_time():
    """Test time formatting."""
    assert format_time(3600) == "1h"
    assert format_time(1800) == "30m"
    assert format_time(45) == "45s"
    assert format_time(5445) == "1h30m45s"


def test_daemon_file_deletion(tmp_path):
    """Test daemon file deletion functionality."""
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    assert test_file.exists()

    # Create a daemon instance
    pidfile = tmp_path / "test.pid"
    daemon = FileDswellDaemon(1, str(test_file), str(pidfile))  # 1 second delay

    # Run the daemon
    daemon.run()

    # Check if file was deleted
    assert not test_file.exists()
    assert not pidfile.exists()


def test_daemon_directory_deletion(tmp_path):
    """Test daemon directory deletion functionality."""
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    assert test_dir.exists()

    # Create a daemon instance
    pidfile = tmp_path / "test.pid"
    daemon = DirectoryDswellDaemon(1, str(test_dir), str(pidfile))  # 1 second delay

    # Run the daemon
    daemon.run()

    # Check if directory was deleted
    assert not test_dir.exists()
    assert not pidfile.exists()
