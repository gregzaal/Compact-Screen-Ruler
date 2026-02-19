"""Painting and visual rendering logic for the ruler widget."""

from PyQt6 import QtCore, QtGui

from ..utils import simplify_ratio


class RulerRenderingMixin:
    """Provide all draw/paint behavior for the ruler widget."""

    def drawAlignedScreenEdges(self, painter):
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

    def paintEvent(self, _event):
        col1 = 255 if not self.invert_colors else 0
        col2 = 100 if not self.invert_colors else 155
        col3 = 0 if not self.invert_colors else 255
        self.resolution_text_rect = QtCore.QRect()

        space = 5
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
            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 128), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1, int(self.width() + 1 / space)):
                    xloc = x * space
                    if xloc % 50 != 0 and xloc < self.width() - 1:
                        painter.drawLine(xloc, 0, xloc, (((x - 1) % 2) + 1) * 5)
                        if self.height() > 43:
                            painter.drawLine(xloc, self.height(), xloc, self.height() - (((x - 1) % 2) + 1) * 5)
            if self.height() > 80:
                if self.width() >= 88:
                    rangestart = 2
                    rangeend = -1
                else:
                    rangestart = 0
                    rangeend = 1

                for y in range(rangestart, int(self.height() / space + rangeend)):
                    yloc = y * space
                    if yloc % 50 != 0 and yloc < self.height() - 1:
                        painter.drawLine(0, yloc, (((y - 1) % 2) + 1) * 5, yloc)
                        if self.width() > 43:
                            painter.drawLine(self.width(), yloc, self.width() - (((y - 1) % 2) + 1) * 5, yloc)

            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1, int(self.width() + 1 / space)):
                    xloc = x * space * 10
                    if xloc < self.width() - 1:
                        painter.drawLine(xloc, 0, xloc, 20)
                        if self.height() > 52:
                            painter.drawLine(xloc, self.height(), xloc, self.height() - 20)

                        if xloc < self.width() - 37 or self.height() > 80:
                            if self.height() > 80:
                                if xloc < self.width() - 37:
                                    painter.drawText(
                                        QtCore.QRect(xloc - 25, 19, 50, 15),
                                        QtCore.Qt.AlignmentFlag.AlignCenter,
                                        str(xloc),
                                    )
                                    painter.drawText(
                                        QtCore.QRect(xloc - 25, self.height() - 35, 50, 15),
                                        QtCore.Qt.AlignmentFlag.AlignCenter,
                                        str(xloc),
                                    )
                            elif self.height() < 54:
                                painter.drawText(
                                    QtCore.QRect(xloc - 25, 19, 50, 15),
                                    QtCore.Qt.AlignmentFlag.AlignCenter,
                                    str(xloc),
                                )
                            else:
                                painter.drawText(
                                    QtCore.QRect(xloc - 25, 0, 50, self.height()),
                                    QtCore.Qt.AlignmentFlag.AlignCenter,
                                    str(xloc),
                                )
            if self.height() > 80:
                for y in range(1, int(self.height() / space / 10) + 1):
                    yloc = y * space * 10
                    if yloc < self.height() - 9:
                        painter.drawLine(0, yloc, 20, yloc)
                        if self.width() > 52:
                            painter.drawLine(self.width(), yloc, self.width() - 20, yloc)

                        if yloc < self.height() - 35:
                            if self.width() >= 88:
                                painter.drawText(
                                    QtCore.QRect(23, yloc - 7, 50, 20),
                                    QtCore.Qt.AlignmentFlag.AlignLeft,
                                    str(yloc),
                                )
                                painter.drawText(
                                    QtCore.QRect(self.width() - 63, yloc - 7, 40, 50),
                                    QtCore.Qt.AlignmentFlag.AlignRight,
                                    str(yloc),
                                )
                            elif self.width() > 62:
                                painter.drawText(
                                    QtCore.QRect(0, yloc - 25, self.width(), 50),
                                    QtCore.Qt.AlignmentFlag.AlignCenter,
                                    str(yloc),
                                )

            size_x = self.width()
            size_y = self.height()
            if self.drawPickPos:
                mouse_xpos = self.mouse_x - self.pos().x()
                mouse_ypos = self.mouse_y - self.pos().y()
                size_x = mouse_xpos
                size_y = mouse_ypos
                if self.height() > 80 and self.width() >= 88:
                    painter.drawLine(mouse_xpos, 0, mouse_xpos, self.height())
                    painter.drawLine(0, mouse_ypos, self.width(), mouse_ypos)
                elif self.width() >= 88:
                    painter.drawLine(mouse_xpos, 0, mouse_xpos, self.height())
                else:
                    painter.drawLine(0, mouse_ypos, self.width(), mouse_ypos)

            if self.height() > 80 and self.width() >= 88:
                resolution_text = f"{size_x} x {size_y}"
                resolution_draw_rect = QtCore.QRect(0, 0, self.width(), self.height())
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
                self.drawStatusMessages(painter, col3)
            elif self.height() > 80 and self.width() < 88:
                resolution_text = str(size_y)
                resolution_draw_rect = QtCore.QRect(0, self.height() - 37, self.width(), 20)
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
            else:
                resolution_text = str(size_x)
                resolution_draw_rect = QtCore.QRect(
                    0, int(max(self.height() / 2 - 6.5, 20)), self.width() - 3, self.height()
                )
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignRight
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)

        painter.end()

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
