import os
import sys
import time
import shutil
import webbrowser
from typing import Dict, Any, List

try:
    from .collector import SystemCollector
except ImportError:
    from collector import SystemCollector

try:
    from cyber_pulse.app import start_server_background
except ImportError:
    try:
        from app import start_server_background
    except ImportError:
        start_server_background = None

# Terminal Control Codes
C_HIDE = "\033[?25l"
C_SHOW = "\033[?25h"
ALT_ENTER = "\033[?1049h"
ALT_EXIT = "\033[?1049l"
HOME = "\033[H"
CLEAR_EOL = "\033[K"
CLEAR_EOS = "\033[J"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# Cyberpunk Themes Definition
THEMES = {
    "1": {
        "name": "NIGHT CITY 2077",
        "primary": "\033[38;2;0;240;255m",      # Cyber Cyan
        "secondary": "\033[38;2;255;0;128m",   # Neon Pink
        "accent": "\033[38;2;252;238;10m",     # Cyber Yellow
        "ok": "\033[38;2;0;255;102m",          # Neon Green
        "warn": "\033[38;2;252;238;10m",       # Amber
        "alert": "\033[38;2;255;34;85m",       # Neon Red
        "muted": "\033[38;2;90;105;130m",      # Steel Gray
        "bright": "\033[38;2;235;245;255m"     # Pure White
    },
    "2": {
        "name": "MATRIX CODE",
        "primary": "\033[38;2;0;255;102m",     # Phosphor Green
        "secondary": "\033[38;2;120;255;160m", # Light Mint
        "accent": "\033[38;2;0;200;80m",       # Dark Green
        "ok": "\033[38;2;0;255;102m",
        "warn": "\033[38;2;220;255;50m",
        "alert": "\033[38;2;255;80;60m",
        "muted": "\033[38;2;40;90;50m",
        "bright": "\033[38;2;200;255;220m"
    },
    "3": {
        "name": "SYNTHWAVE 1984",
        "primary": "\033[38;2;255;45;149m",    # Hot Pink
        "secondary": "\033[38;2;155;77;255m",  # Neon Purple
        "accent": "\033[38;2;255;170;0m",      # Sunset Orange
        "ok": "\033[38;2;0;240;255m",          # Neon Cyan
        "warn": "\033[38;2;255;170;0m",
        "alert": "\033[38;2;255;0;80m",
        "muted": "\033[38;2;110;80;130m",
        "bright": "\033[38;2;255;235;250m"
    },
    "4": {
        "name": "ARASAKA BLOOD OPS",
        "primary": "\033[38;2;255;20;50m",     # Crimson Red
        "secondary": "\033[38;2;255;100;100m", # Light Coral
        "accent": "\033[38;2;250;210;50m",     # Cyber Gold
        "ok": "\033[38;2;240;240;240m",        # Pure Titanium
        "warn": "\033[38;2;255;140;0m",
        "alert": "\033[38;2;255;0;0m",
        "muted": "\033[38;2;120;40;40m",
        "bright": "\033[38;2;255;255;255m"
    }
}

BANNER = f"""{THEMES['1']['primary']}{BOLD}
  ___ _   _ ___ ___ ___     _  _ _   _ ___  
 / __| | | | _ ) __| _ \\   | || | | | |   \\ 
| (__| |_| | _ \\ _||   /---| __ | |_| | |) |
 \\___|\\__, |___/___|_|_\\   |_||_|\\__,_|___/ 
      |___/                                 {RESET}
"""


def setup_console():
    """Configure Windows console: disable QuickEdit to prevent freeze on click, enable VT processing."""
    old_in_mode = None
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            hIn = kernel32.GetStdHandle(-10)   # STD_INPUT_HANDLE
            hOut = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

            in_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(hIn, ctypes.byref(in_mode)):
                old_in_mode = in_mode.value
                # Disable ENABLE_QUICK_EDIT_MODE (0x0040), set ENABLE_EXTENDED_FLAGS (0x0080)
                new_in = (in_mode.value & ~0x0040) | 0x0080
                kernel32.SetConsoleMode(hIn, new_in)

            out_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode)):
                # ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
                kernel32.SetConsoleMode(hOut, out_mode.value | 0x0004)
        except Exception:
            pass
    return old_in_mode


