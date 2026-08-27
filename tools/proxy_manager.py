import os
import sys
import socket
import ssl
import time
import subprocess
import threading
import concurrent.futures

import platform

# Проверенный и актуальный пул стабильных зарубежных SNI-прокси (Германия, Нидерланды)
# Исключены нестабильные и отключенные узлы (111.88.96.50, 95.182.120.241, 45.155.204.190)
PROXIES_POOL = [
    {"name": "comss-node-nl-3",   "ip": "45.88.174.252",  "country": "NL"},
    {"name": "comss-node-nl-1",   "ip": "45.88.174.254",  "country": "NL"},
    {"name": "comss-node-nl-2",   "ip": "45.88.174.253",  "country": "NL"},
    {"name": "comss-node-nl-4",   "ip": "45.88.174.251",  "country": "NL"},
    {"name": "hetzner-node-de-1", "ip": "94.130.180.225", "country": "DE"},
    {"name": "hetzner-node-de-2", "ip": "148.251.10.155", "country": "DE"},
    {"name": "hetzner-node-de-3", "ip": "188.40.142.18",  "country": "DE"},
    {"name": "hetzner-node-de-4", "ip": "136.243.104.148", "country": "DE"},
    {"name": "hetzner-node-de-5", "ip": "168.119.141.192", "country": "DE"},
]

SNI_HOSTS = [
    "cloudcode-pa.googleapis.com",
    "generativelanguage.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "cloudaicompanion.googleapis.com",
    "antigravity.google"
]

PINNED_HOSTS = [
    "cloudcode-pa.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "generativelanguage.googleapis.com",
    "antigravity-unleash.goog",
    "cloudaicompanion.googleapis.com",
    "jetski-webchannel.googleapis.com",
    "antigravity.google",
    "alkalimakersuite-pa.googleapis.com",
    "aistudio.google.com"
]

def get_hosts_path():
    if sys.platform == "win32":
        return os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
    return "/etc/hosts"

HOSTS_PATH = get_hosts_path()
BEGIN_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_START ==="
END_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_END ==="

def flush_dns_cache():
    """Кроссплатформенный сброс системного кэша DNS."""
    if sys.platform == "darwin":
        subprocess.run(["dscacheutil", "-flushcache"], capture_output=True)
        subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True)
    elif sys.platform == "win32":
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    else:
        # Linux
        for cmd in [
            ["resolvectl", "flush-caches"],
            ["systemd-resolve", "--flush-caches"],
            ["service", "nscd", "restart"]
        ]:
            try:
                res = subprocess.run(cmd, capture_output=True)
                if res.returncode == 0:
                    break
            except Exception:
                pass

def probe_single_host(ip, host_name, timeout=2.5):
    """Проверка TCP соединения и валидности TLS 443 рукопожатия с указанным SNI."""
    t0 = time.time()
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((ip, 443), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host_name) as ssock:
                _ = ssock.getpeercert()
                latency = (time.time() - t0) * 1000
                return True, latency, None
    except socket.timeout:
        return False, 9999, "Timeout"
    except ConnectionResetError as e:
        return False, 9999, f"RST 10054 ({e})"
    except Exception as e:
        return False, 9999, str(e)

def probe_proxy_node(node, timeout=2.5):
    """Многопоточная проверка одного узла по всем ключевым доменам Antigravity."""
    ip = node["ip"]
    name = node["name"]
    results = {}
    total_latency = 0
    passed_count = 0
    errors = []

    for sni in SNI_HOSTS:
        ok, lat, err = probe_single_host(ip, sni, timeout=timeout)
        results[sni] = (ok, lat)
        if ok:
            passed_count += 1
            total_latency += lat
        elif err:
            errors.append(f"{sni}: {err}")

    avg_latency = (total_latency / passed_count) if passed_count > 0 else 9999
    is_full_pass = (passed_count == len(SNI_HOSTS))

    return {
        "name": name,
        "ip": ip,
        "country": node.get("country", "EU"),
        "passed_count": passed_count,
        "total_hosts": len(SNI_HOSTS),
        "avg_latency": avg_latency,
        "is_full_pass": is_full_pass,
        "details": results,
        "errors": errors
    }

