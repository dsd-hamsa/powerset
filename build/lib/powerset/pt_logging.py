"""
PowerTrack Logging Module
========================

Consistent logging across all PowerTrack scripts.
Logs are organized by script name in the logs/ directory.

Usage:
    from powertrack.pt_logging import get_logger

    logger = get_logger('my_script')
    logger.info("Starting data fetch...")
    logger.error("Something went wrong")
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Use stdlib logging with alias to avoid conflicts
import logging as stdlib_logging


def setup_logging(script_name: str, log_level: int = stdlib_logging.INFO) -> stdlib_logging.Logger:
    """
    Setup logging for a script with organized file output.

    Args:
        script_name: Name of the script (used for log file organization)
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = stdlib_logging.getLogger(script_name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory structure
    logs_dir = Path('logs')
    script_logs_dir = logs_dir / script_name
    script_logs_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamped log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = script_logs_dir / f'{timestamp}.log'

    # File handler
    file_handler = stdlib_logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = stdlib_logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Formatter
    formatter = stdlib_logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(script_name: str, log_level: Optional[int] = None) -> stdlib_logging.Logger:
    """
    Get or create a logger for the given script name.

    Args:
        script_name: Name of the script
        log_level: Optional log level override

    Returns:
        Logger instance
    """
    if log_level is None:
        log_level = stdlib_logging.INFO

    return setup_logging(script_name, log_level)


def log_api_call(logger: stdlib_logging.Logger, method: str, endpoint: str, status_code: Optional[int] = None) -> None:
    """
    Log API call details.

    Args:
        logger: Logger instance
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code (optional)
    """
    if status_code:
        logger.info(f"API {method} {endpoint} -> {status_code}")
    else:
        logger.debug(f"API {method} {endpoint}")


def log_error_with_context(logger: stdlib_logging.Logger, error: Exception, context: str = "") -> None:
    """
    Log error with additional context.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context information
    """
    error_msg = f"{type(error).__name__}: {error}"
    if context:
        error_msg = f"{context} - {error_msg}"

    logger.error(error_msg)


def setup_global_error_logging() -> None:
    """Setup global error logging to logs/errors.log."""
    error_logger = stdlib_logging.getLogger('powertrack_errors')
    error_logger.setLevel(stdlib_logging.ERROR)

    # Avoid duplicate handlers
    if error_logger.handlers:
        return

    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)

    error_file = logs_dir / 'errors.log'
    error_handler = stdlib_logging.FileHandler(error_file, encoding='utf-8')
    error_handler.setLevel(stdlib_logging.ERROR)

    formatter = stdlib_logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(formatter)

    error_logger.addHandler(error_handler)


# Initialize global error logging
setup_global_error_logging()