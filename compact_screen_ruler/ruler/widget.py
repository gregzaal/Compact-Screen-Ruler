"""Composed ScreenRuler widget class."""

from .core import RulerCore
from .geometry import RulerGeometryMixin
from .interaction import RulerInteractionMixin
from .rendering import RulerRenderingMixin


class ScreenRuler(RulerInteractionMixin, RulerRenderingMixin, RulerGeometryMixin, RulerCore):
    """Concrete ruler widget assembled from focused behavior mixins."""