def find_best_proxy(verbose=True, timeout=2.0):
    """Сканирование всего пула и выбор самого быстрого и полностью здорового узла."""
    if verbose:
        print("[+] Сканирование пула зарубежных SNI-прокси серверов...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(PROXIES_POOL)) as executor:
        futures = [executor.submit(probe_proxy_node, p, timeout) for p in PROXIES_POOL]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Сортировка: сначала с максимальным числом успешных хостов, затем по минимальному пингу
    results.sort(key=lambda x: (-x["passed_count"], x["avg_latency"]))

    if verbose:
        for r in results:
            status = "100% OK" if r["is_full_pass"] else f"{r['passed_count']}/{r['total_hosts']} OK"
            lat_str = f"{r['avg_latency']:.0f} ms" if r["passed_count"] > 0 else "OFFLINE"
            print(f"  * [{status:7}] {r['name']:20} [{r['country']}] ({r['ip']:15}) -> {lat_str}")

    best = results[0]
    if best["passed_count"] > 0:
        if verbose:
            print(f"\n[+] Выбран оптимальный узел: {best['name']} ({best['ip']}) с задержкой {best['avg_latency']:.0f} ms")
        return best["ip"]
    
    # Резервный надежный адрес по умолчанию
    return "94.130.180.225"

def clean_leaking_nrpt_rules():
    """
    Удаление опасных правил NRPT (Windows Only).
    """
    if sys.platform != "win32":
        return True

    ps_cmd = """
    Get-DnsClientNrptRule -ErrorAction SilentlyContinue | 
        Where-Object { 
            $_.Comment -like '*AG_UNLOCKER*' -or 
            $_.NameServers -contains '111.88.96.50' -or 
            $_.NameServers -contains '111.88.96.51' -or
            $_.NameServers -contains '83.220.169.155'
        } | 
        Remove-DnsClientNrptRule -Force -ErrorAction SilentlyContinue;
    Clear-DnsClientCache;
    """
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

def pin_hosts(ip="45.88.174.252"):
    """Закрепление хостов Antigravity/Gemini в системном файле hosts."""
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return False, f"Ошибка чтения hosts: {e}"

    lines = []
    inside = False
    for line in content.splitlines():
        if BEGIN_MARKER in line:
            inside = True
            continue
        if END_MARKER in line:
            inside = False
            continue
        if not inside:
            lines.append(line)

    lines.append("")
    lines.append(BEGIN_MARKER)
    for host in PINNED_HOSTS:
        lines.append(f"{ip:16} {host}")
    lines.append(END_MARKER)
    lines.append("")

    new_content = "\n".join(lines)
    try:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        # Очистка опасных NRPT правил и сброс кэша
        clean_leaking_nrpt_rules()
        flush_dns_cache()
        return True, f"Хосты успешно привязаны к {ip} (DNS кэш очищен)"
    except PermissionError:
        return False, "Отказано в доступе (требуются права Администратора / sudo)"
    except Exception as e:
        return False, f"Ошибка записи hosts: {e}"

def unpin_hosts():
    """Удаление привязок из hosts и возврат к штатному состоянию."""
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return False, f"Ошибка чтения hosts: {e}"

    lines = []
    inside = False
    for line in content.splitlines():
        if BEGIN_MARKER in line:
            inside = True
            continue
        if END_MARKER in line:
            inside = False
            continue
        if not inside:
            lines.append(line)

    new_content = "\n".join(lines)
    try:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        clean_leaking_nrpt_rules()
        flush_dns_cache()
        return True, "Привязки успешно удалены из hosts"
    except PermissionError:
        return False, "Отказано в доступе (требуются права Администратора / sudo)"
    except Exception as e:
        return False, f"Ошибка записи hosts: {e}"

def get_current_pinned_ip():
    """Получение текущего активного IP, прописанного в блоке hosts."""
    if not os.path.exists(HOSTS_PATH):
        return None
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        inside = False
        for line in content.splitlines():
            if BEGIN_MARKER in line:
                inside = True
                continue
            if END_MARKER in line:
                break
            if inside and line.strip() and not line.strip().startswith("#"):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[0]
    except Exception:
        pass
    return None

class ProxyWatchdog:
    """
    Фоновый страж (Watchdog) для автоматического мониторинга здоровья активного прокси
    и мгновенного переключения (Failover) при сбоях (таймаут, RST 10054).
    """
    def __init__(self, check_interval=20, log_callback=None, failover_callback=None):
        self.check_interval = check_interval
        self.log_callback = log_callback
        self.failover_callback = failover_callback
        self.running = False
        self.thread = None
        self.consecutive_failures = 0

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"[Watchdog] {message}")

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.log("Служба активного мониторинга (Auto-Failover Watchdog) запущена.")

    def stop(self):
        self.running = False
        self.log("Служба мониторинга остановлена.")

    def _run_loop(self):
        while self.running:
            current_ip = get_current_pinned_ip()
            if current_ip:
                # Проверяем ключевой стриминговый хост
                ok, lat, err = probe_single_host(current_ip, "cloudcode-pa.googleapis.com", timeout=2.5)
                if not ok:
                    # Повторная быстрая перепроверка
                    time.sleep(1.0)
                    ok, lat, err = probe_single_host(current_ip, "cloudcode-pa.googleapis.com", timeout=2.5)

                if ok:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1
                    self.log(f"[!] Сбой текущего узла {current_ip} (Ошибка: {err}). Неудач подряд: {self.consecutive_failures}")

                    if self.consecutive_failures >= 2:
                        self.log("[*] Инициирован авто-переход (Failover) на резервный живой узел...")
                        new_ip = find_best_proxy(verbose=False, timeout=2.0)
                        if new_ip and new_ip != current_ip:
                            pin_ok, msg = pin_hosts(new_ip)
                            if pin_ok:
                                self.log(f"[+] [FAILOVER УСПЕШЕН] Хосты переключены на {new_ip}!")
                                self.consecutive_failures = 0
                                if self.failover_callback:
                                    self.failover_callback(new_ip)
                            else:
                                self.log(f"[-] Ошибка переключения hosts: {msg}")
            
            # Спим интервал частями для быстрого реагирования на stop()
            for _ in range(int(self.check_interval * 2)):
                if not self.running:
                    break
                time.sleep(0.5)

# Глобальный инстанс Watchdog
watchdog_instance = ProxyWatchdog()

if __name__ == "__main__":
    best_ip = find_best_proxy(verbose=True)
    print(f"\nТекущий закрепленный IP в hosts: {get_current_pinned_ip()}")

