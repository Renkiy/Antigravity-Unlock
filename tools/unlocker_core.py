import os
import sys
import ctypes
import subprocess
import json
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from tools.backup_manager import create_backup, restore_backup, list_backups
from tools.proxy_manager import (
    find_best_proxy, pin_hosts, unpin_hosts, get_current_pinned_ip,
    clean_leaking_nrpt_rules, flush_dns_cache
)

DEFAULT_BACKEND_URL = "https://daily-cloudcode-pa.googleapis.com"

def is_admin():
    """Проверка наличия прав администратора / root."""
    if sys.platform == "win32":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0

def elevate_process(args=None):
    """Перезапуск процесса с правами Администратора / root."""
    if is_admin():
        return True
    
    script = os.path.abspath(sys.argv[0])
    params = args if args is not None else sys.argv[1:]
    executable = sys.executable

    print("[*] Запрос прав Администратора для модификации системных параметров...")
    
    if sys.platform == "win32":
        param_str = " ".join([f'"{a}"' for a in params])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            executable,
            f'"{script}" {param_str}',
            None,
            1 # SW_SHOWNORMAL
        )
        if ret > 32:
            sys.exit(0)
        else:
            print("[-] Пользователь отклонил запрос прав Администратора.")
            return False
    elif sys.platform == "darwin":
        # macOS graphical elevation via AppleScript
        # 'with administrator privileges' уже запускает команду от root (sudo не нужен)
        args_str = " ".join([f"'{a}'" for a in params])
        shell_cmd = f"'{executable}' '{script}' {args_str}".strip()
        as_cmd = shell_cmd.replace('\\', '\\\\').replace('"', '\\"')
        osa = f'do shell script "{as_cmd}" with administrator privileges'
        try:
            res = subprocess.run(["osascript", "-e", osa], capture_output=True, text=True)
            if res.returncode == 0:
                sys.exit(0)
            else:
                print(f"[-] Ошибка авторизации macOS: {res.stderr.strip()}")
                return False
        except Exception as e:
            print(f"[-] Не удалось запросить права: {e}")
            return False
    else:
        # Linux: try pkexec or sudo
        try:
            cmd = ["sudo", executable, script] + params
            res = subprocess.run(cmd)
            sys.exit(res.returncode)
        except Exception as e:
            print(f"[-] Не удалось выполнить sudo: {e}")
            return False

def get_binary_paths():
    """Поиск всех исполняемых файлов Language Server и CLI agy на текущей ОС."""
    candidate_paths = []
    home = os.path.expanduser("~")

    if sys.platform == "win32":
        local_app = os.environ.get("LOCALAPPDATA", "")
        app_data = os.environ.get("APPDATA", "")
        user_prof = os.environ.get("USERPROFILE", home)

        candidate_paths += [
            os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "language_server.exe"),
            os.path.join(local_app, "Programs", "antigravity", "resources", "bin", "agy.exe"),
            os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server_windows_x64.exe"),
            os.path.join(local_app, "Programs", "Antigravity IDE", "resources", "app", "extensions", "antigravity", "bin", "language_server.exe"),
            os.path.join(user_prof, ".antigravity", "bin", "language_server.exe"),
            os.path.join(user_prof, ".antigravity", "bin", "agy.exe")
        ]
        ext_dir = os.path.join(user_prof, ".antigravity", "extensions")
        if os.path.exists(ext_dir):
            for root, _, files in os.walk(ext_dir):
                for f in files:
                    if f.lower() in ("language_server.exe", "language_server_windows_x64.exe", "agy.exe"):
                        candidate_paths.append(os.path.join(root, f))
    elif sys.platform == "darwin":
        candidate_paths += [
            "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm",
            "/Applications/Antigravity IDE.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_x64",
            "/Applications/Antigravity.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm",
            "/Applications/Antigravity.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_x64",
            os.path.join(home, ".local", "bin", "agy"),
            os.path.join(home, "Library", "Application Support", "Antigravity", "bin", "language_server"),
            os.path.join(home, ".antigravity", "bin", "language_server"),
            os.path.join(home, ".antigravity", "bin", "agy")
        ]
        ext_dir = os.path.join(home, ".antigravity", "extensions")
        if os.path.exists(ext_dir):
            for root, _, files in os.walk(ext_dir):
                for f in files:
                    if "language_server" in f.lower() or f.lower() == "agy":
                        candidate_paths.append(os.path.join(root, f))
    else:
        # Linux
        candidate_paths += [
            os.path.join(home, ".local", "bin", "agy"),
            "/opt/Antigravity/resources/app/extensions/antigravity/bin/language_server_linux_x64",
            "/opt/Antigravity/resources/app/extensions/antigravity/bin/language_server_linux_arm64",
            "/opt/Antigravity IDE/resources/app/extensions/antigravity/bin/language_server_linux_x64",
            "/opt/Antigravity IDE/resources/app/extensions/antigravity/bin/language_server_linux_arm64",
            os.path.join(home, ".local", "share", "antigravity", "bin", "language_server"),
            os.path.join(home, ".antigravity", "bin", "language_server"),
            os.path.join(home, ".antigravity", "bin", "agy")
        ]

    found = []
    for p in candidate_paths:
        if os.path.exists(p) and p not in found:
            found.append(p)
    return found

