"""Compact Screen Ruler package.

This package contains the application entrypoint, UI dialogs, and ruler widget
logic split into focused modules.
"""

from .app import main
from .version import __version__

__all__ = ["main", "__version__"]