def restore_console(old_in_mode):
    """Restore console input mode on exit."""
    if sys.platform == "win32" and old_in_mode is not None:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            hIn = kernel32.GetStdHandle(-10)
            kernel32.SetConsoleMode(hIn, old_in_mode)
        except Exception:
            pass


def read_nonblocking_key() -> str:
    """Read single keyboard char non-blocking across Windows & Unix, supporting Unicode & IME."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                if msvcrt.kbhit():
                    msvcrt.getwch()  # Consume scan code for special/extended keys
                return ""
            return ch
        return ""
    else:
        import select
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            return sys.stdin.read(1)
        return ""


def make_bar(percent: float, length: int, theme: dict, color_override: str = None) -> str:
    clamped = max(0.0, min(100.0, percent))
    filled_len = int((clamped / 100.0) * length)
    empty_len = length - filled_len

    if color_override:
        col = color_override
    else:
        if clamped >= 85:
            col = theme["alert"]
        elif clamped >= 60:
            col = theme["warn"]
        else:
            col = theme["primary"]

    return f"{col}" + ("#" * filled_len) + f"{theme['muted']}" + ("." * empty_len) + f"{RESET}"


def format_uptime(uptime_sec: int) -> str:
    days = uptime_sec // 86400
    hours = (uptime_sec % 86400) // 3600
    mins = (uptime_sec % 3600) // 60
    secs = uptime_sec % 60
    if days > 0:
        return f"{days}d {hours:02d}h {mins:02d}m {secs:02d}s"
    return f"{hours:02d}h {mins:02d}m {secs:02d}s"


def generate_report_text(stats: Dict[str, Any]) -> str:
    """Format a comprehensive diagnostic report as plain text for file export."""
    sys_info = stats.get("system", {})
    cpu = stats.get("cpu", {})
    mem = stats.get("memory", {})
    disks = stats.get("disks", {})
    gpus = stats.get("gpus", [])
    net = stats.get("network", {})
    procs = stats.get("processes", [])

    lines = []
    lines.append("=" * 80)
    lines.append("       CYBER_PULSE // NEURAL SYSTEM TELEMETRY DIAGNOSTIC AUDIT REPORT       ")
    lines.append(f"       TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')} | NODE: {sys_info.get('hostname', 'UNKNOWN')}")
    lines.append("=" * 80 + "\n")

    lines.append("[ SYSTEM & HOST PROFILE ]")
    lines.append(f"  Hostname       : {sys_info.get('hostname')}")
    lines.append(f"  Operating Sys  : {sys_info.get('os')} ({sys_info.get('arch')})")
    lines.append(f"  Kernel Version : {sys_info.get('os_version')}")
    lines.append(f"  System Uptime  : {format_uptime(sys_info.get('uptime_sec', 0))}")
    lines.append(f"  Python Runtime : {sys_info.get('python_version')}")
    lines.append("")

    lines.append("[ PROCESSOR (CPU) TELEMETRY ]")
    lines.append(f"  Total Load     : {cpu.get('total_percent', 0.0)}%")
    lines.append(f"  Topology       : {cpu.get('cores_physical', 0)} Physical Cores / {cpu.get('cores_logical', 0)} Logical Threads")
    lines.append(f"  Frequency      : Current {cpu.get('freq_current_mhz', 0.0)} MHz (Max {cpu.get('freq_max_mhz', 0.0)} MHz)")
    per_core = cpu.get("per_core", [])
    if per_core:
        core_strs = [f"C{i:02d}: {val:4.1f}%" for i, val in enumerate(per_core)]
        lines.append("  Core Matrix    : " + " | ".join(core_strs[:8]))
        if len(per_core) > 8:
            lines.append("                   " + " | ".join(core_strs[8:16]))
    lines.append("")

    lines.append("[ MEMORY & VIRTUAL STORAGE ]")
    lines.append(f"  Physical RAM   : {mem.get('used_gb', 0.0)} / {mem.get('total_gb', 0.0)} GB ({mem.get('percent', 0.0)}%)")
    lines.append(f"  Available RAM  : {mem.get('available_gb', 0.0)} GB Free")
    lines.append(f"  Swap Memory    : {mem.get('swap_used_gb', 0.0)} / {mem.get('swap_total_gb', 0.0)} GB ({mem.get('swap_percent', 0.0)}%)")
    lines.append("")

    lines.append("[ STORAGE ARRAYS & PARTITIONS ]")
    for d in disks.get("partitions", []):
        lines.append(f"  Mount [{d.get('mountpoint')}]: {d.get('used_gb', 0.0)} / {d.get('total_gb', 0.0)} GB ({d.get('percent', 0.0)}%) [Free: {d.get('free_gb', 0.0)} GB, Type: {d.get('fstype', '')}]")
    lines.append(f"  Disk Throughput: Read {disks.get('read_mb_sec', 0.0)} MB/s | Write {disks.get('write_mb_sec', 0.0)} MB/s")
    lines.append("")

    if gpus:
        lines.append("[ ACCELERATOR (GPU) TELEMETRY ]")
        for g in gpus:
            lines.append(f"  Device Name    : {g.get('name')}")
            lines.append(f"  GPU Load       : {g.get('utilization_gpu', 0.0)}% | Temp: {g.get('temperature', 0.0)}C | Power: {g.get('power_draw', 0.0)}W")
            lines.append(f"  VRAM Usage     : {g.get('memory_used', 0.0)} / {g.get('memory_total', 0.0)} MB (Free: {g.get('memory_free', 0.0)} MB)")
        lines.append("")

    lines.append("[ NETWORK TELEMETRY RADAR ]")
    lines.append(f"  Downlink RX    : {net.get('rx_kb_sec', 0.0)} KB/s (Total {net.get('total_recv_mb', 0.0)} MB)")
    lines.append(f"  Uplink TX      : {net.get('tx_kb_sec', 0.0)} KB/s (Total {net.get('total_sent_mb', 0.0)} MB)")
    lines.append(f"  Connections    : {net.get('connections_established', 0)} Established / {net.get('connections_total', 0)} Total")
    lines.append("")

    lines.append("[ TOP ACTIVE SURVEILLANCE TARGETS ]")
    lines.append("  PID     NAME                     CPU%    MEM%    RSS(MB)    STATUS")
    lines.append("  " + ("-" * 68))
    for p in procs[:12]:
        pname = p.get('name', '')[:23].ljust(23)
        lines.append(f"  {p.get('pid', 0):6d}  {pname}  {p.get('cpu_percent', 0.0):5.1f}  {p.get('memory_percent', 0.0):5.1f}  {p.get('memory_rss_mb', 0.0):9.1f}    {p.get('status', '')}")
    lines.append("\n" + "=" * 80)
    lines.append("                        [ END OF TELEMETRY REPORT ]                             ")
    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


def export_report_file(stats: Dict[str, Any], filename: str = "cyber_pulse_report.txt") -> str:
    """Export system diagnostic report to a text file."""
    try:
        report_text = generate_report_text(stats)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        return os.path.abspath(filename)
    except Exception as e:
        return f"Report generation failed: {e}"


def render_report_screen(stats: Dict[str, Any], theme_key: str, status_msg: str, input_buffer: str, term_width: int, term_height: int) -> str:
    """Render full-screen diagnostic report card overlay."""
    theme = THEMES.get(theme_key, THEMES["1"])
    pri = theme["primary"]
    sec = theme["secondary"]
    acc = theme["accent"]
    ok = theme["ok"]
    muted = theme["muted"]
    bright = theme["bright"]
    warn = theme["warn"]

    sys_info = stats.get("system", {})
    cpu = stats.get("cpu", {})
    mem = stats.get("memory", {})
    disks = stats.get("disks", {})
    gpus = stats.get("gpus", [])
    net = stats.get("network", {})
    procs = stats.get("processes", [])

    width = max(78, min(term_width, 100))
    border = f"{muted}+" + ("-" * (width - 2)) + f"+{RESET}"

    lines = []
    lines.append(f"{pri}{BOLD}  ___ _   _ ___ ___ ___     _  _ _   _ ___  {RESET} {sec}// SYSTEM DIAGNOSTIC REPORT{RESET}")
    lines.append(f"{pri}{BOLD} / __| | | | _ ) __| _ \\   | || | | | |   \\ {RESET} {muted}TIME:{RESET} {bright}{time.strftime('%H:%M:%S')}{RESET}")
    lines.append(f"{pri}{BOLD}| (__| |_| | _ \\ _||   /---| __ | |_| | |) |{RESET} {acc}[ AUDIT COMPLETE ]{RESET}")
    lines.append(f"{pri}{BOLD} \\___|\\__, |___/___|_|_\\   |_||_|\\__,_|___/ {RESET}")
    lines.append(f"{pri}{BOLD}      |___/                                 {RESET}")

    lines.append(border)
    lines.append(f"  {bright}NODE:{RESET} {pri}{sys_info.get('hostname')}{RESET}  {bright}OS:{RESET} {sys_info.get('os')}  {bright}UPTIME:{RESET} {acc}{format_uptime(sys_info.get('uptime_sec', 0))}{RESET}")
    lines.append(f"  {bright}CPU:{RESET}  {cpu.get('cores_physical')}P/{cpu.get('cores_logical')}T @ {cpu.get('freq_current_mhz')}MHz | Load: {acc}{cpu.get('total_percent')}%{RESET}")
    lines.append(f"  {bright}RAM:{RESET}  {mem.get('used_gb'):.1f}/{mem.get('total_gb'):.1f} GB ({mem.get('percent')}%) | Free: {ok}{mem.get('available_gb'):.1f} GB{RESET} | Swap: {mem.get('swap_used_gb'):.1f}/{mem.get('swap_total_gb'):.1f} GB")
    
    for p in disks.get("partitions", [])[:2]:
        lines.append(f"  {bright}DISK {p.get('mountpoint')}:{RESET} {p.get('used_gb'):.0f}/{p.get('total_gb'):.0f} GB ({p.get('percent')}%) [Free: {p.get('free_gb'):.0f} GB]")
    lines.append(f"  {bright}DISK I/O:{RESET} Read {pri}{disks.get('read_mb_sec', 0.0):.2f} MB/s{RESET} | Write {sec}{disks.get('write_mb_sec', 0.0):.2f} MB/s{RESET}")

    for g in gpus[:1]:
        lines.append(f"  {bright}GPU:{RESET}  {sec}{g.get('name')}{RESET} | Load: {g.get('utilization_gpu')}% | Temp: {acc}{g.get('temperature')}C{RESET} | VRAM: {g.get('memory_used'):.0f}/{g.get('memory_total'):.0f} MB")

    lines.append(f"  {bright}NET:{RESET}  Downlink: {ok}{net.get('rx_kb_sec'):.1f} KB/s{RESET} | Uplink: {sec}{net.get('tx_kb_sec'):.1f} KB/s{RESET} | Conns: {net.get('connections_established')}")

    lines.append(border)
    lines.append(f"  {pri}TOP PROCESS SNAPSHOT:{RESET}")
    for p in procs[:4]:
        pname = p.get('name', '')[:22].ljust(22)
        lines.append(f"  {bright}{p.get('pid', 0):6d}{RESET}  {pname}  CPU:{p.get('cpu_percent', 0.0):5.1f}%  RAM:{p.get('memory_percent', 0.0):4.1f}% ({p.get('memory_rss_mb', 0.0):6.1f} MB)  {ok}{p.get('status')}{RESET}")

    lines.append(f"{muted}+" + ("=" * (width - 2)) + f"+{RESET}")
    if status_msg:
        lines.append(f"  {acc}{BOLD}>>> {status_msg}{RESET}")
    else:
        lines.append(f"  {bright}[+] REPORT SAVED TO cyber_pulse_report.txt // TYPE 'r', 'back', OR ESC TO RETURN{RESET}")

    lines.append(f"  {muted}Navigation: Type 'r' or 'back' to return | Type 'w' for Web HUD | ESC to Close{RESET}")
    lines.append(f"{muted}+--[ COMMAND INPUT ]" + ("-" * (width - 22)) + f"+{RESET}")
    cursor = f"{acc}?{RESET}"
    max_input_len = max(20, width - 20)
    display_input = input_buffer[-max_input_len:] if len(input_buffer) > max_input_len else input_buffer
    lines.append(f"  {pri}COMMAND >{RESET} {bright}[ {display_input}{cursor} ]{RESET}  {muted}(e.g. r, w, f, 1-4, q, help){RESET}")
    lines.append(border)

    formatted_lines = [line + CLEAR_EOL for line in lines]
    return HOME + "\n".join(formatted_lines) + "\n" + CLEAR_EOS


def render_dashboard(
    stats: Dict[str, Any],
    theme_key: str,
    status_msg: str,
    show_help: bool,
    input_buffer: str = "",
    show_report: bool = False,
    term_width: int = 80,
    term_height: int = 30,
) -> str:
    """Render the interactive cyberpunk telemetry dashboard."""
    if show_report:
        return render_report_screen(stats, theme_key, status_msg, input_buffer, term_width, term_height)

    theme = THEMES.get(theme_key, THEMES["1"])
    pri = theme["primary"]
    sec = theme["secondary"]
    acc = theme["accent"]
    ok = theme["ok"]
    muted = theme["muted"]
    bright = theme["bright"]
    alert = theme["alert"]
    warn = theme["warn"]

    sys_info = stats.get("system", {})
    cpu = stats.get("cpu", {})
    mem = stats.get("memory", {})
    net = stats.get("network", {})
    disks = stats.get("disks", {})
    gpus = stats.get("gpus", [])
    procs = stats.get("processes", [])

    width = max(78, min(term_width, 100))
    border = f"{muted}+" + ("-" * (width - 2)) + f"+{RESET}"

    lines = []

    # Banner (Compact if terminal height is limited)
    compact_mode = term_height < 35
    if compact_mode:
        lines.append(f"{pri}{BOLD}[ CYBER_PULSE // NEURAL_HUD v2.0 ]{RESET} {muted}THEME:{RESET}{acc}{theme['name']}{RESET} {muted}TIME:{RESET}{bright}{time.strftime('%H:%M:%S')}{RESET}")
    else:
        lines.append(f"{pri}{BOLD}  ___ _   _ ___ ___ ___     _  _ _   _ ___  {RESET} {sec}// NEURAL HUD v2.0{RESET}")
        lines.append(f"{pri}{BOLD} / __| | | | _ ) __| _ \\   | || | | | |   \\ {RESET} {muted}THEME:{RESET} {acc}{theme['name']}{RESET}")
        lines.append(f"{pri}{BOLD}| (__| |_| | _ \\ _||   /---| __ | |_| | |) |{RESET} {muted}TIME:{RESET} {bright}{time.strftime('%H:%M:%S')}{RESET}")
        lines.append(f"{pri}{BOLD} \\___|\\__, |___/___|_|_\\   |_||_|\\__,_|___/ {RESET}")
        lines.append(f"{pri}{BOLD}      |___/                                 {RESET}")

    # System Status Protocol
    cpu_pct = cpu.get("total_percent", 0.0)
    mem_pct = mem.get("percent", 0.0)
    if cpu_pct >= 85 or mem_pct >= 85:
        defcon_col = alert
        defcon_txt = "DEFCON 1 // CRITICAL OVERLOAD"
    elif cpu_pct >= 60 or mem_pct >= 70:
        defcon_col = warn
        defcon_txt = "DEFCON 2 // ELEVATED LOAD"
    else:
        defcon_col = ok
        defcon_txt = "DEFCON 4 // NOMINAL OPTIMAL"

    lines.append(f"{muted}+--[ SYSTEM PROTOCOL ]" + ("-" * (width - 24)) + f"+{RESET}")
    lines.append(f"  {bright}NODE:{RESET} {pri}{sys_info.get('hostname')}{RESET}  {bright}OS:{RESET} {sys_info.get('os')}  {bright}UPTIME:{RESET} {acc}{format_uptime(sys_info.get('uptime_sec', 0))}{RESET}")
    lines.append(f"  {bright}STATUS:{RESET} {defcon_col}{BOLD}[ {defcon_txt} ]{RESET}")

    # CPU Telemetry
    lines.append(f"{muted}+--[ NEURAL CPU CORE ]" + ("-" * (width - 24)) + f"+{RESET}")
    bar_len = 24 if compact_mode else 28
    cpu_bar = make_bar(cpu_pct, bar_len, theme)
    lines.append(f"  USAGE: [{cpu_bar}] {bright}{cpu_pct:5.1f}%{RESET}  ({cpu.get('cores_physical', 0)}P / {cpu.get('cores_logical', 0)}T @ {cpu.get('freq_current_mhz', 0)} MHz)")

    per_core = cpu.get("per_core", [])
    if per_core and not compact_mode:
        core_chunks = []
        for i in range(0, min(len(per_core), 8), 4):
            chunk = per_core[i:i+4]
            chunk_str = "  " + "  ".join([f"{muted}C{i+idx:02d}:{RESET}[{make_bar(c, 5, theme)}] {c:3.0f}%" for idx, c in enumerate(chunk)])
            core_chunks.append(chunk_str)
        lines.extend(core_chunks[:2])

    # Memory Matrix
    lines.append(f"{muted}+--[ NEURAL MEMORY MATRIX ]" + ("-" * (width - 29)) + f"+{RESET}")
    ram_bar = make_bar(mem_pct, bar_len, theme)
    lines.append(f"  RAM:   [{ram_bar}] {bright}{mem_pct:5.1f}%{RESET}  {mem.get('used_gb', 0):.1f}/{mem.get('total_gb', 0):.1f} GB  ({mem.get('available_gb', 0):.1f} GB Free)")
    if not compact_mode:
        swap_bar = make_bar(mem.get("swap_percent", 0.0), bar_len, theme, color_override=sec)
        lines.append(f"  SWAP:  [{swap_bar}] {bright}{mem.get('swap_percent', 0):5.1f}%{RESET}  {mem.get('swap_used_gb', 0):.1f}/{mem.get('swap_total_gb', 0):.1f} GB")

    # GPU
    if gpus:
        lines.append(f"{muted}+--[ NEURAL ACCELERATOR (GPU) ]" + ("-" * (width - 33)) + f"+{RESET}")
        for gpu in gpus[:1]:
            gpu_bar = make_bar(gpu.get("utilization_gpu", 0.0), 16, theme, color_override=sec)
            lines.append(f"  {sec}{gpu.get('name')[:26]}{RESET} [{gpu_bar}] {gpu.get('utilization_gpu', 0):3.0f}%  TEMP: {acc}{gpu.get('temperature', 0):.0f}C{RESET}  VRAM: {gpu.get('memory_used', 0):.0f}/{gpu.get('memory_total', 0):.0f}MB")

    # Storage & Disks
    lines.append(f"{muted}+--[ STORAGE ARRAYS & DISK I/O ]" + ("-" * (width - 33)) + f"+{RESET}")
    disk_count = 1 if compact_mode else 2
    for p in disks.get("partitions", [])[:disk_count]:
        p_bar = make_bar(p.get("percent", 0.0), 14, theme, color_override=acc)
        lines.append(f"  {bright}{p.get('mountpoint', '')[:4]:4s}{RESET} [{p_bar}] {p.get('percent', 0):4.1f}%  {p.get('used_gb', 0):.0f}/{p.get('total_gb', 0):.0f}GB (Free: {p.get('free_gb', 0):.0f}GB)")
    lines.append(f"  I/O:   READ: {pri}{disks.get('read_mb_sec', 0.0):5.2f} MB/s{RESET}   WRITE: {sec}{disks.get('write_mb_sec', 0.0):5.2f} MB/s{RESET}")

    # Network Radar
    lines.append(f"{muted}+--[ NETWORK RADAR ]" + ("-" * (width - 21)) + f"+{RESET}")
    lines.append(f"  DOWNLINK: {ok}{net.get('rx_kb_sec', 0.0):7.1f} KB/s{RESET} ({net.get('total_recv_mb', 0)} MB)   UPLINK: {sec}{net.get('tx_kb_sec', 0.0):7.1f} KB/s{RESET} ({net.get('total_sent_mb', 0)} MB)   CONNS: {bright}{net.get('connections_established', 0)}{RESET}")

    # Top Threat Surveillance
    lines.append(f"{muted}+--[ TOP SURVEILLANCE TARGETS ]" + ("-" * (width - 31)) + f"+{RESET}")
    lines.append(f"  {pri}PID     NAME                    CPU%   MEM%    RSS(MB)   STATUS{RESET}")
    proc_count = 3 if compact_mode else 4
    for proc in procs[:proc_count]:
        pname = proc.get("name", "")[:22].ljust(22)
        lines.append(f"  {bright}{proc.get('pid', 0):6d}{RESET}  {pname}  {proc.get('cpu_percent', 0.0):5.1f}  {proc.get('memory_percent', 0.0):5.1f}  {proc.get('memory_rss_mb', 0.0):8.1f}   {ok}{proc.get('status', '')}{RESET}")

    # Help overlay (if toggled)
    if show_help:
        lines.append(f"{muted}+--[ COMMAND HELP MATRIX ]" + ("-" * (width - 27)) + f"+{RESET}")
        lines.append(f"  {acc}[W]{RESET} or 'web'     >> Start Web HUD server and launch in default browser")
        lines.append(f"  {ok}[R]{RESET} or 'report'  >> Generate full diagnostic telemetry audit report")
        lines.append(f"  {sec}[F]{RESET} or 'flush'   >> Purge memory working sets to free RAM")
        lines.append(f"  {pri}[1-4]{RESET} or 'theme' >> Switch themes: 1=NightCity 2=Matrix 3=Synthwave 4=Arasaka")
        lines.append(f"  {bright}[H]{RESET} or 'help'    >> Toggle this command matrix help card")
        lines.append(f"  {alert}[Q]{RESET} or 'quit'    >> Exit and disconnect neural link (or press ESC)")
        lines.append(f"  'kill <pid>'       >> Terminate target process by PID")

    # Notification bar
    lines.append(f"{muted}+" + ("=" * (width - 2)) + f"+{RESET}")
    if status_msg:
        lines.append(f"  {acc}{BOLD}>>> {status_msg}{RESET}")
    else:
        lines.append(f"  {DIM}SYSTEM TELEMETRY SYNCHRONIZED // STATUS: ONLINE{RESET}")

    # Hotkey bar
    lines.append(f"  {muted}Hotkeys: {pri}[1-4]{muted}Theme  {sec}[F]{muted}Flush  {acc}[W]{muted}Web  {ok}[R]{muted}Report  {bright}[H]{muted}Help  {alert}[Q/ESC]{muted}Quit{RESET}")

    # Small text input box at the very bottom
    lines.append(f"{muted}+--[ COMMAND INPUT ]" + ("-" * (width - 22)) + f"+{RESET}")
    cursor = f"{acc}?{RESET}"
    max_input_len = max(20, width - 20)
    display_input = input_buffer[-max_input_len:] if len(input_buffer) > max_input_len else input_buffer
    lines.append(f"  {pri}COMMAND >{RESET} {bright}[ {display_input}{cursor} ]{RESET}  {muted}(e.g. w, r, f, 1-4, q, help){RESET}")
    lines.append(border)

    # Format buffer with CLEAR_EOL for zero-flicker
    formatted_lines = [line + CLEAR_EOL for line in lines]
    return HOME + "\n".join(formatted_lines) + "\n" + CLEAR_EOS


def run_cli_hud(theme: str = "1", interval: float = 1.0):
    """Launch interactive cyberpunk terminal HUD."""
    os.system("")  # Enable ANSI in Windows terminal
    old_console_mode = setup_console()

    current_theme = theme if theme in THEMES else "1"
    status_msg = "NEURAL LINK ESTABLISHED // TYPE 'w', 'r', 'f', '1-4', OR 'help'"
    status_time = time.time()
    show_help = False
    show_report = False
    input_buffer = ""

    # Switch to Alternate Screen Buffer and hide cursor
    sys.stdout.write(ALT_ENTER + C_HIDE + HOME)
    sys.stdout.flush()

    # Immediate initialization splash screen so user never sees a frozen/black window
    init_splash = (
        HOME +
        f"{THEMES[current_theme]['primary']}{BOLD}\n"
        f"  ___ _   _ ___ ___ ___     _  _ _   _ ___  \n"
        f" / __| | | | _ ) __| _ \\   | || | | | |   \\ \n"
        f"| (__| |_| | _ \\ _||   /---| __ | |_| | |) |\n"
        f" \\___|\\__, |___/___|_|_\\   |_||_|\\__,_|___/ \n"
        f"      |___/                                 {RESET}\n"
        f" {THEMES[current_theme]['secondary']}// NEURAL CYBERNETIC SYSTEM MONITOR CLI v2.0{RESET}\n\n"
        f"  {THEMES[current_theme]['ok']}[*] INITIALIZING TELEMETRY SENSORS & DAEMON LINK...{RESET}\n"
        f"  {THEMES[current_theme]['muted']}[========================================]{RESET}\n"
        + CLEAR_EOS
    )
    sys.stdout.write(init_splash)
    sys.stdout.flush()

    collector = SystemCollector()

    try:
        last_refresh = 0.0
        last_stats = collector.get_stats()
        force_redraw = True

        while True:
            now = time.time()

            # Poll keyboard events non-blocking
            key = read_nonblocking_key()
            if key:
                if key in ('\r', '\n'):
                    cmd = input_buffer.strip()
                    input_buffer = ""
                    if cmd:
                        cmd_lower = cmd.lower()
                        if cmd_lower in ("q", "quit", "exit"):
                            break
                        elif cmd_lower in ("w", "web"):
                            if start_server_background:
                                start_server_background(host="0.0.0.0", port=8888)
                            webbrowser.open("http://127.0.0.1:8888")
                            status_msg = "WEB HUD ONLINE // LAUNCHED: http://127.0.0.1:8888"
                            status_time = now
                        elif cmd_lower in ("r", "report"):
                            show_report = not show_report
                            if show_report:
                                r_path = export_report_file(last_stats)
                                status_msg = f"DIAGNOSTIC REPORT GENERATED // SAVED: {os.path.basename(r_path)}"
                            else:
                                status_msg = "RETURNED TO REAL-TIME HUD DASHBOARD"
                            status_time = now
                        elif cmd_lower in ("back", "return"):
                            if show_report:
                                show_report = False
                                status_msg = "RETURNED TO REAL-TIME HUD DASHBOARD"
                                status_time = now
                        elif cmd_lower in ("f", "flush"):
                            res = collector.purge_memory()
                            status_msg = res.get("message", "MEMORY PURGED")
                            status_time = now
                        elif cmd_lower in ("1", "2", "3", "4"):
                            current_theme = cmd_lower
                            status_msg = f"THEME SWITCHED TO: {THEMES[cmd_lower]['name']}"
                            status_time = now
                        elif cmd_lower.startswith("theme "):
                            t_arg = cmd_lower.split()[-1]
                            if t_arg in THEMES:
                                current_theme = t_arg
                                status_msg = f"THEME SWITCHED TO: {THEMES[t_arg]['name']}"
                            else:
                                status_msg = "INVALID THEME: SELECT 1, 2, 3, OR 4"
                            status_time = now
                        elif cmd_lower in ("?", "h", "help"):
                            show_help = not show_help
                            status_msg = "HELP DISPLAY TOGGLED" if show_help else ""
                            status_time = now
                        elif cmd_lower.startswith("kill "):
                            pid_str = cmd_lower.split()[-1]
                            try:
                                pid = int(pid_str)
                                res = collector.terminate_process(pid)
                                status_msg = res.get("message", f"PROCESS {pid} TERMINATED")
                            except ValueError:
                                status_msg = f"INVALID PID: {pid_str}"
                            status_time = now
                        elif cmd_lower in ("cls", "clear"):
                            status_msg = ""
                        else:
                            status_msg = f"UNKNOWN COMMAND: '{cmd}' // TYPE 'help' OR '?' FOR SHORTCUTS"
                            status_time = now
                    force_redraw = True

                elif key in ('\x08', '\x7f'):  # Backspace
                    if input_buffer:
                        input_buffer = input_buffer[:-1]
                        force_redraw = True

                elif key == '\x1b':  # ESC
                    if input_buffer:
                        input_buffer = ""
                        force_redraw = True
                    elif show_report:
                        show_report = False
                        status_msg = "RETURNED TO REAL-TIME HUD DASHBOARD"
                        status_time = now
                        force_redraw = True
                    elif show_help:
                        show_help = False
                        force_redraw = True
                    else:
                        break

                elif key.isprintable():
                    input_buffer += key
                    force_redraw = True

            # Auto-expire status message after 5 seconds
            if now - status_time > 5.0 and status_msg:
                status_msg = ""
                force_redraw = True

            # Periodic stats refresh
            if now - last_refresh >= interval:
                last_stats = collector.get_stats()
                last_refresh = now
                force_redraw = True

            if force_redraw:
                term_size = shutil.get_terminal_size((80, 25))
                output = render_dashboard(
                    last_stats,
                    current_theme,
                    status_msg,
                    show_help,
                    input_buffer,
                    show_report,
                    term_size.columns,
                    term_size.lines
                )
                sys.stdout.write(output)
                sys.stdout.flush()
                force_redraw = False

            time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        # Restore primary screen buffer, show cursor, and restore console mode
        sys.stdout.write(ALT_EXIT + C_SHOW)
        sys.stdout.flush()
        restore_console(old_console_mode)
        collector.stop()
        print("\033[38;2;0;240;255m[+] CYBER_PULSE HUD TERMINATED. NEURAL LINK DISENGAGED.\033[0m")


if __name__ == "__main__":
    run_cli_hud()
