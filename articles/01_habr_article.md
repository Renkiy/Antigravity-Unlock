# Как мы обошли блокировку Google Antigravity в РФ без VPN: разбор инцидента 24 августа, Hosts-Pinning и L7 Relay

**Хабы:** Информационная безопасность, Разработка под Windows, Сетевые технологии, Искусственный интеллект, Reverse Engineering  
**Теги:** google antigravity, gemini, sni proxy, windows api, reverse engineering, python, сетевые протоколы, hosts

---

### TL;DR
24–25 августа 2026 года в РФ массово перестали работать **Google Antigravity IDE**, CLI-агент `agy` и модели **Gemini 2.5/3.0**. Привычные решения вроде SmartDNS рухнули с ошибками `WinError 10054 (WSAECONNRESET)` и `User location is not supported`. 

В этой статье — полный инженерный разбор инцидента:
1. Почему каскадный резолвинг Windows NRPT сливал запросы на реальные российские IP Google (`172.217.x.x`).
2. Как устроен трёхуровневый анти-фрод Google (L4 Geo-IP ➔ клиентский Language Server ➔ L7 `:loadCodeAssist`).
3. Как мы реализовали гибридный обход на чистом Python: **Anti-Leak Hosts Pinning**, длина-сохраняющий бинарный патч PE/Protobuf (`ineligible` ➔ `inexigible`) и отказоустойчивый Watchdog с нулевым оверхедом по трафику (Zero-VPN).

---

## 1. Предыстория и анатомия инцидента 24–25 августа

С момента релиза Google Antigravity российские разработчики разделились на два лагеря: те, кто заворачивал всю систему в тяжелый WireGuard/VLESS (теряя в скорости скачивания зависимостей и ломая локальные сервисы), и те, кто использовал SmartDNS / SNI-проксирование.

Однако 24 августа второй лагерь встретил «черный экран»:

```json
{
  "error": {
    "code": 400,
    "message": "User location is not supported for the API use.",
    "status": "FAILED_PRECONDITION"
  }
}
```

А в логах клиентского демона `language_server.exe` посыпались прерывания сокетов:
`[Error] Connection reset by peer (OS Error: 10054) on cloudcode-pa.googleapis.com:443`.

### Что на самом деле произошло под капотом?

1. **Деградация зон в SmartDNS**: Публичные резолверы исключили домен `cloudcode-pa.googleapis.com` из внутренней базы спуфинга.
2. **Каскадный DNS Fallback в Windows**: При сбое первичного шлюза служба `Dnscache` обращается к вторичному DNS. Вторичный резолвер вернул абсолютно честный, валидный по Geo-IP российский адрес Google (`172.217.x.x`).
3. **Кэширование утечки**: Windows сохранила российский IP в кэше DNS на TTL = 300 секунд. Любой последующий запрос gRPC/HTTP2 летел на локальный Google Front End (ESF), который мгновенно сбрасывал сессию.

---

## 2. Архитектура трёхуровневой фильтрации Google

```
┌────────────────────────────────────────────────────────────────────────┐
│                        3 ЭШЕЛОНА БЛОКИРОВКИ                            │
├────────────────────────────────────────────────────────────────────────┤
│  [Уровень 1: L4 / Geo-IP]  ──► Проверка IP-адреса входящего TCP/TLS    │
│  [Уровень 2: Клиентский]   ──► Парсинг строки 'ineligible' в PE-бинаре │
│  [Уровень 3: L7 / Профиль] ──► Проверка страны аккаунта (:loadCodeAssist)│
└────────────────────────────────────────────────────────────────────────┘
```

* **Уровень 1 (L4 Geo-IP):** Проверяется физический IP входящего соединения на `cloudcode-pa.googleapis.com`.
* **Уровень 2 (Language Server):** Зашит парсер статуса `ineligible` в PE-бинаре `language_server.exe`.
* **Уровень 3 (L7 Profile):** Эндпоинт `:loadCodeAssist` возвращает статус ошибки для профилей РФ.

---

## 3. Инженерное решение: Zero-VPN Архитектура

Главное требование — **Zero-VPN**: трафик браузера, онлайн-игр и загрузок идет напрямую без задержек, а маршрутизируются только модельные вызовы.

### Anti-Leak Hosts Pinning (Python)

```python
# tools/hosts_manager.py
import os
import subprocess
from pathlib import Path

HOSTS_PATH = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32/drivers/etc/hosts"

TARGET_DOMAINS = [
    "cloudcode-pa.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "generativelanguage.googleapis.com",
    "antigravity-unleash.goog",
    "cloudaicompanion.googleapis.com",
    "jetski-webchannel.googleapis.com",
]

def apply_hosts_pinning(active_ip: str) -> bool:
    content = HOSTS_PATH.read_text(encoding="utf-8", errors="ignore")
    lines = [l for l in content.splitlines() if "# AntigravityUnlocker" not in l]
    
    new_block = ["\n# >>> AntigravityUnlocker Rules [DO NOT EDIT]"]
    for domain in TARGET_DOMAINS:
        new_block.append(f"{active_ip:<16} {domain} # AntigravityUnlocker")
    new_block.append("# <<< AntigravityUnlocker Rules\n")
    
    HOSTS_PATH.write_text("\n".join(lines) + "\n" + "\n".join(new_block), encoding="utf-8")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=True)
    return True
```

### Длина-сохраняющий бинарный патч PE

Патчим литерал `ineligible` на `inexigible` (ровно 10 байт):

```python
# tools/binary_patcher.py
def patch_language_server(binary_path: Path) -> bool:
    data = bytearray(binary_path.read_bytes())
    target = b"ineligible"
    replacement = b"inexigible"
    
    occurrences = 0
    pos = 0
    while True:
        pos = data.find(target, pos)
        if pos == -1:
            break
        data[pos:pos+len(replacement)] = replacement
        pos += len(replacement)
        occurrences += 1
        
    if occurrences > 0:
        binary_path.write_bytes(data)
        return True
    return False
```

### Smart Auto-Failover Watchdog

```python
# tools/watchdog.py
import socket
import ssl
import time

def check_sni_health(ip: str, domain: str = "cloudcode-pa.googleapis.com", timeout: float = 3.0) -> bool:
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((ip, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                return ssock.version() is not None
    except Exception:
        return False
```

---

## 4. Репозиторий проекта
Исходный код, схемы и скомпилированные релизы полностью открыты:
👉 **[GitHub: Antigravity-Unlock](https://github.com/Renkiy/Antigravity-Unlock)**
