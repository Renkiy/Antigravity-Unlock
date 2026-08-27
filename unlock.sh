#!/usr/bin/env bash
# ==============================================================================
# Antigravity Unlocker — Полноценный консольный терминальный лаунчер (CLI)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Цвета для терминала
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Определение команды Python
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo -e "${RED}[ERROR] Python 3 не найден в системе! Установите Python 3 для продолжения.${NC}"
    exit 1
fi

print_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║               🚀 ANTIGRAVITY UNLOCKER (CLI)                     ║"
    echo "║       Полноценная работа Google Antigravity в РФ без VPN         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

ensure_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}[*] Для работы с /etc/hosts требуются права администратора (sudo).${NC}"
        sudo -v || { echo -e "${RED}[-] Ошибка авторизации sudo.${NC}"; exit 1; }
    fi
}

run_apply() {
    print_banner
    ensure_root
    echo -e "${GREEN}[+] Запуск полной разблокировки Antigravity...${NC}\n"
    sudo "$PYTHON" tools/unlocker_core.py
    echo ""
}

run_restore() {
    print_banner
    ensure_root
    echo -e "${YELLOW}[*] Запуск полного отката изменений...${NC}\n"
    sudo "$PYTHON" tools/unlocker_core.py --restore
    echo ""
}

run_backups() {
    print_banner
    "$PYTHON" tools/backup_manager.py -i
    echo ""
}

run_diag() {
    print_banner
    echo -e "${BLUE}[*] Запуск комплексной диагностики...${NC}\n"
    "$PYTHON" tools/diagnostics.py
    echo ""
}

run_test_proxies() {
    print_banner
    echo -e "${BLUE}[*] Сканирование пула зарубежных SNI-прокси...${NC}\n"
    "$PYTHON" tools/proxy_manager.py
    echo ""
}

run_worker_config() {
    print_banner
    echo -e "${PURPLE}☁️  НАСТРОЙКА CLOUDFLARE WORKER L7${NC}\n"
    echo -e "Текущий URL бэкенда: ${CYAN}${CLOUD_CODE_URL:-https://daily-cloudcode-pa.googleapis.com}${NC}\n"
    echo "1) Установить кастомный URL Cloudflare Worker"
    echo "2) Сбросить на стандартный Google URL"
    echo "0) Назад"
    echo ""
    read -rp "Выберите [0-2]: " w_choice
    case "$w_choice" in
        1)
            read -rp "Введите URL вашего Worker (https://...): " custom_url
            if [[ "$custom_url" =~ ^https?:// ]]; then
                "$PYTHON" -c "from tools.unlocker_core import configure_ide_settings, configure_env_vars; configure_ide_settings('$custom_url'); configure_env_vars('$custom_url')"
                echo -e "\n${GREEN}[+] URL успешно установлен: $custom_url${NC}"
            else
                echo -e "\n${RED}[-] Ошибка: URL должен начинаться с https:// или http://${NC}"
            fi
            ;;
        2)
            default_url="https://daily-cloudcode-pa.googleapis.com"
            "$PYTHON" -c "from tools.unlocker_core import configure_ide_settings, configure_env_vars; configure_ide_settings('$default_url'); configure_env_vars('$default_url')"
            echo -e "\n${GREEN}[+] Сброшено на стандартный URL: $default_url${NC}"
            ;;
        *)
            ;;
    esac
    echo ""
}

run_github_publish() {
    print_banner
    echo -e "${BLUE}🚀 ПУБЛИКАЦИЯ РЕПОЗИТОРИЯ НА GITHUB${NC}\n"
    read -rp "Введите URL вашего репозитория (https://github.com/...): " gh_url
    if [[ "$gh_url" =~ ^(https://|git@) ]]; then
        echo -e "\n${YELLOW}[*] Отправка файлов в репозиторий $gh_url...${NC}"
        git remote remove origin 2>/dev/null || true
        git remote add origin "$gh_url"
        if git push -u origin main; then
            echo -e "\n${GREEN}🎉 [УСПЕХ] Проект успешно опубликован на GitHub!${NC}"
        else
            echo -e "\n${RED}[-] Ошибка отправки на GitHub.${NC}"
        fi
    else
        echo -e "\n${RED}[-] Неверный формат ссылки.${NC}"
    fi
    echo ""
}

# Обработка аргументов командной строки
case "$1" in
    --apply|-a)
        run_apply
        exit 0
        ;;
    --restore|-r)
        run_restore
        exit 0
        ;;
    --backups|-b)
        run_backups
        exit 0
        ;;
    --diag|-d)
        run_diag
        exit 0
        ;;
    --test|-t)
        run_test_proxies
        exit 0
        ;;
    --worker|-w)
        run_worker_config
        exit 0
        ;;
    --help|-h)
        print_banner
        echo "Использование: ./unlock.sh [ОПЦИЯ]"
        echo ""
        echo "Опции:"
        echo "  -a, --apply     Активировать анлок (бэкап + hosts + патч + codesign)"
        echo "  -r, --restore   Полный откат в исходное состояние"
        echo "  -b, --backups   Управление резервными копиями (просмотр / откат)"
        echo "  -d, --diag      Комплексная диагностика сети и подписей"
        echo "  -t, --test      Сканирование и пинг пула SNI-прокси"
        echo "  -w, --worker    Настройка Cloudflare Worker L7"
        echo "  -h, --help      Показать эту справку"
        echo ""
        echo "Без аргументов открывается интерактивное терминальное меню."
        exit 0
        ;;
esac

# Интерактивное меню
while true; do
    clear
    print_banner
    echo -e "${BOLD}Выберите действие:${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} ⚡ ${BOLD}АКТИВИРОВАТЬ АНЛОК${NC} (Авто-прокси + Патч + CodeSign)"
    echo -e "  ${YELLOW}2)${NC} 🔄 ${BOLD}ПОЛНЫЙ ОТКАТ (Restore оригиналов)${NC}"
    echo -e "  ${PURPLE}3)${NC} 🛡️  ${BOLD}Управление бэкапами${NC} (Список, выбор и восстановление)"
    echo -e "  ${BLUE}4)${NC} 🔍 Диагностика сети и бинарников"
    echo -e "  ${CYAN}5)${NC} ⚡ Тестирование скорости пула SNI-прокси"
    echo -e "  ${YELLOW}6)${NC} ☁️  Настройка Cloudflare Worker L7"
    echo -e "  ${BLUE}7)${NC} 🚀 Опубликовать проект на GitHub"
    echo -e "  ${RED}0)${NC} 🚪 Выход"
    echo ""
    read -rp "Введите номер [0-7]: " choice

    case "$choice" in
        1)
            run_apply
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        2)
            run_restore
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        3)
            run_backups
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        4)
            run_diag
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        5)
            run_test_proxies
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        6)
            run_worker_config
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        7)
            run_github_publish
            read -rp "Нажмите Enter для возврата в меню..."
            ;;
        0|q|Q)
            echo -e "\n${GREEN}До свидания!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Неверный ввод, попробуйте снова.${NC}"
            sleep 1
            ;;
    esac
done
