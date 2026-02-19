"""Core widget lifecycle and command handlers for the ruler."""

from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets

from ..dialogs import ChooseGeometry, HelpDialog


class RulerCore(QtWidgets.QWidget):
    """Base widget with initialization, state, and non-paint command handlers."""

    MIN_WINDOW_SIZE = 10
    GRAB_HANDLE_SIZE = 21

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
        self.measurement_unit = "px"
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

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.setWindowTitle("Compact Screen Ruler")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.resize(self.window_size_x, self.window_size_y)
        self.center()

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

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
            "U": self.toggleMeasurementUnit,
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
        self.update()

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

    def toggleMeasurementUnit(self):
        units = ("px", "cm", "in")
        current_index = units.index(self.measurement_unit) if self.measurement_unit in units else 0
        self.measurement_unit = units[(current_index + 1) % len(units)]
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

        default_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save screenshot",
            default_name,
            "PNG File (*.png)",
        )
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
