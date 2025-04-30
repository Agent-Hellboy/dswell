import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name: str = "dswell") -> logging.Logger:
    """
    Set up and configure the logger for dswell.

    Args:
        name: Name of the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create .dswell directory if it doesn't exist
    dswell_dir = Path.home() / ".dswell"
    dswell_dir.mkdir(exist_ok=True)

    # Configure logger
    logger = logging.getLogger(name)

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Prevent propagation to root logger

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter("%(message)s")  # Simple format for console

    # File handler (with rotation) - captures all levels
    log_file = dswell_dir / "dswell.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5  # 1MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler - only shows INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Create a default logger instance
logger = setup_logger()
