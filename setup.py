from cx_Freeze import setup, Executable
import sys

# from PyQt6 import QtGui, QtCore, QtWidgets

build_exe_options = {"includes": ["sip", "re", "atexit", "PyQt6.QtGui", "PyQt6.QtCore", "PyQt6.QtWidgets"]}

b = None
if sys.platform == "win32":
    b = "Win32GUI"

setup(
    name="Screen Ruler",
    version="0.5",
    description="A tool to measure distances on your screen",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "screen_ruler.pyw",
            base=b,
            targetName="screenshot_ruler.exe",
            icon="icon.ico",
            compress=True,
        )
    ],
)
