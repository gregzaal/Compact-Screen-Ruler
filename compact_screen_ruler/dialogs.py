"""Dialog classes used by the Compact Screen Ruler UI."""

from PyQt6 import QtCore, QtGui, QtWidgets


class ChooseGeometry(QtWidgets.QDialog):
    """Dialog for editing ruler position and size with exact numeric values."""

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

        self.setTabOrder(self.pos_x, self.pos_y)
        self.setTabOrder(self.pos_y, self.size_x)
        self.setTabOrder(self.size_x, self.size_y)
        self.setTabOrder(self.size_y, self.buttons)

        self.size_x.setFocus()
        self.size_x.selectAll()

    def get_values(self):
        """Return selected geometry values as [x, y, width, height]."""
        return [self.pos_x.value(), self.pos_y.value(), self.size_x.value(), self.size_y.value()]

    def getValues(self):
        """Legacy alias for compatibility with older call sites."""
        return self.get_values()


class HelpDialog(QtWidgets.QDialog):
    """Dialog displaying usage and hotkey help text."""

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
            "U\t\tToggle units (px, cm, in)\n"
            "G\t\tToggle full-window grid from tick marks\n"
            "Ctrl\t\tHold down Ctrl to snap to medium tick spacing\n"
            "Ctrl + C\t\tCopy current dimensions to clipboard (123x456)\n"
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
