@echo off
echo Building Windows executable for PySnakes Game...
echo IMPORTANT: This must be run on a Windows machine with Python and PyInstaller installed.

REM Install requirements including pygame-ce
echo Installing requirements...
pip install -r requirements.txt

REM Install PyInstaller if not already installed
echo Installing PyInstaller...
pip install pyinstaller

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "main.spec" del "main.spec"

REM Build the executable for Windows with all assets
echo Building executable with PyInstaller...
pyinstaller --onefile ^
    --windowed ^
    --add-data "assets;assets" ^
    --add-data "highscores.json;." ^
    --collect-all pygame ^
    --collect-submodules pygame ^
    --name "PySnakes" ^
    --distpath "dist" ^
    --workpath "build" ^
    main.py

echo.
if exist "dist\PySnakes.exe" (
    echo SUCCESS: Windows executable has been created!
    echo You can find it in: dist\PySnakes.exe
    echo.
    echo The executable includes all fonts, sounds, and data files.
    echo It should run on any Windows PC without Python installed.
    echo.
    echo To distribute: Simply copy PySnakes.exe to target PC and double-click to run!
) else (
    echo ERROR: Build failed! Check the output above for errors.
)
echo.
pause