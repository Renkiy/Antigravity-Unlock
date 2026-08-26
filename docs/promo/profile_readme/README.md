<div align="center">

# ⚡ RENKIY

### *Системный инженер • Низкоуровневая сетевая архитектура • Reverse Engineering & AI-инструментарий*

<p align="center">
  <a href="https://github.com/Renkiy">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&duration=3000&pause=1000&color=89B4FA&center=true&vCenter=true&multiline=false&width=780&height=50&lines=%D0%A1%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%BD%D0%BE%D0%B5+%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B5+%E2%80%A2+Zero-VPN+%D0%B0%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D1%8B;Reverse+Engineering+%E2%80%A2+WinAPI+%26+%D0%B1%D0%B8%D0%BD%D0%B0%D1%80%D0%BD%D1%8B%D0%B9+%D0%BF%D0%B0%D1%82%D1%87%D0%B8%D0%BD%D0%B3+PE;AI-%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B+%E2%80%A2+Model+Context+Protocol+(FastMCP);Open-Source+%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0+%E2%80%A2+Python+%26+C%2B%2B" alt="Typing SVG" />
  </a>
</p>

[![Telegram](https://img.shields.io/badge/Telegram-@renkiy-2BA6E1?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/renkiy)
[![GitHub](https://img.shields.io/badge/GitHub-Renkiy-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Renkiy)
[![Статус](https://img.shields.io/badge/%D0%A1%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%A1%D0%BE%D0%B7%D0%B4%D0%B0%D1%8E%20%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B-a6e3a1?style=for-the-badge&labelColor=1e1e2e)](#)
[![Фокус](https://img.shields.io/badge/%D0%A4%D0%BE%D0%BA%D1%83%D1%81-Zero--VPN+%7C+RE+%7C+AI-89b4fa?style=for-the-badge&labelColor=1e1e2e)](#)

</div>

---

## 👨‍💻 Обо мне

Создаю **высокопроизводительные системные утилиты**, низкоуровневые сетевые решения, инструменты реверс-инжиниринга и AI-автоматизации. Верю, что хороший софт должен быть **точным, прозрачным и уважать ресурсы системы** — никакого bloatware, никаких скрытых зависимостей.

- 🔭 **Сейчас работаю над:** Селективные маршрутизаторы сверхнизкой задержки, FastMCP-серверы для AI-агентов, бинарные патчеры с сохранением длины.
- ⚡ **Специализация:** Windows Internals (Winsock2, NRPT, PE/COFF, WinAPI), TLS 1.3 SNI диспатчинг, реверс-инжиниринг (x64dbg, Ghidra), Python/C++, Godot 4.
- 💬 **Спрашивайте про:** Реверс сетевых протоколов, изоляцию DNS, обход геоблокировок без VPN, интеграцию AI-агентов через Model Context Protocol.
- 📫 **Связь:** Telegram [**@renkiy**](https://t.me/renkiy) или через [**GitHub Issues**](https://github.com/Renkiy).

---

## 🌟 Главный проект

<div align="center">

### 🚀 [Antigravity Unlocker](https://github.com/Renkiy/Antigravity-Unlock)
#### *Автономный Zero-VPN комплекс для работы Google Antigravity IDE и Gemini в РФ/РБ*

[![Zero VPN](https://img.shields.io/badge/%D0%90%D1%80%D1%85%D0%B8%D1%82%D0%B5%D0%BA%D1%82%D1%83%D1%80%D0%B0-Zero--VPN-89b4fa?style=for-the-badge&logo=cloudflare&logoColor=white)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![Standalone EXE](https://img.shields.io/badge/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA-1--Click+EXE-a6e3a1?style=for-the-badge&logo=windows&logoColor=white)](#)
[![Failover](https://img.shields.io/badge/Watchdog-%D0%90%D0%B2%D1%82%D0%BE--Failover-fab387?style=for-the-badge&logo=speedtest&logoColor=white)](#)

</div>

**Antigravity Unlocker** решает проблему геоблокировок Google AI в России и Беларуси. Вместо медленных VPN, пропускающих 100% трафика через туннель, Unlocker реализует **хирургический многоуровневый обход**:

```
                          ┌─────────────────────────────────────────────────┐
                          │            ВАШ КОМПЬЮТЕР (WINDOWS)             │
                          └─────────────────────────────────────────────────┘
                                       │                           │
                [Только AI-трафик]     │                           │  [Весь остальной трафик (99.9%)]
   (cloudcode-pa.googleapis.com)       │                           │  (Браузер, YouTube 4K, Steam, Игры)
                                       ▼                           ▼
                     ┌────────────────────────┐      ┌────────────────────────┐
                     │ Anti-Leak Hosts Pinning │      │  Прямое подключение    │
                     │ (Европейские SNI-узлы)  │      │  (Полная скорость ISP) │
                     └────────────────────────┘      └────────────────────────┘
                                │                                  │
              ┌─────────────────┴──────────────┐                   │
              ▼                                ▼                   ▼
┌──────────────────────┐  ┌────────────────────────┐  ┌────────────────────────┐
│ Hetzner DE / Comss NL│  │ Cloudflare Worker (L7) │  │ Игры / Рунет / Банки / │
│ (TLS 1.3 Passthrough)│  │ (Очистка заголовков)   │  │ Госуслуги — 100% OK    │
└──────────────────────┘  └────────────────────────┘  └────────────────────────┘
```

### 🔑 Ключевые механизмы:
- **Anti-Leak Hosts Pinning (L4):** Принудительная привязка DNS — Windows `Dnscache` не откатится на российские IP Google (`172.217.x.x`).
- **10-байтный PE-патч без изменения длины:** Модификация `language_server.exe` (`ineligible` ➔ `inexigible`) с сохранением таблиц секций PE и Protobuf-выравнивания.
- **Smart Auto-Failover Watchdog:** Фоновый демон мониторит порт 443 каждые 20 секунд — при сбое переключает на резервный узел мгновенно.
- **Ноль внешних зависимостей:** Только стандартная библиотека Python 3.10+ (`socket`, `ssl`, `ctypes`, `tkinter`).
- **Standalone EXE:** Запуск в 1 клик без установки Python.

---

## 🛠️ Стек технологий

### 💻 Системное программирование
<p>
  <img src="https://img.shields.io/badge/Python_3.10+-1E1E2E?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python" />
  <img src="https://img.shields.io/badge/C%2B%2B_20-1E1E2E?style=for-the-badge&logo=c%2B%2B&logoColor=00599C" alt="C++" />
  <img src="https://img.shields.io/badge/Windows_API-1E1E2E?style=for-the-badge&logo=windows&logoColor=0078D6" alt="WinAPI" />
  <img src="https://img.shields.io/badge/PE%2FCOFF-1E1E2E?style=for-the-badge&logo=windows-terminal&logoColor=CBA6F7" alt="PE/COFF" />
  <img src="https://img.shields.io/badge/Winsock2-1E1E2E?style=for-the-badge&logo=gnubash&logoColor=A6E3A1" alt="Winsock2" />
</p>

### 🌐 Сети и протоколы
<p>
  <img src="https://img.shields.io/badge/TCP%2FIP-1E1E2E?style=for-the-badge&logo=wireshark&logoColor=89B4FA" alt="TCP/IP" />
  <img src="https://img.shields.io/badge/TLS_1.3_%26_SNI-1E1E2E?style=for-the-badge&logo=letsencrypt&logoColor=A6E3A1" alt="TLS 1.3" />
  <img src="https://img.shields.io/badge/DNS_%2F_DoH-1E1E2E?style=for-the-badge&logo=cloudflare&logoColor=F38020" alt="DNS" />
  <img src="https://img.shields.io/badge/gRPC_%26_Protobuf-1E1E2E?style=for-the-badge&logo=grpc&logoColor=4285F4" alt="gRPC" />
</p>

### 🧠 AI и LLM
<p>
  <img src="https://img.shields.io/badge/Google_Gemini-1E1E2E?style=for-the-badge&logo=google&logoColor=8E75C2" alt="Gemini" />
  <img src="https://img.shields.io/badge/Claude_Sonnet-1E1E2E?style=for-the-badge&logo=anthropic&logoColor=D97706" alt="Claude" />
  <img src="https://img.shields.io/badge/Model_Context_Protocol-1E1E2E?style=for-the-badge&logo=openai&logoColor=89B4FA" alt="MCP" />
  <img src="https://img.shields.io/badge/FastMCP-1E1E2E?style=for-the-badge&logo=fastapi&logoColor=10B981" alt="FastMCP" />
</p>

### 🔍 Безопасность и Reverse Engineering
<p>
  <img src="https://img.shields.io/badge/Ghidra-1E1E2E?style=for-the-badge&logo=nsa&logoColor=A6E3A1" alt="Ghidra" />
  <img src="https://img.shields.io/badge/x64dbg-1E1E2E?style=for-the-badge&logo=gnubash&logoColor=89B4FA" alt="x64dbg" />
  <img src="https://img.shields.io/badge/Wireshark-1E1E2E?style=for-the-badge&logo=wireshark&logoColor=1679A7" alt="Wireshark" />
  <img src="https://img.shields.io/badge/Sysinternals-1E1E2E?style=for-the-badge&logo=microsoft&logoColor=00A4EF" alt="Sysinternals" />
</p>

### 🎮 Игровые движки
<p>
  <img src="https://img.shields.io/badge/Godot_4-1E1E2E?style=for-the-badge&logo=godotengine&logoColor=478CBF" alt="Godot 4" />
  <img src="https://img.shields.io/badge/Unity-1E1E2E?style=for-the-badge&logo=unity&logoColor=FFFFFF" alt="Unity" />
  <img src="https://img.shields.io/badge/GLSL_%2F_HLSL-1E1E2E?style=for-the-badge&logo=opengl&logoColor=5586A4" alt="Shaders" />
</p>

---

## 📈 Статистика GitHub

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=Renkiy&show_icons=true&theme=catppuccin_mocha&hide_border=true&bg_color=1E1E2E&title_color=89B4FA&icon_color=A6E3A1&text_color=CDD6F4&locale=ru" alt="GitHub Stats" width="49%" />
<img src="https://github-readme-streak-stats.herokuapp.com/?user=Renkiy&theme=catppuccin-mocha&hide_border=true&background=1E1E2E&stroke=89B4FA&ring=A6E3A1&fire=F38BA8&currStreakLabel=89B4FA&sideLabels=CDD6F4&locale=ru" alt="GitHub Streak" width="49%" />

</div>

---

## 🌐 Контакты

<div align="center">

| Канал | Ссылка | Для чего |
| :--- | :--- | :--- |
| 💬 **Telegram** | [**@renkiy**](https://t.me/renkiy) | Вопросы, обсуждения, коллаборации |
| 🐙 **GitHub** | [**@Renkiy**](https://github.com/Renkiy) | Код, Issues, Pull Requests |

</div>

<br>

<div align="center">

*«Простота — необходимое условие надёжности. Создавай точные системы, оптимизируй критический путь и держи код открытым.»*

<sub>Catppuccin Mocha • Open Source • <b>Renkiy</b></sub>

</div>
