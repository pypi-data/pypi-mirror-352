"""
savecode/utils/logger.py - Centralized logging configuration for savecode.
This module sets up a dedicated logger for the savecode application with modular handlers.
"""

import logging


def configure_logging(level: int = logging.WARNING) -> None:
    """
    Configures the logging settings for the savecode application.

    Creates a dedicated logger named 'savecode' with a StreamHandler,
    sets a consistent log format and date format, and avoids conflicts with third-party loggers.

    :param level: Logging level (default: logging.WARNING)
    """
    logger = logging.getLogger("savecode")

    # Only configure if no handlers exist for this logger to avoid duplicate logs.
    if not logger.handlers:
        logger.setLevel(level)
        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Prevent messages from propagating to the root logger to avoid duplicate logs.
        logger.propagate = False

    # Optionally, configure the root logger if desired (uncomment the following line)
    # logging.getLogger().setLevel(level)
