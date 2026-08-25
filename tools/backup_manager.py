import os
import sys
import shutil
import json
import time
import subprocess
from datetime import datetime

BACKUP_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backups")

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")

def get_target_files():
    local_app = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    
    files = {
        "hosts": HOSTS_PATH,
        "ide_settings": os.path.join(app_data, "Antigravity IDE", "User", "settings.json"),
        "language_server_desktop": os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "language_server.exe"),
        "language_server_ide": os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server_windows_x64.exe"),
    }
    return files

def create_backup(label="auto"):
    os.makedirs(BACKUP_ROOT, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_ROOT, f"backup_{ts}_{label}")
    os.makedirs(backup_dir, exist_ok=True)

    manifest = {
        "timestamp": ts,
        "label": label,
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

    # Бэкап правил NRPT
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
    subprocess.run(["taskkill", "/F", "/IM", "language_server.exe"], capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "language_server_windows_x64.exe"], capture_output=True)
    time.sleep(0.5)

    for key, info in manifest.get("files", {}).items():
        orig_path = info["original_path"]
        bak_file = os.path.join(backup_path, info["backup_file"])
        if os.path.exists(bak_file):
            try:
                os.makedirs(os.path.dirname(orig_path), exist_ok=True)
                shutil.copy2(bak_file, orig_path)
                print(f"  [+] Восстановлен: {orig_path}")
                restored_count += 1
            except Exception as e:
                print(f"  [-] Ошибка восстановления {orig_path}: {e}")

    # Очистка DNS кэша
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
    print(f"[+] Восстановлено файлов: {restored_count}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        restore_backup()
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        bks = list_backups()
        print(f"Найдено бэкапов: {len(bks)}")
        for name, path, mf in bks:
            print(f" - {name} ({mf.get('created_at')})")
    else:
        create_backup("manual")
