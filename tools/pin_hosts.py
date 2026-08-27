import os
import sys
import subprocess

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts") if sys.platform == "win32" else "/etc/hosts"

BEGIN_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_START ==="
END_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_END ==="

# Working SNI-proxies verified on 2026-08-25:
# 45.88.174.252 (comss-node-nl-3)
PINNED_ENTRIES = [
    ("generativelanguage.googleapis.com", "45.88.174.252"),
    ("daily-cloudcode-pa.googleapis.com", "45.88.174.252"),
    ("antigravity-unleash.goog", "45.88.174.252"),
    ("cloudaicompanion.googleapis.com", "45.88.174.252"),
    ("cloudcode-pa.googleapis.com", "45.88.174.252"),
    ("jetski-webchannel.googleapis.com", "45.88.174.252"),
    ("alkalimakersuite-pa.googleapis.com", "45.88.174.252"),
    ("aistudio.google.com", "45.88.174.252"),
    ("antigravity.google", "45.88.174.252")
]

def flush_dns():
    if sys.platform == "darwin":
        subprocess.run(["dscacheutil", "-flushcache"], capture_output=True)
        subprocess.run(["killall", "-HUP", "mDNSResponder"], capture_output=True)
    elif sys.platform == "win32":
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    else:
        for cmd in [["resolvectl", "flush-caches"], ["systemd-resolve", "--flush-caches"]]:
            try:
                subprocess.run(cmd, capture_output=True)
            except Exception:
                pass

def apply_hosts_pin():
    print(f"[+] Чтение {HOSTS_PATH}...")
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"[-] Ошибка чтения hosts: {e}")
        return False

    # Удаляем предыдущий блок, если есть
    lines = []
    inside_block = False
    for line in content.splitlines():
        if BEGIN_MARKER in line:
            inside_block = True
            continue
        if END_MARKER in line:
            inside_block = False
            continue
        if not inside_block:
            lines.append(line)

    # Добавляем новый блок
    lines.append("")
    lines.append(BEGIN_MARKER)
    for host, ip in PINNED_ENTRIES:
        lines.append(f"{ip:16} {host}")
    lines.append(END_MARKER)
    lines.append("")

    new_content = "\n".join(lines)
    try:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("  [+] Hosts файл успешно обновлен с привязкой к активному прокси 45.88.174.252!")
        flush_dns()
        return True
    except PermissionError:
        print("  [-] Требуются права Администратора / sudo для записи в hosts файл.")
        return False
    except Exception as e:
        print(f"  [-] Ошибка записи hosts: {e}")
        return False

def remove_hosts_pin():
    print(f"[+] Очистка {HOSTS_PATH} от привязок анлокера...")
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"[-] Ошибка чтения hosts: {e}")
        return False

    lines = []
    inside_block = False
    for line in content.splitlines():
        if BEGIN_MARKER in line:
            inside_block = True
            continue
        if END_MARKER in line:
            inside_block = False
            continue
        if not inside_block:
            lines.append(line)

    new_content = "\n".join(lines)
    try:
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("  [+] Записи анлокера удалены из hosts.")
        flush_dns()
        return True
    except Exception as e:
        print(f"  [-] Ошибка записи: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        remove_hosts_pin()
    else:
        apply_hosts_pin()
