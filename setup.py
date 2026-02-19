from cx_Freeze import setup, Executable
import sys
#from PyQt4 import QtGui, QtCore, Qt

build_exe_options = {"includes": ["sip", "re", "atexit", "PyQt4.QtGui", "PyQt4.QtCore", "PyQt4.Qt"]}

b = None
if sys.platform == "win32":
    b = "Win32GUI"

setup(
    name = "Screen Ruler",
    version = "0.5",
    description = "A tool to measure distances on your screen",
    options = {"build_exe": build_exe_options},
    executables = [Executable("screen_ruler.pyw", base = b, targetName="screenshot_ruler.exe", icon="icon.ico", compress=True)])