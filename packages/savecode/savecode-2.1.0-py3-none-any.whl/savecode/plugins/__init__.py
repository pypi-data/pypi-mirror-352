"""
savecode/plugins/__init__.py - Initialize the plugins package for savecode.
"""

# Import plugins to ensure they are registered.
__all__ = ["gather", "save", "extra_args", "git_status"]
from . import git_status
from . import gather
from . import save
from . import extra_args
