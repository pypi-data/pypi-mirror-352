"""
savecode/plugins/extra_args.py - Plugin to process and parse extra command-line arguments.
This module defines a plugin that processes extra arguments into key-value pairs
and stores them in the shared context.
"""

import logging
from typing import Any, Dict, List
from savecode.plugin_manager.manager import register_plugin
from savecode.plugin_manager.decorators import handle_plugin_errors
from savecode.constants.reserved_keys import RESERVED_KEYS

logger = logging.getLogger("savecode.plugins.extra_args")


def parse_extra_args(extra_args: List[str]) -> Dict[str, Any]:
    """
    Parse extra arguments into a dictionary.

    - Arguments with '=' are split into key and value.
    - Standalone arguments are treated as boolean flags.
    Skips keys in RESERVED_KEYS.

    :param extra_args: List of argument strings.
    :return: Dictionary of parsed arguments.
    """
    parsed: Dict[str, Any] = {}
    for arg in extra_args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            if key in RESERVED_KEYS:
                logger.warning(
                    "Extra argument key '%s' is reserved and will be ignored.", key
                )
                continue
            parsed[key] = value
        else:
            if arg in RESERVED_KEYS:
                logger.warning(
                    "Extra argument flag '%s' is reserved and will be ignored.", arg
                )
                continue
            parsed[arg] = True
    return parsed


@register_plugin(order=10)
class ExtraArgsPlugin:
    """
    Processes extra command-line arguments into a key-value dictionary and stores the result in context.
    """

    @handle_plugin_errors
    def run(self, context: Dict[str, Any]) -> None:
        extra_args: List[str] = context.get("extra_args", [])
        if extra_args:
            logger.info("Extra arguments provided: %s", extra_args)
            parsed: Dict[str, Any] = parse_extra_args(extra_args)
            context["parsed_extra_args"] = parsed
            logger.info("Parsed extra arguments: %s", parsed)


# End of savecode/plugins/extra_args.py
