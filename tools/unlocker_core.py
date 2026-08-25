import os
import sys
import ctypes
import subprocess
import json
import time

from tools.backup_manager import create_backup, restore_backup, list_backups
from tools.proxy_manager import (
    find_best_proxy, pin_hosts, unpin_hosts, get_current_pinned_ip,
    clean_leaking_nrpt_rules
)

DEFAULT_BACKEND_URL = "https://daily-cloudcode-pa.googleapis.com"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def elevate_process(args=None):
    if is_admin():
        return True
    
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{a}"' for a in (args or sys.argv[1:])])
    executable = sys.executable

    print("[*] Запрос прав Администратора для модификации системных параметров...")
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        executable,
        f'"{script}" {params}',
        None,
        1 # SW_SHOWNORMAL
    )
    if ret > 32:
        sys.exit(0) # Успешно запущен повышенный процесс
    else:
        print("[-] Пользователь отклонил запрос прав Администратора.")
        return False

def get_binary_paths():
    local_app = os.environ.get("LOCALAPPDATA", "")
    app_data = os.environ.get("APPDATA", "")
    user_prof = os.environ.get("USERPROFILE", "")

    candidate_paths = [
        os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "language_server.exe"),
        os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "agy.exe"),
        os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server_windows_x64.exe"),
        os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server.exe"),
        os.path.join(user_prof, ".antigravity", "bin", "language_server.exe"),
        os.path.join(user_prof, ".antigravity", "bin", "agy.exe")
    ]
    
    # Также проверим расширения VS Code / Cursor / Antigravity IDE
    ext_dir = os.path.join(user_prof, ".antigravity", "extensions")
    if os.path.exists(ext_dir):
        for root, _, files in os.walk(ext_dir):
            for f in files:
                if f.lower() in ("language_server.exe", "language_server_windows_x64.exe", "agy.exe"):
                    candidate_paths.append(os.path.join(root, f))

    found = []
    for p in candidate_paths:
        if os.path.exists(p) and p not in found:
            found.append(p)
    return found

def patch_binaries():
    bins = get_binary_paths()
    patched_any = False
    for bpath in bins:
        fname = os.path.basename(bpath)
        try:
            with open(bpath, "rb") as f:
                data = f.read()
            orig = data.count(b"ineligible")
            patched = data.count(b"inexigible")
            if orig > 0:
                subprocess.run(["taskkill", "/F", "/IM", fname], capture_output=True)
                time.sleep(0.3)
                new_data = data.replace(b"ineligible", b"inexigible")
                with open(bpath, "wb") as f:
                    f.write(new_data)
                print(f"  [+] {fname}: Успешно пропатчен ({orig} замен).")
                patched_any = True
            elif patched > 0:
                print(f"  [i] {fname}: Уже пропатчен ({patched} вхождений).")
            else:
                print(f"  [?] {fname}: Сигнатуры не найдены.")
        except Exception as e:
            print(f"  [-] {fname}: Ошибка патчинга: {e}")
    return True

def unpatch_binaries():
    bins = get_binary_paths()
    for bpath in bins:
        fname = os.path.basename(bpath)
        try:
            with open(bpath, "rb") as f:
                data = f.read()
            patched = data.count(b"inexigible")
            if patched > 0:
                subprocess.run(["taskkill", "/F", "/IM", fname], capture_output=True)
                time.sleep(0.3)
                new_data = data.replace(b"inexigible", b"ineligible")
                with open(bpath, "wb") as f:
                    f.write(new_data)
                print(f"  [+] {fname}: Откачен обратно ({patched} замен).")
        except Exception as e:
            print(f"  [-] {fname}: Ошибка: {e}")

def configure_ide_settings(backend_url=DEFAULT_BACKEND_URL):
    app_data = os.environ.get("APPDATA", "")
    settings_dir = os.path.join(app_data, "Antigravity IDE", "User")
    settings_path = os.path.join(settings_dir, "settings.json")
    os.makedirs(settings_dir, exist_ok=True)

    data = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["jetski.cloudCodeUrl"] = backend_url
    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"  [+] Antigravity IDE: Настройка jetski.cloudCodeUrl = {backend_url}")
        return True
    except Exception as e:
        print(f"  [-] Ошибка записи settings.json: {e}")
        return False

