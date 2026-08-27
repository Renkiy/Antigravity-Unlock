import os
import sys
import shutil
import json
import time
import subprocess
from datetime import datetime

BACKUP_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts") if sys.platform == "win32" else "/etc/hosts"

def get_target_files():
    home = os.path.expanduser("~")
    files = {"hosts": HOSTS_PATH}

    if sys.platform == "win32":
        local_app = os.environ.get("LOCALAPPDATA", "")
        app_data = os.environ.get("APPDATA", "")
        files.update({
            "ide_settings": os.path.join(app_data, "Antigravity IDE", "User", "settings.json"),
            "language_server_desktop": os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "language_server.exe"),
            "language_server_ide": os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server_windows_x64.exe"),
            "agy": os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "agy.exe")
        })
    elif sys.platform == "darwin":
        files.update({
            "ide_settings": os.path.join(home, "Library", "Application Support", "Antigravity IDE", "User", "settings.json"),
            "language_server_macos_arm": "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm",
            "language_server_macos_x64": "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_x64",
            "agy": os.path.join(home, ".local", "bin", "agy")
        })
    else:
        # Linux
        files.update({
            "ide_settings": os.path.join(home, ".config", "Antigravity IDE", "User", "settings.json"),
            "language_server_linux_x64": "/opt/Antigravity/resources/app/extensions/antigravity/bin/language_server_linux_x64",
            "language_server_linux_arm64": "/opt/Antigravity/resources/app/extensions/antigravity/bin/language_server_linux_arm64",
            "agy": os.path.join(home, ".local", "bin", "agy")
        })
    return files

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

def create_backup(label="auto"):
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_ROOT, f"backup_{ts}_{label}")
    os.makedirs(backup_dir, exist_ok=True)

    manifest = {
        "timestamp": ts,
        "label": label,
        "platform": sys.platform,
        "created_at": datetime.now().isoformat(),
        "files": {},
        "nrpt_rules": []
    }

    files = get_target_files()
    for key, path in files.items():
        if os.path.exists(path):
            dest_name = f"{key}_{os.path.basename(path)}"
            dest_path = os.path.join(backup_dir, dest_name)
            try:
                shutil.copy2(path, dest_path)
                manifest["files"][key] = {
                    "original_path": path,
                    "backup_file": dest_name,
                    "size": os.path.getsize(path)
                }
            except Exception as e:
                print(f"[-] Ошибка бэкапа {key} ({path}): {e}")

    # Бэкап правил NRPT только для Windows
    if sys.platform == "win32":
        try:
            cmd = ["powershell", "-NoProfile", "-Command", "Get-DnsClientNrptRule -ErrorAction SilentlyContinue | Select-Object Namespace, NameServers, Comment | ConvertTo-Json -Depth 3"]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
            if res.returncode == 0 and res.stdout.strip():
                manifest["nrpt_rules"] = json.loads(res.stdout)
        except Exception as e:
            print(f"[-] Ошибка экспорта NRPT: {e}")

    manifest_path = os.path.join(backup_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[+] Бэкап успешно создан: {backup_dir}")
    return backup_dir, manifest

def list_backups():
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    backups = []
    for item in sorted(os.listdir(BACKUP_ROOT), reverse=True):
        bpath = os.path.join(BACKUP_ROOT, item)
        mpath = os.path.join(bpath, "manifest.json")
        if os.path.isdir(bpath) and os.path.exists(mpath):
            try:
                with open(mpath, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    backups.append((item, bpath, manifest))
            except Exception:
                pass
    return backups

def restore_backup(backup_path=None):
    if not backup_path:
        backups = list_backups()
        if not backups:
            print("[-] Доступных резервных копий не найдено.")
            return False
        backup_path = backups[0][1] # Берем самый свежий

    manifest_path = os.path.join(backup_path, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"[-] Файл манифеста не найден в {backup_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"[+] Восстановление из бэкапа: {manifest.get('created_at', backup_path)}")
    restored_count = 0

    # Закрываем процессы перед восстановлением файлов
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", "language_server.exe"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "language_server_windows_x64.exe"], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "agy.exe"], capture_output=True)
    else:
        subprocess.run(["pkill", "-f", "language_server"], capture_output=True)
        subprocess.run(["pkill", "-f", "agy"], capture_output=True)
    time.sleep(0.5)

    for key, info in manifest.get("files", {}).items():
        orig_path = info["original_path"]
        bak_file = os.path.join(backup_path, info["backup_file"])
        if os.path.exists(bak_file):
            try:
                os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                shutil.copy2(bak_file, orig_path)
                print(f"  [+] Восстановлен: {orig_path}")
                
                # На macOS переподписываем
                if sys.platform == "darwin" and ("language_server" in orig_path or "agy" in orig_path):
                    subprocess.run(["xattr", "-cr", orig_path], capture_output=True)
                    subprocess.run(["codesign", "--force", "--deep", "--sign", "-", orig_path], capture_output=True)

                restored_count += 1
            except Exception as e:
                print(f"  [-] Ошибка восстановления {orig_path}: {e}")

    # Очистка DNS кэша
    flush_dns()
    print(f"[+] Восстановлено файлов: {restored_count}")
    return True

def print_backups_table():
    backups = list_backups()
    if not backups:
        print("\n  [-] Резервных копий пока нет.\n")
        return []
    
    print("\n" + "=" * 80)
    print(f"{'#':<3} | {'Имя бэкапа':<35} | {'Дата создания':<20} | {'Файлов':<8}")
    print("-" * 80)
    for idx, (name, bpath, mf) in enumerate(backups, 1):
        created = str(mf.get("created_at", "N/A"))[:19].replace("T", " ")
        files_cnt = f"{len(mf.get('files', {}))} шт."
        badge = " (Оригиналы)" if "initial_original" in name else ""
        print(f"[{idx}] | {name + badge:<35} | {created:<20} | {files_cnt:<8}")
    print("=" * 80 + "\n")
    return backups

def interactive_cli():
    while True:
        print("\n" + "=" * 60)
        print("🛡️  УПРАВЛЕНИЕ РЕЗЕРВНЫМИ КОПИЯМИ (БЭКАПЫ)")
        print("=" * 60)
        backups = print_backups_table()
        
        print("Действия:")
        if backups:
            print("  [1-N] - Восстановить выбранный бэкап по номеру")
        print("  [c]   - Создать новый бэкап сейчас")
        print("  [0]   - Вернуться в главное меню")
        print("-" * 60)
        
        choice = input("Введите команду: ").strip()
        if choice == "0" or choice.lower() in ("q", "exit"):
            break
        elif choice.lower() == "c":
            create_backup("manual")
        elif choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(backups):
                name, bpath, mf = backups[idx - 1]
                confirm = input(f"Восстановить файлы из бэкапа '{name}'? (y/n): ").strip().lower()
                if confirm in ("y", "yes", "д", "да"):
                    restore_backup(bpath)
            else:
                print("[-] Неверный номер бэкапа.")
        else:
            print("[-] Неизвестная команда.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        restore_backup(target)
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        print_backups_table()
    elif len(sys.argv) > 1 and sys.argv[1] == "--create":
        label = sys.argv[2] if len(sys.argv) > 2 else "manual"
        create_backup(label)
    elif len(sys.argv) > 1 and sys.argv[1] in ("-i", "--interactive"):
        interactive_cli()
    else:
        interactive_cli()
