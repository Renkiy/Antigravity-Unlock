@echo off
chcp 65001 >nul
title Публикация Antigravity Unlocker на GitHub

echo ============================================================
echo   ПУБЛИКАЦИЯ РЕПОЗИТОРИЯ НА GITHUB
echo ============================================================
echo.

if not exist .git (
    echo [*] Инициализация локального Git-репозитория...
    git init
    git branch -M main
)

echo [*] Добавление файлов в коммит...
git add .
git commit -m "feat: release Antigravity Unlocker 2.0 with Smart Failover & L7 Account Bypass"

echo.
echo ============================================================
echo   Для привязки к вашему аккаунту GitHub:
echo ============================================================
echo 1. Создайте новый пустой репозиторий на github.com (например, antigravity-unlocker)
echo 2. Скопируйте ссылку на ваш репозиторий (например: https://github.com/ВАШ_ЛОГИН/antigravity-unlocker.git)
echo.
set /p REPO_URL="Вставьте ссылку на ваш GitHub репозиторий: "

if "%REPO_URL%"=="" (
    echo [-] Ссылка не была введена. Отмена отправки.
    pause
    exit /b
)

git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo [*] Отправка файлов на GitHub (git push -u origin main)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo [УСПЕХ] Проект успешно опубликован на вашем GitHub!
    echo ============================================================
) else (
    echo.
    echo [-] Ошибка отправки. Проверьте правильность ссылки и авторизацию в Git.
)

echo.
pause
