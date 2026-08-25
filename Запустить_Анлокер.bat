@echo off
chcp 65001 >nul
title Antigravity Unlocker Launcher

:: Проверка прав администратора
net session >nul 2>&1
if %errorlevel% == 0 (
    goto :run_app
) else (
    echo [i] Запрос прав Администратора...
    powershell -Command "Start-Process -Verb RunAs -FilePath 'python.exe' -ArgumentList '\"%~dp0gui.py\"'"
    exit /b
)

:run_app
cd /d "%~dp0"
python gui.py
pause
