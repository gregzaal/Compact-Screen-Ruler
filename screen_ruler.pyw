from PyQt4 import QtGui, QtCore, Qt

from sys import version as sysversion
print (sysversion)

def snap(num):
    return int(5 * round(float(num)/5))

class ChooseGeometry(QtGui.QDialog):
    def __init__(self, prev_geo):
        super(ChooseGeometry, self).__init__()

        self.setWindowTitle('Set Position and Size')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.label_pos = QtGui.QLabel("Position: ", self)
        self.label_size = QtGui.QLabel("Size: ", self)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.label_pos)
        vbox1.addWidget(self.label_size)

        self.size_x = QtGui.QSpinBox(self)
        self.size_x.setRange(-99999, 99999)
        self.size_x.setPrefix("Width: ")
        self.size_x.setValue(prev_geo[2])
        self.pos_x = QtGui.QSpinBox(self)
        self.pos_x.setRange(-99999, 99999)
        self.pos_x.setPrefix("X: ")
        self.pos_x.setValue(prev_geo[0])
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.size_x)
        vbox2.addWidget(self.pos_x)

        self.size_y = QtGui.QSpinBox(self)
        self.size_y.setRange(-99999, 99999)
        self.size_y.setPrefix("Height: ")
        self.size_y.setValue(prev_geo[3])
        self.pos_y = QtGui.QSpinBox(self)
        self.pos_y.setRange(-99999, 99999)
        self.pos_y.setPrefix("Y: ")
        self.pos_y.setValue(prev_geo[1])
        vbox3 = QtGui.QVBoxLayout()
        vbox3.addWidget(self.size_y)
        vbox3.addWidget(self.pos_y)

        main_hbox = QtGui.QHBoxLayout()
        main_hbox.addLayout(vbox1)
        main_hbox.addLayout(vbox2)
        main_hbox.addLayout(vbox3)

        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        main_vbox = QtGui.QVBoxLayout()
        main_vbox.addLayout(main_hbox)
        main_vbox.addWidget(self.buttons)

        self.setLayout(main_vbox)

        QtCore.QObject.connect(self.buttons, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttons, QtCore.SIGNAL("rejected()"), self.reject)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        # Box layouts have their own tab order - tell it manually where to go
        self.setTabOrder(self.pos_x, self.pos_y)
        self.setTabOrder(self.pos_y, self.size_x)
        self.setTabOrder(self.size_x, self.size_y)
        self.setTabOrder(self.size_y, self.buttons)

        self.size_x.setFocus()
        self.size_x.selectAll()


    def getValues(self):
        return ([self.pos_x.value(), self.pos_y.value(), self.size_x.value(), self.size_y.value()])

class HelpDialog(QtGui.QDialog):
    def __init__(self):
        super(HelpDialog, self).__init__()

        self.setWindowTitle('Help and Info')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.setFixedSize(400, 225)

        text = ("This program is a simple tool you can use to measure distances on your screen, such as the width of a banner on some website.\n\n"
               "This compact tool has almost no interface. All interactions are done through a handful of hotkeys:\n\n"
               "Q / Ctrl+Q\tQuit\n"
               "F\t\tSwap the X and Y axis dimensions\n"
               "S\t\tSet the window position and size to exact values\n"
               "R\t\tReset the window size and position to defaults\n"
               "T\t\tMake the window transparent\n"
               "I\t\tSwitch between light and dark colors\n"
               "Ctrl\t\tHold down Ctrl to snap to increments of 5\n"
               "Ctrl + S\t\tTake a screenshot of what's behind the ruler\n"
               "F1 / H\t\tDisplay this Help dialog")
        self.main_label = QtGui.QLabel(text, self)
        self.main_label.setGeometry(10, 0, 380, 215)
        self.main_label.setWordWrap(True)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

