"""Utility helpers for snapping and aspect-ratio math."""

import math

from .constants import SNAP_INCREMENT


def snap(num, increment=SNAP_INCREMENT):
    """Snap a numeric value to the nearest increment."""
    return int(increment * round(float(num) / increment))


def simplify_ratio(width, height):
    """Return a simplified integer ratio for width and height."""
    ratio_width = max(1, int(width))
    ratio_height = max(1, int(height))
    divisor = math.gcd(ratio_width, ratio_height)
    return ratio_width // divisor, ratio_height // divisor
