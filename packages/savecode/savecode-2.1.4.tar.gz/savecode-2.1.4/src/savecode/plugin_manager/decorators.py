"""
savecode/plugin_manager/decorators.py - Decorators for plugin error handling.

This module provides a decorator to wrap plugin run() methods, catch exceptions,
log them, and record the error in the shared context.
"""

import functools
import logging
from typing import Any, Callable, Dict, TypeVar, cast
from savecode.utils.error_handler import log_and_record_error

F = TypeVar("F", bound=Callable[..., Any])


def handle_plugin_errors(func: F) -> F:
    """
    Decorator to wrap a plugin's run() method to catch exceptions, log the error,
    and record the error in the shared context.

    Args:
        func (Callable): The plugin's run method.

    Returns:
        Callable: The wrapped function with the same signature as the original.
    """

    @functools.wraps(func)
    def wrapper(self: Any, context: Dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, context, *args, **kwargs)
        except Exception as e:
            plugin_name = self.__class__.__name__
            message = f"Unhandled exception in plugin {plugin_name}: {e}"
            # Use the plugin's logger if available; otherwise, use a default logger.
            logger = getattr(self, "logger", logging.getLogger(plugin_name))
            log_and_record_error(message, context, logger, exc_info=True)
            return None

    return cast(F, wrapper)
