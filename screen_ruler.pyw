import math
import sys

from PyQt6 import QtCore, QtGui, QtWidgets


SNAP_INCREMENT = 5


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

        self.label_pos = QtWidgets.QLabel("Position: ", self)
        self.label_size = QtWidgets.QLabel("Size: ", self)
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.label_pos)
        vbox1.addWidget(self.label_size)

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
            "L\t\tLock/unlock aspect ratio while resizing\n"
            "Ctrl\t\tHold down Ctrl to snap to increments of 5\n"
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

    def paintEvent(self, _event):
        col1 = 255 if not self.invert_colors else 0
        col2 = 100 if not self.invert_colors else 155
        col3 = 0 if not self.invert_colors else 255

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
                painter.drawText(
                    QtCore.QRect(0, 0, self.width(), self.height()),
                    QtCore.Qt.AlignmentFlag.AlignCenter,
                    f"{size_x} x {size_y}",
                )
                self.drawStatusMessages(painter, col3)
            elif self.height() > 80 and self.width() < 88:
                painter.drawText(
                    QtCore.QRect(0, self.height() - 37, self.width(), 20),
                    QtCore.Qt.AlignmentFlag.AlignCenter,
                    str(size_y),
                )
            else:
                painter.drawText(
                    QtCore.QRect(0, int(max(self.height() / 2 - 6.5, 20)), self.width() - 3, self.height()),
                    QtCore.Qt.AlignmentFlag.AlignRight,
                    str(size_x),
                )

        painter.end()

    def getStatusMessages(self):
        messages = []
        if self.aspect_lock_enabled:
            ratio_width, ratio_height = simplify_ratio(self.aspect_lock_target_width, self.aspect_lock_target_height)
            messages.append(f"Aspect Ratio Locked [{ratio_width}:{ratio_height}]")
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

        # hiding title bar, always on top
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowTitle("Compact Screen Ruler")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # setting window size and position
        self.resize(self.window_size_x, self.window_size_y)
        self.center()

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

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
            "L": self.toggleAspectRatioLock,
            "Ctrl+S": self.takeScreenshot,
            "F1": self.displayHelp,
            "H": self.displayHelp,
        }
        for keys, callback in shortcut_map.items():
            shortcut = QtGui.QShortcut(QtGui.QKeySequence(keys), self)
            shortcut.activated.connect(callback)
            self.shortcuts.append(shortcut)

    def center(self):
        qr = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        cp = screen.availableGeometry().center() if screen else QtCore.QPoint(0, 0)
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.leftclick = event.button() == QtCore.Qt.MouseButton.LeftButton
        self.drawPickPos = event.button() == QtCore.Qt.MouseButton.RightButton
        self.offset = event.pos()
        self.opos = self.pos()

    def mouseMoveEvent(self, event):
        ctrl_is_held = bool(QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ControlModifier)
        window_x = self.pos().x()
        window_y = self.pos().y()
        global_pos = event.globalPosition()
        global_x = int(global_pos.x())
        global_y = int(global_pos.y())
        local_x = self.offset.x()
        local_y = self.offset.y()

        self.mouse_x = global_x
        self.mouse_y = global_y

        if self.leftclick:
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

        else:
            self.update()

    def mouseReleaseEvent(self, event):
        self.window_size_x = self.width()
        self.window_size_y = self.height()
        self.drawPickPos = False
        self.update()

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
