# 📋 Handoff Report: Codebase Exploration & Technical Survey (Antigravity Unlocker)

**Agent:** `explorer_survey_1`  
**Working Directory:** `c:\Users\Rnkiy\Desktop\Анлок антигравити\.agents\explorer_survey_1`  
**Timestamp:** 2026-08-26T13:51:25Z  
**Type:** Hard Handoff (Task Complete)

---

## 1. Observation

### 1.1. Репозиторий и исходные файлы:
Прямым инспектированием подтверждена структура и содержимое ключевых файлов:
1. `tools/unlocker_core.py` (249 строк):
   - Строка 23: `def is_admin()` с вызовом `ctypes.windll.shell32.IsUserAnAdmin()`.
   - Строка 29: `def elevate_process(args=None)` через `ShellExecuteW(None, "runas", executable, ...)` с кодом `ret > 32`.
   - Строки 57–64: `candidate_paths` поиска `language_server.exe` и `agy.exe` в `%LOCALAPPDATA%`, `%APPDATA%`, `%USERPROFILE%`.
   - Строки 80–104: `patch_binaries()` заменяет `b"ineligible"` на `b"inexigible"` с предварительным вызовом `taskkill /F /IM fname`.
   - Строки 161–167: `set_ipv4_priority(enable=True)` вызывает `netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 46 4` (или `35 4`).
   - Строки 168–212: `execute_unlock()` координирует 6 шагов (бэкап, NRPT purge, find_best_proxy, pin_hosts, patch_binaries, configure_ide_settings, flushdns).
   - Строки 214–238: `execute_rollback()` полностью возвращает систему в исходное состояние.

2. `tools/pin_hosts.py` (102 строки):
   - Строки 5–8: `HOSTS_PATH` указывает на `%SystemRoot%\System32\drivers\etc\hosts`, маркеры `BEGIN_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_START ==="` и `END_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_END ==="`.
   - Строки 13–19: `PINNED_ENTRIES` содержит целевые домены (`cloudcode-pa.googleapis.com`, `daily-cloudcode-pa.googleapis.com`, `generativelanguage.googleapis.com`, `antigravity-unleash.goog`, `cloudaicompanion.googleapis.com`).
   - Строки 21–64: `apply_hosts_pin()` перезаписывает блок между маркерами и выполняет `ipconfig /flushdns`.

3. `tools/proxy_manager.py` (317 строк):
   - Строки 12–22: `PROXIES_POOL` содержит 9 проверенных узлов (5 узлов Hetzner в Германии `94.130.180.225`, `148.251.10.155`, `188.40.142.18`, `136.243.104.148`, `168.119.141.192` и 4 узла Comss в Нидерландах `45.88.174.254`, `45.88.174.253`, `45.88.174.252`, `45.88.174.251`).
   - Строки 48–64: `probe_single_host()` открывает `socket.create_connection((ip, 443))` и выполняет `ctx.wrap_socket(..., server_hostname=host_name)`, замеряя миллисекунды.
   - Строки 98–126: `find_best_proxy()` выполняет параллельный опрос через `ThreadPoolExecutor` и сортирует узлы по `(-x["passed_count"], x["avg_latency"])`.
   - Строки 127–147: `clean_leaking_nrpt_rules()` удаляет сбойные правила NRPT (`111.88.96.50`, `83.220.169.155`, `*AG_UNLOCKER*`) через PowerShell `Remove-DnsClientNrptRule`.
   - Строки 243–309: `ProxyWatchdog` — фоновый поток демона (интервал 20 сек), отслеживающий ошибки 10054/таймауты и автоматически запускающий `pin_hosts(new_ip)` при двух последовательных сбоях.

4. `tools/backup_manager.py` (136 строк):
   - Строки 25–69: `create_backup(label)` создает снимки `hosts`, `settings.json`, исполняемых файлов Language Server и JSON-дамп правил NRPT в `backups/backup_<timestamp>_<label>` с `manifest.json`.
   - Строки 85–125: `restore_backup()` завершает заблокированные процессы `taskkill /F /IM language_server.exe` и побайтово копирует файлы обратно.

5. `tools/diagnostics.py` (155 строк):
   - Реализует 5 тестов: проверка записей `hosts`, аудит правил NRPT, анализ резолвинга DNS (проверка на совпадение с префиксами прямого Google `172.217.`, `142.250.`, `216.58.`, `173.194.`, `74.125.`), проверка TLS 443 Handshake / Issuer и подсчет сигнатур `ineligible`/`inexigible` в бинарниках.