class ScreenRuler(QtGui.QWidget):

    def paintEvent(self, e):
        col1 = 255 if not self.invert_colors else 0
        col2 = 100 if not self.invert_colors else 155
        col3 = 0 if not self.invert_colors else 255

        space = 5
        painter = QtGui.QPainter()
        painter.begin(self)

        pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QColor(col2, col2, col2, (0 if self.is_transparent else 180)))
        painter.drawRoundedRect(Qt.QRect(0,0,self.width(),self.height()), 4, 4)

        pen = QtGui.QPen(QtGui.QColor(col1, col1, col1, 0), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        # Grab bars
        painter.setBrush(QtGui.QColor(col1, col1, col1, 25))
        if self.is_transparent:
            painter.drawRect(Qt.QRect(0, 0, max(self.width(), 0), max(self.height(), 0)))
        else:
            painter.drawRect(Qt.QRect(21, 21, max(self.width()-21*2, 0), max(self.height()-21*2, 0)))

        pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.SolidLine)
        painter.setPen(pen)

        if not self.is_transparent:
            # Small ticks
            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 128), 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1,int(self.width()+1/space)):
                    xloc = x*space
                    if xloc % 50 != 0:
                        if xloc < self.width()-1:
                            painter.drawLine(xloc, 0, xloc, (((x-1)%2)+1)*5)
                            if self.height() > 43:
                                painter.drawLine(xloc, self.height(), xloc, self.height()-(((x-1)%2)+1)*5)
            if self.height() > 80:
                if self.width() >= 88:
                    rangestart = 2
                    rangeend = -1
                else:
                    rangestart = 0
                    rangeend = 1

                for y in range(rangestart,int(self.height()/space+rangeend)):
                    yloc = y*space
                    if yloc % 50 != 0:
                        if yloc < self.height()-1:
                            painter.drawLine(0, yloc, (((y-1)%2)+1)*5, yloc)
                            if self.width() > 43:
                                painter.drawLine(self.width(), yloc, self.width()-(((y-1)%2)+1)*5, yloc)

            # Big ticks
            pen = QtGui.QPen(QtGui.QColor(col3, col3, col3, 200), 1, QtCore.Qt.SolidLine)
            painter.setPen(pen)
            if self.width() >= 88:
                for x in range(1,int(self.width()+1/space)):
                    xloc = x*space*10
                    if xloc < self.width()-1:
                        painter.drawLine(xloc, 0, xloc, 20)
                        if self.height() > 52:  # Bottom Line
                            painter.drawLine(xloc, self.height(), xloc, self.height()-20)

                        # Numbers
                        if xloc < self.width()-37 or self.height() > 80:
                            if self.height() > 80:
                                if xloc < self.width()-37:
                                    painter.drawText(Qt.QRect(xloc-25, 19, 50, 15), QtCore.Qt.AlignCenter, str(xloc))
                                    painter.drawText(Qt.QRect(xloc-25, self.height()-35, 50, 15), QtCore.Qt.AlignCenter, str(xloc))
                            elif self.height() < 54:
                                painter.drawText(Qt.QRect(xloc-25, 19, 50, 15), QtCore.Qt.AlignCenter, str(xloc))
                            else:
                                painter.drawText(Qt.QRect(xloc-25, 0, 50, self.height()), QtCore.Qt.AlignCenter, str(xloc))
            if self.height() > 80:
                for y in range(1,int(self.height()/space/10)+1):
                    yloc = y*space*10
                    if yloc < self.height()-9:
                        painter.drawLine(0, yloc, 20, yloc)
                        if self.width() > 52:  # Right Line
                            painter.drawLine(self.width(), yloc, self.width()-20, yloc)

                        # Numbers
                        if yloc < self.height()-35:
                            if self.width() >= 88:
                                painter.drawText(Qt.QRect(23, yloc-7, 50, 20), QtCore.Qt.AlignLeft, str(yloc))
                                painter.drawText(Qt.QRect(self.width()-63, yloc-7, 40, 50), QtCore.Qt.AlignRight, str(yloc))
                            elif self.width() > 62:
                                painter.drawText(Qt.QRect(0, yloc-25, self.width(), 50), QtCore.Qt.AlignCenter, str(yloc))

            # Size display
            size_x = self.width()
            size_y = self.height()
            if self.drawPickPos:
                mouse_xpos = self.mouse_x-self.pos().x()
                mouse_ypos = self.mouse_y-self.pos().y()
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
                painter.drawText(Qt.QRect(0, 0, self.width(), self.height()), QtCore.Qt.AlignCenter, str(size_x)+" x "+str(size_y))
            elif self.height() > 80 and self.width() < 88:
                painter.drawText(Qt.QRect(0, self.height()-37, self.width(), 20), QtCore.Qt.AlignCenter, str(size_y))
            else:
                painter.drawText(Qt.QRect(0, max(self.height()/2-6.5, 20), self.width()-3, self.height()), QtCore.Qt.AlignRight, str(size_x))

        painter.end()

    def __init__(self):
        super(ScreenRuler, self).__init__()

        self.leftclick = False
        self.drawPickPos = False

        self.window_size_x = 690  # adaptivesamples post width
        self.window_size_y = 70

        self.is_transparent = False
        self.invert_colors = False

        # hiding title bar, always on top
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)


        self.setWindowTitle('Compact Screen Ruler')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        # setting window size and position
        self.resize(self.window_size_x, self.window_size_y)
        self.center()

        self.setAttribute(Qt.Qt.WA_TranslucentBackground)

        # Hotkeys
        QtGui.QShortcut(QtGui.QKeySequence("Q"), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.close)
        QtGui.QShortcut(QtGui.QKeySequence("S"), self, self.setWindowSize)
        QtGui.QShortcut(QtGui.QKeySequence("F"), self, self.flipOrientation)
        QtGui.QShortcut(QtGui.QKeySequence("R"), self, self.resetWindow)
        QtGui.QShortcut(QtGui.QKeySequence("T"), self, self.makeTransparent)
        QtGui.QShortcut(QtGui.QKeySequence("I"), self, self.doInvertColors)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self.takeScreenshot)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Alt+S"), self, self.screenWatch)
        QtGui.QShortcut(QtGui.QKeySequence("F1"), self, self.displayHelp)
        QtGui.QShortcut(QtGui.QKeySequence("H"), self, self.displayHelp)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.leftclick = event.button() == 1
        self.drawPickPos = event.button() == 2
        self.offset = event.pos()
        self.opos = self.pos()

    def mouseMoveEvent(self, event):
        ctrl_is_held = QtGui.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier
        window_x = self.pos().x()
        window_y = self.pos().y()
        global_x=event.globalX()
        global_y=event.globalY()
        local_x = self.offset.x()
        local_y = self.offset.y()

        self.mouse_x = global_x
        self.mouse_y = global_y

        if self.leftclick:

            gsize = 21

            resize_x = -99999999  # impossible value
            resize_y = -99999999

            move_x = -99999999
            move_y = -99999999

            if local_x > self.window_size_x-gsize and local_y > self.window_size_y-gsize:  # bottom right
                resize_x = max(10, global_x-window_x+(self.window_size_x-local_x))
                resize_y = max(10, global_y-window_y+(self.window_size_y-local_y))
            elif local_x < gsize and local_y > self.window_size_y-gsize:  # bottom left
                resize_x = max(10, self.window_size_x-global_x+self.opos.x()+local_x)
                resize_y = max(10, global_y-window_y+(self.window_size_y-local_y))
                move_x = global_x-local_x
                move_y = window_y
            elif local_x > self.window_size_x-gsize and local_y < gsize:  # top right
                resize_x = max(10, global_x-window_x+(self.window_size_x-local_x))
                resize_y = max(10, self.window_size_y-global_y+self.opos.y()+local_y)
                move_x = window_x
                move_y = global_y-local_y
            elif local_x < gsize and local_y < gsize:  # top left
                resize_x = max(10, self.window_size_x-global_x+self.opos.x()+local_x)
                resize_y = max(10, self.window_size_y-global_y+self.opos.y()+local_y)
                move_x = global_x-local_x
                move_y = global_y-local_y
            elif local_y > self.window_size_y-gsize:  # bottom edge
                resize_x = max(10, self.window_size_x)
                resize_y = max(10, global_y-window_y+(self.window_size_y-local_y))
            elif local_y < gsize:  # top edge
                resize_x = max(10, self.window_size_x)
                resize_y = max(10, self.window_size_y-global_y+self.opos.y()+local_y)
                move_x = window_x
                move_y = global_y-local_y
            elif local_x > self.window_size_x-gsize:  # right edge
                resize_x = max(10, global_x-window_x+(self.window_size_x-local_x))
                resize_y = max(10, self.window_size_y)
            elif local_x < gsize:  # left edge
                resize_x = max(10, self.window_size_x-global_x+self.opos.x()+local_x)
                resize_y = max(10, self.window_size_y)
                move_x = global_x-local_x
                move_y = window_y
            else:
                move_x = global_x-local_x
                move_y = global_y-local_y

            if resize_x != -99999999 and resize_y != -99999999:
                if ctrl_is_held:
                    self.resize(snap(resize_x), snap(resize_y))
                else:
                    self.resize(resize_x, resize_y)
            if move_x != -99999999 and move_y != -99999999:
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
        self.dialog = ChooseGeometry([self.pos().x(), self.pos().y(), self.window_size_x, self.window_size_y])
        self.dialog.show()

        values = []
        if self.dialog.exec_():
            values = self.dialog.getValues()

        if values:
            pos_x, pos_y, size_x, size_y = values
            self.move(pos_x, pos_y)
            self.resize(size_x, size_y)
            self.window_size_x = size_x
            self.window_size_y = size_y

    def flipOrientation(self):
        x = self.width()
        y = self.height()

        self.resize(y, x)
        self.window_size_x = y
        self.window_size_y = x

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

    def takeScreenshot(self):
        self.hide()
        window_x = self.pos().x()
        window_y = self.pos().y()

        raw = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
        rect = QtCore.QRect(window_x, window_y, self.window_size_x, self.window_size_y)
        new = raw.copy(rect)

        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save screenshot', 'Z:/', "PNG File (*.png)")
        try:
            fname += '.png' if not fname.endsWith('.png') else ''  # capital W for python 2.x
        except:
            fname += '.png' if not fname.endswith('.png') else ''  # lower case W for python 3.x

        if fname:
            new.save(fname, 'png')

        self.show()

    # def screenWatch(self):
    #     window_x = self.pos().x()
    #     window_y = self.pos().y()
    #     print(window_x, window_y)

    #     raw = QtGui.QPixmap.grabWindow(QtGui.QApplication.desktop().winId())
    #     rect = QtCore.QRect(window_x, window_y, self.window_size_x, self.window_size_y)
    #     new = raw.copy(rect)

    #     fname = QtGui.QFileDialog.getSaveFileName(self, 'Save screenshot', 'Z:/', "PNG File (*.png)")
    #     try:
    #         fname += '.png' if not fname.endsWith('.png') else ''  # capital W for python 2.x
    #     except:
    #         fname += '.png' if not fname.endswith('.png') else ''  # lower case W for python 3.x

    #     if fname:
    #         new.save(fname, 'png')

    def displayHelp(self):
        self.dialog = HelpDialog()
        self.dialog.show()


def main():
    app = QtGui.QApplication([])
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    exm = ScreenRuler()
    exm.show()
    app.exec_()


if __name__ == '__main__':
    main()