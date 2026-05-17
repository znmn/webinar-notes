import logging

from app.core.config import LOG_LEVEL

_VALID_LOG_LEVELS = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}


def setup_logging() -> None:
    """Configure application logging from environment settings."""
    log_level = LOG_LEVEL if LOG_LEVEL in _VALID_LOG_LEVELS else "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance for a module."""
    return logging.getLogger(name)
