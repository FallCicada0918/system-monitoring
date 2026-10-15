import os
import sys
import time
import shutil
import webbrowser
import unicodedata
from typing import Dict, Any, List, Optional

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

try:
    from cyber_pulse.i18n import (
        t, get_language, set_language, next_language,
        detect_system_language, LANGUAGE_NAMES,
        LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
    )
except ImportError:
    try:
        from .i18n import (
            t, get_language, set_language, next_language,
            detect_system_language, LANGUAGE_NAMES,
            LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
        )
    except ImportError:
        from i18n import (
            t, get_language, set_language, next_language,
            detect_system_language, LANGUAGE_NAMES,
            LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
        )

# Terminal Control Codes
C_HIDE = "[?25l"
C_SHOW = "[?25h"
ALT_ENTER = "[?1049h"
ALT_EXIT = "[?1049l"
HOME = "[H"
CLEAR_EOL = "[K"
CLEAR_EOS = "[J"
BOLD = "[1m"
DIM = "[2m"
RESET = "[0m"

# Cyberpunk Themes Definition
THEMES = {
    "1": {
        "name": "NIGHT CITY 2077",
        "primary": "[38;2;0;240;255m",      # Cyber Cyan
        "secondary": "[38;2;255;0;128m",   # Neon Pink
        "accent": "[38;2;252;238;10m",     # Cyber Yellow
        "ok": "[38;2;0;255;102m",          # Neon Green
        "warn": "[38;2;252;238;10m",       # Amber
        "alert": "[38;2;255;34;85m",       # Neon Red
        "muted": "[38;2;90;105;130m",      # Steel Gray
        "bright": "[38;2;235;245;255m"     # Pure White
    },
    "2": {
        "name": "MATRIX CODE",
        "primary": "[38;2;0;255;102m",     # Phosphor Green
        "secondary": "[38;2;120;255;160m", # Light Mint
        "accent": "[38;2;0;200;80m",       # Dark Green
        "ok": "[38;2;0;255;102m",
        "warn": "[38;2;220;255;50m",
        "alert": "[38;2;255;80;60m",
        "muted": "[38;2;40;90;50m",
        "bright": "[38;2;200;255;220m"
    },
    "3": {
        "name": "SYNTHWAVE 1984",
        "primary": "[38;2;255;45;149m",    # Hot Pink
        "secondary": "[38;2;155;77;255m",  # Neon Purple
        "accent": "[38;2;255;170;0m",      # Sunset Orange
        "ok": "[38;2;0;240;255m",          # Neon Cyan
        "warn": "[38;2;255;170;0m",
        "alert": "[38;2;255;0;80m",
        "muted": "[38;2;110;80;130m",
        "bright": "[38;2;255;235;250m"
    },
    "4": {
        "name": "ARASAKA BLOOD OPS",
        "primary": "[38;2;255;20;50m",     # Crimson Red
        "secondary": "[38;2;255;100;100m", # Light Coral
        "accent": "[38;2;250;210;50m",     # Cyber Gold
        "ok": "[38;2;240;240;240m",        # Pure Titanium
        "warn": "[38;2;255;140;0m",
        "alert": "[38;2;255;0;0m",
        "muted": "[38;2;120;40;40m",
        "bright": "[38;2;255;255;255m"
    }
}


def str_width(s: str) -> int:
    """Calculate visual terminal display width taking East Asian characters into account."""
    w = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            w += 2
        else:
            w += 1
    return w


def pad_to_width(s: str, target_width: int, align: str = 'center') -> str:
    """Pad string with spaces according to display width."""
    w = str_width(s)
    if w >= target_width:
        return s
    pad = target_width - w
    if align == 'center':
        left = pad // 2
        right = pad - left
        return (' ' * left) + s + (' ' * right)
    elif align == 'left':
        return s + (' ' * pad)
    else:
        return (' ' * pad) + s


def make_section_header(label: str, width: int, muted: str) -> str:
    """Render aligned section header border with localized label."""
    lbl_w = str_width(label)
    dashes = max(2, width - lbl_w - 8)
    return f"{muted}+--[ {label} ]" + ("-" * dashes) + f"+{RESET}"


