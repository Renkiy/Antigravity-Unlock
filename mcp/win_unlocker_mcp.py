"""
win_unlocker_mcp.py - FastMCP сервер для автоматизации сетевого анлокера Antigravity
"""
import subprocess
import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("antigravity-unlocker-tools")

@mcp.tool()
def query_nrpt_rules() -> str:
    """Возвращает текущие правила Name Resolution Policy Table (NRPT) Windows."""
    cmd = ["powershell", "-NoProfile", "-Command", "Get-DnsClientNrptRule -ErrorAction SilentlyContinue | Select-Object Namespace, NameServers, Comment | ConvertTo-Json -Depth 3"]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout if res.returncode == 0 else f"Error: {res.stderr}"

@mcp.tool()
def run_diagnostics() -> str:
    """Запускает полную сетевую и бинарную диагностику Antigravity."""
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    diag_script = os.path.join(os.path.dirname(tools_dir), "tools", "diagnostics.py")
    res = subprocess.run(["python", diag_script], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout if res.returncode == 0 else f"Error: {res.stderr}"

@mcp.tool()
def apply_unlock() -> str:
    """Применяет полный комплекс анлока (бинарный патч, NRPT, IPv4 priority)."""
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    unlocker_script = os.path.join(os.path.dirname(tools_dir), "tools", "unlocker.py")
    res = subprocess.run(["python", unlocker_script, "--apply"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout if res.returncode == 0 else f"Error: {res.stderr}"

@mcp.tool()
def restore_system() -> str:
    """Выполняет полный откат всех изменений системы в исходное состояние."""
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    unlocker_script = os.path.join(os.path.dirname(tools_dir), "tools", "unlocker.py")
    res = subprocess.run(["python", unlocker_script, "--restore"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return res.stdout if res.returncode == 0 else f"Error: {res.stderr}"

if __name__ == "__main__":
    mcp.run()