def stop_process_by_name(name):
    """Кроссплатформенное завершение процессов."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/IM", name], capture_output=True)
    else:
        subprocess.run(["pkill", "-f", name], capture_output=True)

def codesign_mac_binary(bpath):
    """Снятие карантина Gatekeeper и ad-hoc переподпись бинарников на macOS."""
    if sys.platform != "darwin":
        return
    try:
        # Снимаем quarantine
        subprocess.run(["xattr", "-cr", bpath], capture_output=True)
        # Переподписываем файл
        res = subprocess.run(["codesign", "--force", "--deep", "--sign", "-", bpath], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [+] macOS CodeSign: подпись успешно обновлена ({os.path.basename(bpath)})")
        # Если файл находится внутри .app бандла, переподпишем и сам .app
        if "/Applications/Antigravity IDE.app" in bpath:
            subprocess.run(["xattr", "-cr", "/Applications/Antigravity IDE.app"], capture_output=True)
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", "/Applications/Antigravity IDE.app"], capture_output=True)
    except Exception as e:
        print(f"    [-] Предупреждение codesign: {e}")

def patch_binaries():
    bins = get_binary_paths()
    if not bins:
        print("  [-] Исполняемые файлы Antigravity не найдены в стандартных путях.")
        return False

    patched_any = False
    for bpath in bins:
        fname = os.path.basename(bpath)
        try:
            with open(bpath, "rb") as f:
                data = f.read()
            orig = data.count(b"ineligible")
            patched = data.count(b"inexigible")
            if orig > 0:
                stop_process_by_name(fname)
                time.sleep(0.3)
                new_data = data.replace(b"ineligible", b"inexigible")
                with open(bpath, "wb") as f:
                    f.write(new_data)
                print(f"  [+] {fname}: Успешно пропатчен ({orig} замен).")
                # На macOS обязательно переподписываем бинарник
                codesign_mac_binary(bpath)
                patched_any = True
            elif patched > 0:
                print(f"  [i] {fname}: Уже пропатчен ({patched} вхождений).")
                codesign_mac_binary(bpath)
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
                stop_process_by_name(fname)
                time.sleep(0.3)
                new_data = data.replace(b"inexigible", b"ineligible")
                with open(bpath, "wb") as f:
                    f.write(new_data)
                print(f"  [+] {fname}: Откачен обратно ({patched} замен).")
                codesign_mac_binary(bpath)
        except Exception as e:
            print(f"  [-] {fname}: Ошибка: {e}")

def configure_ide_settings(backend_url=DEFAULT_BACKEND_URL):
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA", "")
        settings_dir = os.path.join(app_data, "Antigravity IDE", "User")
    elif sys.platform == "darwin":
        settings_dir = os.path.join(home, "Library", "Application Support", "Antigravity IDE", "User")
    else:
        settings_dir = os.path.join(home, ".config", "Antigravity IDE", "User")

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
    if sys.platform == "win32":
        cmd = f'[Environment]::SetEnvironmentVariable("CLOUD_CODE_URL", "{backend_url}", "User")'
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    os.environ["CLOUD_CODE_URL"] = backend_url
    print(f"  [+] Переменная окружения CLOUD_CODE_URL установлена ({backend_url}).")

def remove_env_vars():
    if sys.platform == "win32":
        cmd = '[Environment]::SetEnvironmentVariable("CLOUD_CODE_URL", $null, "User")'
        subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
    if "CLOUD_CODE_URL" in os.environ:
        del os.environ["CLOUD_CODE_URL"]
    print("  [+] Переменная окружения CLOUD_CODE_URL удалена.")

def set_ipv4_priority(enable=True):
    if sys.platform == "win32":
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

    # 2. Очистка опасных правил NRPT (только для Windows)
    if sys.platform == "win32":
        print("\n[Шаг 2/6] Очистка сбойных правил NRPT и изоляция DNS...")
        clean_leaking_nrpt_rules()
    else:
        print("\n[Шаг 2/6] Проверка системного сетевого стека...")

    # 3. Выбор живого прокси
    if not target_ip:
        if auto_find_proxy:
            print("\n[Шаг 3/6] Поиск самого быстрого живого зарубежного SNI-прокси...")
            target_ip = find_best_proxy(verbose=True)
        else:
            target_ip = "45.88.174.252"

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
    print(f"\n[Шаг 6/6] Настройка эндпоинтов IDE ({backend_url}) и сброс DNS...")
    configure_ide_settings(backend_url)
    configure_env_vars(backend_url)
    set_ipv4_priority(True)
    flush_dns_cache()

    print("\n" + "=" * 60)
    print("[УСПЕХ] Разблокировка успешно завершена! Antigravity готова к работе.")
    print("=" * 60)
    return True

def execute_rollback():
    print("=" * 60)
    print("ПОЛНЫЙ ОТКАТ ВСЕХ ИЗМЕНЕНИЙ (RESTORE)")
    print("=" * 60)

    print("\n[1/5] Удаление привязок из hosts...")
    ok, msg = unpin_hosts()
    print(f"  {msg}")

    print("\n[2/5] Откат бинарных патчей...")
    unpatch_binaries()

    print("\n[3/5] Удаление переменных окружения...")
    remove_env_vars()

    print("\n[4/5] Восстановление сетевых политик...")
    set_ipv4_priority(False)

    print("\n[5/5] Очистка DNS кэша...")
    flush_dns_cache()

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

