"""Painting and visual rendering logic for the ruler widget."""

from PyQt6 import QtCore, QtGui

from ..utils import simplify_ratio


class RulerRenderingMixin:
    """Provide all draw/paint behavior for the ruler widget."""

    def getTickConfig(self, axis):
        if self.measurement_unit == "px":
            return {
                "small_step_px": 5.0,
                "medium_step_px": 10.0,
                "major_step_px": 50.0,
                "major_unit": 5.0,
                "distinct_subticks": False,
            }

        major_unit = 1.0
        if self.measurement_unit == "cm":
            medium_unit = 0.5
            small_unit = 0.1
        else:
            medium_unit = 0.25
            small_unit = 0.125

        small_step_px = self.convertUnitToPixels(small_unit, axis, self.measurement_unit)
        medium_step_px = self.convertUnitToPixels(medium_unit, axis, self.measurement_unit)
        major_step_px = self.convertUnitToPixels(major_unit, axis, self.measurement_unit)

        if small_step_px <= 0 or medium_step_px <= 0 or major_step_px <= 0:
            return {
                "small_step_px": 5.0,
                "medium_step_px": 10.0,
                "major_step_px": 50.0,
                "major_unit": 5.0,
                "distinct_subticks": False,
            }

        small_step_px = max(3.0, small_step_px)
        medium_step_px = max(6.0, medium_step_px)
        major_step_px = max(20.0, major_step_px)
        return {
            "small_step_px": small_step_px,
            "medium_step_px": medium_step_px,
            "major_step_px": major_step_px,
            "major_unit": major_unit,
            "distinct_subticks": True,
        }

    def isNearStep(self, value, step, tolerance):
        if step <= 0:
            return False
        nearest_index = int(round(value / step))
        nearest_value = nearest_index * step
        return abs(value - nearest_value) <= tolerance

    def formatTickLabel(self, value):
        if self.measurement_unit == "px":
            return str(int(round(value)))
        return f"{value:.2f}".rstrip("0").rstrip(".")

    def formatMeasurementValue(self, value_px, axis):
        unit = self.measurement_unit
        if unit == "px":
            return str(int(round(float(value_px))))

        converted_value = self.convertPixelsToUnit(value_px, axis, unit)
        return f"{converted_value:.2f}".rstrip("0").rstrip(".")

    def buildResolutionText(self, size_x, size_y, include_y):
        unit = self.measurement_unit
        size_x_text = self.formatMeasurementValue(size_x, "x")
        if include_y:
            size_y_text = self.formatMeasurementValue(size_y, "y")
            return f"{size_x_text} x {size_y_text} {unit}"
        return f"{size_x_text} {unit}"

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
        self.resolution_text_click_enabled = False

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
            right_label_limit = self.width() - 37
            if self.height() <= 80:
                preview_resolution_text = self.buildResolutionText(self.width(), self.height(), include_y=False)
                preview_resolution_width = painter.fontMetrics().horizontalAdvance(preview_resolution_text)
                right_label_limit = self.width() - max(37, preview_resolution_width + 12)

            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 128), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            x_tick_config = self.getTickConfig("x")
            y_tick_config = self.getTickConfig("y")
            x_small_step = x_tick_config["small_step_px"]
            x_medium_step = x_tick_config["medium_step_px"]
            x_major_step = x_tick_config["major_step_px"]
            x_major_unit = x_tick_config["major_unit"]
            y_small_step = y_tick_config["small_step_px"]
            y_medium_step = y_tick_config["medium_step_px"]
            y_major_step = y_tick_config["major_step_px"]
            y_major_unit = y_tick_config["major_unit"]
            if self.width() >= 88:
                x_small_pos = x_small_step
                x_tolerance = max(1.0, x_small_step * 0.2)
                while x_small_pos < self.width() - 1:
                    if not self.isNearStep(x_small_pos, x_major_step, x_tolerance):
                        xloc = int(round(x_small_pos))
                        if x_tick_config["distinct_subticks"] and self.isNearStep(
                            x_small_pos, x_medium_step, x_tolerance
                        ):
                            tick_size = 10
                        elif x_tick_config["distinct_subticks"]:
                            tick_size = 5
                        else:
                            small_index = int(round(x_small_pos / x_small_step))
                            tick_size = (((small_index - 1) % 2) + 1) * 5
                        painter.drawLine(xloc, 0, xloc, tick_size)
                        if self.height() > 43:
                            painter.drawLine(xloc, self.height(), xloc, self.height() - tick_size)
                    x_small_pos += x_small_step
            if self.height() > 80:
                y_small_pos = y_small_step
                y_tolerance = max(1.0, y_small_step * 0.2)
                while y_small_pos < self.height() - 1:
                    if not self.isNearStep(y_small_pos, y_major_step, y_tolerance):
                        yloc = int(round(y_small_pos))
                        if y_tick_config["distinct_subticks"] and self.isNearStep(
                            y_small_pos, y_medium_step, y_tolerance
                        ):
                            tick_size = 10
                        elif y_tick_config["distinct_subticks"]:
                            tick_size = 5
                        else:
                            small_index = int(round(y_small_pos / y_small_step))
                            tick_size = (((small_index - 1) % 2) + 1) * 5
                        painter.drawLine(0, yloc, tick_size, yloc)
                        if self.width() > 43:
                            painter.drawLine(self.width(), yloc, self.width() - tick_size, yloc)
                    y_small_pos += y_small_step

            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                x_major_index = 1
                x_major_pos = x_major_step
                while x_major_pos < self.width() - 1:
                    xloc = int(round(x_major_pos))
                    label = self.formatTickLabel(x_major_index * x_major_unit)
                    painter.drawLine(xloc, 0, xloc, 20)
                    if self.height() > 52:
                        painter.drawLine(xloc, self.height(), xloc, self.height() - 20)

                    if xloc < right_label_limit or self.height() > 80:
                        if self.height() > 80:
                            if xloc < self.width() - 37:
                                painter.drawText(
                                    QtCore.QRect(xloc - 25, 19, 50, 15),
                                    QtCore.Qt.AlignmentFlag.AlignCenter,
                                    label,
                                )
                                painter.drawText(
                                    QtCore.QRect(xloc - 25, self.height() - 35, 50, 15),
                                    QtCore.Qt.AlignmentFlag.AlignCenter,
                                    label,
                                )
                        elif self.height() < 54:
                            painter.drawText(
                                QtCore.QRect(xloc - 25, 19, 50, 15),
                                QtCore.Qt.AlignmentFlag.AlignCenter,
                                label,
                            )
                        else:
                            painter.drawText(
                                QtCore.QRect(xloc - 25, 0, 50, self.height()),
                                QtCore.Qt.AlignmentFlag.AlignCenter,
                                label,
                            )

                    x_major_index += 1
                    x_major_pos += x_major_step
            if self.height() > 80:
                y_major_index = 1
                y_major_pos = y_major_step
                while y_major_pos < self.height() - 9:
                    yloc = int(round(y_major_pos))
                    label = self.formatTickLabel(y_major_index * y_major_unit)
                    painter.drawLine(0, yloc, 20, yloc)
                    if self.width() > 52:
                        painter.drawLine(self.width(), yloc, self.width() - 20, yloc)

                    if yloc < self.height() - 35:
                        if self.width() >= 88:
                            painter.drawText(
                                QtCore.QRect(23, yloc - 7, 50, 20),
                                QtCore.Qt.AlignmentFlag.AlignLeft,
                                label,
                            )
                            painter.drawText(
                                QtCore.QRect(self.width() - 63, yloc - 7, 40, 50),
                                QtCore.Qt.AlignmentFlag.AlignRight,
                                label,
                            )
                        elif self.width() > 62:
                            painter.drawText(
                                QtCore.QRect(0, yloc - 25, self.width(), 50),
                                QtCore.Qt.AlignmentFlag.AlignCenter,
                                label,
                            )

                    y_major_index += 1
                    y_major_pos += y_major_step

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
                resolution_text = self.buildResolutionText(size_x, size_y, include_y=True)
                resolution_draw_rect = QtCore.QRect(0, 0, self.width(), self.height())
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.resolution_text_click_enabled = True
                self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
                self.drawStatusMessages(painter, col3)
            elif self.height() > 80 and self.width() < 88:
                resolution_text = f"{self.formatMeasurementValue(size_y, 'y')} {self.measurement_unit}"
                resolution_draw_rect = QtCore.QRect(0, self.height() - 37, self.width(), 20)
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(painter, resolution_draw_rect, resolution_alignment, resolution_text)
            else:
                resolution_text = self.buildResolutionText(size_x, size_y, include_y=False)
                if self.height() < 54:
                    resolution_draw_rect = QtCore.QRect(0, 19, self.width() - 3, 15)
                else:
                    resolution_draw_rect = QtCore.QRect(0, 0, self.width() - 3, self.height())
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
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
