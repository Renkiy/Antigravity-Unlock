# System Rule & Project Knowledge Base: Antigravity Unlocker

```
Document Version: 1.0.0
Status: ACTIVE / PRODUCTION SPECIFICATION
Target Engine: Antigravity 2.0, Antigravity IDE, Antigravity CLI (agy), Language Server
Operating System: Windows 10 (1809+) / Windows 11 (21H2+)
Architectures: x86_64, ARM64
```

---

## 1. Информация о проекте (Project Overview)

### 1.1. Название и назначение
**Antigravity Unlocker** — системный комплекс маршрутизации, DNS-селекции и бинарного патчинга для обеспечения беспрепятственной работы **Google Antigravity IDE**, CLI-утилиты `agy`, языкового сервера (`language_server.exe`) и моделей Google Gemini Code Assist в условиях географических ограничений РФ/РБ **без глобального VPN**.

### 1.2. Ключевые принципы
1. **Zero VPN:** Прямой интернет для всех приложений, кроме модельного трафика Google AI.
2. **Strict Length-Preserving Binary Patching:** Никаких смещений структуры PE/Protobuf (`ineligible` -> `inexigible`, 10 байт в 10 байт).
3. **Selective DNS (NRPT):** Направление только строго определенных хостов (`cloudcode-pa`, `daily-cloudcode-pa`, `generativelanguage`, `antigravity-unleash`).
4. **100% обратимость (Rollback):** Возможность полного отката системы в исходное состояние одной командой.
5. **Безопасность аутентификации:** Домены авторизации (`accounts.google.com`, `oauth2.googleapis.com`) никогда не подвергаются MITM/расшифровке и идут сквозным TLS.

---

## 2. Сетевая инфраструктура и домены

| Домен / Хост | Назначение | Протокол | Обработка |
| :--- | :--- | :--- | :--- |
| `accounts.google.com` | Форма логина Google | HTTPS (TLS 1.3) | **Прямой (Direct)** — без прокси |
| `oauth2.googleapis.com` | Выдача/рефреш access токенов | HTTPS REST | **Прямой (Direct)** — без прокси |
| `cloudcode-pa.googleapis.com` | Ядро Gemini Code Assist (генерация, контекст) | HTTP/2, gRPC, Protobuf | **NRPT / SNI-прокси / Carrier Relay** |
| `daily-cloudcode-pa.googleapis.com` | Canary/Staging эндпоинт Cloud Code | HTTP/2, gRPC | **NRPT / SNI-прокси** |
| `generativelanguage.googleapis.com` | Прямой Gemini API (Flash/Pro) | HTTP/2, REST, gRPC | **NRPT / SNI-прокси (xbox-dns, geohide)** |
| `antigravity-unleash.goog` | Удаленные фичефлаги и проверки среды | HTTPS REST | **NRPT / SNI-прокси** |
| `jetski-webchannel.googleapis.com` | Duplex стриминг для агентских сессий | WebChannel over HTTP/2 | **Локальный TLS Carrier Relay** |

---

## 3. Архитектура и методы достижения цели

### 3.1. Бинарный патч Language Server & CLI
- **Файлы:**
  - `%LOCALAPPDATA%\Programs\antigravity\resources\bin\language_server.exe`
  - `%LOCALAPPDATA%\Programs\Antigravity IDE\resources\app\extensions\antigravity\bin\language_server_windows_x64.exe`
  - `%LOCALAPPDATA%\Programs\antigravity\resources\bin\agy.exe` (при наличии)
- **Суть патча:** Замена литерала `ineligible` (10 байт: `69 6e 65 6c 69 67 69 62 6c 65`) на `inexigible` (10 байт: `69 6e 65 78 69 67 69 62 6c 65`).
- **Результат:** Пропускаются встроенные проверки региона при парсинге ответа `:loadCodeAssist`.

### 3.2. Изоляция DNS и Hosts-Pinning с активным Watchdog (Smart Failover)
- **Защита от DNS-утечек (Инцидент 24–25 августа):**
  - Полный отказ от ненадежных SmartDNS (111.88.96.50, xbox-dns), которые могут отдавать реальные российские IP (`172.217.x.x`).
  - Очистка правил NRPT с помощью `clean_leaking_nrpt_rules()`.
  - Принудительная привязка доменов в `%SystemRoot%\System32\drivers\etc\hosts` к проверенному пулу зарубежных SNI-узлов (Германия, Нидерланды).
  - Фоновая служба `ProxyWatchdog` непрерывно проверяет порт 443 и при ошибке 10054 (RST) автоматически переключает `hosts` на следующий живой узел.

### 3.3. Обход блокировки Российских Google-Аккаунтов (L7 & Binary)
- **Уровень 1 (Клиент):** Замена `ineligible` на `inexigible` в `language_server.exe` и `agy.exe`.
- **Уровень 2 (Бэкенд):** Поддержка `Cloudflare Worker L7 Relay` (`tools/cloudflare_worker.js`). Воркер перехватывает эндпоинт `:loadCodeAssist`, удаляет геолокационные заголовки и на лету подменяет статус аккаунта с `INELIGIBLE` на `ALLOWED`, гарантируя вход с любого аккаунта.

### 3.4. Приоритет IPv4 над IPv6
- Для предотвращения утечек через нативный IPv6 провайдера:
  ```powershell
  netsh interface ipv6 set prefixpolicy ::ffff:0:0/96 46 4
  ```

