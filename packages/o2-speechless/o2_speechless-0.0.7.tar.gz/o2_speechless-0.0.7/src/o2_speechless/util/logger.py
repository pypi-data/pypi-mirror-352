"""Configuration of logging"""

import logging
import sys
from typing import Optional


def configure_logging(
    log_file: Optional[str] = None, logger_name: Optional[str] = None
):
    """
    Configures the logging for the application.

    Parameters
    ----------
    log_file : str or None, optional
        The path to the log file where logs will be written, by default None.
        If None, logs will not be written to a file.
    logger_name : str or None, optional
        The name of the logger to configure, by default None.
        If None, the root logger will be configured.
    """
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("[%(asctime)s %(name)s %(levelname)s] %(message)s")

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console handlers
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setLevel(logging.INFO)
    handler_stdout.setFormatter(formatter)
    handler_stdout.addFilter(lambda record: record.levelno <= logging.WARNING)
    logger.addHandler(handler_stdout)

    handler_error = logging.StreamHandler(sys.stderr)
    handler_error.setLevel(logging.ERROR)
    handler_error.setFormatter(formatter)
    logger.addHandler(handler_error)

    # File handler (conditionally added)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
