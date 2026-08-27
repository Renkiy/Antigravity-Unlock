import os
import sys
import socket
import subprocess
import ssl

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TARGET_DOMAINS = [
    "antigravity.google",
    "cloudcode-pa.googleapis.com",
    "generativelanguage.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "antigravity-unleash.goog",
    "cloudaicompanion.googleapis.com",
    "accounts.google.com",
    "oauth2.googleapis.com"
]

# Известные префиксы прямых серверов Google в РФ / СНГ, блокирующих по Geo-IP
KNOWN_DIRECT_GOOGLE_PREFIXES = ("172.217.", "142.250.", "216.58.", "173.194.", "74.125.")

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts") if sys.platform == "win32" else "/etc/hosts"

def check_hosts_pinning():
    print("=" * 60)
    print(f"[1] Проверка привязки хостов в файле {HOSTS_PATH}:")
    found_pins = []
    if os.path.exists(HOSTS_PATH):
        try:
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for line in lines:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    parts = line_str.split()
                    if len(parts) >= 2 and any(d in parts[1] for d in ("googleapis.com", "antigravity")):
                        found_pins.append((parts[0], parts[1]))
        except Exception as e:
            print(f"  [-] Ошибка чтения hosts: {e}")

    if found_pins:
        print(f"  [+] Обнаружено {len(found_pins)} активных привязок в hosts:")
        for ip, host in found_pins:
            print(f"      {ip:16} -> {host}")
    else:
        print("  [!] Внимание: Привязки в hosts отсутствуют! Используется системный DNS.")

def check_nrpt_rules():
    if sys.platform != "win32":
        return
    print("=" * 60)
    print("[2] Проверка таблицы правил NRPT (Windows Name Resolution Policy Table):")
    cmd = ["powershell", "-NoProfile", "-Command", "Get-DnsClientNrptRule -ErrorAction SilentlyContinue | Select-Object Namespace, NameServers, Comment | Format-Table -AutoSize"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = res.stdout.strip()
    if out:
        print(out)
        if "111.88.96.50" in out or "111.88.96.51" in out:
            print("  [!] ВНИМАНИЕ: Обнаружен сбойный DNS (111.88.96.50)! Возможна утечка в российский IP.")
        else:
            print("  [+] Активные правила NRPT зафиксированы.")
    else:
        print("  [+] Правила NRPT отсутствуют (Безопасно: исключен риск fallback-утечки).")

def check_dns_resolving():
    print("=" * 60)
    print("[2/3] Проверка разрешения целевых доменов (Анализ IP-адресов):")
    leak_detected = False
    for domain in TARGET_DOMAINS:
        try:
            ips = socket.gethostbyname_ex(domain)[2]
            ip_str = ", ".join(ips)
            # Проверяем, не резолвится ли в прямой IP Google для заблокированных зон
            is_direct = any(any(ip.startswith(p) for p in KNOWN_DIRECT_GOOGLE_PREFIXES) for ip in ips)
            
            if is_direct and "accounts" not in domain and "oauth" not in domain:
                print(f"  [!] ОПАСНОСТЬ: {domain:35} -> {ip_str} (ПРЯМОЙ GOOGLE IP — БУДЕТ GEO-BLOCK!)")
                leak_detected = True
            else:
                print(f"  [+] {domain:35} -> {ip_str}")
        except Exception as e:
            print(f"  [-] {domain:35} -> ОШИБКА: {e}")
    
    if leak_detected:
        print("\n  [ВНИМАНИЕ] Обнаружена утечка прямых IP Google! Рекомендуется активировать анлокер.")

def check_tls_connectivity():
    print("=" * 60)
    print("[3/4] Проверка TCP и TLS 443 хэндшейка (Стриминг и API):")
    for domain in TARGET_DOMAINS[:4]:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=3.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    issuer = dict(x[0] for x in cert.get('issuer', [])).get('commonName', 'Unknown')
                    print(f"  [+] TLS 443 OK: {domain:35} (Issuer: {issuer})")
        except socket.timeout:
            print(f"  [-] TLS 443 TIMEOUT: {domain:35} -> Таймаут сокета")
        except ConnectionResetError:
            print(f"  [-] TLS 443 RESET (10054): {domain:35} -> Соединение сброшено узлом")
        except Exception as e:
            print(f"  [-] TLS 443 FAIL: {domain:35} -> {e}")

def check_binary_patches():
    print("=" * 60)
    print("[4/5] Проверка бинарных патчей (Обход блокировки российских аккаунтов):")
    
    # Import paths from unlocker_core
    try:
        from tools.unlocker_core import get_binary_paths
        bin_paths = get_binary_paths()
    except Exception:
        home = os.path.expanduser("~")
        bin_paths = [
            "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm",
            os.path.join(home, ".local", "bin", "agy")
        ]
    
    found_any = False
    for bp in bin_paths:
        if os.path.exists(bp):
            found_any = True
            try:
                with open(bp, "rb") as f:
                    data = f.read()
                inel = data.count(b"ineligible")
                inex = data.count(b"inexigible")
                print(f"  File: {os.path.basename(bp)} ({bp})")
                print(f"    - 'ineligible' (оригинальный блок): {inel}")
                print(f"    - 'inexigible' (патч аккаунта):      {inex}")
                
                # Check code signature on macOS
                if sys.platform == "darwin":
                    cs_res = subprocess.run(["codesign", "-v", bp], capture_output=True, text=True)
                    cs_status = "ПОДПИСЬ ВАЛИДНА [OK]" if cs_res.returncode == 0 else f"ПОДПИСЬ ПОВРЕЖДЕНА (Нужен codesign): {cs_res.stderr.strip()}"
                    print(f"    - macOS CodeSign: {cs_status}")

                if inex > 0 and inel == 0:
                    print("    -> СТАТУС: ПОЛНОСТЬЮ ПРОПАТЧЕН [OK]")
                elif inel > 0:
                    print("    -> СТАТУС: ТРЕБУЕТСЯ ПАТЧИНГ [NEED PATCH]")
                else:
                    print("    -> СТАТУС: Сигнатуры не обнаружены")
            except Exception as e:
                print(f"  File: {bp} -> Ошибка чтения: {e}")

    if not found_any:
        print("  [-] Исполняемые файлы Antigravity не найдены в стандартных путях.")

if __name__ == "__main__":
    print("Комплексная диагностика Antigravity Unlocker...")
    check_hosts_pinning()
    if sys.platform == "win32":
        check_nrpt_rules()
    check_dns_resolving()
    check_tls_connectivity()
    check_binary_patches()
    print("=" * 60)

