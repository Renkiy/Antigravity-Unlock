@echo off
chcp 65001 > nul
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Требуются права администратора. Перезапуск от имени администратора...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo ============================================================
echo   ANTIGRAVITY UNLOCKER: ИСПРАВЛЕНИЕ СЕТИ И DNS (NRPT)
echo ============================================================

echo [+] Удаление старых/неработающих правил NRPT...
powershell -NoProfile -Command "Get-DnsClientNrptRule -ErrorAction SilentlyContinue | ForEach-Object { Remove-DnsClientNrptRule -Name $_.Name -Force -ErrorAction SilentlyContinue }"

echo [+] Установка актуальных DNS правил (Comss + Xbox-DNS)...
powershell -NoProfile -Command "Add-DnsClientNrptRule -Namespace @('generativelanguage.googleapis.com', 'cloudcode-pa.googleapis.com', 'daily-cloudcode-pa.googleapis.com', 'antigravity-unleash.goog') -NameServers @('83.220.169.155', '212.109.195.93', '111.88.96.50', '111.88.96.51') -Comment 'AG_UNLOCKER_NRPT_V2'"

echo [+] Очистка кэша DNS...
ipconfig /flushdns

echo [+] Запуск проверки подключения...
python "%~dp0tools\diagnostics.py"

echo ============================================================
echo [OK] Готово! Нажмите любую клавишу для закрытия.
pause > nul