def render_banner(pri: str, sec: str, acc: str, muted: str, lang: str, width: int = 80) -> List[str]:
    """Render the header banner for 机体生命征象诊断仪 (Somatic Vital Signs Diagnostic Monitor)."""
    title = t("title", lang)
    sub = t("subtitle", lang)
    inner_w = max(40, width - 4)
    line_title = pad_to_width(f"✦  {title}  ✦", inner_w, "center")
    line_sub = pad_to_width(f"{sub} // v2.0", inner_w, "center")
    border_top = "╔" + ("═" * (inner_w + 2)) + "╗"
    border_bot = "╚" + ("═" * (inner_w + 2)) + "╝"
    return [
        f"{pri}{BOLD}{border_top}{RESET}",
        f"{pri}{BOLD}║ {acc}{line_title}{pri}{BOLD} ║{RESET}",
        f"{pri}{BOLD}║ {muted}{line_sub}{pri}{BOLD} ║{RESET}",
        f"{pri}{BOLD}{border_bot}{RESET}",
    ]


def setup_console():
    """Configure console: on Windows disable QuickEdit; on Unix enable cbreak mode."""
    old_mode = None
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            hIn = kernel32.GetStdHandle(-10)   # STD_INPUT_HANDLE
            hOut = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

            in_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(hIn, ctypes.byref(in_mode)):
                old_mode = ("win32", in_mode.value)
                new_in = (in_mode.value & ~0x0040) | 0x0080
                kernel32.SetConsoleMode(hIn, new_in)

            out_mode = wintypes.DWORD()
            if kernel32.GetConsoleMode(hOut, ctypes.byref(out_mode)):
                kernel32.SetConsoleMode(hOut, out_mode.value | 0x0004)
        except Exception:
            pass
    else:
        try:
            import termios
            import tty
            if sys.stdin.isatty():
                fd = sys.stdin.fileno()
                old_attr = termios.tcgetattr(fd)
                tty.setcbreak(fd)
                old_mode = ("unix", old_attr)
        except Exception:
            pass
    return old_mode


def restore_console(old_mode):
    """Restore console mode on exit across Windows & Unix."""
    if not old_mode:
        return
    mode_type, saved_val = old_mode
    if mode_type == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            hIn = kernel32.GetStdHandle(-10)
            kernel32.SetConsoleMode(hIn, saved_val)
        except Exception:
            pass
    elif mode_type == "unix":
        try:
            import termios
            if sys.stdin.isatty():
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved_val)
        except Exception:
            pass


def read_nonblocking_key() -> str:
    """Read single keyboard char non-blocking across Windows & Unix, supporting Unicode & IME."""
    if sys.platform == "win32":
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch in ('\x00', 'à'):
                if msvcrt.kbhit():
                    msvcrt.getwch()  # Consume scan code for special/extended keys
                return ""
            return ch
        return ""
    else:
        import select
        try:
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                return sys.stdin.read(1)
        except Exception:
            pass
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


