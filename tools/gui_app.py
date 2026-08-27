import os
import sys
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure tools directory in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from tools.unlocker_core import (
    is_admin, elevate_process, execute_unlock, execute_rollback,
    patch_binaries, unpatch_binaries, set_ipv4_priority,
    configure_ide_settings, configure_env_vars, get_binary_paths
)
from tools.proxy_manager import (
    find_best_proxy, pin_hosts, unpin_hosts, get_current_pinned_ip,
    probe_single_host, PROXIES_POOL
)
from tools.backup_manager import create_backup, restore_backup, list_backups

# Colors - Catppuccin Mocha Dark Theme
BG_MAIN = "#1E1E2E"
BG_CARD = "#252538"
BG_CARD_BORDER = "#45475A"
BG_CONSOLE = "#11111B"
TEXT_WHITE = "#FFFFFF"
TEXT_MUTED = "#BAC2DE"
ACCENT_BLUE = "#89B4FA"
ACCENT_GREEN = "#A6E3A1"
ACCENT_RED = "#F38BA8"
ACCENT_YELLOW = "#F9E2AF"
ACCENT_PURPLE = "#CBA6F7"

# Typography
if sys.platform == "darwin":
    FONT_FAMILY = "Helvetica"
    FONT_MONO = "Menlo"
elif sys.platform == "win32":
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"
else:
    FONT_FAMILY = "DejaVu Sans"
    FONT_MONO = "Monospace"

