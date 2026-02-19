from cx_Freeze import setup, Executable
import sys

build_exe_options = {"includes": ["re", "atexit", "PyQt6.QtGui", "PyQt6.QtCore", "PyQt6.QtWidgets"]}

base = None
if sys.platform == "win32":
    base = "gui"

setup(
    name="Screen Ruler",
    version="0.5",
    description="A tool to measure distances on your screen",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "screen_ruler.py",
            base=base,
            target_name="screen_ruler.exe",
            icon="icon.ico",
        )
    ],
)