def generate_report_text(stats: Dict[str, Any], lang: Optional[str] = None) -> str:
    """Format a comprehensive diagnostic report as plain text for file export."""
    cur_lang = lang or get_language()
    sys_info = stats.get("system", {})
    cpu = stats.get("cpu", {})
    mem = stats.get("memory", {})
    disks = stats.get("disks", {})
    gpus = stats.get("gpus", [])
    net = stats.get("network", {})
    procs = stats.get("processes", [])

    report_title = t("report_title", cur_lang)
    lines = []
    lines.append("=" * 80)
    lines.append(f"       {report_title}       ")
    lines.append(f"       TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')} | NODE: {sys_info.get('hostname', 'UNKNOWN')}")
    lines.append("=" * 80 + "\n")

    lines.append(f"[ {t('system_protocol', cur_lang)} ]")
    lines.append(f"  Hostname       : {sys_info.get('hostname')}")
    lines.append(f"  Operating Sys  : {sys_info.get('os')} ({sys_info.get('arch')})")
    lines.append(f"  Kernel Version : {sys_info.get('os_version')}")
    lines.append(f"  System Uptime  : {format_uptime(sys_info.get('uptime_sec', 0))}")
    lines.append(f"  Python Runtime : {sys_info.get('python_version')}")
    lines.append("")

    lines.append(f"[ {t('neural_cpu', cur_lang)} ]")
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

    lines.append(f"[ {t('neural_mem', cur_lang)} ]")
    lines.append(f"  Physical RAM   : {mem.get('used_gb', 0.0)} / {mem.get('total_gb', 0.0)} GB ({mem.get('percent', 0.0)}%)")
    lines.append(f"  Available RAM  : {mem.get('available_gb', 0.0)} GB Free")
    lines.append(f"  Swap Memory    : {mem.get('swap_used_gb', 0.0)} / {mem.get('swap_total_gb', 0.0)} GB ({mem.get('swap_percent', 0.0)}%)")
    lines.append("")

    lines.append(f"[ {t('storage_io', cur_lang)} ]")
    for d in disks.get("partitions", []):
        lines.append(f"  Mount [{d.get('mountpoint')}]: {d.get('used_gb', 0.0)} / {d.get('total_gb', 0.0)} GB ({d.get('percent', 0.0)}%) [Free: {d.get('free_gb', 0.0)} GB, Type: {d.get('fstype', '')}]")
    lines.append(f"  Disk Throughput: Read {disks.get('read_mb_sec', 0.0)} MB/s | Write {disks.get('write_mb_sec', 0.0)} MB/s")
    lines.append("")

    if gpus:
        lines.append(f"[ {t('neural_gpu', cur_lang)} ]")
        for g in gpus:
            lines.append(f"  Device Name    : {g.get('name')}")
            lines.append(f"  GPU Load       : {g.get('utilization_gpu', 0.0)}% | Temp: {g.get('temperature', 0.0)}C | Power: {g.get('power_draw', 0.0)}W")
            lines.append(f"  VRAM Usage     : {g.get('memory_used', 0.0)} / {g.get('memory_total', 0.0)} MB (Free: {g.get('memory_free', 0.0)} MB)")
        lines.append("")

    lines.append(f"[ {t('network_radar', cur_lang)} ]")
    lines.append(f"  Downlink RX    : {net.get('rx_kb_sec', 0.0)} KB/s (Total {net.get('total_recv_mb', 0.0)} MB)")
    lines.append(f"  Uplink TX      : {net.get('tx_kb_sec', 0.0)} KB/s (Total {net.get('total_sent_mb', 0.0)} MB)")
    lines.append(f"  Connections    : {net.get('connections_established', 0)} Established / {net.get('connections_total', 0)} Total")
    lines.append("")

    lines.append(f"[ {t('top_targets', cur_lang)} ]")
    lines.append("  PID     NAME                     CPU%    MEM%    RSS(MB)    STATUS")
    lines.append("  " + ("-" * 68))
    for p in procs[:12]:
        pname = p.get('name', '')[:23].ljust(23)
        lines.append(f"  {p.get('pid', 0):6d}  {pname}  {p.get('cpu_percent', 0.0):5.1f}  {p.get('memory_percent', 0.0):5.1f}  {p.get('memory_rss_mb', 0.0):9.1f}    {p.get('status', '')}")
    lines.append("\n" + "=" * 80)
    lines.append("                        [ END OF TELEMETRY REPORT ]                             ")
    lines.append("=" * 80 + "\n")
    return "\n".join(lines)


def export_report_file(stats: Dict[str, Any], filename: str = "cyber_pulse_report.txt", lang: Optional[str] = None) -> str:
    """Export system diagnostic report to a text file."""
    try:
        report_text = generate_report_text(stats, lang=lang)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_text)
        return os.path.abspath(filename)
    except Exception as e:
        return f"Report generation failed: {e}"


