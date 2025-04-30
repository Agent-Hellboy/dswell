# Dswell

A daemon-based file deletion utility that allows you to schedule files or directories for deletion after a specified time period.

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
