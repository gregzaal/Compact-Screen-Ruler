"""Composed painting pipeline for the ruler widget."""

from PyQt6 import QtCore, QtGui

from .rendering_format import RulerRenderingFormatMixin
from .rendering_overlays import RulerRenderingOverlaysMixin
from .rendering_text import RulerRenderingTextMixin
from .rendering_ticks import RulerRenderingTicksMixin


class RulerRenderingMixin(
    RulerRenderingTicksMixin,
    RulerRenderingTextMixin,
    RulerRenderingOverlaysMixin,
    RulerRenderingFormatMixin,
):
    """Coordinate paint flow using focused rendering mixins."""

    def paintEvent(self, _event):
        col1 = 255 if not self.invert_colors else 0
        col2 = 100 if not self.invert_colors else 155
        col3 = 0 if not self.invert_colors else 255
        self.resetResolutionTextState()

        painter = QtGui.QPainter()
        painter.begin(self)

        pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QColor(col2, col2, col2, (0 if self.is_transparent else 180)))
        painter.drawRoundedRect(QtCore.QRect(0, 0, self.width(), self.height()), 4, 4)

        pen = QtGui.QPen(QtGui.QColor(col1, col1, col1, 0), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        painter.setBrush(QtGui.QColor(col1, col1, col1, 25))
        if self.is_transparent:
            painter.drawRect(QtCore.QRect(0, 0, max(self.width(), 0), max(self.height(), 0)))
        else:
            painter.drawRect(QtCore.QRect(21, 21, max(self.width() - 21 * 2, 0), max(self.height() - 21 * 2, 0)))

        self.drawHoverHints(painter, col1)
        self.drawAlignedScreenEdges(painter)

        pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        if not self.is_transparent:
            right_label_limit = self.getRightLabelLimit(painter)
            x_tick_config, y_tick_config = self.drawSubticks(painter, col3)
            self.drawMajorTicksAndLabels(painter, col3, right_label_limit, x_tick_config, y_tick_config)

            size_x, size_y = self.getMeasurementSize(painter)
            self.drawResolutionReadout(painter, size_x, size_y, col3)

        painter.end()
