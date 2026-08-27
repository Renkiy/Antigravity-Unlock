import os
import sys
import subprocess

# Подавление предупреждения macOS о системном Tk
os.environ["TK_SILENCE_DEPRECATION"] = "1"

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter
    from tools.gui_app import AntigravityUnlockerApp
except (ImportError, ModuleNotFoundError):
    # Если текущий Python (например, pyenv) собран без tcl-tk, пробуем системный Python
    if sys.platform == "darwin":
        script_path = os.path.abspath(__file__)
        for fallback in ["/usr/bin/python3", "/opt/homebrew/bin/python3"]:
            if os.path.exists(fallback) and fallback != sys.executable:
                res = subprocess.run([fallback, "-c", "import tkinter"], capture_output=True)
                if res.returncode == 0:
                    args = [fallback, script_path] + [a for a in sys.argv[1:] if a != "-c"]
                    os.execv(fallback, args)
    
    print("=" * 60)
    print("[-] Ошибка: в текущем окружении Python отсутствует модуль tkinter.")
    print("=" * 60)
    if sys.platform == "darwin":
        print("[i] Для решения на macOS:")
        print("    1. Запустите через системный Python: /usr/bin/python3 gui.py")
        print("    2. Или установите tkinter: brew install python-tk")
        print("    3. Или используйте CLI-режим: ./unlock.sh")
    else:
        print("[i] Для Linux установите: sudo apt install python3-tk  (или sudo pacman -S tk)")
    print("=" * 60)
    sys.exit(1)

if __name__ == "__main__":
    app = AntigravityUnlockerApp()
    app.mainloop()
