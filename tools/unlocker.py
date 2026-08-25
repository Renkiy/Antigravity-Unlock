import os
import sys
import subprocess
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

CORE_DOMAINS = [
    "cloudcode-pa.googleapis.com",
    "daily-cloudcode-pa.googleapis.com",
    "generativelanguage.googleapis.com",
    "antigravity-unleash.goog"
]

FALLBACK_DNS_SERVERS = [
    "83.220.169.155",  # comss.one (основной рабочий SNI/DNS)
    "212.109.195.93",  # comss.one (резервный)
    "111.88.96.50",    # xbox-dns.ru
    "111.88.96.51"     # xbox-dns.ru
]

def get_binaries():
    local_app = os.environ.get("LOCALAPPDATA", "")
    paths = [
        os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "language_server.exe"),
        os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server_windows_x64.exe"),
        os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "agy.exe")
    ]
    return [p for p in paths if os.path.exists(p)]

def patch_binaries():
    print("[+] Патчинг исполняемых файлов Language Server...")
    bins = get_binaries()
    if not bins:
        print("  [-] Исполняемые файлы Antigravity не найдены в стандартных путях.")
        return

    for bpath in bins:
        fname = os.path.basename(bpath)
        try:
            with open(bpath, "rb") as f:
                data = f.read()
            
            orig_cnt = data.count(b"ineligible")
            patched_cnt = data.count(b"inexigible")

            if orig_cnt > 0:
                # Резервная копия
                bak = bpath + ".orig.bak"
                if not os.path.exists(bak):
                    with open(bak, "wb") as bf:
                        bf.write(data)
                    print(f"  [+] Создан бэкап: {bak}")
                
                # Закрытие процессов, если файл заблокирован
                subprocess.run(["taskkill", "/F", "/IM", fname], capture_output=True)
                
                # Замена
                new_data = data.replace(b"ineligible", b"inexigible")
                with open(bpath, "wb") as f:
                    f.write(new_data)
                print(f"  [+] {fname}: Успешно заменено {orig_cnt} вхождений ineligible -> inexigible")
            elif patched_cnt > 0:
                print(f"  [i] {fname}: Уже пропатчен ({patched_cnt} вхождений inexigible)")
            else:
                print(f"  [?] {fname}: Сигнатуры не обнаружены")
        except Exception as e:
            print(f"  [-] {fname}: Ошибка: {e}")

def restore_binaries():
    print("[+] Восстановление оригинальных бинарников...")
    bins = get_binaries()
    for bpath in bins:
        fname = os.path.basename(bpath)
        bak = bpath + ".orig.bak"
        if os.path.exists(bak):
            try:
                subprocess.run(["taskkill", "/F", "/IM", fname], capture_output=True)
                with open(bak, "rb") as bf:
                    data = bf.read()
                with open(bpath, "wb") as f:
                    f.write(data)
                print(f"  [+] {fname}: Восстановлен из {bak}")
            except Exception as e:
                print(f"  [-] {fname}: Ошибка восстановления: {e}")
        else:
            try:
                with open(bpath, "rb") as f:
                    data = f.read()
                cnt = data.count(b"inexigible")
                if cnt > 0:
                    subprocess.run(["taskkill", "/F", "/IM", fname], capture_output=True)
                    new_data = data.replace(b"inexigible", b"ineligible")
                    with open(bpath, "wb") as f:
                        f.write(new_data)
                    print(f"  [+] {fname}: Откачено {cnt} патчей обратно на ineligible")
            except Exception as e:
                print(f"  [-] {fname}: Ошибка: {e}")

def apply_nrpt():
    print("[+] Настройка правил NRPT (Windows Name Resolution Policy Table)...")
    ns_str = ", ".join(f"'{d}'" for d in CORE_DOMAINS)
    dns_str = ", ".join(f"'{s}'" for s in FALLBACK_DNS_SERVERS)
    
    ps_cmd = f"""
    Get-DnsClientNrptRule -ErrorAction SilentlyContinue | Where-Object {{ $_.Comment -like '*AG_UNLOCKER*' }} | Remove-DnsClientNrptRule -Force -ErrorAction SilentlyContinue;
    Add-DnsClientNrptRule -Namespace @({ns_str}) -NameServers @({dns_str}) -Comment 'AG_UNLOCKER_NRPT_V2' -ErrorAction SilentlyContinue;
    Clear-DnsClientCache;
    """
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    if res.returncode == 0:
        print("  [+] Правила NRPT успешно применены!")
    else:
        print(f"  [-] Ошибка применения NRPT: {res.stderr}")

def remove_nrpt():
    print("[+] Удаление правил NRPT...")
    ps_cmd = """
    Get-DnsClientNrptRule -ErrorAction SilentlyContinue | Where-Object { $_.Comment -like '*AG_UNLOCKER*' } | Remove-DnsClientNrptRule -Force -ErrorAction SilentlyContinue;
    Clear-DnsClientCache;
    """
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
    if res.returncode == 0:
        print("  [+] Правила NRPT удалены, DNS кэш очищен.")
    else:
        print(f"  [-] Ошибка: {res.stderr}")

def set_ipv4_priority(enable=True):
    val = "46" if enable else "35"
    action = "Включение приоритета IPv4" if enable else "Восстановление приоритета IPv6"
    print(f"[+] {action}...")
    cmd = ["netsh", "interface", "ipv6", "set", "prefixpolicy", "::ffff:0:0/96", val, "4"]
    subprocess.run(cmd, capture_output=True)

def apply_all():
    print("=" * 60)
    print("ANTIGRAVITY UNLOCKER: АКТИВАЦИЯ АНЛОКА В РФ")
    print("=" * 60)
    patch_binaries()
    apply_nrpt()
    set_ipv4_priority(True)
    print("=" * 60)
    print("[OK] Разблокировка успешно применена! Antigravity готова к работе.")

def rollback_all():
    print("=" * 60)
    print("ANTIGRAVITY UNLOCKER: ПОЛНЫЙ ОТКАТ (ROLLBACK)")
    print("=" * 60)
    restore_binaries()
    remove_nrpt()
    set_ipv4_priority(False)
    print("=" * 60)
    print("[OK] Все изменения отменены, система возвращена в исходное состояние.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Unlocker CLI")
    parser.add_argument("--apply", action="store_true", help="Применить полный анлок")
    parser.add_argument("--restore", action="store_true", help="Полный откат системы")
    parser.add_argument("--patch-only", action="store_true", help="Только бинарный патч")
    parser.add_argument("--nrpt-only", action="store_true", help="Только правила NRPT")
    args = parser.parse_args()

    if args.restore:
        rollback_all()
    elif args.patch_only:
        patch_binaries()
    elif args.nrpt_only:
        apply_nrpt()
    else:
        apply_all()