class CanvasLabel(tk.Canvas):
    """
    Кроссплатформенный Label на базе Canvas CoreGraphics.
    Гарантирует 100% видимость и отрисовку любого цвета текста на macOS (включая Dark Mode Tk 8.5).
    """
    def __init__(self, parent, text="", font_spec=(FONT_FAMILY, 10), fg=TEXT_WHITE, bg=BG_MAIN, height=22, anchor="w", **kwargs):
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0, height=height, **kwargs)
        self._text = text
        self._font = font_spec
        self._fg = fg
        self._anchor = anchor
        self._item = self.create_text(4, height // 2, text=text, font=font_spec, fill=fg, anchor=anchor)
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        y = event.height // 2
        x = 4 if self._anchor == "w" else (event.width - 4 if self._anchor == "e" else event.width // 2)
        self.coords(self._item, x, y)

    def config(self, **kwargs):
        if "text" in kwargs:
            self._text = kwargs["text"]
            self.itemconfig(self._item, text=kwargs["text"])
        if "fg" in kwargs:
            self._fg = kwargs["fg"]
            self.itemconfig(self._item, fill=kwargs["fg"])
        if "foreground" in kwargs:
            self._fg = kwargs["foreground"]
            self.itemconfig(self._item, fill=kwargs["foreground"])
        if "bg" in kwargs:
            super().config(bg=kwargs["bg"])
        if "background" in kwargs:
            super().config(bg=kwargs["background"])

    def cget(self, key):
        if key in ("text",):
            return self._text
        if key in ("fg", "foreground"):
            return self._fg
        return super().cget(key)

class AntigravityUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antigravity Unlocker — Работа в РФ без VPN")
        self.geometry("920x700")
        self.minsize(820, 620)
        self.configure(bg=BG_MAIN)

        # Thread-safe event queue
        self.msg_queue = queue.Queue()

        # UI Elements
        self.create_header()
        self.create_dashboard()
        self.create_action_buttons()
        self.create_console()

        # Start queue processor on main thread
        self.poll_queue()

        # Initial check
        self.log("[*] Запуск интерфейса Antigravity Unlocker...")
        self.check_admin_status()
        self.refresh_dashboard_async()

    def poll_queue(self):
        """Единый диспетчер очереди сообщений в главном потоке GUI."""
        while not self.msg_queue.empty():
            try:
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "log":
                    self._do_log(payload)
                elif msg_type == "dashboard":
                    self._apply_dashboard_state(*payload)
                elif msg_type == "msgbox_info":
                    title, text = payload
                    messagebox.showinfo(title, text)
                elif msg_type == "msgbox_error":
                    title, text = payload
                    messagebox.showerror(title, text)
                elif msg_type == "watchdog_btn":
                    btn_text = payload
                    self.btn_watchdog.config(text=btn_text)
            except Exception:
                pass
        self.after(80, self.poll_queue)

    def log(self, text):
        """Безопасная отправка лога из любого потока."""
        self.msg_queue.put(("log", text))

    def _do_log(self, text):
        ts = time.strftime("[%H:%M:%S] ")
        self.console.insert(tk.END, ts + text + "\n")
        self.console.see(tk.END)

    def check_admin_status(self):
        if is_admin():
            self.admin_badge.config(text="● Права Администратора: ДА", fg=ACCENT_GREEN)
            self.log("[+] Приложение запущено с правами Администратора / root.")
        else:
            self.admin_badge.config(text="● Права Администратора: НЕТ", fg=ACCENT_RED)
            self.log("[!] Внимание: Для изменения hosts требуются права Администратора / sudo.")

    def create_header(self):
        header_frame = tk.Frame(self, bg=BG_MAIN, pady=12, padx=20)
        header_frame.pack(side="top", fill="x")

        title_label = CanvasLabel(
            header_frame, 
            text="🚀 Antigravity Unlocker", 
            font_spec=(FONT_FAMILY, 18, "bold"),
            bg=BG_MAIN, 
            fg=ACCENT_BLUE,
            height=30,
            width=320
        )
        title_label.pack(side="left")

        self.admin_badge = CanvasLabel(
            header_frame,
            text="● Проверка прав...",
            font_spec=(FONT_FAMILY, 10, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_YELLOW,
            height=30,
            width=260,
            anchor="e"
        )
        self.admin_badge.pack(side="right")

    def create_dashboard(self):
        dash_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=5)
        dash_frame.pack(side="top", fill="x")

        dash_frame.columnconfigure(0, weight=1)
        dash_frame.columnconfigure(1, weight=1)
        dash_frame.columnconfigure(2, weight=1)
        dash_frame.columnconfigure(3, weight=1)

        # Card 1: Binary Patch
        c1 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1, highlightbackground=BG_CARD_BORDER, highlightcolor=BG_CARD_BORDER)
        c1.grid(row=0, column=0, padx=4, sticky="nsew")
        CanvasLabel(c1, text="Бинарный патч", font_spec=(FONT_FAMILY, 9), bg=BG_CARD, fg=TEXT_MUTED, height=18).pack(fill="x")
        self.lbl_patch_status = CanvasLabel(c1, text="Проверка...", font_spec=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW, height=22)
        self.lbl_patch_status.pack(fill="x", pady=(2, 0))

        # Card 2: Hosts Pin
        c2 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1, highlightbackground=BG_CARD_BORDER, highlightcolor=BG_CARD_BORDER)
        c2.grid(row=0, column=1, padx=4, sticky="nsew")
        CanvasLabel(c2, text="Привязка Hosts", font_spec=(FONT_FAMILY, 9), bg=BG_CARD, fg=TEXT_MUTED, height=18).pack(fill="x")
        self.lbl_hosts_status = CanvasLabel(c2, text="Проверка...", font_spec=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW, height=22)
        self.lbl_hosts_status.pack(fill="x", pady=(2, 0))

        # Card 3: Ping Gemini API
        c3 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1, highlightbackground=BG_CARD_BORDER, highlightcolor=BG_CARD_BORDER)
        c3.grid(row=0, column=2, padx=4, sticky="nsew")
        CanvasLabel(c3, text="Gemini API TLS", font_spec=(FONT_FAMILY, 9), bg=BG_CARD, fg=TEXT_MUTED, height=18).pack(fill="x")
        self.lbl_ping_status = CanvasLabel(c3, text="Тестирование...", font_spec=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW, height=22)
        self.lbl_ping_status.pack(fill="x", pady=(2, 0))

        # Card 4: IPv4 Priority
        c4 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, relief="solid", bd=1, highlightbackground=BG_CARD_BORDER, highlightcolor=BG_CARD_BORDER)
        c4.grid(row=0, column=3, padx=4, sticky="nsew")
        CanvasLabel(c4, text="Статус DNS / Сети", font_spec=(FONT_FAMILY, 9), bg=BG_CARD, fg=TEXT_MUTED, height=18).pack(fill="x")
        self.lbl_ipv4_status = CanvasLabel(c4, text="Активен", font_spec=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=ACCENT_GREEN, height=22)
        self.lbl_ipv4_status.pack(fill="x", pady=(2, 0))

    def create_action_buttons(self):
        btn_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=8)
        btn_frame.pack(side="top", fill="x")

        # Row 1 Main Buttons
        r1 = tk.Frame(btn_frame, bg=BG_MAIN)
        r1.pack(fill="x", pady=3)

        btn_unlock = tk.Button(
            r1,
            text="⚡ АКТИВИРОВАТЬ АНЛОК (Авто-прокси + Патч + CodeSign)",
            font=(FONT_FAMILY, 11, "bold"),
            highlightbackground=BG_MAIN,
            command=self.run_unlock_thread
        )
        btn_unlock.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_rollback = tk.Button(
            r1,
            text="🔄 ПОЛНЫЙ ОТКАТ (Restore)",
            font=(FONT_FAMILY, 10, "bold"),
            highlightbackground=BG_MAIN,
            command=self.run_rollback_thread
        )
        btn_rollback.pack(side="right", padx=(5, 0))

        # Row 2 Utility Buttons
        r2 = tk.Frame(btn_frame, bg=BG_MAIN)
        r2.pack(fill="x", pady=4)

        btn_backup = tk.Button(
            r2,
            text="🛡️ Создать бэкап",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.run_backup_thread
        )
        btn_backup.pack(side="left", padx=(0, 3))

        btn_backups_list = tk.Button(
            r2,
            text="📁 Список бэкапов",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.show_backups_dialog
        )
        btn_backups_list.pack(side="left", padx=3)

        btn_find_proxy = tk.Button(
            r2,
            text="⚡ Быстрый прокси",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.run_find_proxy_thread
        )
        btn_find_proxy.pack(side="left", padx=3)

        self.btn_watchdog = tk.Button(
            r2,
            text="🐕 Watchdog: ВКЛ",
            font=(FONT_FAMILY, 9, "bold"),
            highlightbackground=BG_MAIN,
            command=self.toggle_watchdog
        )
        self.btn_watchdog.pack(side="left", padx=3)

        btn_worker = tk.Button(
            r2,
            text="☁️ Cloudflare L7",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.show_worker_dialog
        )
        btn_worker.pack(side="left", padx=3)

        btn_github = tk.Button(
            r2,
            text="🚀 GitHub",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.show_github_dialog
        )
        btn_github.pack(side="left", padx=3)

        btn_diag = tk.Button(
            r2,
            text="🔍 Диагностика",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=self.run_diagnostics_thread
        )
        btn_diag.pack(side="left", padx=3)

        btn_elevate = tk.Button(
            r2,
            text="🔑 sudo / Admin",
            font=(FONT_FAMILY, 9, "bold"),
            highlightbackground=BG_MAIN,
            command=lambda: elevate_process([])
        )
        btn_elevate.pack(side="right", padx=(3, 0))

    def create_console(self):
        console_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=5)
        console_frame.pack(side="top", fill="both", expand=True)

        CanvasLabel(
            console_frame,
            text="Лог операций и статус выполнения:",
            font_spec=(FONT_FAMILY, 9, "bold"),
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            height=20
        ).pack(fill="x", pady=(0, 4))

        # Text widget configured as read-only with vibrant terminal font
        self.console = tk.Text(
            console_frame,
            bg=BG_CONSOLE,
            fg="#A6E3A1",
            font=(FONT_MONO, 10),
            relief="flat",
            padx=10,
            pady=10,
            highlightbackground=BG_CARD_BORDER,
            highlightthickness=1,
            insertbackground=TEXT_WHITE,
            wrap="word"
        )
        self.console.bind("<Key>", lambda e: "break" if e.keysym not in ("c", "C") or not (e.state & 4 or e.state & 8) else None)

        scrollbar = tk.Scrollbar(console_frame, command=self.console.yview)
        scrollbar.pack(side="right", fill="y")
        self.console.config(yscrollcommand=scrollbar.set)
        self.console.pack(side="left", fill="both", expand=True)

    def toggle_watchdog(self):
        from tools.proxy_manager import watchdog_instance
        if watchdog_instance.running:
            watchdog_instance.stop()
            self.btn_watchdog.config(text="🐕 Watchdog: ВЫКЛ")
        else:
            watchdog_instance.log_callback = lambda msg: self.log(msg)
            watchdog_instance.failover_callback = lambda new_ip: self.refresh_dashboard_async()
            watchdog_instance.start()
            self.btn_watchdog.config(text="🐕 Watchdog: ВКЛ")

    def show_worker_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Настройка Cloudflare Worker L7")
        dialog.geometry("680x400")
        dialog.configure(bg=BG_MAIN)

        CanvasLabel(
            dialog,
            text="☁️ Cloudflare Worker L7 Relay (Для 100% защиты русских аккаунтов)",
            font_spec=(FONT_FAMILY, 12, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_BLUE,
            height=26
        ).pack(fill="x", padx=15, pady=(15, 5))

        CanvasLabel(dialog, text="Cloudflare Worker устраняет проблему блокировки аккаунта в РФ,", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15)
        CanvasLabel(dialog, text="перехватывая ответы API и подменяя статус ineligible на eligible на лету.", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15)
        CanvasLabel(dialog, text="Готовый скрипт воркера находится в файле: tools/cloudflare_worker.js", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15, pady=(0, 10))

        f_url = tk.Frame(dialog, bg=BG_MAIN)
        f_url.pack(fill="x", padx=15, pady=10)

        CanvasLabel(f_url, text="URL вашего Worker:", font_spec=(FONT_FAMILY, 10, "bold"), bg=BG_MAIN, fg=TEXT_WHITE, height=20).pack(fill="x")
        ent_url = tk.Entry(f_url, font=(FONT_MONO, 10), bg=BG_CARD, fg=TEXT_WHITE, insertbackground=TEXT_WHITE)
        ent_url.pack(fill="x", pady=5)
        
        cur_url = os.environ.get("CLOUD_CODE_URL", "https://daily-cloudcode-pa.googleapis.com")
        ent_url.insert(0, cur_url)

        def apply_worker_url():
            url = ent_url.get().strip()
            if not url.startswith("http"):
                messagebox.showerror("Ошибка", "URL должен начинаться с https:// или http://")
                return
            configure_ide_settings(url)
            configure_env_vars(url)
            self.log(f"[+] Установлен кастомный CloudCode URL: {url}")
            messagebox.showinfo("Успех", f"URL бэкенда успешно обновлен на:\n{url}")
            dialog.destroy()

        def reset_worker_url():
            default_url = "https://daily-cloudcode-pa.googleapis.com"
            configure_ide_settings(default_url)
            configure_env_vars(default_url)
            self.log("[+] Сброшен CloudCode URL на дефолтный.")
            messagebox.showinfo("Сброс", "URL сброшен на стандартный (daily-cloudcode-pa.googleapis.com)")
            dialog.destroy()

        btn_f = tk.Frame(dialog, bg=BG_MAIN)
        btn_f.pack(fill="x", padx=15, pady=15)

        tk.Button(btn_f, text="💾 Применить Worker URL", command=apply_worker_url, highlightbackground=BG_MAIN).pack(side="left")
        tk.Button(btn_f, text="🔄 Сброс на дефолт", command=reset_worker_url, highlightbackground=BG_MAIN).pack(side="left", padx=10)
        tk.Button(btn_f, text="Закрыть", command=dialog.destroy, highlightbackground=BG_MAIN).pack(side="right")

        dialog.update_idletasks()
        try:
            dialog.transient(self)
            dialog.grab_set()
            dialog.focus_set()
        except Exception:
            pass

    def show_github_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Публикация на GitHub")
        dialog.geometry("680x380")
        dialog.configure(bg=BG_MAIN)

        CanvasLabel(
            dialog,
            text="🚀 Публикация Antigravity Unlocker на ваш GitHub",
            font_spec=(FONT_FAMILY, 12, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_BLUE,
            height=26
        ).pack(fill="x", padx=15, pady=(15, 5))

        CanvasLabel(dialog, text="1. Создайте пустой репозиторий на github.com/new (без README)", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15)
        CanvasLabel(dialog, text="2. Вставьте ссылку на ваш репозиторий ниже", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15)
        CanvasLabel(dialog, text="3. Нажмите кнопку «Опубликовать» — проект будет выгружен автоматически!", font_spec=(FONT_FAMILY, 9), bg=BG_MAIN, fg=TEXT_MUTED, height=18).pack(fill="x", padx=15, pady=(0, 10))

        f_url = tk.Frame(dialog, bg=BG_MAIN)
        f_url.pack(fill="x", padx=15, pady=10)

        CanvasLabel(f_url, text="Ссылка на ваш GitHub репозиторий (.git):", font_spec=(FONT_FAMILY, 10, "bold"), bg=BG_MAIN, fg=TEXT_WHITE, height=20).pack(fill="x")
        ent_url = tk.Entry(f_url, font=(FONT_MONO, 10), bg=BG_CARD, fg=TEXT_WHITE, insertbackground=TEXT_WHITE)
        ent_url.pack(fill="x", pady=5)
        ent_url.insert(0, "https://github.com/ВАШ_ЛОГИН/antigravity-unlocker.git")

        def do_publish():
            url = ent_url.get().strip()
            if not url.startswith("http") and not url.startswith("git@"):
                messagebox.showerror("Ошибка", "Ссылка должна начинаться с https:// или git@")
                return
            dialog.destroy()
            
            def _push_worker():
                self.log("\n" + "=" * 50)
                self.log(f"🚀 Публикация проекта на GitHub ({url})...")
                import subprocess
                subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
                subprocess.run(["git", "remote", "add", "origin", url], capture_output=True)
                res = subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
                if res.returncode == 0:
                    self.log("🎉 [УСПЕХ] Проект успешно опубликован на GitHub!")
                    self.log(f"  Ссылка: {url.replace('.git', '')}")
                    self.msg_queue.put(("msgbox_info", ("Успех", f"Репозиторий успешно опубликован на GitHub!\n\n{url.replace('.git', '')}")))
                else:
                    self.log(f"[-] Ошибка отправки:\n{res.stderr}")
                    self.msg_queue.put(("msgbox_error", ("Ошибка публикации", f"Не удалось отправить репозиторий:\n{res.stderr}")))
                self.log("=" * 50)

            threading.Thread(target=_push_worker, daemon=True).start()

        btn_f = tk.Frame(dialog, bg=BG_MAIN)
        btn_f.pack(fill="x", padx=15, pady=15)

        tk.Button(btn_f, text="🚀 Опубликовать на GitHub", command=do_publish, highlightbackground=BG_MAIN).pack(side="left")
        tk.Button(btn_f, text="Закрыть", command=dialog.destroy, highlightbackground=BG_MAIN).pack(side="right")

        dialog.update_idletasks()
        try:
            dialog.transient(self)
            dialog.grab_set()
            dialog.focus_set()
        except Exception:
            pass

    def refresh_dashboard_async(self):
        threading.Thread(target=self._refresh_dashboard, daemon=True).start()

    def _apply_dashboard_state(self, patch_text, patch_fg, hosts_text, hosts_fg, ping_text, ping_fg):
        self.lbl_patch_status.config(text=patch_text, fg=patch_fg)
        self.lbl_hosts_status.config(text=hosts_text, fg=hosts_fg)
        self.lbl_ping_status.config(text=ping_text, fg=ping_fg)

    def _refresh_dashboard(self):
        # 1. Check Binary Patches
        bins = get_binary_paths()
        all_patched = True
        for b in bins:
            try:
                with open(b, "rb") as f:
                    data = f.read()
                if data.count(b"inexigible") == 0:
                    all_patched = False
                    break
            except Exception:
                all_patched = False

        if all_patched and bins:
            patch_text, patch_fg = "ПРОПАТЧЕН [OK]", ACCENT_GREEN
        else:
            patch_text, patch_fg = "ТРЕБУЕТСЯ ПАТЧ", ACCENT_RED

        # 2. Check Hosts Pin
        pinned_ip = get_current_pinned_ip()
        if pinned_ip:
            hosts_text, hosts_fg = f"АКТИВЕН ({pinned_ip})", ACCENT_GREEN
        else:
            hosts_text, hosts_fg = "НЕ ПРИВЯЗАН", TEXT_MUTED

        # 3. Check Gemini API Ping
        target_host = "cloudcode-pa.googleapis.com"
        probe_target_ip = pinned_ip or "45.88.174.252"
        ok, lat, err = probe_single_host(probe_target_ip, target_host, timeout=2.0)
        if ok:
            ping_text, ping_fg = f"OK ({lat:.0f} ms)", ACCENT_GREEN
        else:
            ping_text, ping_fg = "ТАЙМАУТ / ОШИБКА", ACCENT_RED

        self.msg_queue.put(("dashboard", (patch_text, patch_fg, hosts_text, hosts_fg, ping_text, ping_fg)))

    def run_unlock_thread(self):
        if not is_admin():
            if messagebox.askyesno("Требуются права Администратора", "Для применения анлока (запись в hosts и настройка сети) требуются права Администратора / sudo.\n\nПерезапустить приложение с правами Администратора?"):
                elevate_process([])
            return

        threading.Thread(target=self._do_unlock, daemon=True).start()

    def _do_unlock(self):
        self.log("\n" + "="*50)
        self.log("🚀 ЗАПУСК ПОЛНОЙ АКТИВАЦИИ АНЛОКА...")
        try:
            # 1. Backup
            self.log("[1/5] Создание резервной копии...")
            bdir, _ = create_backup("auto_unlock")
            self.log(f"  [+] Бэкап сохранен в {os.path.basename(bdir)}")

            # 2. Best proxy
            self.log("[2/5] Поиск самого быстрого живого SNI-прокси...")
            best_ip = find_best_proxy(verbose=False)
            self.log(f"  [+] Выбран лучший IP: {best_ip}")

            # 3. Pin hosts
            self.log(f"[3/5] Привязка хостов в hosts к {best_ip}...")
            ok, msg = pin_hosts(best_ip)
            self.log(f"  {'[+]' if ok else '[-]'} {msg}")

            # 4. Binary patch
            self.log("[4/5] Патчинг Language Server / agy и CodeSign...")
            patch_binaries()

            # 5. Settings & IPv4
            self.log("[5/5] Конфигурация IDE и сетевых политик...")
            configure_ide_settings()
            configure_env_vars()
            set_ipv4_priority(True)

            # Запуск Watchdog
            from tools.proxy_manager import watchdog_instance
            watchdog_instance.log_callback = lambda msg: self.log(msg)
            watchdog_instance.failover_callback = lambda new_ip: self.refresh_dashboard_async()
            watchdog_instance.start()
            self.msg_queue.put(("watchdog_btn", "🐕 Watchdog: ВКЛ"))

            self.log("="*50)
            self.log("🎉 [УСПЕХ] Анлок успешно активирован! Antigravity готова к работе без VPN.")
            self.msg_queue.put(("msgbox_info", ("Успех", "Разблокировка успешно применена!\n\nВсе запросы зафиксированы на быстрый зарубежный SNI-прокси.\nWatchdog активен и защитит от сбоев.")))
        except Exception as e:
            self.log(f"[-] Ошибка во время выполнения: {e}")
            self.msg_queue.put(("msgbox_error", ("Ошибка", f"Произошла ошибка: {e}")))
        finally:
            self.refresh_dashboard_async()

    def run_rollback_thread(self):
        if not is_admin():
            if messagebox.askyesno("Требуются права Администратора", "Для отката изменений требуются права Администратора / sudo.\n\nПерезапустить приложение с правами Администратора?"):
                elevate_process([])
            return

        if not messagebox.askyesno("Подтверждение отката", "Вы уверены, что хотите отменить все изменения и вернуть систему в исходное состояние?"):
            return

        threading.Thread(target=self._do_rollback, daemon=True).start()

    def _do_rollback(self):
        self.log("\n" + "="*50)
        self.log("🔄 ЗАПУСК ПОЛНОГО ОТКАТА...")
        try:
            from tools.proxy_manager import watchdog_instance
            watchdog_instance.stop()
            self.msg_queue.put(("watchdog_btn", "🐕 Watchdog: ВЫКЛ"))

            execute_rollback()
            self.log("="*50)
            self.log("✅ [УСПЕХ] Все изменения полностью отменены.")
            self.msg_queue.put(("msgbox_info", ("Откат завершен", "Система успешно возвращена в исходное состояние.")))
        except Exception as e:
            self.log(f"[-] Ошибка отката: {e}")
        finally:
            self.refresh_dashboard_async()

    def run_backup_thread(self):
        threading.Thread(target=self._do_backup, daemon=True).start()

    def _do_backup(self):
        self.log("\n[+] Создание резервной копии...")
        bdir, _ = create_backup("manual")
        self.log(f"[+] Бэкап создан: {bdir}")
        self.msg_queue.put(("msgbox_info", ("Бэкап создан", f"Резервная копия успешно создана в:\n{bdir}")))

    def run_find_proxy_thread(self):
        threading.Thread(target=self._do_find_proxy, daemon=True).start()

    def _do_find_proxy(self):
        self.log("\n[+] Тестирование всех прокси серверов...")
        best_ip = find_best_proxy(verbose=True)
        self.log(f"[+] Самый быстрый прокси: {best_ip}")
        self.refresh_dashboard_async()

    def run_diagnostics_thread(self):
        threading.Thread(target=self._do_diagnostics, daemon=True).start()

    def _do_diagnostics(self):
        self.log("\n" + "="*50)
        self.log("🔍 ДИАГНОСТИКА СЕТИ И СТАТУСА...")
        from tools.diagnostics import (
            check_hosts_pinning, check_nrpt_rules, check_dns_resolving,
            check_tls_connectivity, check_binary_patches
        )
        
        old_stdout = sys.stdout
        class StdoutRedirector:
            def __init__(self, app):
                self.app = app
            def write(self, s):
                if s.strip():
                    self.app.log(s.strip())
            def flush(self):
                pass
        
        sys.stdout = StdoutRedirector(self)
        try:
            check_hosts_pinning()
            check_nrpt_rules()
            check_dns_resolving()
            check_tls_connectivity()
            check_binary_patches()
        finally:
            sys.stdout = old_stdout
            self.log("="*50)

    def show_backups_dialog(self):
        backups = list_backups()
        dialog = tk.Toplevel(self)
        dialog.title("Управление резервными копиями (Бэкапы)")
        dialog.geometry("800x540")
        dialog.minsize(720, 460)
        dialog.configure(bg=BG_MAIN)

        # Header Title
        CanvasLabel(
            dialog,
            text="📁 Список доступных резервных копий:",
            font_spec=(FONT_FAMILY, 13, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_BLUE,
            height=28
        ).pack(fill="x", padx=20, pady=(15, 2))

        CanvasLabel(
            dialog,
            text="Нажмите «Восстановить» на карточке нужного бэкапа для отката файлов.",
            font_spec=(FONT_FAMILY, 9),
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            height=20
        ).pack(fill="x", padx=20, pady=(0, 10))

        # Canvas with Scrollable Cards
        outer_frame = tk.Frame(dialog, bg=BG_CARD, padx=2, pady=2, relief="solid", bd=1)
        outer_frame.pack(fill="both", expand=True, padx=20, pady=5)

        canvas = tk.Canvas(outer_frame, bg=BG_CONSOLE, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_CONSOLE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_frame_id, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def make_restore_handler(b_path, b_name, b_date):
            def _handler():
                if messagebox.askyesno("Восстановление бэкапа", f"Восстановить систему из бэкапа:\n\n{b_name}\n({b_date})?"):
                    dialog.destroy()
                    threading.Thread(
                        target=lambda: (restore_backup(b_path), self.refresh_dashboard_async()),
                        daemon=True
                    ).start()
            return _handler

        if not backups:
            no_b = tk.Frame(scrollable_frame, bg=BG_CONSOLE, pady=40)
            no_b.pack(fill="x")
            CanvasLabel(no_b, text="Резервных копий пока нет", font_spec=(FONT_FAMILY, 12, "bold"), bg=BG_CONSOLE, fg=TEXT_MUTED, height=30).pack()
        else:
            for name, bpath, manifest in backups:
                created = str(manifest.get("created_at", "N/A"))[:19].replace("T", " ")
                files_dict = manifest.get("files", {})
                files_list = ", ".join(files_dict.keys()) if files_dict else "нет данных"
                
                # Card Container
                card = tk.Frame(
                    scrollable_frame,
                    bg=BG_CARD,
                    padx=14,
                    pady=12,
                    relief="solid",
                    bd=1,
                    highlightbackground=BG_CARD_BORDER
                )
                card.pack(fill="x", padx=12, pady=6)

                # Info Left
                info_left = tk.Frame(card, bg=BG_CARD)
                info_left.pack(side="left", fill="x", expand=True)

                is_orig = "initial_original" in name
                title_color = ACCENT_YELLOW if is_orig else ACCENT_GREEN
                title_badge = " [ЗАВОДСКИЕ ОРИГИНАЛЫ GOOGLE]" if is_orig else ""

                CanvasLabel(
                    info_left,
                    text=f"🛡️ {name}{title_badge}",
                    font_spec=(FONT_FAMILY, 11, "bold"),
                    bg=BG_CARD,
                    fg=title_color,
                    height=24
                ).pack(fill="x")

                CanvasLabel(
                    info_left,
                    text=f"📅 Дата: {created}   •   Файлов: {len(files_dict)} ({files_list})",
                    font_spec=(FONT_FAMILY, 9),
                    bg=BG_CARD,
                    fg=TEXT_MUTED,
                    height=20
                ).pack(fill="x", pady=(2, 0))

                # Restore Button Right
                btn_restore = tk.Button(
                    card,
                    text="🔄 Восстановить",
                    font=(FONT_FAMILY, 9, "bold"),
                    highlightbackground=BG_CARD,
                    command=make_restore_handler(bpath, name, created)
                )
                btn_restore.pack(side="right", padx=(10, 0))

        # Bottom Bar
        btn_box = tk.Frame(dialog, bg=BG_MAIN, pady=12)
        btn_box.pack(fill="x", padx=20)

        def create_new_backup():
            dialog.destroy()
            self.run_backup_thread()

        tk.Button(
            btn_box,
            text="➕ Создать новый бэкап сейчас",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=create_new_backup
        ).pack(side="left")

        tk.Button(
            btn_box,
            text="Закрыть",
            font=(FONT_FAMILY, 9),
            highlightbackground=BG_MAIN,
            command=dialog.destroy
        ).pack(side="right")

        dialog.update_idletasks()
        try:
            dialog.transient(self)
            dialog.grab_set()
            dialog.focus_set()
        except Exception:
            pass

if __name__ == "__main__":
    app = AntigravityUnlockerApp()
    app.mainloop()
