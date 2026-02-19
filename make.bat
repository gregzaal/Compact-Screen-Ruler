@echo off
setlocal

set "PY=py -3.11"

for /f %%v in ('%PY% -c "from compact_screen_ruler.version import __version__; print(__version__)"') do set "VERSION=%%v"
if "%VERSION%"=="" (
	echo Failed to determine version.
	exit /b 1
)

set "DIST_ROOT=build\nuitka"
set "OUT_DIR=%DIST_ROOT%\screen_ruler.dist"
set "RELEASE_DIR=build\release\Compact-Screen-Ruler-v%VERSION%-win64"
set "ZIP_PATH=build\release\Compact-Screen-Ruler-v%VERSION%-win64.zip"

echo [1/5] Installing build dependencies...
%PY% -m pip install -q nuitka ordered-set zstandard
if errorlevel 1 exit /b 1

echo [2/5] Cleaning previous outputs...
if exist "%DIST_ROOT%" rmdir /s /q "%DIST_ROOT%"
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
if exist "%ZIP_PATH%" del /q "%ZIP_PATH%"

echo [3/5] Building standalone executable with Nuitka...
%PY% -m nuitka --standalone --assume-yes-for-downloads --enable-plugin=pyqt6 --windows-console-mode=disable --windows-icon-from-ico=icon.ico --include-data-files=icon.png=icon.png --include-data-files=icon.ico=icon.ico --output-dir=%DIST_ROOT% --output-filename=screen_ruler.exe screen_ruler.py
if errorlevel 1 exit /b 1

echo [4/5] Preparing release folder...
mkdir "%RELEASE_DIR%"
xcopy "%OUT_DIR%\*" "%RELEASE_DIR%\" /e /i /y >nul
copy /y "README.md" "%RELEASE_DIR%\README.md" >nul
copy /y "LICENSE" "%RELEASE_DIR%\LICENSE" >nul

echo [5/5] Creating zip archive...
powershell -NoProfile -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%ZIP_PATH%' -CompressionLevel Optimal"
if errorlevel 1 exit /b 1

echo.
echo Build complete.
echo Version: v%VERSION%
echo Folder : %RELEASE_DIR%
echo Zip    : %ZIP_PATH%
pause