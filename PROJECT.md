# Project: Antigravity Unlocker Publication & Branding Ecosystem

## Architecture & System Overview
Antigravity Unlocker is a zero-VPN, zero-dependency, ultra-lightweight Windows bypass and unblocking ecosystem for Google Antigravity and AI services. It employs a multi-tiered architecture:
- **L4 Routing & DNS Pinning (`tools/pin_hosts.py`, `tools/proxy_manager.py`)**: Resolves SNI endpoints against clean foreign Geo-IPs (Frankfurt Hetzner, Amsterdam Comss), pins them to Windows `%SystemRoot%\System32\drivers\etc\hosts` with atomic rollback markers, and flushes DNS caches (`DnsFlushResolverCache` via `ipconfig /flushdns`).
- **Binary Language Server Patching (`tools/unlocker_core.py`)**: 10-byte length-invariant string substitution (`ineligible` -> `inexigible`) across PE binaries and protobuf schemas to bypass client-side geo-checks without breaking binary offset tables or cryptographic hash structures.
- **Dynamic Proxy Health & Watchdog (`tools/proxy_manager.py`)**: Multi-threaded SNI latency and handshake probe with continuous scoring, failover, and background daemon thread (`ProxyWatchdog`) monitoring connections every 20s.
- **L7 Cloudflare Edge Relay (`cloudflare_worker.js`)**: Serverless edge proxy that strips Russian geolocation headers and transforms regional response payloads (`"status": "ALLOWED"`).
- **Safety & Management Core (`tools/backup_manager.py`, `tools/diagnostics.py`, `installer_gui.py`, `gui_app.py`)**: SHA-256 backup manifests, 1-click restore, Catppuccin Mocha themed Tkinter GUI, and automated Windows registry / shortcut management.

## Feature Inventory
| # | Feature / Deliverable | Description | Milestone | Source |
|---|---|---|---|---|
| 1 | Comparison Matrix | Multi-dimensional technical matrix comparing 5 tool paradigms across 8+ criteria with architectural rationales | M1 | survey |
| 2 | Habr Deep-Dive Article | Hardcore engineering article covering the August 24-25 incident, NRPT cascades, PE patching, SNI scoring, watchdog, and benchmarks | M2 | survey |
| 3 | VC.ru Business Article | ROI and productivity-driven case study on developer downtime, team unblocking, zero security risk, and 1-click deployment | M3 | survey |
| 4 | DTF.ru Creator/Community Article | Gamer/Creator friendly article focusing on Discord, Steam, YouTube 4K, AI coding, zero-lag gaming, and Catppuccin GUI | M4 | survey |
| 5 | Renkiy GitHub Profile README | Elite dark-mode GitHub profile README with SVG badges, Telegram links, tech stack matrix, and Antigravity 2.0 spotlight | M5 | survey |
| 6 | Quality Verification & Audit | Multi-agent review (2 Reviewers, 2 Challengers, 1 Forensic Auditor) verifying zero placeholders, technical veracity, and GFM compliance | M6 | survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|---|---|---|---|
| M1 | Technical Comparison Matrix | `docs/promo/comparison_matrix.md` | Survey | DONE |
| M2 | Habr Technical Deep-Dive | `docs/promo/habr_article.md` | Survey, M1 | DONE |
| M3 | VC.ru Business/Productivity | `docs/promo/vc_article.md` | Survey, M1 | DONE |
| M4 | DTF.ru Creator/Community | `docs/promo/dtf_article.md` | Survey, M1 | DONE |
| M5 | Personal GitHub Profile README | `docs/promo/profile_readme/README.md` | Survey | DONE |
| M6 | Independent Review & Audit | Reviewers, Challengers, Auditor | M1, M2, M3, M4, M5 | DONE |

## Code Layout & Deliverables Structure
- `docs/promo/comparison_matrix.md` (Technical comparison against VPN, GoodbyeDPI/Zapret, Proxies, Cloudflare WARP)
- `docs/promo/habr_article.md` (Russian language Habr technical deep-dive)
- `docs/promo/vc_article.md` (Russian language VC.ru business/productivity article)
- `docs/promo/dtf_article.md` (Russian language DTF.ru creator/community article)
- `docs/promo/profile_readme/README.md` (GitHub profile README for Renkiy)

## Interface Contracts & Guidelines
- **Zero Placeholder Policy**: Verified 100% complete prose, zero `[TODO]`, zero placeholders across all files.
- **Image Placement Instructions**: Explicit markdown callout blocks with visual specifications, alt text, and captions across all 3 articles.
- **SEO Metadata**: Full SEO YAML/markdown headers across all 3 articles.
- **Code Fidelity**: 100% fidelity with `tools/unlocker_core.py`, `tools/pin_hosts.py`, `tools/backup_manager.py`, `tools/proxy_manager.py`, `tools/diagnostics.py`, `gui_app.py`, `cloudflare_worker.js`.
