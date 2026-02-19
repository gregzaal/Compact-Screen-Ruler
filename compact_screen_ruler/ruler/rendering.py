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
        highlight_gray = 255 if not self.invert_colors else 0
        background_gray = 100 if not self.invert_colors else 120
        stroke_gray = 0 if not self.invert_colors else 255
        self.resetResolutionTextState()

        painter = QtGui.QPainter()
        painter.begin(self)

        stroke_pen = QtGui.QPen(
            QtGui.QColor(stroke_gray, stroke_gray, stroke_gray, 200), 1, QtCore.Qt.PenStyle.SolidLine
        )
        painter.setPen(stroke_pen)

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(
            QtGui.QColor(background_gray, background_gray, background_gray, (0 if self.is_transparent else 180))
        )
        painter.drawRoundedRect(QtCore.QRect(0, 0, self.width(), self.height()), 4, 4)

        transparent_pen = QtGui.QPen(
            QtGui.QColor(highlight_gray, highlight_gray, highlight_gray, 0),
            1,
            QtCore.Qt.PenStyle.SolidLine,
        )
        painter.setPen(transparent_pen)

        painter.setBrush(QtGui.QColor(highlight_gray, highlight_gray, highlight_gray, 10))
        if self.is_transparent:
            painter.drawRect(QtCore.QRect(0, 0, max(self.width(), 0), max(self.height(), 0)))
        else:
            painter.drawRect(QtCore.QRect(21, 21, max(self.width() - 21 * 2, 0), max(self.height() - 21 * 2, 0)))

        self.drawHoverHints(painter, highlight_gray)
        self.drawAlignedScreenEdges(painter)

        painter.setPen(stroke_pen)

        if not self.is_transparent:
            right_label_limit = self.getRightLabelLimit(painter)
            x_tick_config, y_tick_config = self.drawSubticks(painter, stroke_gray)
            self.drawMajorTicksAndLabels(painter, stroke_gray, right_label_limit, x_tick_config, y_tick_config)

            size_x, size_y = self.getMeasurementSize(painter)
            self.drawResolutionReadout(painter, size_x, size_y, stroke_gray)

        painter.end()
