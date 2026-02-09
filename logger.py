"""Centralized logging configuration for the M3U8 Transcript Generator."""

import logging
import sys
from typing import Optional


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level (e.g. logging.DEBUG, logging.INFO).
        log_file: Optional path to a log file. If provided, logs are also
                  written to this file.
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Avoid adding duplicate handlers on repeated calls
    if root.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
