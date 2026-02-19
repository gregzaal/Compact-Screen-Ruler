"""Application entrypoint helpers for Compact Screen Ruler."""

import sys

from PyQt6 import QtGui, QtWidgets

from .ruler_widget import ScreenRuler


def main():
    """Start the Qt application and run the ruler widget event loop."""
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icon.ico"))
    exm = ScreenRuler()
    exm.show()
    return app.exec()
