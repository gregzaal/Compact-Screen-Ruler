"""Overlay and status drawing helpers for ruler rendering."""

from PyQt6 import QtCore, QtGui

from ..utils import simplify_ratio


class RulerRenderingOverlaysMixin:
    """Provide hover/edge overlays and status text drawing."""

    def drawAlignedScreenEdges(self, painter):
        is_dragging = self.leftclick or self.middleclick
        if not is_dragging:
            return

        aligned_edges = self.getScreenEdgeAlignment()
        if not any(aligned_edges.values()):
            return

        painter.save()
        pen = QtGui.QPen(QtGui.QColor(0, 255, 0, 255), 2, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        max_x = max(self.width() - 1, 0)
        max_y = max(self.height() - 1, 0)

        if aligned_edges["top"]:
            painter.drawLine(0, 0, max_x, 0)
        if aligned_edges["bottom"]:
            painter.drawLine(0, max_y, max_x, max_y)
        if aligned_edges["left"]:
            painter.drawLine(0, 0, 0, max_y)
        if aligned_edges["right"]:
            painter.drawLine(max_x, 0, max_x, max_y)

        painter.restore()

    def drawResolutionText(self, painter, draw_rect, alignment, text):
        painter.save()
        if self.resolution_text_hovered:
            text_font = QtGui.QFont(painter.font())
            text_font.setUnderline(True)
            painter.setFont(text_font)
        painter.drawText(draw_rect, alignment, text)
        painter.restore()

    def drawHoverHints(self, painter, base_color):
        is_interacting = self.leftclick or self.middleclick or self.drawPickPos
        zones_to_draw = self.active_interaction_zones if is_interacting else self.hover_zones

        if not any(zones_to_draw.values()):
            return

        grab_size = self.GRAB_HANDLE_SIZE
        width = self.width()
        height = self.height()

        painter.save()

        edge_alpha = 55 if not self.is_transparent else 35
        corner_alpha = 95 if not self.is_transparent else 65
        edge_brush = QtGui.QBrush(QtGui.QColor(base_color, base_color, base_color, edge_alpha))
        corner_brush = QtGui.QBrush(QtGui.QColor(base_color, base_color, base_color, corner_alpha))
        pen = QtGui.QPen(QtGui.QColor(base_color, base_color, base_color, 0), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        if zones_to_draw["top"]:
            painter.setBrush(edge_brush)
            painter.drawRect(QtCore.QRect(0, 0, width, grab_size))
        if zones_to_draw["bottom"]:
            painter.setBrush(edge_brush)
            painter.drawRect(QtCore.QRect(0, max(height - grab_size, 0), width, grab_size))
        if zones_to_draw["left"]:
            painter.setBrush(edge_brush)
            painter.drawRect(QtCore.QRect(0, 0, grab_size, height))
        if zones_to_draw["right"]:
            painter.setBrush(edge_brush)
            painter.drawRect(QtCore.QRect(max(width - grab_size, 0), 0, grab_size, height))

        if zones_to_draw["left"] and zones_to_draw["top"]:
            painter.setBrush(corner_brush)
            painter.drawRect(QtCore.QRect(0, 0, grab_size, grab_size))
        if zones_to_draw["right"] and zones_to_draw["top"]:
            painter.setBrush(corner_brush)
            painter.drawRect(QtCore.QRect(max(width - grab_size, 0), 0, grab_size, grab_size))
        if zones_to_draw["left"] and zones_to_draw["bottom"]:
            painter.setBrush(corner_brush)
            painter.drawRect(QtCore.QRect(0, max(height - grab_size, 0), grab_size, grab_size))
        if zones_to_draw["right"] and zones_to_draw["bottom"]:
            painter.setBrush(corner_brush)
            painter.drawRect(QtCore.QRect(max(width - grab_size, 0), max(height - grab_size, 0), grab_size, grab_size))

        painter.restore()

    def getStatusMessages(self):
        messages = []
        if self.aspect_lock_enabled:
            ratio_width, ratio_height = simplify_ratio(self.aspect_lock_target_width, self.aspect_lock_target_height)
            messages.append(f"Aspect Ratio Locked [{ratio_width}:{ratio_height}]")
        if self.clickthrough_enabled:
            messages.append("Clickthrough Mode Enabled")
        return messages

    def drawStatusMessages(self, painter, color_value):
        messages = self.getStatusMessages()
        if not messages:
            return

        painter.save()

        font = QtGui.QFont(painter.font())
        point_size = font.pointSizeF()
        if point_size > 0:
            font.setPointSizeF(point_size * 0.9)
        else:
            pixel_size = font.pixelSize()
            if pixel_size > 0:
                font.setPixelSize(max(1, int(round(pixel_size * 0.9))))
        painter.setFont(font)

        pen = QtGui.QPen(QtGui.QColor(color_value, color_value, color_value, 150), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        metrics = QtGui.QFontMetrics(font)
        line_height = metrics.height()
        start_y = int(self.height() / 2) + 10

        for index, message in enumerate(messages):
            top = start_y + (index * line_height)
            painter.drawText(
                QtCore.QRect(0, top, self.width(), line_height + 2),
                QtCore.Qt.AlignmentFlag.AlignHCenter,
                message,
            )

        painter.restore()
