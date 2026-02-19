"""Tick rendering helpers for ruler scales and labels."""

from PyQt6 import QtCore, QtGui


class RulerRenderingTicksMixin:
    """Provide border tick rendering for all measurement units."""

    def getRightLabelLimit(self, painter):
        right_label_limit = self.width() - 37
        if self.height() <= 80:
            preview_resolution_text = self.buildResolutionText(self.width(), self.height(), include_y=False)
            preview_resolution_width = painter.fontMetrics().horizontalAdvance(preview_resolution_text)
            right_label_limit = self.width() - max(37, preview_resolution_width + 12)
        return right_label_limit

    def drawSubticks(self, painter, color_value):
        normal_subtick_alpha = 128
        smallest_grid_alpha = int(round(normal_subtick_alpha * 0.5))
        normal_pen = QtGui.QPen(
            QtGui.QColor(color_value, color_value, color_value, normal_subtick_alpha),
            1,
            QtCore.Qt.PenStyle.SolidLine,
        )
        smallest_grid_pen = QtGui.QPen(
            QtGui.QColor(color_value, color_value, color_value, smallest_grid_alpha),
            1,
            QtCore.Qt.PenStyle.SolidLine,
        )
        painter.setPen(normal_pen)

        x_tick_config = self.getTickConfig("x")
        y_tick_config = self.getTickConfig("y")
        x_small_step = x_tick_config["small_step_px"]
        x_medium_step = x_tick_config["medium_step_px"]
        x_major_step = x_tick_config["major_step_px"]
        y_small_step = y_tick_config["small_step_px"]
        y_medium_step = y_tick_config["medium_step_px"]
        y_major_step = y_tick_config["major_step_px"]

        if self.width() >= 88:
            x_small_pos = x_small_step
            x_tolerance = max(1.0, x_small_step * 0.2)
            while x_small_pos < self.width() - 1:
                if not self.isNearStep(x_small_pos, x_major_step, x_tolerance):
                    is_smallest_tick = False
                    if x_tick_config["distinct_subticks"] and self.isNearStep(x_small_pos, x_medium_step, x_tolerance):
                        tick_size = 10
                    elif x_tick_config["distinct_subticks"]:
                        tick_size = 5
                        is_smallest_tick = True
                    else:
                        small_index = int(round(x_small_pos / x_small_step))
                        tick_size = (((small_index - 1) % 2) + 1) * 5
                        is_smallest_tick = tick_size == 5

                    if self.grid_enabled and is_smallest_tick:
                        painter.setPen(smallest_grid_pen)
                    else:
                        painter.setPen(normal_pen)

                    if x_tick_config["distinct_subticks"]:
                        xloc = float(x_small_pos)
                        if self.grid_enabled:
                            painter.drawLine(QtCore.QLineF(xloc, 0.0, xloc, float(self.height())))
                        else:
                            painter.drawLine(QtCore.QLineF(xloc, 0.0, xloc, float(tick_size)))
                    else:
                        xloc = int(round(x_small_pos))
                        if self.grid_enabled:
                            painter.drawLine(xloc, 0, xloc, self.height())
                        else:
                            painter.drawLine(xloc, 0, xloc, tick_size)

                    if self.height() > 43 and not self.grid_enabled:
                        if x_tick_config["distinct_subticks"]:
                            painter.drawLine(
                                QtCore.QLineF(
                                    xloc,
                                    float(self.height()),
                                    xloc,
                                    float(self.height() - tick_size),
                                )
                            )
                        else:
                            painter.drawLine(xloc, self.height(), xloc, self.height() - tick_size)
                x_small_pos += x_small_step

        if self.height() > 80:
            y_small_pos = y_small_step
            y_tolerance = max(1.0, y_small_step * 0.2)
            while y_small_pos < self.height() - 1:
                if not self.isNearStep(y_small_pos, y_major_step, y_tolerance):
                    is_smallest_tick = False
                    if y_tick_config["distinct_subticks"] and self.isNearStep(y_small_pos, y_medium_step, y_tolerance):
                        tick_size = 10
                    elif y_tick_config["distinct_subticks"]:
                        tick_size = 5
                        is_smallest_tick = True
                    else:
                        small_index = int(round(y_small_pos / y_small_step))
                        tick_size = (((small_index - 1) % 2) + 1) * 5
                        is_smallest_tick = tick_size == 5

                    if self.grid_enabled and is_smallest_tick:
                        painter.setPen(smallest_grid_pen)
                    else:
                        painter.setPen(normal_pen)

                    if y_tick_config["distinct_subticks"]:
                        yloc = float(y_small_pos)
                        if self.grid_enabled:
                            painter.drawLine(QtCore.QLineF(0.0, yloc, float(self.width()), yloc))
                        else:
                            painter.drawLine(QtCore.QLineF(0.0, yloc, float(tick_size), yloc))
                    else:
                        yloc = int(round(y_small_pos))
                        if self.grid_enabled:
                            painter.drawLine(0, yloc, self.width(), yloc)
                        else:
                            painter.drawLine(0, yloc, tick_size, yloc)

                    if self.width() > 43 and not self.grid_enabled:
                        if y_tick_config["distinct_subticks"]:
                            painter.drawLine(
                                QtCore.QLineF(
                                    float(self.width()),
                                    yloc,
                                    float(self.width() - tick_size),
                                    yloc,
                                )
                            )
                        else:
                            painter.drawLine(self.width(), yloc, self.width() - tick_size, yloc)
                y_small_pos += y_small_step

        return x_tick_config, y_tick_config

    def drawMajorTicksAndLabels(self, painter, color_value, right_label_limit, x_tick_config, y_tick_config):
        pen = QtGui.QPen(QtGui.QColor(color_value, color_value, color_value, 200), 1, QtCore.Qt.PenStyle.SolidLine)
        painter.setPen(pen)

        x_major_step = x_tick_config["major_step_px"]
        x_major_unit = x_tick_config["major_unit"]
        y_major_step = y_tick_config["major_step_px"]
        y_major_unit = y_tick_config["major_unit"]

        if self.width() >= 88:
            x_major_index = 1
            x_major_pos = x_major_step
            while x_major_pos < self.width() - 1:
                xloc = int(round(x_major_pos))
                label = self.formatTickLabel(x_major_index * x_major_unit)
                if self.grid_enabled:
                    painter.drawLine(xloc, 0, xloc, self.height())
                else:
                    painter.drawLine(xloc, 0, xloc, 20)
                if self.height() > 52 and not self.grid_enabled:
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
                if self.grid_enabled:
                    painter.drawLine(0, yloc, self.width(), yloc)
                else:
                    painter.drawLine(0, yloc, 20, yloc)
                if self.width() > 52 and not self.grid_enabled:
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
