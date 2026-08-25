import os
import sys
import subprocess

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")

BEGIN_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_START ==="
END_MARKER = "# === ANTIGRAVITY_UNLOCKER_PIN_END ==="

# Working SNI-proxies verified on 2026-08-25:
# 45.88.174.254 (gemini-pool.comss.one) - TLS verified for all hosts
# 87.228.47.194 (xbox-dns) - TLS verified for generativelanguage
PINNED_ENTRIES = [
    ("generativelanguage.googleapis.com", "45.88.174.254"),
    ("daily-cloudcode-pa.googleapis.com", "45.88.174.254"),
    ("antigravity-unleash.goog", "45.88.174.254"),
    ("cloudaicompanion.googleapis.com", "45.88.174.254"),
    ("cloudcode-pa.googleapis.com", "45.88.174.254"),
]

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
        print("  [+] Hosts файл успешно обновлен с привязкой к активному прокси 45.88.174.254!")
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
        return True
    except PermissionError:
        print("  [-] Требуются права Администратора для записи в hosts файл.")
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
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
        return True
    except Exception as e:
        print(f"  [-] Ошибка записи: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        remove_hosts_pin()
    else:
        apply_hosts_pin()
