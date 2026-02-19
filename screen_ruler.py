import math
import sys

from PyQt6 import QtCore, QtGui, QtWidgets


SNAP_INCREMENT = 5
SCREEN_EDGE_SNAP_DISTANCE = 12


def snap(num, increment=SNAP_INCREMENT):
    return int(increment * round(float(num) / increment))


def simplify_ratio(width, height):
    ratio_width = max(1, int(width))
    ratio_height = max(1, int(height))
    divisor = math.gcd(ratio_width, ratio_height)
    return ratio_width // divisor, ratio_height // divisor


class ChooseGeometry(QtWidgets.QDialog):
    def __init__(self, prev_geo):
        super().__init__()

        self.setWindowTitle("Set Position and Size")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.label_size = QtWidgets.QLabel("Size: ", self)
        self.label_pos = QtWidgets.QLabel("Position: ", self)
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.label_size)
        vbox1.addWidget(self.label_pos)

        self.size_x = QtWidgets.QSpinBox(self)
        self.size_x.setRange(-99999, 99999)
        self.size_x.setPrefix("Width: ")
        self.size_x.setValue(prev_geo[2])
        self.pos_x = QtWidgets.QSpinBox(self)
        self.pos_x.setRange(-99999, 99999)
        self.pos_x.setPrefix("X: ")
        self.pos_x.setValue(prev_geo[0])
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.size_x)
        vbox2.addWidget(self.pos_x)

        self.size_y = QtWidgets.QSpinBox(self)
        self.size_y.setRange(-99999, 99999)
        self.size_y.setPrefix("Height: ")
        self.size_y.setValue(prev_geo[3])
        self.pos_y = QtWidgets.QSpinBox(self)
        self.pos_y.setRange(-99999, 99999)
        self.pos_y.setPrefix("Y: ")
        self.pos_y.setValue(prev_geo[1])
        vbox3 = QtWidgets.QVBoxLayout()
        vbox3.addWidget(self.size_y)
        vbox3.addWidget(self.pos_y)

        main_hbox = QtWidgets.QHBoxLayout()
        main_hbox.addLayout(vbox1)
        main_hbox.addLayout(vbox2)
        main_hbox.addLayout(vbox3)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel,
            QtCore.Qt.Orientation.Horizontal,
            self,
        )

        main_vbox = QtWidgets.QVBoxLayout()
        main_vbox.addLayout(main_hbox)
        main_vbox.addWidget(self.buttons)

        self.setLayout(main_vbox)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # Box layouts have their own tab order - tell it manually where to go
        self.setTabOrder(self.pos_x, self.pos_y)
        self.setTabOrder(self.pos_y, self.size_x)
        self.setTabOrder(self.size_x, self.size_y)
        self.setTabOrder(self.size_y, self.buttons)

        self.size_x.setFocus()
        self.size_x.selectAll()

    def get_values(self):
        return [self.pos_x.value(), self.pos_y.value(), self.size_x.value(), self.size_y.value()]

    def getValues(self):
        return self.get_values()


class HelpDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Help and Info")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.resize(420, 250)
        self.setMinimumSize(360, 220)

        text = (
            "This program is a simple tool you can use to measure distances on your screen, "
            "such as the width of a banner on some website.\n\n"
            "This compact tool has almost no interface. All interactions are done through a "
            "handful of hotkeys:\n\n"
            "Q / Ctrl+Q\tQuit\n"
            "F\t\tSwap the X and Y axis dimensions\n"
            "S\t\tSet the window position and size to exact values\n"
            "R\t\tReset the window size and position to defaults\n"
            "T\t\tMake the window transparent\n"
            "I\t\tSwitch between light and dark colors\n"
            "C\t\tToggle clickthrough mode\n"
            "L\t\tLock/unlock aspect ratio while resizing\n"
            "Ctrl\t\tHold down Ctrl to snap to increments of 5\n"
            "Shift\t\tHold down Shift to disable screen-edge snapping\n"
            "Ctrl + S\t\tTake a screenshot of what's behind the ruler\n"
            "F1 / H\t\tDisplay this Help dialog"
        )
        self.main_label = QtWidgets.QLabel(text)
        self.main_label.setWordWrap(True)
        self.main_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(0)
        layout.addWidget(self.main_label)

        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)


