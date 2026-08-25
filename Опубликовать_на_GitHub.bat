@echo off
title GitHub Publisher
cd /d "%~dp0"
python tools\github_publisher.py
if %errorlevel% neq 0 (
    echo.
    echo Python execution failed. Press any key to exit.
    pause >nul
)