6. `tools/cloudflare_worker.js` (75 строк):
   - Реализует прокси-воркер, удаляющий заголовки `CF-Connecting-IP`, `CF-IPCountry`, `X-Forwarded-For` и перехватывающий путь `:loadCodeAssist`, заменяя `"ineligible"` -> `"eligible"` и `"INELIGIBLE"` / `"UNSUPPORTED"` -> `"ALLOWED"`.

7. `tools/gui_app.py` (691 строка) и `installer/installer_gui.py` (294 строки):
   - Современный UI на Tkinter в темной теме Catppuccin Mocha с асинхронным обновлением дашборда и диалогами бэкапов/воркера/GitHub.
   - Мастер установки с созданием ярлыков через `WScript.Shell` и регистрацией в реестре Windows `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\AntigravityUnlocker`.

---

## 2. Logic Chain

1. **Изоляция от утечек DNS (Наблюдение 1.1, 1.2, 1.3):**
   - Инцидент 24–25 августа показал, что Windows при таймаутах SmartDNS каскадно резолвит резервные DNS и кэширует прямые российские IP Google (`172.217.x.x`).
   - Использование `pin_hosts()` в файле `%SystemRoot%\System32\drivers\etc\hosts` имеет наивысший приоритет в резолвере Windows, исключая любые запросы к провайдерскому DNS. Очистка NRPT через `clean_leaking_nrpt_rules()` ликвидирует возможность DNS-fallback.

2. **Безопасность бинарных модификаций (Наблюдение 1.1):**
   - Замена `ineligible` (10 символов) на `inexigible` (10 символов) сохраняет точные смещения секций PE и сериализации Protobuf. Размер файла на диске не меняется. Процесс предварительно убивается через `taskkill`, исключая блокировку записи.

3. **Защита аутентификации (Наблюдение 1.2, 1.3):**
   - Домены `accounts.google.com` и `oauth2.googleapis.com` исключены из `PINNED_HOSTS` и идут строго через сквозной прямой TLS 1.3, что гарантирует сохранность учетных данных пользователя.

4. **Отказоустойчивость (Наблюдение 1.3):**
   - `ProxyWatchdog` проверяет живой TLS-хэндшейк каждые 20 сек. При сбое узла (RST 10054) в течение 2 циклов переключает запись в `hosts` на следующий живой узел за < 1 секунды, автоматически вызывая `ipconfig /flushdns`.

---

## 3. Caveats

1. **Требование прав Администратора:** Модификация системного файла `hosts`, таблицы NRPT и сетевых политик `netsh` требует запуска с повышенными привилегиями (UAC elevation). Для пользователей без прав локального администратора потребуется запуск только Cloudflare Worker с настройкой переменной окружения `CLOUD_CODE_URL`.
2. **Антивирусные сканеры:** Некоторые агрессивные антивирусы могут временно блокировать запись в `hosts` файл (требуется добавление процесса в исключения).
3. **Другие операционные системы:** Комплекс полностью оптимизирован под сетевой стек Windows 10/11 (PowerShell, netsh, WScript.Shell, winreg).

---

## 4. Conclusion

Кодовая база Antigravity Unlocker полностью изучена, структурирована и задокументирована.
Создан исчерпывающий аналитический отчет в `analysis.md` (включающий карту файлов, разбор инцидента 24 августа, трёхуровневую модель фильтрации Google, механику DNS-pinning, бинарного патчинга, Cloudflare Worker, CLI-интерфейсы, таблицу сравнения с 4 конкурирующими классами решений и примеры кода для технических статей).

Все материалы готовы для передачи другим агентам для написания статей для Habr, VC, DTF, матрицы сравнения и GitHub профиля.

---

## 5. Verification Method

Для независимой проверки выводов отчета выполнить:

1. **Проверка файловой структуры и наличия отчетов:**
   ```powershell
   dir "c:\Users\Rnkiy\Desktop\Анлок антигравити\.agents\explorer_survey_1"
   ```
2. **Проверка работы сканера диагностики:**
   ```powershell
   python "c:\Users\Rnkiy\Desktop\Анлок антигравити\tools\diagnostics.py"
   ```
3. **Проверка бенчмарка прокси-пула:**
   ```powershell
   python "c:\Users\Rnkiy\Desktop\Анлок антигравити\tools\proxy_manager.py"
   ```
4. **Проверка целостности отчета `analysis.md`:**
   Открыть `c:\Users\Rnkiy\Desktop\Анлок антигравити\.agents\explorer_survey_1\analysis.md` и проверить соответствие описанных модулей и функций реальным строкам исходного кода.