class ScreenRuler(QtWidgets.QWidget):
    MIN_WINDOW_SIZE = 10
    GRAB_HANDLE_SIZE = 21

    def getResolutionTextRect(self, draw_rect, alignment, text):
        metrics = QtGui.QFontMetrics(self.font())
        flags = int(alignment) | int(QtCore.Qt.TextFlag.TextSingleLine)
        return metrics.boundingRect(draw_rect, flags, text)

    def getResizeHitZones(self, local_x, local_y):
        grab_size = self.GRAB_HANDLE_SIZE
        width = self.width()
        height = self.height()

        return {
            "left": local_x < grab_size,
            "right": local_x > width - grab_size,
            "top": local_y < grab_size,
            "bottom": local_y > height - grab_size,
        }

    def getResizeCursorShape(self, hover_zones):
        on_left = hover_zones["left"]
        on_right = hover_zones["right"]
        on_top = hover_zones["top"]
        on_bottom = hover_zones["bottom"]

        if (on_left and on_top) or (on_right and on_bottom):
            return QtCore.Qt.CursorShape.SizeFDiagCursor
        if (on_right and on_top) or (on_left and on_bottom):
            return QtCore.Qt.CursorShape.SizeBDiagCursor
        if on_left or on_right:
            return QtCore.Qt.CursorShape.SizeHorCursor
        if on_top or on_bottom:
            return QtCore.Qt.CursorShape.SizeVerCursor
        return QtCore.Qt.CursorShape.OpenHandCursor

    def getScreenGeometryForRect(self, x_pos, y_pos, width, height):
        center_point = QtCore.QPoint(int(x_pos + width / 2), int(y_pos + height / 2))
        screen = QtGui.QGuiApplication.screenAt(center_point)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()
        return screen.availableGeometry() if screen else QtCore.QRect()

    def snapPositionToScreenEdges(self, x_pos, y_pos, width, height):
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return x_pos, y_pos

        snap_distance = SCREEN_EDGE_SNAP_DISTANCE
        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        x_candidates = [(abs(x_pos - left_edge), left_edge), (abs((x_pos + width) - right_edge), right_edge - width)]
        y_candidates = [(abs(y_pos - top_edge), top_edge), (abs((y_pos + height) - bottom_edge), bottom_edge - height)]

        x_distance, snapped_x = min(x_candidates, key=lambda item: item[0])
        y_distance, snapped_y = min(y_candidates, key=lambda item: item[0])

        if x_distance <= snap_distance:
            x_pos = snapped_x
        if y_distance <= snap_distance:
            y_pos = snapped_y

        return x_pos, y_pos

    def snapResizeGeometryToScreenEdges(self, x_pos, y_pos, width, height, on_left, on_right, on_top, on_bottom):
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return x_pos, y_pos, width, height

        snap_distance = SCREEN_EDGE_SNAP_DISTANCE
        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        right_side = x_pos + width
        bottom_side = y_pos + height

        if on_left and abs(x_pos - left_edge) <= snap_distance:
            x_pos = left_edge
            width = max(self.MIN_WINDOW_SIZE, right_side - x_pos)
            right_side = x_pos + width
        if on_right and abs(right_side - right_edge) <= snap_distance:
            width = max(self.MIN_WINDOW_SIZE, right_edge - x_pos)
            right_side = x_pos + width

        if on_top and abs(y_pos - top_edge) <= snap_distance:
            y_pos = top_edge
            height = max(self.MIN_WINDOW_SIZE, bottom_side - y_pos)
            bottom_side = y_pos + height
        if on_bottom and abs(bottom_side - bottom_edge) <= snap_distance:
            height = max(self.MIN_WINDOW_SIZE, bottom_edge - y_pos)

        return x_pos, y_pos, width, height

    def getScreenEdgeAlignment(self):
        x_pos = self.pos().x()
        y_pos = self.pos().y()
        width = self.width()
        height = self.height()
        screen_rect = self.getScreenGeometryForRect(x_pos, y_pos, width, height)
        if screen_rect.isNull():
            return {"left": False, "right": False, "top": False, "bottom": False}

        left_edge = screen_rect.x()
        top_edge = screen_rect.y()
        right_edge = left_edge + screen_rect.width()
        bottom_edge = top_edge + screen_rect.height()

        return {
            "left": x_pos == left_edge,
            "right": x_pos + width == right_edge,
            "top": y_pos == top_edge,
            "bottom": y_pos + height == bottom_edge,
        }

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

    def updateHoverState(self, local_x, local_y):
        hover_zones = self.getResizeHitZones(local_x, local_y)
        if hover_zones != self.hover_zones:
            self.hover_zones = hover_zones
            self.update()

        if self.middleclick:
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            return

        if self.leftclick:
            return

        is_over_resolution_text = not self.is_transparent and self.resolution_text_rect.contains(
            QtCore.QPoint(local_x, local_y)
        )
        if self.resolution_text_hovered != is_over_resolution_text:
            self.resolution_text_hovered = is_over_resolution_text
            self.update()

        if is_over_resolution_text:
            self.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
            return

        self.setCursor(self.getResizeCursorShape(hover_zones))

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

        # Grab bars
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
            # Small ticks
            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 128), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1, int(self.width() + 1 / space)):
                    xloc = x * space
                    if xloc % 50 != 0:
                        if xloc < self.width() - 1:
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
                    if yloc % 50 != 0:
                        if yloc < self.height() - 1:
                            painter.drawLine(0, yloc, (((y - 1) % 2) + 1) * 5, yloc)
                            if self.width() > 43:
                                painter.drawLine(self.width(), yloc, self.width() - (((y - 1) % 2) + 1) * 5, yloc)

            # Big ticks
            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1, int(self.width() + 1 / space)):
                    xloc = x * space * 10
                    if xloc < self.width() - 1:
                        painter.drawLine(xloc, 0, xloc, 20)
                        if self.height() > 52:  # Bottom Line
                            painter.drawLine(xloc, self.height(), xloc, self.height() - 20)

                        # Numbers
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
                        if self.width() > 52:  # Right Line
                            painter.drawLine(self.width(), yloc, self.width() - 20, yloc)

                        # Numbers
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

            # Size display
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
                self.drawResolutionText(
                    painter,
                    resolution_draw_rect,
                    resolution_alignment,
                    resolution_text,
                )
                self.drawStatusMessages(painter, col3)
            elif self.height() > 80 and self.width() < 88:
                resolution_text = str(size_y)
                resolution_draw_rect = QtCore.QRect(0, self.height() - 37, self.width(), 20)
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(
                    painter,
                    resolution_draw_rect,
                    resolution_alignment,
                    resolution_text,
                )
            else:
                resolution_text = str(size_x)
                resolution_draw_rect = QtCore.QRect(
                    0, int(max(self.height() / 2 - 6.5, 20)), self.width() - 3, self.height()
                )
                resolution_alignment = QtCore.Qt.AlignmentFlag.AlignRight
                self.resolution_text_rect = self.getResolutionTextRect(
                    resolution_draw_rect, resolution_alignment, resolution_text
                )
                self.drawResolutionText(
                    painter,
                    resolution_draw_rect,
                    resolution_alignment,
                    resolution_text,
                )

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

    def setAspectLockTarget(self, width, height):
        self.aspect_lock_target_width = max(1, abs(int(width)))
        self.aspect_lock_target_height = max(1, abs(int(height)))
        self.aspect_lock_ratio = self.aspect_lock_target_width / self.aspect_lock_target_height

    def __init__(self):
        super().__init__()

        self.leftclick = False
        self.middleclick = False
        self.drawPickPos = False

        self.window_size_x = 690
        self.window_size_y = 70

        self.is_transparent = False
        self.invert_colors = False
        self.aspect_lock_enabled = False
        self.aspect_lock_target_width = self.window_size_x
        self.aspect_lock_target_height = self.window_size_y
        self.aspect_lock_ratio = self.window_size_x / self.window_size_y if self.window_size_y else 1.0
        self.help_dialog = None
        self.clickthrough_enabled = False
        self.hover_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.resolution_text_hovered = False
        self.resolution_text_rect = QtCore.QRect()
        self.left_press_started_on_resolution_text = False
        self.left_dragged_since_press = False
        self.press_global_pos = QtCore.QPoint(0, 0)
        self.offset = QtCore.QPoint(0, 0)

        # hiding title bar, always on top
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowTitle("Compact Screen Ruler")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # setting window size and position
        self.resize(self.window_size_x, self.window_size_y)
        self.center()

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        # Hotkeys
        self.shortcuts = []
        shortcut_map = {
            "Q": self.close,
            "Ctrl+Q": self.close,
            "S": self.setWindowSize,
            "F": self.flipOrientation,
            "R": self.resetWindow,
            "T": self.makeTransparent,
            "I": self.doInvertColors,
            "C": self.toggleClickthroughMode,
            "L": self.toggleAspectRatioLock,
            "Ctrl+S": self.takeScreenshot,
            "F1": self.displayHelp,
            "H": self.displayHelp,
        }
        for keys, callback in shortcut_map.items():
            shortcut = QtGui.QShortcut(QtGui.QKeySequence(keys), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

        self.disable_clickthrough_button = QtWidgets.QPushButton("Disable Clickthrough Mode", None)
        self.disable_clickthrough_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.disable_clickthrough_button.setWindowFlags(
            QtCore.Qt.WindowType.Tool
            | QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.disable_clickthrough_button.clicked.connect(self.disableClickthroughMode)
        self.disable_clickthrough_button.hide()
        self.updateClickthroughButtonGeometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateClickthroughButtonGeometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.updateClickthroughButtonGeometry()

    def updateClickthroughButtonGeometry(self):
        button_width = min(
            max(170, self.disable_clickthrough_button.sizeHint().width() + 16),
            max(50, self.width() - 16),
        )
        button_height = self.disable_clickthrough_button.sizeHint().height()
        local_x = int((self.width() - button_width) / 2)
        local_y = max(8, self.height() - button_height - 8)
        global_pos = self.mapToGlobal(QtCore.QPoint(local_x, local_y))
        x_pos = global_pos.x()
        y_pos = global_pos.y()
        self.disable_clickthrough_button.setGeometry(x_pos, y_pos, button_width, button_height)

    def setClickthroughEnabled(self, enabled):
        enabled = bool(enabled)
        if self.clickthrough_enabled == enabled:
            return

        self.clickthrough_enabled = enabled
        self.setWindowFlag(QtCore.Qt.WindowType.WindowTransparentForInput, enabled)
        self.show()
        self.disable_clickthrough_button.setVisible(enabled)
        if enabled:
            self.disable_clickthrough_button.raise_()
            self.updateClickthroughButtonGeometry()
        else:
            self.raise_()
            self.activateWindow()
        self.update()

    def toggleClickthroughMode(self):
        self.setClickthroughEnabled(not self.clickthrough_enabled)

    def disableClickthroughMode(self):
        self.setClickthroughEnabled(False)

    def center(self):
        qr = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        cp = screen.availableGeometry().center() if screen else QtCore.QPoint(0, 0)
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        local_pos = event.position().toPoint()
        self.left_press_started_on_resolution_text = (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.resolution_text_rect.contains(local_pos)
            and not self.is_transparent
        )
        self.left_dragged_since_press = False
        self.press_global_pos = event.globalPosition().toPoint()

        self.leftclick = event.button() == QtCore.Qt.MouseButton.LeftButton
        self.middleclick = event.button() == QtCore.Qt.MouseButton.MiddleButton
        self.drawPickPos = event.button() == QtCore.Qt.MouseButton.RightButton
        self.offset = event.pos()
        self.opos = self.pos()

        if self.middleclick:
            self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        elif self.leftclick:
            press_zones = self.getResizeHitZones(local_pos.x(), local_pos.y())
            self.active_interaction_zones = dict(press_zones)
            if any(press_zones.values()):
                self.setCursor(self.getResizeCursorShape(press_zones))
            else:
                self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
        else:
            self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}

    def mouseMoveEvent(self, event):
        ctrl_is_held = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        shift_is_held = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier)
        screen_edge_snap_enabled = not shift_is_held
        window_x = self.pos().x()
        window_y = self.pos().y()
        global_pos = event.globalPosition()
        global_x = int(global_pos.x())
        global_y = int(global_pos.y())
        local_pos = event.position().toPoint()
        self.updateHoverState(local_pos.x(), local_pos.y())

        self.mouse_x = global_x
        self.mouse_y = global_y

        if self.middleclick:
            move_x = global_x - self.offset.x()
            move_y = global_y - self.offset.y()
            if screen_edge_snap_enabled:
                move_x, move_y = self.snapPositionToScreenEdges(move_x, move_y, self.window_size_x, self.window_size_y)
            if ctrl_is_held:
                self.move(snap(move_x), snap(move_y))
            else:
                self.move(move_x, move_y)
            self.update()
        elif self.leftclick:
            drag_distance = (global_pos.toPoint() - self.press_global_pos).manhattanLength()
            if drag_distance >= QtWidgets.QApplication.startDragDistance():
                self.left_dragged_since_press = True

            local_x = self.offset.x()
            local_y = self.offset.y()
            gsize = self.GRAB_HANDLE_SIZE

            resize_x = None
            resize_y = None

            move_x = None
            move_y = None

            if local_x > self.window_size_x - gsize and local_y > self.window_size_y - gsize:  # bottom right
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
            elif local_x < gsize and local_y > self.window_size_y - gsize:  # bottom left
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
                move_x = global_x - local_x
                move_y = window_y
            elif local_x > self.window_size_x - gsize and local_y < gsize:  # top right
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = window_x
                move_y = global_y - local_y
            elif local_x < gsize and local_y < gsize:  # top left
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = global_x - local_x
                move_y = global_y - local_y
            elif local_y > self.window_size_y - gsize:  # bottom edge
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x)
                resize_y = max(self.MIN_WINDOW_SIZE, global_y - window_y + (self.window_size_y - local_y))
            elif local_y < gsize:  # top edge
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y - global_y + self.opos.y() + local_y)
                move_x = window_x
                move_y = global_y - local_y
            elif local_x > self.window_size_x - gsize:  # right edge
                resize_x = max(self.MIN_WINDOW_SIZE, global_x - window_x + (self.window_size_x - local_x))
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y)
            elif local_x < gsize:  # left edge
                resize_x = max(self.MIN_WINDOW_SIZE, self.window_size_x - global_x + self.opos.x() + local_x)
                resize_y = max(self.MIN_WINDOW_SIZE, self.window_size_y)
                move_x = global_x - local_x
                move_y = window_y
            else:
                move_x = global_x - local_x
                move_y = global_y - local_y

            on_left = local_x < gsize
            on_right = local_x > self.window_size_x - gsize
            on_top = local_y < gsize
            on_bottom = local_y > self.window_size_y - gsize

            if self.aspect_lock_enabled and resize_x is not None and resize_y is not None:
                ratio = self.aspect_lock_ratio if self.aspect_lock_ratio > 0 else 1.0
                base_resize_x = resize_x
                base_resize_y = resize_y
                delta_x = abs(base_resize_x - self.window_size_x)
                delta_y = abs(base_resize_y - self.window_size_y)

                if delta_x >= delta_y:
                    resize_x = max(self.MIN_WINDOW_SIZE, base_resize_x)
                    resize_y = max(self.MIN_WINDOW_SIZE, int(round(resize_x / ratio)))
                    resize_x = max(self.MIN_WINDOW_SIZE, int(round(resize_y * ratio)))
                else:
                    resize_y = max(self.MIN_WINDOW_SIZE, base_resize_y)
                    resize_x = max(self.MIN_WINDOW_SIZE, int(round(resize_y * ratio)))
                    resize_y = max(self.MIN_WINDOW_SIZE, int(round(resize_x / ratio)))

                orig_left = self.opos.x()
                orig_top = self.opos.y()
                orig_right = orig_left + self.window_size_x
                orig_bottom = orig_top + self.window_size_y

                if on_left and not on_right:
                    move_x = orig_right - resize_x
                elif on_right and not on_left:
                    move_x = orig_left
                elif not on_left and not on_right:
                    move_x = orig_left + int(round((self.window_size_x - resize_x) / 2))

                if on_top and not on_bottom:
                    move_y = orig_bottom - resize_y
                elif on_bottom and not on_top:
                    move_y = orig_top
                elif not on_top and not on_bottom:
                    move_y = orig_top + int(round((self.window_size_y - resize_y) / 2))

            if screen_edge_snap_enabled:
                if resize_x is not None and resize_y is not None:
                    geometry_x = move_x if move_x is not None else window_x
                    geometry_y = move_y if move_y is not None else window_y
                    geometry_x, geometry_y, resize_x, resize_y = self.snapResizeGeometryToScreenEdges(
                        geometry_x,
                        geometry_y,
                        resize_x,
                        resize_y,
                        on_left,
                        on_right,
                        on_top,
                        on_bottom,
                    )
                    move_x = geometry_x
                    move_y = geometry_y
                elif move_x is not None and move_y is not None:
                    move_x, move_y = self.snapPositionToScreenEdges(
                        move_x, move_y, self.window_size_x, self.window_size_y
                    )

            if resize_x is not None and resize_y is not None:
                if ctrl_is_held:
                    self.resize(snap(resize_x), snap(resize_y))
                else:
                    self.resize(resize_x, resize_y)
            if move_x is not None and move_y is not None:
                if ctrl_is_held:
                    self.move(snap(move_x), snap(move_y))
                else:
                    self.move(move_x, move_y)
            self.update()

        else:
            self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hover_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.resolution_text_hovered = False
        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        self.update()

    def mouseReleaseEvent(self, event):
        release_pos = event.position().toPoint()
        should_open_size_dialog = (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.left_press_started_on_resolution_text
            and not self.left_dragged_since_press
            and not self.is_transparent
            and self.resolution_text_rect.contains(release_pos)
        )

        self.leftclick = False
        self.middleclick = False
        self.window_size_x = self.width()
        self.window_size_y = self.height()
        self.drawPickPos = False
        self.active_interaction_zones = {"left": False, "right": False, "top": False, "bottom": False}
        self.left_press_started_on_resolution_text = False
        self.left_dragged_since_press = False
        local_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        self.updateHoverState(local_pos.x(), local_pos.y())
        self.update()

        if should_open_size_dialog:
            self.setWindowSize()

    def setWindowSize(self):
        dialog = ChooseGeometry([self.pos().x(), self.pos().y(), self.window_size_x, self.window_size_y])

        values = []
        if dialog.exec():
            values = dialog.get_values()

        if values:
            pos_x, pos_y, size_x, size_y = values
            self.move(pos_x, pos_y)
            self.resize(size_x, size_y)
            self.window_size_x = size_x
            self.window_size_y = size_y
            if self.aspect_lock_enabled:
                self.setAspectLockTarget(size_x, size_y)

    def flipOrientation(self):
        width = self.width()
        height = self.height()

        self.resize(height, width)
        self.window_size_x = height
        self.window_size_y = width
        if self.aspect_lock_enabled:
            self.setAspectLockTarget(self.window_size_x, self.window_size_y)

    def resetWindow(self):
        self.window_size_x = 500
        self.window_size_y = 70
        self.resize(self.window_size_x, self.window_size_y)
        self.center()

    def makeTransparent(self):
        self.is_transparent = not self.is_transparent
        self.doInvertColors()
        self.update()

    def doInvertColors(self):
        self.invert_colors = not self.invert_colors
        self.update()

    def toggleAspectRatioLock(self):
        self.aspect_lock_enabled = not self.aspect_lock_enabled
        if self.aspect_lock_enabled:
            self.setAspectLockTarget(self.width(), self.height())
        self.update()

    def takeScreenshot(self):
        window_x = self.pos().x()
        window_y = self.pos().y()
        window_w = self.width()
        window_h = self.height()

        center_point = self.frameGeometry().center()
        screen = QtGui.QGuiApplication.screenAt(center_point)
        if not screen:
            screen = QtGui.QGuiApplication.primaryScreen()

        if not screen:
            return

        self.hide()

        screen_geo = screen.geometry()
        local_x = window_x - screen_geo.x()
        local_y = window_y - screen_geo.y()
        screenshot = screen.grabWindow(0, local_x, local_y, window_w, window_h)

        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save screenshot", "", "PNG File (*.png)")
        if fname and not fname.lower().endswith(".png"):
            fname += ".png"

        if fname:
            screenshot.save(fname, "png")

        self.show()

    def displayHelp(self):
        if self.help_dialog is None:
            self.help_dialog = HelpDialog()

        self.help_dialog.show()
        self.help_dialog.raise_()
        self.help_dialog.activateWindow()


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icon.ico"))
    exm = ScreenRuler()
    exm.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
