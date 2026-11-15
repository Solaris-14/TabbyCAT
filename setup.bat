@echo off
title TabbyPatrol - Quick Setup & Launch
echo ===================================================
echo     🐱 TabbyPatrol - Autonomous Desktop AI Agent
echo              HackPrinceton Fall 2026
echo ===================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Warning: Some dependencies could not be installed via pip. Attempting launch with standard packages...
)

echo.
echo [*] Launching TabbyPatrol Overlay...
echo [*] Kitten will appear on its plush pillow in the bottom-right corner!
echo.
python overlay\tabby_overlay.py
pause
