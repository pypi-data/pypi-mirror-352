"""
savecode/plugin_manager/__init__.py - Initializes the plugin_manager module for savecode.
"""

__all__ = ["register_plugin", "run_plugins", "list_plugins"]
from .manager import register_plugin, run_plugins, list_plugins
