import os
import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_cmd(cmd, check=True):
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.returncode, res.stdout, res.stderr

def publish():
    print("=" * 60)
    print("  🚀 ПУБЛИКАЦИЯ РЕПОЗИТОРИЯ ANTIGRAVITY UNLOCKER НА GITHUB")
    print("=" * 60)
    print()

    # 1. Check Git
    code, out, err = run_cmd(["git", "--version"], check=False)
    if code != 0:
        print("[-] Ошибка: Git не установлен в системе или не добавлен в PATH.")
        input("\nНажмите Enter для выхода...")
        return

    # 2. Check Repo
    if not os.path.exists(".git"):
        print("[*] Инициализация локального Git-репозитория...")
        run_cmd(["git", "init"])
        run_cmd(["git", "branch", "-M", "main"])

    # 3. Add & Commit
    print("[*] Проверка и подготовка файлов...")
    run_cmd(["git", "add", "."])
    code, out, err = run_cmd(["git", "commit", "-m", "feat: release Antigravity Unlocker with Smart Failover & L7 Account Bypass"], check=False)
    if "nothing to commit" in out or "nothing to commit" in err:
        print("[+] Все файлы уже закоммичены.")
    else:
        print("[+] Коммит успешно сформирован.")

    print()
    print("=" * 60)
    print("  Инструкция по привязке к вашему GitHub:")
    print("=" * 60)
    print("1. Откройте в браузере: https://github.com/new")
    print("2. Введите имя репозитория (например: antigravity-unlocker)")
    print("3. Выберите 'Public' и НЕ ставьте галочки у README / .gitignore")
    print("4. Нажмите кнопку 'Create repository'")
    print("5. Скопируйте ссылку (например: https://github.com/ВАШ_ЛОГИН/antigravity-unlocker.git)")
    print("=" * 60)
    print()

    repo_url = input("Вставьте ссылку на ваш GitHub репозиторий: ").strip()

    if not repo_url:
        print("\n[-] Ссылка не была введена. Отмена публикации.")
        input("\nНажмите Enter для выхода...")
        return

    if not repo_url.startswith("http") and not repo_url.startswith("git@"):
        print("\n[-] Некорректный формат ссылки! Ссылка должна начинаться с https:// или git@")
        input("\nНажмите Enter для выхода...")
        return

    print(f"\n[*] Привязка удаленного репозитория: {repo_url}...")
    run_cmd(["git", "remote", "remove", "origin"], check=False)
    code, out, err = run_cmd(["git", "remote", "add", "origin", repo_url], check=False)
    if code != 0:
        print(f"[-] Ошибка привязки remote: {err}")

    print("[*] Отправка файлов на GitHub (git push -u origin main)...")
    print("[*] (Если появится окно авторизации GitHub — войдите в свой аккаунт)")
    
    # Run interactive push so credentials manager can show GUI prompt if needed
    push_res = subprocess.run(["git", "push", "-u", "origin", "main"])

    print()
    if push_res.returncode == 0:
        print("=" * 60)
        print("🎉 [УСПЕХ] Проект успешно опубликован на вашем GitHub!")
        print(f"Ссылка: {repo_url.replace('.git', '')}")
        print("=" * 60)
    else:
        print("=" * 60)
        print("[-] Ошибка отправки. Возможные причины:")
        print("  1. Вы не авторизованы в Git на этом компьютере.")
        print("  2. Репозиторий на GitHub уже содержит файлы (README/License).")
        print("  3. Неправильно указан адрес репозитория.")
        print()
        print("Подсказка: если репозиторий уже содержит файлы, выполните:")
        print(f"  git push -u origin main --force")
        print("=" * 60)

    print()
    input("Нажмите Enter для закрытия окна...")

if __name__ == "__main__":
    publish()
