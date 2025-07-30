"""
savecode/utils/error_handler.py - Helper functions for error logging and aggregation.

Provides a unified function to log messages and record them in the shared context.
"""

from typing import Dict, Any, List
import logging


def log_and_record_error(
    message: str,
    context: Dict[str, Any],
    logger: logging.Logger,
    level: str = "error",
    **kwargs: Any,
) -> None:
    """Log a message and record it in the context's error list.

    Args:
        message (str): The error message to log and record.
        context (Dict[str, Any]): The shared context dictionary where errors are aggregated.
        logger (logging.Logger): The logger instance to use for logging.
        level (str, optional): Logging level; one of "error", "warning", "info", or "debug". Defaults to "error".
        **kwargs: Additional keyword arguments to pass to the logger (e.g., exc_info=True).

    Returns:
        None
    """
    level = level.lower()
    if level == "error":
        logger.error(message, **kwargs)
    elif level == "warning":
        logger.warning(message, **kwargs)
    elif level == "info":
        logger.info(message, **kwargs)
    else:
        logger.debug(message, **kwargs)
    errors: List[str] = context.setdefault("errors", [])
    errors.append(message)
