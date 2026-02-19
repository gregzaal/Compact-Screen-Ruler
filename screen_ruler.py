"""Compatibility launcher script for Compact Screen Ruler.

The application logic now lives under the `compact_screen_ruler` package.
"""

from compact_screen_ruler.app import main


if __name__ == "__main__":
    raise SystemExit(main())