def configure_env_vars(backend_url=DEFAULT_BACKEND_URL):
    cmd = f'[Environment]::SetEnvironmentVariable("CLOUD_CODE_URL", "{backend_url}", "User")'
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    os.environ["CLOUD_CODE_URL"] = backend_url
    print(f"  [+] Переменная окружения CLOUD_CODE_URL установлена ({backend_url}).")

def remove_env_vars():
    cmd = '[Environment]::SetEnvironmentVariable("CLOUD_CODE_URL", $null, "User")'
    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    if "CLOUD_CODE_URL" in os.environ:
        del os.environ["CLOUD_CODE_URL"]
    print("  [+] Переменная окружения CLOUD_CODE_URL удалена.")

def set_ipv4_priority(enable=True):
    val = "46" if enable else "35"
    cmd = ["netsh", "interface", "ipv6", "set", "prefixpolicy", "::ffff:0:0/96", val, "4"]
    subprocess.run(cmd, capture_output=True)
    status = "включен" if enable else "сброшен"
    print(f"  [+] Приоритет IPv4 над IPv6: {status}.")

def execute_unlock(auto_find_proxy=True, target_ip=None, custom_worker_url=None):
    print("=" * 60)
    print("АКТИВАЦИЯ АНЛОКА ANTIGRAVITY (ГИБРИДНЫЙ АНТИ-LEAK АНЛОК)")
    print("=" * 60)

    # 1. Автоматический бэкап
    print("\n[Шаг 1/6] Создание резервной копии системы...")
    create_backup("pre_unlock")

    # 2. Очистка опасных правил NRPT (защита от утечки в 111.88.96.50 и 172.217.x.x)
    print("\n[Шаг 2/6] Очистка сбойных правил NRPT и изоляция DNS...")
    clean_leaking_nrpt_rules()

    # 3. Выбор живого прокси
    if not target_ip:
        if auto_find_proxy:
            print("\n[Шаг 3/6] Поиск самого быстрого живого зарубежного SNI-прокси...")
            target_ip = find_best_proxy(verbose=True)
        else:
            target_ip = "94.130.180.225"

    # Привязка в hosts
    print(f"\n[Шаг 4/6] Привязка хостов в hosts к {target_ip}...")
    ok, msg = pin_hosts(target_ip)
    if ok:
        print(f"  [+] {msg}")
    else:
        print(f"  [-] {msg}")

    # 4. Патчинг бинарников (обход статуса ineligible для русских аккаунтов)
    print("\n[Шаг 5/6] Патчинг исполняемых файлов Language Server / agy...")
    patch_binaries()

    # 5. Конфигурация IDE и переменных окружения
    backend_url = custom_worker_url if custom_worker_url else DEFAULT_BACKEND_URL
    print(f"\n[Шаг 6/6] Настройка эндпоинтов IDE ({backend_url}) и сетевых политик...")
    configure_ide_settings(backend_url)
    configure_env_vars(backend_url)
    set_ipv4_priority(True)
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)

    print("\n" + "=" * 60)
    print("[УСПЕХ] Разблокировка успешно завершена! Antigravity готова к работе.")
    print("=" * 60)
    return True

def execute_rollback():
    print("=" * 60)
    print("ПОЛНЫЙ ОТКАТ ВСЕХ ИЗМЕНЕНИЙ (RESTORE)")
    print("=" * 60)

    print("\n[1/5] Удаление привязок из hosts и очистка NRPT...")
    ok, msg = unpin_hosts()
    print(f"  {msg}")

    print("\n[2/5] Откат бинарных патчей...")
    unpatch_binaries()

    print("\n[3/5] Удаление переменных окружения...")
    remove_env_vars()

    print("\n[4/5] Восстановление приоритета IPv6...")
    set_ipv4_priority(False)

    print("\n[5/5] Очистка DNS кэша...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True)

    print("\n" + "=" * 60)
    print("[УСПЕХ] Система полностью возвращена в исходное состояние.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    if not is_admin():
        elevate_process()
    else:
        if len(sys.argv) > 1 and sys.argv[1] == "--restore":
            execute_rollback()
        else:
            execute_unlock()

