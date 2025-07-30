"""
Logging utilities for GeoIP API.
"""

import logging
import sys
from typing import List, Optional


def setup_logging(
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Set up logging configuration.

    Args:
        level: Logging level
        log_format: Format string for log messages
        log_file: Path to log file (logs to stdout if None)
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers: List[logging.Handler] = []

    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(level=level, format=log_format, handlers=handlers)