def render_report_screen(
    stats: Dict[str, Any],
    theme_key: str,
    status_msg: str,
    input_buffer: str,
    term_width: int,
    term_height: int,
    lang: Optional[str] = None
) -> str:
    """Render full-screen diagnostic report card overlay."""
    cur_lang = lang or get_language()
    theme = THEMES.get(theme_key, THEMES["1"])
    pri = theme["primary"]
    sec = theme["secondary"]
    acc = theme["accent"]
    ok = theme["ok"]
    muted = theme["muted"]
    bright = theme["bright"]

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
    lines.extend(render_banner(pri, sec, acc, muted, cur_lang, width))
    lines.append(border)
    lines.append(f"  {bright}NODE:{RESET} {pri}{sys_info.get('hostname')}{RESET}  {bright}OS:{RESET} {sys_info.get('os')}  {bright}UPTIME:{RESET} {acc}{format_uptime(sys_info.get('uptime_sec', 0))}{RESET}")
    lines.append(f"  {bright}CPU:{RESET}  {cpu.get('cores_physical')}P/{cpu.get('cores_logical')}T @ {cpu.get('freq_current_mhz')}MHz | Load: {acc}{cpu.get('total_percent')}%")
    lines.append(f"  {bright}RAM:{RESET}  {mem.get('used_gb'):.1f}/{mem.get('total_gb'):.1f} GB ({mem.get('percent')}%) | Free: {ok}{mem.get('available_gb'):.1f} GB{RESET} | Swap: {mem.get('swap_used_gb'):.1f}/{mem.get('swap_total_gb'):.1f} GB")
    
    for p in disks.get("partitions", [])[:2]:
        lines.append(f"  {bright}DISK {p.get('mountpoint')}:{RESET} {p.get('used_gb'):.0f}/{p.get('total_gb'):.0f} GB ({p.get('percent')}%) [Free: {p.get('free_gb'):.0f} GB]")
    lines.append(f"  {bright}DISK I/O:{RESET} Read {pri}{disks.get('read_mb_sec', 0.0):.2f} MB/s{RESET} | Write {sec}{disks.get('write_mb_sec', 0.0):.2f} MB/s{RESET}")

    for g in gpus[:1]:
        lines.append(f"  {bright}GPU:{RESET}  {sec}{g.get('name')}{RESET} | Load: {g.get('utilization_gpu')}% | Temp: {acc}{g.get('temperature')}C{RESET} | VRAM: {g.get('memory_used'):.0f}/{g.get('memory_total'):.0f} MB")

    lines.append(f"  {bright}NET:{RESET}  Downlink: {ok}{net.get('rx_kb_sec'):.1f} KB/s{RESET} | Uplink: {sec}{net.get('tx_kb_sec'):.1f} KB/s{RESET} | Conns: {net.get('connections_established')}")

    lines.append(border)
    lines.append(f"  {pri}{t('top_targets', cur_lang)}:{RESET}")
    for p in procs[:4]:
        pname = p.get('name', '')[:22].ljust(22)
        lines.append(f"  {bright}{p.get('pid', 0):6d}{RESET}  {pname}  CPU:{p.get('cpu_percent', 0.0):5.1f}%  RAM:{p.get('memory_percent', 0.0):4.1f}% ({p.get('memory_rss_mb', 0.0):6.1f} MB)  {ok}{p.get('status')}{RESET}")

    lines.append(f"{muted}+" + ("=" * (width - 2)) + f"+{RESET}")
    if status_msg:
        lines.append(f"  {acc}{BOLD}>>> {status_msg}{RESET}")
    else:
        lines.append(f"  {bright}[+] {t('report_saved', cur_lang)} cyber_pulse_report.txt // {t('report_return_hint', cur_lang)}{RESET}")

    lines.append(f"  {muted}{t('hotkey_bar', cur_lang)}{RESET}")
    lines.append(make_section_header(t('cmd_input', cur_lang), width, muted))
    cursor = f"{acc}?{RESET}"
    max_input_len = max(20, width - 20)
    display_input = input_buffer[-max_input_len:] if len(input_buffer) > max_input_len else input_buffer
    lines.append(f"  {pri}COMMAND >{RESET} {bright}[ {display_input}{cursor} ]{RESET}  {muted}(e.g. r, w, f, l, 1-4, q, help){RESET}")
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
    lang: Optional[str] = None
) -> str:
    """Render the interactive terminal HUD dashboard."""
    cur_lang = lang or get_language()
    if show_report:
        return render_report_screen(stats, theme_key, status_msg, input_buffer, term_width, term_height, lang=cur_lang)

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

    compact_mode = term_height < 35
    if compact_mode:
        lang_name = LANGUAGE_NAMES.get(cur_lang, cur_lang)
        lines.append(f"{pri}{BOLD}[ {t('title', cur_lang)} // v2.0 ]{RESET} {muted}{t('theme_label', cur_lang)}:{RESET}{acc}{theme['name']}{RESET} {muted}{t('lang_label', cur_lang)}:{RESET}{pri}{lang_name}{RESET} {muted}{t('time_label', cur_lang)}:{RESET}{bright}{time.strftime('%H:%M:%S')}{RESET}")
    else:
        lines.extend(render_banner(pri, sec, acc, muted, cur_lang, width))

    # System Status Protocol
    cpu_pct = cpu.get("total_percent", 0.0)
    mem_pct = mem.get("percent", 0.0)
    if cpu_pct >= 85 or mem_pct >= 85:
        defcon_col = alert
        defcon_txt = t("defcon_1", cur_lang)
    elif cpu_pct >= 60 or mem_pct >= 70:
        defcon_col = warn
        defcon_txt = t("defcon_2", cur_lang)
    else:
        defcon_col = ok
        defcon_txt = t("defcon_4", cur_lang)

    lines.append(make_section_header(t("system_protocol", cur_lang), width, muted))
    lines.append(f"  {bright}NODE:{RESET} {pri}{sys_info.get('hostname')}{RESET}  {bright}OS:{RESET} {sys_info.get('os')}  {bright}UPTIME:{RESET} {acc}{format_uptime(sys_info.get('uptime_sec', 0))}{RESET}")
    lines.append(f"  {bright}STATUS:{RESET} {defcon_col}{BOLD}[ {defcon_txt} ]{RESET}")

    # CPU Telemetry
    lines.append(make_section_header(t("neural_cpu", cur_lang), width, muted))
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
    lines.append(make_section_header(t("neural_mem", cur_lang), width, muted))
    ram_bar = make_bar(mem_pct, bar_len, theme)
    lines.append(f"  RAM:   [{ram_bar}] {bright}{mem_pct:5.1f}%{RESET}  {mem.get('used_gb', 0):.1f}/{mem.get('total_gb', 0):.1f} GB  ({mem.get('available_gb', 0):.1f} GB Free)")
    if not compact_mode:
        swap_bar = make_bar(mem.get("swap_percent", 0.0), bar_len, theme, color_override=sec)
        lines.append(f"  SWAP:  [{swap_bar}] {bright}{mem.get('swap_percent', 0):5.1f}%{RESET}  {mem.get('swap_used_gb', 0):.1f}/{mem.get('swap_total_gb', 0):.1f} GB")

    # GPU
    if gpus:
        lines.append(make_section_header(t("neural_gpu", cur_lang), width, muted))
        for gpu in gpus[:1]:
            gpu_bar = make_bar(gpu.get("utilization_gpu", 0.0), 16, theme, color_override=sec)
            lines.append(f"  {sec}{gpu.get('name')[:26]}{RESET} [{gpu_bar}] {gpu.get('utilization_gpu', 0):3.0f}%  TEMP: {acc}{gpu.get('temperature', 0):.0f}C{RESET}  VRAM: {gpu.get('memory_used', 0):.0f}/{gpu.get('memory_total', 0):.0f}MB")

    # Storage & Disks
    lines.append(make_section_header(t("storage_io", cur_lang), width, muted))
    disk_count = 1 if compact_mode else 2
    for p in disks.get("partitions", [])[:disk_count]:
        p_bar = make_bar(p.get("percent", 0.0), 14, theme, color_override=acc)
        lines.append(f"  {bright}{p.get('mountpoint', '')[:4]:4s}{RESET} [{p_bar}] {p.get('percent', 0):4.1f}%  {p.get('used_gb', 0):.0f}/{p.get('total_gb', 0):.0f}GB (Free: {p.get('free_gb', 0):.0f}GB)")
    lines.append(f"  I/O:   READ: {pri}{disks.get('read_mb_sec', 0.0):5.2f} MB/s{RESET}   WRITE: {sec}{disks.get('write_mb_sec', 0.0):5.2f} MB/s{RESET}")

    # Network Radar
    lines.append(make_section_header(t("network_radar", cur_lang), width, muted))
    lines.append(f"  DOWNLINK: {ok}{net.get('rx_kb_sec', 0.0):7.1f} KB/s{RESET} ({net.get('total_recv_mb', 0)} MB)   UPLINK: {sec}{net.get('tx_kb_sec', 0.0):7.1f} KB/s{RESET} ({net.get('total_sent_mb', 0)} MB)   CONNS: {bright}{net.get('connections_established', 0)}{RESET}")

    # Top Targets
    lines.append(make_section_header(t("top_targets", cur_lang), width, muted))
    lines.append(f"  {pri}PID     NAME                    CPU%   MEM%    RSS(MB)   STATUS{RESET}")
    proc_count = 3 if compact_mode else 4
    for proc in procs[:proc_count]:
        pname = proc.get("name", "")[:22].ljust(22)
        lines.append(f"  {bright}{proc.get('pid', 0):6d}{RESET}  {pname}  {proc.get('cpu_percent', 0.0):5.1f}  {proc.get('memory_percent', 0.0):5.1f}  {proc.get('memory_rss_mb', 0.0):8.1f}   {ok}{proc.get('status', '')}{RESET}")

    # Help overlay (if toggled)
    if show_help:
        lines.append(make_section_header(t("cmd_help", cur_lang), width, muted))
        lines.append(f"  {acc}[W]{RESET} or 'web'     >> {t('help_w', cur_lang)}")
        lines.append(f"  {ok}[R]{RESET} or 'report'  >> {t('help_r', cur_lang)}")
        lines.append(f"  {sec}[F]{RESET} or 'flush'   >> {t('help_f', cur_lang)}")
        lines.append(f"  {pri}[L]{RESET} or 'lang'    >> {t('help_l', cur_lang)}")
        lines.append(f"  {acc}[1-4]{RESET} or 'theme' >> {t('help_theme', cur_lang)}")
        lines.append(f"  {bright}[H]{RESET} or 'help'    >> {t('help_h', cur_lang)}")
        lines.append(f"  {alert}[Q]{RESET} or 'quit'    >> {t('help_q', cur_lang)}")
        lines.append(f"  'kill <pid>'       >> {t('help_kill', cur_lang)}")

    # Notification bar
    lines.append(f"{muted}+" + ("=" * (width - 2)) + f"+{RESET}")
    if status_msg:
        lines.append(f"  {acc}{BOLD}>>> {status_msg}{RESET}")
    else:
        lines.append(f"  {DIM}{t('status_online', cur_lang)}{RESET}")

    # Hotkey bar
    lines.append(f"  {muted}{t('hotkey_bar', cur_lang)}{RESET}")

    # Command input
    lines.append(make_section_header(t("cmd_input", cur_lang), width, muted))
    cursor = f"{acc}?{RESET}"
    max_input_len = max(20, width - 20)
    display_input = input_buffer[-max_input_len:] if len(input_buffer) > max_input_len else input_buffer
    lines.append(f"  {pri}COMMAND >{RESET} {bright}[ {display_input}{cursor} ]{RESET}  {muted}(e.g. w, r, f, l, 1-4, q, help){RESET}")
    lines.append(border)

    formatted_lines = [line + CLEAR_EOL for line in lines]
    return HOME + "\n".join(formatted_lines) + "\n" + CLEAR_EOS


