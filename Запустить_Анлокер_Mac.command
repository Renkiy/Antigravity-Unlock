#!/usr/bin/env bash
# Antigravity Unlocker — Двойной клик для запуска на macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

chmod +x unlock.sh 2>/dev/null || true
./unlock.sh
