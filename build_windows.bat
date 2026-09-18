@echo off
setlocal
cd /d "%~dp0"
title Build JobSniffer

echo [1/3] Installing dependencies...
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error

echo [2/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist JobSniffer.spec del /q JobSniffer.spec

echo [3/3] Building JobSniffer.exe...
pyinstaller --noconfirm --clean --onefile --windowed --name JobSniffer --icon JobSniffer.ico --add-data "JobSniffer.ico;." main.py
if errorlevel 1 goto error

echo.
echo Build complete: dist\JobSniffer.exe
pause
exit /b 0

:error
echo.
echo Build failed. Check the messages above.
pause
exit /b 1