def run_cli_hud(theme: str = "1", interval: float = 1.0, lang: Optional[str] = None):
    """Launch interactive terminal HUD for 机体生命征象诊断仪."""
    os.system("")  # Enable ANSI in Windows terminal
    old_console_mode = setup_console()

    # Determine language
    if lang:
        set_language(lang)
    else:
        set_language(detect_system_language())

    current_lang = get_language()
    current_theme = theme if theme in THEMES else "1"
    status_msg = t("link_established", current_lang)
    status_time = time.time()
    show_help = False
    show_report = False
    input_buffer = ""

    # Switch to Alternate Screen Buffer and hide cursor
    sys.stdout.write(ALT_ENTER + C_HIDE + HOME)
    sys.stdout.flush()

    pri = THEMES[current_theme]["primary"]
    sec = THEMES[current_theme]["secondary"]
    acc = THEMES[current_theme]["accent"]
    muted = THEMES[current_theme]["muted"]

    banner_lines = render_banner(pri, sec, acc, muted, current_lang, 80)
    init_splash = (
        HOME +
        "\n".join(banner_lines) + "\n\n"
        f"  {THEMES[current_theme]['ok']}{t('initializing', current_lang)}{RESET}\n"
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
                                r_path = export_report_file(last_stats, lang=current_lang)
                                status_msg = f"{t('report_saved', current_lang)}: {os.path.basename(r_path)}"
                            else:
                                status_msg = t('status_online', current_lang)
                            status_time = now
                        elif cmd_lower in ("back", "return"):
                            if show_report:
                                show_report = False
                                status_msg = t('status_online', current_lang)
                                status_time = now
                        elif cmd_lower in ("f", "flush"):
                            res = collector.purge_memory()
                            status_msg = res.get("message", "MEMORY PURGED")
                            status_time = now
                        elif cmd_lower in ("l", "lang", "language"):
                            current_lang = next_language()
                            lang_name = LANGUAGE_NAMES.get(current_lang, current_lang)
                            status_msg = f"{t('lang_label', current_lang)}: {lang_name}"
                            status_time = now
                        elif cmd_lower.startswith("lang "):
                            l_arg = cmd_lower.split()[-1].strip()
                            if l_arg in ("cn", "zh", "zh_cn", "zh-cn", "simplified"):
                                set_language(LANG_ZH_CN)
                            elif l_arg in ("tw", "hk", "zh_tw", "zh-tw", "traditional"):
                                set_language(LANG_ZH_TW)
                            elif l_arg in ("en", "english", "us"):
                                set_language(LANG_EN)
                            elif l_arg in ("ja", "jp", "japanese"):
                                set_language(LANG_JA)
                            else:
                                set_language(l_arg)
                            current_lang = get_language()
                            lang_name = LANGUAGE_NAMES.get(current_lang, current_lang)
                            status_msg = f"{t('lang_label', current_lang)}: {lang_name}"
                            status_time = now
                        elif cmd_lower in ("1", "2", "3", "4"):
                            current_theme = cmd_lower
                            status_msg = f"{t('theme_label', current_lang)}: {THEMES[cmd_lower]['name']}"
                            status_time = now
                        elif cmd_lower.startswith("theme "):
                            t_arg = cmd_lower.split()[-1]
                            if t_arg in THEMES:
                                current_theme = t_arg
                                status_msg = f"{t('theme_label', current_lang)}: {THEMES[t_arg]['name']}"
                            else:
                                status_msg = "INVALID THEME: SELECT 1, 2, 3, OR 4"
                            status_time = now
                        elif cmd_lower in ("?", "h", "help"):
                            show_help = not show_help
                            status_msg = t('cmd_help', current_lang) if show_help else ""
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
                            status_msg = f"UNKNOWN COMMAND: '{cmd}' // TYPE 'help' OR '?'"
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
                        status_msg = t('status_online', current_lang)
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
                    term_size.lines,
                    lang=current_lang
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
        print(f"[38;2;0;240;255m{t('terminated', current_lang)}[0m")


if __name__ == "__main__":
    theme_arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    run_cli_hud(theme=theme_arg)
