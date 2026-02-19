# Compact Screen Ruler

Small always-on-top screen ruler for measuring on-screen distances.

<img width="690" height="70" alt="Screenshot" src="https://github.com/user-attachments/assets/f79fe4bd-ad99-40c6-acbb-13d40efaffb0" />


## Features

- Frameless ruler window that stays on top.
- Drag to move the ruler.
- Resize from edges and corners.
- Optional snapping to 5-pixel increments while holding Ctrl (move + resize).
- Right-click measure mode shows crosshair lines and live X/Y distance from the window origin.
- Axis flip (swap width and height).
- Manual position/size dialog.
- Reset to default size and centered position.
- Transparency toggle.
- Light/dark color inversion toggle.
- Aspect ratio lock during resize.
- Aspect lock ratio display in-window.
- Aspect lock target updates after axis flip.
- Screenshot capture of the screen area behind the ruler.
- Help dialog.
- Quit shortcut.

## Hotkeys

- `Q` or `Ctrl+Q`: Quit
- `Ctrl` (hold): Snap move/resize to 5 px
- `S`: Set exact position and size
- `T`: Toggle transparency
- `I`: Toggle light/dark colors
- `F`: Flip axes (swap width/height)
- `R`: Reset to defaults
- `L`: Toggle aspect ratio lock
- `Ctrl+S`: Save screenshot of area behind ruler
- `F1` or `H`: Open help

----

## Requirements

- Python 3.11+
- PyQt6
- cx_Freeze (only for building an executable)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
py -3.11 screen_ruler.pyw
```

Or use:

- `launch_screen_ruler.bat`

## Build

```bash
py -3.11 setup.py build
```

Or use:

- `make.bat`
