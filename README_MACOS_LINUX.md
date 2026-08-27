# 🍏 🐧 Antigravity Unlocker — Руководство для macOS и Linux

### Полноценный комплекс для автономной работы Google Antigravity, Antigravity IDE и моделей Gemini в РФ/РБ без VPN

[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon%20%7C%20Intel-black?style=for-the-badge&logo=apple&logoColor=white)](https://apple.com)
[![Linux](https://img.shields.io/badge/Linux-Ubuntu%20%7C%20Debian%20%7C%20Arch%20%7C%20Fedora-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Zero VPN](https://img.shields.io/badge/Traffic-Zero%20VPN-success?style=for-the-badge&logo=cloudflare&logoColor=white)](#)

---

## 📌 Архитектурные особенности на macOS и Linux

В отличие от Windows, на Unix-системах (macOS/Linux):
1. **Нет механизма NRPT** — маршрутизация строится через приоритетную привязку в системный файл `/etc/hosts`. Это исключает внезапные утечки DNS через сторонние резолверы.
2. **Apple Silicon & AMFI (Code Signing на macOS):**
   * Модификация бинарных файлов (`language_server_macos_arm`, `agy`) на macOS инвалидирует цифровую подпись Mach-O.
   * Без переподписи ядро macOS немедленно завершает процесс с ошибкой `SIGKILL (Code Signature Invalid)` («Antigravity server crashed unexpectedly»).
   * **Antigravity Unlocker автоматически снимает карантин (`xattr -cr`) и накладывает ad-hoc подпись (`codesign --force --deep --sign -`)** сразу после применения патча.

---

## 🚀 Быстрый запуск

### Вариант 1: Запуск в 1 клик на macOS (Finder)
1. Дважды кликните по файлу **`Запустить_Анлокер_Mac.command`** в папке проекта.
2. Откроется терминал с интерактивным меню.
3. Выберите пункт **`1`** (Активировать анлок) и введите пароль администратора при запросе.

---

### Вариант 2: Интерактивный CLI-терминал

```bash
# Сделать скрипт исполняемым (при необходимости)
chmod +x unlock.sh

# Запуск интерактивного меню
./unlock.sh
```

Вы увидите удобное консольное меню:
```text
╔══════════════════════════════════════════════════════════════════╗
║               🚀 ANTIGRAVITY UNLOCKER (CLI)                     ║
║       Полноценная работа Google Antigravity в РФ без VPN         ║
╚══════════════════════════════════════════════════════════════════╝

Выберите действие:

  1) ⚡ АКТИВИРОВАТЬ АНЛОК (Авто-прокси + Патч + CodeSign)
  2) 🔄 ПОЛНЫЙ ОТКАТ (Restore оригиналов)
  3) 🛡️  Управление бэкапами (Список, выбор и восстановление)
  4) 🔍 Диагностика сети и бинарников
  5) ⚡ Тестирование скорости пула SNI-прокси
  6) ☁️  Настройка Cloudflare Worker L7
  7) 🚀 Опубликовать проект на GitHub
  0) 🚪 Выход
```

---

### Вариант 3: Однострочные команды (для автоматизации)

```bash
# 1. Полная активация анлока
./unlock.sh --apply
# (или: sudo python3 tools/unlocker_core.py)

# 2. Управление резервными копиями (список и откат)
./unlock.sh --backups
# (или: python3 tools/backup_manager.py -i)

# 3. Комплексная диагностика сети, подписей и патчей
./unlock.sh --diag
# (или: python3 tools/diagnostics.py)

# 4. Сканирование и бенчмарк пула прокси
./unlock.sh --test
# (или: python3 tools/proxy_manager.py)

# 5. Настройка Cloudflare Worker L7
./unlock.sh --worker

# 6. Полный откат всех изменений в исходное состояние
./unlock.sh --restore
# (или: sudo python3 tools/unlocker_core.py --restore)
```

---

## 🛡️ Управление резервными копиями (Бэкапы)

При выборе пункта **`3`** (или вызове `./unlock.sh --backups`) выводится таблица всех доступных точек восстановления:

```text
================================================================================
#   | Имя бэкапа                          | Дата создания        | Файлов  
--------------------------------------------------------------------------------
[1] | backup_20260827_121514_manual       | 2026-08-27 12:15:14  | 4 шт.   
[2] | backup_20260827_120228_manual       | 2026-08-27 12:02:28  | 4 шт.   
[3] | backup_20260827_102000_initial_original (Оригиналы) | 2026-08-27 10:20:00  | 3 шт.   
================================================================================

Действия:
  [1-N] - Восстановить выбранный бэкап по номеру
  [c]   - Создать новый бэкап сейчас
  [0]   - Вернуться в главное меню
```

- Чтобы вернуть **заводские нетронутые файлы Google**, просто введите номер бэкапа с пометкой `(Оригиналы)`.
- Система сама остановит процессы, восстановит файлы, переподпишет их для macOS и сбросит кэш DNS.

---

## 🛠️ Что делает комплекс под капотом

| Шаг | Действие | macOS | Linux |
|:---|:---|:---|:---|
| **1. Бэкап** | Создание резервной копии оригиналов с манифестом SHA-256 | `backups/backup_...` | `backups/backup_...` |
| **2. Proxy Probe** | Тестирование пула европейских SNI-узлов по TLS 443 | Выбор минимального пинга | Выбор минимального пинга |
| **3. Hosts Pinning** | Фиксация доменов Google AI в системном файле | Запись в `/etc/hosts` | Запись в `/etc/hosts` |
| **4. DNS Flush** | Сброс системного кэша DNS | `dscacheutil` + `mDNSResponder` | `resolvectl` / `systemd-resolve` |
| **5. Binary Patch** | Длина-сохраняющая замена `ineligible` ➔ `inexigible` (10 байт) | В `language_server_macos_*` и `agy` | В `language_server_linux_*` и `agy` |
| **6. CodeSign** | Снятие карантина и ad-hoc подпись Mach-O | `xattr -cr` + `codesign -s -` | Не требуется |
| **7. IDE Config** | Настройка `jetski.cloudCodeUrl` в `settings.json` | `~/Library/Application Support/...` | `~/.config/Antigravity IDE/...` |

---

## 📍 Пути к файлам Antigravity на macOS и Linux

### macOS:
* **IDE Application Bundle:** `/Applications/Antigravity IDE.app`
* **Language Server:** `/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm` (или `_macos_x64`)
* **CLI Утилита:** `~/.local/bin/agy`
* **Настройки IDE:** `~/Library/Application Support/Antigravity IDE/User/settings.json`
* **Системный hosts:** `/etc/hosts`

### Linux:
* **IDE Directory:** `/opt/Antigravity` или `/opt/Antigravity IDE`
* **Language Server:** `/opt/Antigravity/resources/app/extensions/antigravity/bin/language_server_linux_x64`
* **CLI Утилита:** `~/.local/bin/agy`
* **Настройки IDE:** `~/.config/Antigravity IDE/User/settings.json`
* **Системный hosts:** `/etc/hosts`

---

## ⚠️ Решение возможных проблем (Troubleshooting)

### 1. Ошибка "Antigravity server crashed unexpectedly" на macOS
**Причина:** Бинарный файл был изменен без обновления подписи `codesign`.  
**Решение:**
```bash
sudo xattr -cr "/Applications/Antigravity IDE.app"
sudo codesign --force --deep --sign - "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm"
sudo codesign --force --deep --sign - "/Applications/Antigravity IDE.app"
sudo codesign --force --sign - "$HOME/.local/bin/agy"
```

### 2. Запросы идут в российский IP Google (`172.217.x.x`)
**Причина:** Не сбросился системный кэш DNS.  
**Решение на macOS:**
```bash
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
```
**Решение на Linux:**
```bash
sudo resolvectl flush-caches || sudo systemd-resolve --flush-caches
```

### 3. После обновления Antigravity IDE анлок перестал работать
**Причина:** При обновлении IDE перезаписала бинарник `language_server`.  
**Решение:** Просто выполните `./unlock.sh --apply` повторно.
