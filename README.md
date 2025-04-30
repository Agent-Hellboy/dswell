# dswell

A CLI tool that runs a daemon process in the background to automatically delete files or directories after a specified time period.

## Installation

```bash
# Install from source
git clone https://github.com/Agent-Hellboy/dswell.git
cd dswell
pip install -e .

# Or install directly from PyPI (when published)
pip install dswell
```

## Usage

dswell provides a simple command-line interface to create files or directories and schedule them for automatic deletion.

### Basic Commands

Create a file and schedule it for deletion:
```bash
dswell create test.txt --time 1h
```

Create a directory and schedule it for deletion:
```bash
dswell create --dir test_dir --time 30m
```

### Time Format

The `--time` option accepts time strings in the following format:
- `1h` - 1 hour
- `30m` - 30 minutes
- `45s` - 45 seconds
- `1h30m45s` - 1 hour, 30 minutes, and 45 seconds

### Examples

```bash
# Create a file that will be deleted after 1 hour
dswell create test.txt --time 1h

# Create a directory that will be deleted after 30 minutes
dswell create --dir test_dir --time 30m

# Create a file that will be deleted after 1 hour, 3 minutes, and 2 seconds
dswell create test.txt --time 1h3m2s
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/dswell.git
cd dswell

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/dswell
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