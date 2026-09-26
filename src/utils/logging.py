"""Logging helpers."""

import logging
from pathlib import Path


def setup_logging(log_file: str, level: str = "INFO") -> logging.Logger:
    """Configure a logger with console and file handlers."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("spam_xai")
    logger.setLevel(level.upper())
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level.upper())

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level.upper())

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
