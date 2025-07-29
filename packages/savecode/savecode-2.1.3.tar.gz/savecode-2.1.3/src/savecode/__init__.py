"""
src/savecode/__init__.py
Keep runtime version in sync with packaging metadata.
"""

from importlib.metadata import version

# Get version from installed package metadata
__version__ = version(__name__)

__all__ = ["run_plugins", "list_plugins"]
from .plugin_manager import run_plugins, list_plugins
