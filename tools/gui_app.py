import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

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

# Colors - Catppuccin Mocha inspired Dark Theme
BG_MAIN = "#1E1E2E"
BG_CARD = "#252538"
BG_CARD_BORDER = "#313244"
BG_CONSOLE = "#181825"
TEXT_MAIN = "#CDD6F4"
TEXT_MUTED = "#A6ADC8"
ACCENT_BLUE = "#89B4FA"
ACCENT_GREEN = "#A6E3A1"
ACCENT_RED = "#F38BA8"
ACCENT_YELLOW = "#F9E2AF"
ACCENT_PURPLE = "#CBA6F7"

class AntigravityUnlockerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Antigravity Unlocker — Работа в РФ без VPN")
        self.geometry("900x680")
        self.minsize(800, 600)
        self.configure(bg=BG_MAIN)

        # Style configuration
        self.setup_styles()
        
        # UI Elements
        self.create_header()
        self.create_dashboard()
        self.create_action_buttons()
        self.create_console()

        # Start initial status check
        self.log("[*] Запуск интерфейса Antigravity Unlocker...")
        self.check_admin_status()
        self.refresh_dashboard_async()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TFrame", background=BG_MAIN)
        self.style.configure("Card.TFrame", background=BG_CARD, relief="solid", borderwidth=1)
        self.style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=ACCENT_BLUE)
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background=BG_CARD, foreground=TEXT_MUTED)
        self.style.configure("CardValue.TLabel", font=("Segoe UI", 12, "bold"), background=BG_CARD, foreground=TEXT_MAIN)

    def log(self, text, color=None):
        self.console.config(state="normal")
        ts = time.strftime("[%H:%M:%S] ")
        self.console.insert(tk.END, ts + text + "\n")
        self.console.see(tk.END)
        self.console.config(state="disabled")

    def check_admin_status(self):
        if is_admin():
            self.admin_badge.config(text="● Права Администратора: ДА", foreground=ACCENT_GREEN)
            self.log("[+] Приложение запущено с правами Администратора.")
        else:
            self.admin_badge.config(text="● Права Администратора: НЕТ", foreground=ACCENT_RED)
            self.log("[!] Внимание: Для изменения hosts и NRPT требуются права Администратора.")

    def create_header(self):
        header_frame = tk.Frame(self, bg=BG_MAIN, pady=10, padx=20)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame, 
            text="🚀 Antigravity Unlocker 2.0", 
            font=("Segoe UI", 18, "bold"),
            bg=BG_MAIN, 
            fg=ACCENT_BLUE
        )
        title_label.pack(side="left")

        self.admin_badge = tk.Label(
            header_frame,
            text="● Проверка прав...",
            font=("Segoe UI", 10, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_YELLOW
        )
        self.admin_badge.pack(side="right")

    def create_dashboard(self):
        dash_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=5)
        dash_frame.pack(fill="x")

        # 4 Cards: LSP Patch, Hosts Pin, Live Proxy Ping, IPv4 Precedence
        dash_frame.columnconfigure(0, weight=1)
        dash_frame.columnconfigure(1, weight=1)
        dash_frame.columnconfigure(2, weight=1)
        dash_frame.columnconfigure(3, weight=1)

        # Card 1: Binary Patch
        c1 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        c1.grid(row=0, column=0, padx=5, sticky="nsew")
        tk.Label(c1, text="Бинарный патч", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.lbl_patch_status = tk.Label(c1, text="Проверка...", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW)
        self.lbl_patch_status.pack(anchor="w", pady=(4, 0))

        # Card 2: Hosts Pin
        c2 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        c2.grid(row=0, column=1, padx=5, sticky="nsew")
        tk.Label(c2, text="Привязка Hosts", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.lbl_hosts_status = tk.Label(c2, text="Проверка...", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW)
        self.lbl_hosts_status.pack(anchor="w", pady=(4, 0))

        # Card 3: Ping Gemini API
        c3 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        c3.grid(row=0, column=2, padx=5, sticky="nsew")
        tk.Label(c3, text="Gemini API TLS", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.lbl_ping_status = tk.Label(c3, text="Тестирование...", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_YELLOW)
        self.lbl_ping_status.pack(anchor="w", pady=(4, 0))

        # Card 4: IPv4 Priority
        c4 = tk.Frame(dash_frame, bg=BG_CARD, padx=12, pady=10, highlightbackground=BG_CARD_BORDER, highlightthickness=1)
        c4.grid(row=0, column=3, padx=5, sticky="nsew")
        tk.Label(c4, text="Приоритет IPv4", font=("Segoe UI", 9), bg=BG_CARD, fg=TEXT_MUTED).pack(anchor="w")
        self.lbl_ipv4_status = tk.Label(c4, text="Активен", font=("Segoe UI", 11, "bold"), bg=BG_CARD, fg=ACCENT_GREEN)
        self.lbl_ipv4_status.pack(anchor="w", pady=(4, 0))

    def create_action_buttons(self):
        btn_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=10)
        btn_frame.pack(fill="x")

        # Row 1 Main Buttons
        r1 = tk.Frame(btn_frame, bg=BG_MAIN)
        r1.pack(fill="x", pady=3)

        btn_unlock = tk.Button(
            r1,
            text="⚡ АКТИВИРОВАТЬ АНЛОК (Вариант Б + Авто-прокси)",
            font=("Segoe UI", 11, "bold"),
            bg="#2E7D32",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.run_unlock_thread
        )
        btn_unlock.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_rollback = tk.Button(
            r1,
            text="🔄 ПОЛНЫЙ ОТКАТ (Rollback)",
            font=("Segoe UI", 10, "bold"),
            bg="#C62828",
            fg="white",
            activebackground="#D32F2F",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.run_rollback_thread
        )
        btn_rollback.pack(side="right", padx=(5, 0))

        # Row 2 Utility Buttons
        r2 = tk.Frame(btn_frame, bg=BG_MAIN)
        r2.pack(fill="x", pady=5)

        btn_backup = tk.Button(
            r2,
            text="🛡️ Создать бэкап",
            font=("Segoe UI", 9, "bold"),
            bg="#37474F",
            fg=TEXT_MAIN,
            activebackground="#455A64",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.run_backup_thread
        )
        btn_backup.pack(side="left", padx=(0, 4))

        btn_backups_list = tk.Button(
            r2,
            text="📁 Список бэкапов",
            font=("Segoe UI", 9),
            bg="#37474F",
            fg=TEXT_MAIN,
            activebackground="#455A64",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.show_backups_dialog
        )
        btn_backups_list.pack(side="left", padx=4)

        btn_find_proxy = tk.Button(
            r2,
            text="⚡ Найти быстрый прокси",
            font=("Segoe UI", 9),
            bg="#37474F",
            fg=TEXT_MAIN,
            activebackground="#455A64",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.run_find_proxy_thread
        )
        btn_find_proxy.pack(side="left", padx=4)

        self.btn_watchdog = tk.Button(
            r2,
            text="🐕 Watchdog: ВКЛЮЧЕН",
            font=("Segoe UI", 9, "bold"),
            bg="#1B5E20",
            fg="white",
            activebackground="#2E7D32",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.toggle_watchdog
        )
        self.btn_watchdog.pack(side="left", padx=4)

        btn_worker = tk.Button(
            r2,
            text="☁️ Cloudflare L7 Relay",
            font=("Segoe UI", 9),
            bg="#BF360C",
            fg="white",
            activebackground="#D84315",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.show_worker_dialog
        )
        btn_worker.pack(side="left", padx=4)

        btn_diag = tk.Button(
            r2,
            text="🔍 Диагностика сети",
            font=("Segoe UI", 9),
            bg="#37474F",
            fg=TEXT_MAIN,
            activebackground="#455A64",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=self.run_diagnostics_thread
        )
        btn_diag.pack(side="left", padx=4)

        btn_elevate = tk.Button(
            r2,
            text="🔑 Администратор",
            font=("Segoe UI", 9),
            bg="#4A148C",
            fg="white",
            activebackground="#6A1B9A",
            activeforeground="white",
            relief="flat",
            padx=10,
            pady=5,
            command=lambda: elevate_process([])
        )
        btn_elevate.pack(side="right", padx=(4, 0))

    def create_console(self):
        console_frame = tk.Frame(self, bg=BG_MAIN, padx=20, pady=5)
        console_frame.pack(fill="both", expand=True)

        tk.Label(
            console_frame,
            text="Лог операций и статус выполнения:",
            font=("Segoe UI", 9, "bold"),
            bg=BG_MAIN,
            fg=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 2))

        self.console = scrolledtext.ScrolledText(
            console_frame,
            bg=BG_CONSOLE,
            fg=TEXT_MAIN,
            font=("Consolas", 10),
            relief="flat",
            padx=10,
            pady=10,
            state="disabled",
            highlightbackground=BG_CARD_BORDER,
            highlightthickness=1
        )
        self.console.pack(fill="both", expand=True)

    def toggle_watchdog(self):
        from tools.proxy_manager import watchdog_instance
        if watchdog_instance.running:
            watchdog_instance.stop()
            self.btn_watchdog.config(text="🐕 Watchdog: ВЫКЛ", bg="#37474F")
        else:
            watchdog_instance.log_callback = lambda msg: self.log(msg)
            watchdog_instance.failover_callback = lambda new_ip: self.after(100, self._refresh_dashboard)
            watchdog_instance.start()
            self.btn_watchdog.config(text="🐕 Watchdog: ВКЛЮЧЕН", bg="#1B5E20")

    def show_worker_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Настройка Cloudflare Worker L7 (Обход блокировки аккаунтов)")
        dialog.geometry("680x420")
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="☁️ Cloudflare Worker L7 Relay (Для 100% защиты русских аккаунтов)",
            font=("Segoe UI", 12, "bold"),
            bg=BG_MAIN,
            fg=ACCENT_BLUE
        ).pack(anchor="w", padx=15, pady=(15, 5))

        desc = (
            "Cloudflare Worker полностью устраняет проблему блокировки аккаунта Google в РФ,\n"
            "перехватывая ответы API и подменяя статус 'ineligible' на 'eligible' на лету.\n\n"
            "Готовый скрипт воркера находится в файле: tools/cloudflare_worker.js"
        )
        tk.Label(dialog, text=desc, font=("Segoe UI", 9), bg=BG_MAIN, fg=TEXT_MUTED, justify="left").pack(anchor="w", padx=15, pady=5)

        f_url = tk.Frame(dialog, bg=BG_MAIN)
        f_url.pack(fill="x", padx=15, pady=10)

        tk.Label(f_url, text="URL вашего Worker:", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_MAIN).pack(anchor="w")
        ent_url = tk.Entry(f_url, font=("Consolas", 10), bg=BG_CARD, fg=TEXT_MAIN, insertbackground=TEXT_MAIN)
        ent_url.pack(fill="x", pady=5)
        
        # Текущий URL
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

        tk.Button(btn_f, text="💾 Применить Worker URL", bg="#2E7D32", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5, command=apply_worker_url).pack(side="left")
        tk.Button(btn_f, text="🔄 Сброс на дефолт", bg="#C62828", fg="white", font=("Segoe UI", 9), relief="flat", padx=10, pady=5, command=reset_worker_url).pack(side="left", padx=10)
        tk.Button(btn_f, text="Закрыть", bg="#37474F", fg="white", font=("Segoe UI", 9), relief="flat", padx=10, pady=5, command=dialog.destroy).pack(side="right")

    def refresh_dashboard_async(self):
        threading.Thread(target=self._refresh_dashboard, daemon=True).start()

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
            self.lbl_patch_status.config(text="ПРОПАТЧЕН [OK]", fg=ACCENT_GREEN)
        else:
            self.lbl_patch_status.config(text="ТРЕБУЕТСЯ ПАТЧ", fg=ACCENT_RED)

        # 2. Check Hosts Pin
        pinned_ip = get_current_pinned_ip()
        if pinned_ip:
            self.lbl_hosts_status.config(text=f"АКТИВЕН ({pinned_ip})", fg=ACCENT_GREEN)
        else:
            self.lbl_hosts_status.config(text="НЕ ПРИВЯЗАН", fg=TEXT_MUTED)

        # 3. Check Gemini API Ping
        target_host = "cloudcode-pa.googleapis.com"
        probe_target_ip = pinned_ip or "94.130.180.225"
        ok, lat, err = probe_single_host(probe_target_ip, target_host, timeout=2.0)
        if ok:
            self.lbl_ping_status.config(text=f"OK ({lat:.0f} ms)", fg=ACCENT_GREEN)
        else:
            self.lbl_ping_status.config(text="ТАЙМАУТ / ОШИБКА", fg=ACCENT_RED)

    def run_unlock_thread(self):
        if not is_admin():
            if messagebox.askyesno("Требуются права Администратора", "Для применения анлока (запись в hosts и настройка сети) требуются права Администратора.\n\nПерезапустить приложение с правами Администратора?"):
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

            # 3. Pin hosts & NRPT clean
            self.log(f"[3/5] Привязка хостов в hosts к {best_ip} и очистка NRPT...")
            ok, msg = pin_hosts(best_ip)
            self.log(f"  {'[+]' if ok else '[-]'} {msg}")

            # 4. Binary patch
            self.log("[4/5] Патчинг Language Server / agy...")
            patch_binaries()

            # 5. Settings & IPv4
            self.log("[5/5] Конфигурация IDE и сетевых политик...")
            configure_ide_settings()
            configure_env_vars()
            set_ipv4_priority(True)

            # Запуск Watchdog
            from tools.proxy_manager import watchdog_instance
            watchdog_instance.log_callback = lambda msg: self.log(msg)
            watchdog_instance.failover_callback = lambda new_ip: self.after(100, self._refresh_dashboard)
            watchdog_instance.start()
            self.btn_watchdog.config(text="🐕 Watchdog: ВКЛЮЧЕН", bg="#1B5E20")

            self.log("="*50)
            self.log("🎉 [УСПЕХ] Анлок успешно активирован! Antigravity готова к работе без VPN.")
            messagebox.showinfo("Успех", "Разблокировка успешно применена!\n\nВсе запросы зафиксированы на быстрый зарубежный SNI-прокси.\nWatchdog активен и защитит от сбоев.")
        except Exception as e:
            self.log(f"[-] Ошибка во время выполнения: {e}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        finally:
            self._refresh_dashboard()

    def run_rollback_thread(self):
        if not is_admin():
            if messagebox.askyesno("Требуются права Администратора", "Для отката изменений требуются права Администратора.\n\nПерезапустить приложение с правами Администратора?"):
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
            self.btn_watchdog.config(text="🐕 Watchdog: ВЫКЛ", bg="#37474F")

            execute_rollback()
            self.log("="*50)
            self.log("✅ [УСПЕХ] Все изменения полностью отменены.")
            messagebox.showinfo("Откат завершен", "Система успешно возвращена в исходное состояние.")
        except Exception as e:
            self.log(f"[-] Ошибка отката: {e}")
        finally:
            self._refresh_dashboard()

    def run_backup_thread(self):
        threading.Thread(target=self._do_backup, daemon=True).start()

    def _do_backup(self):
        self.log("\n[+] Создание резервной копии...")
        bdir, _ = create_backup("manual")
        self.log(f"[+] Бэкап создан: {bdir}")
        messagebox.showinfo("Бэкап создан", f"Резервная копия успешно создана в:\n{bdir}")

    def run_find_proxy_thread(self):
        threading.Thread(target=self._do_find_proxy, daemon=True).start()

    def _do_find_proxy(self):
        self.log("\n[+] Тестирование всех прокси серверов...")
        best_ip = find_best_proxy(verbose=True)
        self.log(f"[+] Самый быстрый прокси: {best_ip}")
        self._refresh_dashboard()

    def run_diagnostics_thread(self):
        threading.Thread(target=self._do_diagnostics, daemon=True).start()

    def _do_diagnostics(self):
        self.log("\n" + "="*50)
        self.log("🔍 ДИАГНОСТИКА СЕТИ И СТАТУСА...")
        from tools.diagnostics import (
            check_hosts_pinning, check_nrpt_rules, check_dns_resolving,
            check_tls_connectivity, check_binary_patches
        )
        
        # Capture stdout
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
        dialog.geometry("650x400")
        dialog.configure(bg=BG_MAIN)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Список доступных резервных копий:", font=("Segoe UI", 11, "bold"), bg=BG_MAIN, fg=TEXT_MAIN).pack(anchor="w", padx=15, pady=10)

        tree_frame = tk.Frame(dialog, bg=BG_MAIN)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=5)

        cols = ("name", "created", "files")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        tree.heading("name", text="Имя бэкапа")
        tree.heading("created", text="Дата создания")
        tree.heading("files", text="Файлов")
        tree.column("name", width=220)
        tree.column("created", width=180)
        tree.column("files", width=80)

        for name, bpath, manifest in backups:
            tree.insert("", "end", values=(name, manifest.get("created_at", "N/A"), len(manifest.get("files", {}))), tags=(bpath,))

        tree.pack(side="left", fill="both", expand=True)

        btn_box = tk.Frame(dialog, bg=BG_MAIN, pady=10)
        btn_box.pack(fill="x", padx=15)

        def restore_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Внимание", "Выберите бэкап из списка!")
                return
            item = tree.item(sel[0])
            bpath = tree.item(sel[0], "tags")[0]
            if messagebox.askyesno("Восстановление", f"Восстановить файлы из бэкапа {item['values'][0]}?"):
                dialog.destroy()
                threading.Thread(target=lambda: (restore_backup(bpath), self._refresh_dashboard()), daemon=True).start()

        btn_restore = tk.Button(btn_box, text="🔄 Восстановить выбранный бэкап", bg="#2E7D32", fg="white", font=("Segoe UI", 9, "bold"), relief="flat", padx=10, pady=5, command=restore_selected)
        btn_restore.pack(side="left")

        btn_close = tk.Button(btn_box, text="Закрыть", bg="#37474F", fg="white", font=("Segoe UI", 9), relief="flat", padx=10, pady=5, command=dialog.destroy)
        btn_close.pack(side="right")

if __name__ == "__main__":
    app = AntigravityUnlockerApp()
    app.mainloop()
