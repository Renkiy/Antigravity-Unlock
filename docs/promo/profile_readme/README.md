<div align="center">

# ⚡ RENKIY

### *Systems Software Engineer • Low-Level Network Architect • Reverse Engineering & AI Tooling*

<p align="center">
  <a href="https://github.com/Renkiy">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&duration=3000&pause=1000&color=89B4FA&center=true&vCenter=true&multiline=false&width=780&height=50&lines=Low-Level+Network+Engineering+%E2%80%A2+Zero-VPN+Architectures;Reverse+Engineering+%E2%80%A2+WinAPI+%26+PE+Binary+Patching;Distributed+AI+Tooling+%E2%80%A2+Model+Context+Protocol+(FastMCP);High-Performance+Systems+Programming+%E2%80%A2+Open-Source+Evangelist" alt="Typing SVG" />
  </a>
</p>

[![Telegram Direct](https://img.shields.io/badge/Telegram-@renkiy-2BA6E1?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/renkiy)
[![Telegram Channel](https://img.shields.io/badge/Channel-Renkiy%20Lab-blueviolet?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/renkiy)
[![GitHub](https://img.shields.io/badge/GitHub-Renkiy-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Renkiy)
[![Status](https://img.shields.io/badge/Status-Building%20High--Perf%20Systems-a6e3a1?style=for-the-badge&labelColor=1e1e2e)](#)
[![Focus](https://img.shields.io/badge/Focus-Zero--VPN%20%7C%20Reverse%20Eng%20%7C%20AI-89b4fa?style=for-the-badge&labelColor=1e1e2e)](#)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

</div>

---

## 👨‍💻 About Me & Engineering Philosophy

I build **high-performance, zero-bloat systems software**, low-level networking primitives, reverse-engineering solutions, and distributed AI tooling. My work is centered around the belief that modern software should be **surgical, transparent, and respectful of system resources**.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ⚙️ CORE ENGINEERING TENETS                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Zero-Bloat Primitives  │ Native OS APIs over heavyweight runtimes; zero unnecessary deps.     │
│ 2. Surgical Precision     │ Byte-invariant binary modifications instead of destructive overrides.│
│ 3. Selective Routing      │ Targeted L4/L7 dispatching (Zero-VPN) to preserve 100% line speed.   │
│ 4. Deterministic Safety   │ Cryptographic SHA-256 state snapshots and 1-click atomic rollbacks.  │
│ 5. Open-Source Autonomy   │ Free, transparent, auditable code without telemetry or paywalls.     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- 🔭 **Current Focus:** Ultra-low-latency selective routing engines, FastMCP protocol tooling for agentic AI architectures, and length-preserving binary patchers.
- ⚡ **Specialties:** Windows Internals (Winsock2, NRPT, PE/COFF, WinAPI), TLS 1.3 SNI dispatching, reverse engineering (x64dbg, Ghidra), high-throughput Python/C++ architectures, and Godot 4 systems.
- 💬 **Ask Me About:** Network protocol reverse engineering, DNS isolation mechanics, bypassing geoblocks without system-wide VPNs, and integrating AI agents via Model Context Protocol.
- 📫 **Direct Reach:** Connect on Telegram [**@renkiy**](https://t.me/renkiy) or via [**GitHub Issues**](https://github.com/Renkiy).

---

## 🌟 Featured Project Spotlight

<div align="center">

### 🚀 [Antigravity Unlocker 2.0](https://github.com/Renkiy/antigravity-unlocker)
#### *Zero-VPN, Zero-Dependency Autonomous Geoblock Bypass & AI Tooling Ecosystem for Windows*

[![Zero VPN](https://img.shields.io/badge/Architecture-Zero--VPN%20Hybrid-89b4fa?style=for-the-badge&logo=cloudflare&logoColor=white)](#)
[![Python 3.10+](https://img.shields.io/badge/Runtime-Python%203.10%2B%20StdLib-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
[![FastMCP](https://img.shields.io/badge/Integration-FastMCP%20Server-10b981?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Auto Failover](https://img.shields.io/badge/Watchdog-Sub--Second%20Failover-fab387?style=for-the-badge&logo=speedtest&logoColor=white)](#)
[![1-Click Rollback](https://img.shields.io/badge/Safety-1--Click%20Rollback%20%28SHA--256%29-a6e3a1?style=for-the-badge&logo=shieldcheck&logoColor=white)](#)

</div>

Antigravity Unlocker 2.0 solves the **August 24–25 Google Antigravity geoblock crisis** across Eastern Europe, which invalidated traditional SmartDNS and caused cascading Google Front End (GFE) resets (`10054 WSAECONNRESET`). Instead of forcing 100% of system traffic through sluggish full-tunnel VPNs, Unlocker implements a **surgical multi-tiered bypass**:

```
                              ┌─────────────────────────────────────────────────────────┐
                              │                 CLIENT WORKSTATION (WINDOWS)            │
                              └─────────────────────────────────────────────────────────┘
                                           │                                │
                    [AI Model Traffic Only]│                                │[All Other Traffic (99.9%)]
       (cloudcode-pa.googleapis.com)       │                                │(Web, YouTube 4K, Steam, Games)
                                           ▼                                ▼
                     ┌───────────────────────────┐             ┌───────────────────────────┐
                     │ Anti-Leak Hosts Pinning   │             │   Direct ISP Connection   │
                     │ (European SNI Relays)     │             │   (Full Gigabit Speed)    │
                     └───────────────────────────┘             └───────────────────────────┘
                                   │                                         │
                 ┌─────────────────┴─────────────────┐                       │
                 ▼                                   ▼                       ▼
   ┌───────────────────────────┐       ┌───────────────────────────┐  ┌───────────────────────────┐
   │ Hetzner DE / Comss NL     │       │ Cloudflare Worker Relay   │  │ Gaming / Local RuNet /    │
   │ (L4 TLS 1.3 SNI Passthr.) │       │ (L7 Header Sanitization)  │  │ Banking & Gosuslugi 100%  │
   └───────────────────────────┘       └───────────────────────────┘  └───────────────────────────┘
                 │                                   │                       │
                 └─────────────────┬─────────────────┘                       │
                                   ▼                                         ▼
                     ┌───────────────────────────┐             ┌───────────────────────────┐
                     │  Google Cloud AI Backend  │             │   Global Internet (0 ms   │
                     │ (Gemini 2.5/3.0 & Claude) │             │     Additional Latency)   │
                     └───────────────────────────┘             └───────────────────────────┘
```

### 🔑 Architectural Highlights:
- **Anti-Leak Hosts Pinning (L4):** Deterministic DNS isolation preventing Windows `Dnscache` fallback to Russian GFE clusters (`172.217.x.x`).
- **10-Byte Length-Invariant PE Patch:** Modifies `language_server.exe` (`ineligible` ➔ `inexigible`, exactly 10 bytes: `0x69 0x6E 0x65 0x6C 0x69 0x67 0x69 0x62 0x6C 0x65` ➔ `0x69 0x6E 0x65 0x78 0x69 0x67 0x69 0x62 0x6C 0x65`), maintaining PE section tables, relocation offsets, and Protobuf alignment.
- **Smart Auto-Failover Watchdog:** Daemon thread monitoring port 443 TLS health every 20s with sub-second automated failover.
- **Zero External Dependencies:** Built entirely on Python 3.10+ standard library (`socket`, `ssl`, `ctypes`, `concurrent.futures`, `tkinter`).
- **FastMCP Control Plane:** Exposes `@mcp.tool()` interfaces for AI-driven orchestration, live telemetry, and automated remediation.

---

## 🛠️ Technical Arsenal & Core Matrix

### 💻 Systems & Low-Level Engineering
<p>
  <img src="https://img.shields.io/badge/Python_3.10+-1E1E2E?style=for-the-badge&logo=python&logoColor=3776AB" alt="Python" />
  <img src="https://img.shields.io/badge/C%2B%2B_20-1E1E2E?style=for-the-badge&logo=c%2B%2B&logoColor=00599C" alt="C++" />
  <img src="https://img.shields.io/badge/Rust-1E1E2E?style=for-the-badge&logo=rust&logoColor=DEA584" alt="Rust" />
  <img src="https://img.shields.io/badge/C_Lang-1E1E2E?style=for-the-badge&logo=c&logoColor=A8B9CC" alt="C" />
  <img src="https://img.shields.io/badge/x86__64_Assembly-1E1E2E?style=for-the-badge&logo=assemblyscript&logoColor=89B4FA" alt="x86_64" />
  <img src="https://img.shields.io/badge/Windows_API_(Win32)-1E1E2E?style=for-the-badge&logo=windows&logoColor=0078D6" alt="WinAPI" />
  <img src="https://img.shields.io/badge/PE%2FCOFF_Internals-1E1E2E?style=for-the-badge&logo=windows-terminal&logoColor=CBA6F7" alt="PE/COFF" />
  <img src="https://img.shields.io/badge/Winsock2-1E1E2E?style=for-the-badge&logo=gnubash&logoColor=A6E3A1" alt="Winsock2" />
  <img src="https://img.shields.io/badge/Linux_Internals-1E1E2E?style=for-the-badge&logo=linux&logoColor=FCC624" alt="Linux" />
</p>

### 🌐 Networking, Protocols & Routing
<p>
  <img src="https://img.shields.io/badge/TCP%2FIP_Stack-1E1E2E?style=for-the-badge&logo=wireshark&logoColor=89B4FA" alt="TCP/IP" />
  <img src="https://img.shields.io/badge/TLS_1.3_%26_SNI-1E1E2E?style=for-the-badge&logo=letsencrypt&logoColor=A6E3A1" alt="TLS 1.3" />
  <img src="https://img.shields.io/badge/DNS_%2F_DoH_%2F_NRPT-1E1E2E?style=for-the-badge&logo=cloudflare&logoColor=F38020" alt="DNS/NRPT" />
  <img src="https://img.shields.io/badge/FastMCP_(MCP)-1E1E2E?style=for-the-badge&logo=fastapi&logoColor=10B981" alt="FastMCP" />
  <img src="https://img.shields.io/badge/gRPC_%26_Protobuf-1E1E2E?style=for-the-badge&logo=grpc&logoColor=4285F4" alt="gRPC" />
  <img src="https://img.shields.io/badge/HTTP%2F2_%26_HTTP%2F3-1E1E2E?style=for-the-badge&logo=nginx&logoColor=009639" alt="HTTP/3" />
  <img src="https://img.shields.io/badge/BGP_%26_Anycast-1E1E2E?style=for-the-badge&logo=cisco&logoColor=1BA0D7" alt="BGP" />
  <img src="https://img.shields.io/badge/Socket_Programming-1E1E2E?style=for-the-badge&logo=gnubash&logoColor=FAB387" alt="Sockets" />
</p>

### 🧠 AI Engineering, LLMs & Model Context Protocol
<p>
  <img src="https://img.shields.io/badge/Google_Gemini_2.5%2F3.0-1E1E2E?style=for-the-badge&logo=google&logoColor=8E75C2" alt="Gemini" />
  <img src="https://img.shields.io/badge/Claude_3.5%2F3.7_Sonnet-1E1E2E?style=for-the-badge&logo=anthropic&logoColor=D97706" alt="Claude" />
  <img src="https://img.shields.io/badge/Model_Context_Protocol-1E1E2E?style=for-the-badge&logo=openai&logoColor=89B4FA" alt="MCP" />
  <img src="https://img.shields.io/badge/LangChain_%2F_LlamaIndex-1E1E2E?style=for-the-badge&logo=chainlink&logoColor=375BD2" alt="LangChain" />
  <img src="https://img.shields.io/badge/PyTorch-1E1E2E?style=for-the-badge&logo=pytorch&logoColor=EE4C2C" alt="PyTorch" />
  <img src="https://img.shields.io/badge/Agentic_Workflows-1E1E2E?style=for-the-badge&logo=probot&logoColor=A6E3A1" alt="Agents" />
</p>

### 🎮 Game Engines & Graphics Programming
<p>
  <img src="https://img.shields.io/badge/Godot_Engine_4.x-1E1E2E?style=for-the-badge&logo=godotengine&logoColor=478CBF" alt="Godot 4" />
  <img src="https://img.shields.io/badge/Unity_3D-1E1E2E?style=for-the-badge&logo=unity&logoColor=FFFFFF" alt="Unity" />
  <img src="https://img.shields.io/badge/GLSL_%2F_HLSL_Shaders-1E1E2E?style=for-the-badge&logo=opengl&logoColor=5586A4" alt="Shaders" />
  <img src="https://img.shields.io/badge/Vulkan_API-1E1E2E?style=for-the-badge&logo=vulkan&logoColor=A81C1D" alt="Vulkan" />
  <img src="https://img.shields.io/badge/DirectX_12-1E1E2E?style=for-the-badge&logo=windows&logoColor=0078D6" alt="DirectX 12" />
</p>

### ☁️ Cloud, Edge & Infrastructure
<p>
  <img src="https://img.shields.io/badge/Cloudflare_Workers-1E1E2E?style=for-the-badge&logo=cloudflare&logoColor=F38020" alt="Cloudflare" />
  <img src="https://img.shields.io/badge/Docker-1E1E2E?style=for-the-badge&logo=docker&logoColor=2496ED" alt="Docker" />
  <img src="https://img.shields.io/badge/GitHub_Actions-1E1E2E?style=for-the-badge&logo=githubactions&logoColor=2088FF" alt="CI/CD" />
  <img src="https://img.shields.io/badge/Hetzner_Cloud-1E1E2E?style=for-the-badge&logo=hetzner&logoColor=D50C2D" alt="Hetzner" />
  <img src="https://img.shields.io/badge/PowerShell_Core-1E1E2E?style=for-the-badge&logo=powershell&logoColor=5391FE" alt="PowerShell" />
</p>

### 🔍 Security, Forensics & Reverse Engineering
<p>
  <img src="https://img.shields.io/badge/Ghidra-1E1E2E?style=for-the-badge&logo=nsa&logoColor=A6E3A1" alt="Ghidra" />
  <img src="https://img.shields.io/badge/x64dbg-1E1E2E?style=for-the-badge&logo=gnubash&logoColor=89B4FA" alt="x64dbg" />
  <img src="https://img.shields.io/badge/Sysinternals-1E1E2E?style=for-the-badge&logo=microsoft&logoColor=00A4EF" alt="Sysinternals" />
  <img src="https://img.shields.io/badge/Wireshark-1E1E2E?style=for-the-badge&logo=wireshark&logoColor=1679A7" alt="Wireshark" />
  <img src="https://img.shields.io/badge/Binary_Diffing-1E1E2E?style=for-the-badge&logo=git&logoColor=F05032" alt="Binary Diffing" />
</p>

---

## 🔬 Selected Research & Open-Source Projects

| Project | Domain / Tech | Description | Status |
| :--- | :--- | :--- | :--- |
| **[Antigravity Unlocker 2.0](https://github.com/Renkiy/antigravity-unlocker)** | `Python` `WinAPI` `TLS 1.3` `PE` | Autonomous zero-VPN bypass suite for Google Antigravity & Gemini with L4 hosts pinning, length-preserving PE patcher, and auto-watchdog. | `Production Ready` |
| **[FastMCP Windows Sentinel](https://github.com/Renkiy)** | `FastMCP` `Python` `Winsock2` | Model Context Protocol server enabling LLM agents to perform zero-overhead Windows network diagnostics, NRPT rules auditing, and latency scoring. | `Active` |
| **[Userland SNI Router Core](https://github.com/Renkiy)** | `C++20` `Winsock` `Asio` | Zero-driver, anti-cheat safe L4 SNI reverse router designed for zero-latency multiplayer and selective traffic forwarding. | `Active` |
| **[Godot 4 High-Perf ECS Engine](https://github.com/Renkiy)** | `Godot 4` `C++` `GLSL` | Data-oriented architecture framework for Godot 4 with custom spatial partitioning and compute shader particle systems. | `Open Source` |

---

## 📈 GitHub Telemetry & Activity Metrics

<div align="center">

<table border="0">
  <tr>
    <td width="50%">
      <img src="https://github-readme-stats.vercel.app/api?username=Renkiy&show_icons=true&theme=catppuccin_mocha&hide_border=true&bg_color=1E1E2E&title_color=89B4FA&icon_color=A6E3A1&text_color=CDD6F4" alt="Renkiy's GitHub Stats" width="100%" />
    </td>
    <td width="50%">
      <img src="https://github-readme-streak-stats.herokuapp.com/?user=Renkiy&theme=catppuccin-mocha&hide_border=true&background=1E1E2E&stroke=89B4FA&ring=A6E3A1&fire=F38BA8&currStreakLabel=89B4FA&sideLabels=CDD6F4" alt="Renkiy's GitHub Streak" width="100%" />
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Renkiy&layout=compact&theme=catppuccin_mocha&hide_border=true&bg_color=1E1E2E&title_color=89B4FA&text_color=CDD6F4" alt="Top Languages" width="60%" />
    </td>
  </tr>
</table>

</div>

---

## 🌐 Community & Connection Grid

I am always open to discussing **systems programming, networking architectures, binary security, reverse engineering, and open-source tooling**.

<div align="center">

| Channel | Handle / Link | Purpose |
| :--- | :--- | :--- |
| 💬 **Telegram Direct** | [**@renkiy**](https://t.me/renkiy) | Direct inquiries, technical discussions, collaborations |
| 📢 **Telegram Channel** | [**Renkiy Lab**](https://t.me/renkiy) | Engineering post-mortems, reverse-engineering writeups, release alerts |
| 🐙 **GitHub** | [**@Renkiy**](https://github.com/Renkiy) | Code repositories, issues, PRs, and stars |
| 📧 **Email** | [**contact@renkiy.dev**](mailto:contact@renkiy.dev) | Formal business inquiries and security disclosures |

</div>

<br>

<div align="center">

*"Simplicity is prerequisite for reliability — build surgical systems, optimize the critical path, and keep code open."*

<sub>Crafted with precision • Styled with Catppuccin Mocha • Maintained by <b>Renkiy</b></sub>

</div>
