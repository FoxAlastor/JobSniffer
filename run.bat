@echo off
setlocal
cd /d "%~dp0"
title JobSniffer - Robota.ua Remote Vacancies Explorer

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=py"
) else (
    set "PYTHON=python"
)

%PYTHON% main.py
if errorlevel 1 (
    echo.
    echo Could not start JobSniffer.
    echo Install dependencies with: %PYTHON% -m pip install -r requirements.txt
    pause
)
endlocal
