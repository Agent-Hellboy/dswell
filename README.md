# Dswell

[![CI](https://github.com/agent-hellboy/dswell/actions/workflows/ci.yml/badge.svg)](https://github.com/agent-hellboy/dswell/actions/workflows/ci.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/dswell.svg)](https://pypi.org/project/dswell/)
[![PyPI Downloads](https://static.pepy.tech/badge/dswell)](https://pepy.tech/projects/dswell)

A daemon-based file deletion utility that allows you to schedule files or directories for deletion after a specified time period.

Why did I create this?

- I often end up writing temporary scripts and then forgetting to delete them, so they clutter my workspace.

What does it do?

- It automatically removes files after a specified age—you just pass the duration in hours, minutes, and seconds (for example, 1h30m3s), and it deletes the file after the specified time period.


```bash
dswell
Usage: dswell [OPTIONS] COMMAND [ARGS]...

  dswell - Delayed file deletion utility

Options:
  --help  Show this message and exit.

Commands:
  create   Create a file or directory and schedule it for deletion.
  list     List all pending file/directory deletions.
  watcher  Manage the pending deletion file watcher.

```

## Installation

```bash
# Install from source
git clone https://github.com/Agent-Hellboy/dswell.git
cd dswell
pip install -e .

# Or install directly from PyPI (current source is not updated)
pip install dswell
```

## Usage

Create a file or directory that will be automatically deleted after a specified time:

```bash
# Create a file that will be deleted after 1 hour
dswell create --file test.txt --time 1h

# Create a directory that will be deleted after 30 minutes
dswell create --dir test_dir --time 30m
```

Time format supports:
- Hours (h)
- Minutes (m)
- Seconds (s)

### File Watcher

The file watcher monitors pending deletions and automatically cleans up `pending.json` when files/directories are manually deleted before their scheduled deletion time.

```bash
# Start the file watcher daemon
dswell watcher start

# Check watcher status
dswell watcher status

# Stop the watcher daemon
dswell watcher stop
```

**Features:**
- Automatically monitors all files/directories scheduled for deletion
- Removes entries from `pending.json` when files are manually deleted
- Runs as a background daemon process
- Uses efficient file system event watching (via watchdog library)

### List Pending Deletions

```bash
# View all scheduled deletions
dswell list
```

## Features

### Automatic Log Cleanup

- Logs are automatically rotated every 7 days
- Keeps up to 4 weeks (28 days) of log history
- Logs stored in `~/.dswell/dswell.log`

### Intelligent Monitoring

- File watcher automatically detects manual deletions
- Cleans up stale entries in `pending.json`
- No manual intervention required

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Agent-Hellboy/dswell.git
cd dswell

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src/dswell
```

### Code Quality

The project uses several tools to maintain code quality:

- **black**: Code formatting
- **ruff**: Linting
- **isort**: Import sorting
- **pytest**: Testing

Run all checks:
```bash
tox
```

Or run individual checks:
```bash
tox -e black  # Run black
tox -e ruff   # Run ruff
tox -e isort  # Run isort
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

Prince Roshan - [princekrroshan01@gmail.com](mailto:princekrroshan01@gmail.com)
