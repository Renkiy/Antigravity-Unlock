import os
import sys
import shutil
import ctypes
import winreg
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Colors
BG_DARK = "#121316"
BG_CARD = "#1B1D23"
ACCENT_BLUE = "#4A90E2"
ACCENT_GREEN = "#2ECC71"
TEXT_MAIN = "#FFFFFF"
TEXT_MUTED = "#8A8D93"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def get_default_install_dir():
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    return os.path.join(local_app_data, "Programs", "Antigravity Unlocker")

def create_shortcut(target_path, shortcut_path, description="Antigravity Unlocker"):
    try:
        ps_script = f'''
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{target_path}"
        $Shortcut.Description = "{description}"
        $Shortcut.WorkingDirectory = "{os.path.dirname(target_path)}"
        $Shortcut.Save()
        '''
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True)
        return True
    except Exception:
        return False

def register_in_add_remove_programs(install_dir, exe_path, uninstaller_path):
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\AntigravityUnlocker"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Antigravity Unlocker")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "2.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Antigravity Unlocker Team")
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, exe_path)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_path}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception as e:
        print(f"Failed to register in Windows Uninstall: {e}")

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Установка Antigravity Unlocker 2.0")
        self.geometry("620x460")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)

        # Center on screen
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w // 2 - size[0] // 2
        y = h // 2 - size[1] // 2
        self.geometry(f"{size[0]}x{size[1]}+{x}+{y}")

        self.install_dir = tk.StringVar(value=get_default_install_dir())
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_menu_shortcut = tk.BooleanVar(value=True)
        self.launch_after = tk.BooleanVar(value=True)

        self.current_step = 0
        self.steps = [self.step_welcome, self.step_options, self.step_installing, self.step_finish]

        self.container = tk.Frame(self, bg=BG_DARK)
        self.container.pack(fill="both", expand=True)

        self.footer = tk.Frame(self, bg=BG_CARD, height=60)
        self.footer.pack(fill="x", side="bottom")

        self.btn_cancel = tk.Button(self.footer, text="Отмена", bg="#37474F", fg="white", font=("Segoe UI", 9), relief="flat", padx=15, pady=5, command=self.destroy)
        self.btn_cancel.pack(side="left", padx=20, pady=15)

        self.btn_next = tk.Button(self.footer, text="Далее >", bg=ACCENT_BLUE, fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=20, pady=5, command=self.next_step)
        self.btn_next.pack(side="right", padx=20, pady=15)

        self.btn_back = tk.Button(self.footer, text="< Назад", bg="#37474F", fg="white", font=("Segoe UI", 9), relief="flat", padx=15, pady=5, command=self.prev_step)
        self.btn_back.pack(side="right", padx=5, pady=15)

        self.show_step(0)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_step(self, index):
        self.current_step = index
        self.clear_container()
        self.steps[index]()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            if self.launch_after.get():
                target_exe = os.path.join(self.install_dir.get(), "AntigravityUnlocker.exe")
                if os.path.exists(target_exe):
                    subprocess.Popen([target_exe], shell=True)
            self.destroy()

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def step_welcome(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(text="Далее >", state="normal")

        header = tk.Frame(self.container, bg=BG_DARK)
        header.pack(fill="x", padx=25, pady=(25, 10))

        tk.Label(header, text="🚀 Мастер установки Antigravity Unlocker", font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(anchor="w")
        tk.Label(header, text="Версия 2.0.0 (Smart Failover & Zero VPN)", font=("Segoe UI", 10), bg=BG_DARK, fg=ACCENT_BLUE).pack(anchor="w", pady=(2, 0))

        card = tk.Frame(self.container, bg=BG_CARD, padx=20, pady=15)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        info = (
            "Добро пожаловать в программу установки Antigravity Unlocker!\n\n"
            "Программа обеспечит стабильный доступ к Google Antigravity, Antigravity IDE "
            "и языковым моделям Gemini / Claude в РФ и РБ без использования глобального VPN.\n\n"
            "Ключевые возможности:\n"
            " • Разблокировка в 1 клик для любых Google-аккаунтов\n"
            " • Защита от сбоев и авто-переключение серверов (Watchdog)\n"
            " • Сохранение полной скорости вашего интернета (Zero VPN)\n"
            " • 100% безопасность и сквозное шифрование TLS 1.3\n\n"
            "Нажмите «Далее», чтобы продолжить установку."
        )
        tk.Label(card, text=info, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED, justify="left").pack(anchor="w")

    def step_options(self):
        self.btn_back.config(state="normal")
        self.btn_next.config(text="Установить", state="normal")

        header = tk.Frame(self.container, bg=BG_DARK)
        header.pack(fill="x", padx=25, pady=(25, 10))
        tk.Label(header, text="📁 Выбор папки установки и параметров", font=("Segoe UI", 14, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(anchor="w")

        card = tk.Frame(self.container, bg=BG_CARD, padx=20, pady=15)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        tk.Label(card, text="Папка установки:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w")

        f_dir = tk.Frame(card, bg=BG_CARD)
        f_dir.pack(fill="x", pady=(5, 15))

        ent = tk.Entry(f_dir, textvariable=self.install_dir, font=("Segoe UI", 9), bg="#262930", fg=TEXT_MAIN, insertbackground="white")
        ent.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=3)

        def browse():
            d = filedialog.askdirectory(initialdir=self.install_dir.get())
            if d:
                self.install_dir.set(d)

        tk.Button(f_dir, text="Обзор...", bg="#37474F", fg="white", font=("Segoe UI", 9), relief="flat", padx=10, command=browse).pack(side="right")

        tk.Label(card, text="Дополнительные задачи:", font=("Segoe UI", 9, "bold"), bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w", pady=(10, 5))

        c1 = tk.Checkbutton(card, text="Создать ярлык на Рабочем столе", variable=self.create_desktop_shortcut, bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_DARK, activebackground=BG_CARD, activeforeground=TEXT_MAIN, font=("Segoe UI", 9))
        c1.pack(anchor="w", pady=2)

        c2 = tk.Checkbutton(card, text="Создать ярлык в меню «Пуск»", variable=self.create_start_menu_shortcut, bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_DARK, activebackground=BG_CARD, activeforeground=TEXT_MAIN, font=("Segoe UI", 9))
        c2.pack(anchor="w", pady=2)

    def step_installing(self):
        self.btn_back.config(state="disabled")
        self.btn_next.config(state="disabled")
        self.btn_cancel.config(state="disabled")

        header = tk.Frame(self.container, bg=BG_DARK)
        header.pack(fill="x", padx=25, pady=(25, 10))
        tk.Label(header, text="⚙️ Идет установка...", font=("Segoe UI", 14, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(anchor="w")

        card = tk.Frame(self.container, bg=BG_CARD, padx=20, pady=25)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        self.lbl_status = tk.Label(card, text="Копирование файлов...", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED)
        self.lbl_status.pack(anchor="w", pady=(10, 5))

        self.progress = ttk.Progressbar(card, orient="horizontal", mode="determinate", length=500)
        self.progress.pack(fill="x", pady=10)

        self.after(100, self.do_install)

    def do_install(self):
        target_dir = self.install_dir.get().strip()
        os.makedirs(target_dir, exist_ok=True)

        self.progress['value'] = 20
        self.lbl_status.config(text="Извлечение исполняемых файлов программы...")
        self.update()

        # Find bundled source or executable
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_root = os.path.dirname(base_dir) if os.path.basename(base_dir) == "installer" else base_dir

        # Copy executable or generate from bundled
        src_exe = os.path.join(app_root, "release", "AntigravityUnlocker.exe")
        dst_exe = os.path.join(target_dir, "AntigravityUnlocker.exe")

        if os.path.exists(src_exe):
            shutil.copyfile(src_exe, dst_exe)
        else:
            # Copy from dist if available
            src_dist = os.path.join(app_root, "dist", "AntigravityUnlocker.exe")
            if os.path.exists(src_dist):
                shutil.copyfile(src_dist, dst_exe)

        self.progress['value'] = 50
        self.lbl_status.config(text="Создание модуля деинсталляции...")
        self.update()

        # Create uninstaller
        dst_uninstaller = os.path.join(target_dir, "uninstall.bat")
        with open(dst_uninstaller, "w", encoding="utf-8") as f:
            f.write(f'''@echo off
chcp 65001 >nul
echo Удаление Antigravity Unlocker...
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\AntigravityUnlocker" /f >nul 2>&1
del /q "%USERPROFILE%\\Desktop\\Antigravity Unlocker.lnk" >nul 2>&1
del /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Antigravity Unlocker.lnk" >nul 2>&1
cd /d "%TEMP%"
rd /s /q "{target_dir}" >nul 2>&1
echo Программа успешно удалена.
pause
''')

        self.progress['value'] = 75
        self.lbl_status.config(text="Создание ярлыков Windows...")
        self.update()

        if self.create_desktop_shortcut.get():
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            create_shortcut(dst_exe, os.path.join(desktop, "Antigravity Unlocker.lnk"))

        if self.create_start_menu_shortcut.get():
            start_menu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
            if os.path.exists(start_menu):
                create_shortcut(dst_exe, os.path.join(start_menu, "Antigravity Unlocker.lnk"))

        # Register in Windows Add/Remove Programs
        register_in_add_remove_programs(target_dir, dst_exe, dst_uninstaller)

        self.progress['value'] = 100
        self.lbl_status.config(text="Установка успешно завершена!")
        self.update()

        self.after(500, lambda: self.show_step(3))

    def step_finish(self):
        self.btn_back.config(state="disabled")
        self.btn_cancel.config(state="disabled")
        self.btn_next.config(text="Завершить", state="normal")

        header = tk.Frame(self.container, bg=BG_DARK)
        header.pack(fill="x", padx=25, pady=(25, 10))
        tk.Label(header, text="🎉 Установка успешно завершена!", font=("Segoe UI", 16, "bold"), bg=BG_DARK, fg=ACCENT_GREEN).pack(anchor="w")

        card = tk.Frame(self.container, bg=BG_CARD, padx=20, pady=20)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        info = (
            "Antigravity Unlocker 2.0 успешно установлен на ваш компьютер!\n\n"
            f"Папка установки: {self.install_dir.get()}\n\n"
            "Вы можете в любой момент запустить программу с Рабочего стола,\n"
            "из меню «Пуск» или удалить через стандартную «Установку и удаление программ» Windows."
        )
        tk.Label(card, text=info, font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MAIN, justify="left").pack(anchor="w")

        c_launch = tk.Checkbutton(card, text="Запустить Antigravity Unlocker сейчас", variable=self.launch_after, bg=BG_CARD, fg=TEXT_MAIN, selectcolor=BG_DARK, activebackground=BG_CARD, activeforeground=TEXT_MAIN, font=("Segoe UI", 9, "bold"))
        c_launch.pack(anchor="w", pady=(20, 0))

if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
