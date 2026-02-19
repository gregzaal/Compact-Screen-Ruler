# Compact Screen Ruler

Small always-on-top screen ruler for measuring on-screen distances.

<img width="690" height="70" alt="Screenshot" src="https://github.com/user-attachments/assets/f79fe4bd-ad99-40c6-acbb-13d40efaffb0" />


## Features

- Frameless ruler window that stays on top.
- Resize from edges and corners.
- Drag to move the ruler (LMB in the center area, or MMB from anywhere).
- Hold Ctrl to snap when moving or resizing.
- Snap to screen edges by default when moving or resizing (hold Shift to disable).
- Right-click measure mode shows crosshair lines and live X/Y distance from the window origin.
- Set exact position/size.
- Light/dark color inversion and transparency toggle.
- Aspect ratio lock.
- Screenshot capture of the screen area behind the ruler.
- Clickthrough mode to interact with apps behind the ruler.

## Hotkeys

- `Right Click`: Measuring mode
- `Q` or `Ctrl+Q`: Quit
- `Ctrl` (hold): Snap move/resize to 5 px
- `Shift` (hold): Disable screen-edge snap
- `S`: Set exact position and size
- `T`: Toggle transparency
- `I`: Toggle light/dark colors
- `F`: Flip axes (swap width/height)
- `R`: Reset to defaults
- `L`: Toggle aspect ratio lock
- `C`: Toggle clickthrough mode
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
