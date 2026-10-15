import os
import sys
import json
import time
import argparse
from typing import Optional

try:
    from cyber_pulse import __version__
    from cyber_pulse.collector import SystemCollector
    from cyber_pulse.cli_hud import run_cli_hud, THEMES
    from cyber_pulse.i18n import (
        t, get_language, set_language, detect_system_language,
        LANGUAGE_NAMES, LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
    )
except (ImportError, ValueError):
    try:
        from . import __version__
        from .collector import SystemCollector
        from .cli_hud import run_cli_hud, THEMES
        from .i18n import (
            t, get_language, set_language, detect_system_language,
            LANGUAGE_NAMES, LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
        )
    except (ImportError, ValueError):
        try:
            import __init__ as _pkg
            __version__ = getattr(_pkg, '__version__', '2.0.0')
        except Exception:
            __version__ = '2.0.0'
        from collector import SystemCollector
        from cli_hud import run_cli_hud, THEMES
        from i18n import (
            t, get_language, set_language, detect_system_language,
            LANGUAGE_NAMES, LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA
        )

CYAN = "\033[38;2;0;240;255m"
MAGENTA = "\033[38;2;255;0;128m"
YELLOW = "\033[38;2;252;238;10m"
GREEN = "\033[38;2;0;255;102m"
RED = "\033[38;2;255;34;85m"
GRAY = "\033[38;2;90;105;130m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ✦  机体生命征象诊断仪  ✦                            ║
║       SOMATIC VITAL SIGNS DIAGNOSTIC MONITOR CLI v{__version__}                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
{RESET}"""


def cmd_hud(args):
    """Launch interactive terminal HUD."""
    theme = getattr(args, "theme", "1")
    interval = getattr(args, "interval", 1.0)
    lang = getattr(args, "lang", None)
    run_cli_hud(theme=str(theme), interval=interval, lang=lang)


def cmd_web(args):
    """Launch Web HUD server / browser."""
    try:
        from cyber_pulse.app import launch_web
    except ImportError:
        try:
            from .app import launch_web
        except ImportError as exc:
            print(f"{RED}[!] Web HUD dependencies missing (fastapi/uvicorn): {exc}{RESET}")
            print("    Please install required dependencies: pip install -r requirements.txt")
            return
    mode = "server" if getattr(args, "headless", False) else ("window" if getattr(args, "window", False) else "browser")
    launch_web(mode=mode, host=args.host, port=args.port)


def cmd_flush(args):
    """Execute memory purge action."""
    os.system("")
    cur_lang = getattr(args, "lang", None) or get_language()
    collector = SystemCollector()
    print(f"{CYAN}{t('flush_start', cur_lang)}{RESET}")
    res = collector.purge_memory()
    freed_mb = res.get("freed_mb", 0.0)
    before_mb = res.get("available_before_mb", 0.0)
    after_mb = res.get("available_after_mb", 0.0)
    print(f"{GREEN}{BOLD}[+] {t('ram_reclaimed', cur_lang)}: {freed_mb:.1f} MB{RESET}")
    print(f"    {t('avail_ram', cur_lang)}: {before_mb:.1f} MB -> {after_mb:.1f} MB")
    collector.stop()


def cmd_top(args):
    """Display top processes ranking."""
    os.system("")
    collector = SystemCollector()
    count = getattr(args, "count", 10)
    sort_by = getattr(args, "sort", "cpu")
    watch = getattr(args, "watch", False)

    try:
        while True:
            stats = collector.get_stats()
            procs = stats.get("processes", [])
            if sort_by == "mem":
                procs = sorted(procs, key=lambda x: x.get("memory_percent", 0), reverse=True)
            else:
                procs = sorted(procs, key=lambda x: x.get("cpu_percent", 0), reverse=True)

            if watch:
                sys.stdout.write("\033[H\033[2J")

            print(f"{CYAN}{BOLD}PID     NAME                    CPU%   MEM%    RSS(MB)   STATUS{RESET}")
            print(f"{GRAY}" + ("-" * 64) + f"{RESET}")
            for p in procs[:count]:
                pname = p["name"][:22].ljust(22)
                print(f"{BOLD}{p['pid']:6d}{RESET}  {pname}  {p['cpu_percent']:5.1f}  {p['memory_percent']:5.1f}  {p['memory_rss_mb']:8.1f}   {GREEN}{p['status']}{RESET}")

            if not watch:
                break
            print(f"\n{GRAY}[Press Ctrl+C to exit top surveillance]{RESET}")
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        collector.stop()


def cmd_kill(args):
    """Terminate target process."""
    os.system("")
    pid = args.pid
    collector = SystemCollector()
    if not args.yes:
        confirm = input(f"{YELLOW}[?] Terminate process PID {pid}? (y/N): {RESET}").strip().lower()
        if confirm != "y":
            print(f"{GRAY}[-] Aborted.{RESET}")
            collector.stop()
            return

    res = collector.terminate_process(pid)
    if res.get("success"):
        print(f"{GREEN}[+] {res.get('message')}{RESET}")
    else:
        print(f"{RED}[!] {res.get('message')}{RESET}")
    collector.stop()


def cmd_report(args):
    """Export or print system diagnostic telemetry."""
    collector = SystemCollector()
    stats = collector.get_stats()
    collector.stop()

    if getattr(args, "json", False):
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    os.system("")
    cur_lang = getattr(args, "lang", None) or get_language()
    sys_info = stats["system"]
    cpu = stats["cpu"]
    mem = stats["memory"]
    net = stats["network"]
    disks = stats["disks"]
    gpus = stats["gpus"]

    print(BANNER)
    print(f"{CYAN}[ {t('report_title', cur_lang)} ]" + ("=" * 40) + f"{RESET}")
    print(f"  HOST     : {sys_info['hostname']} ({sys_info['os']})")
    print(f"  CPU      : {cpu['cores_physical']} Cores / {cpu['cores_logical']} Threads @ {cpu['freq_current_mhz']} MHz | Usage: {cpu['total_percent']}%")
    print(f"  MEMORY   : {mem['used_gb']} / {mem['total_gb']} GB ({mem['percent']}%) | Free: {mem['available_gb']} GB")
    print(f"  SWAP     : {mem['swap_used_gb']} / {mem['swap_total_gb']} GB ({mem['swap_percent']}%)")
    for d in disks.get("partitions", []):
        print(f"  DISK {d['mountpoint']}: {d['used_gb']:.1f}/{d['total_gb']:.1f} GB ({d['percent']}%)")
    for g in gpus:
        print(f"  GPU      : {g['name']} | Load: {g['utilization_gpu']}% | Temp: {g['temperature']}C | VRAM: {g['memory_used']}/{g['memory_total']} MB")
    print(f"  NETWORK  : RX {net['total_recv_mb']} MB ({net['rx_kb_sec']} KB/s) | TX {net['total_sent_mb']} MB ({net['tx_kb_sec']} KB/s)")
    print(f"{CYAN}" + ("=" * 73) + f"{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="cpulse",
        description="CYBER_PULSE // 机体生命征象诊断仪 (Somatic Vital Signs Diagnostic Monitor)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  cpulse              Launch full interactive terminal HUD\n  cpulse -l en        Launch HUD in English\n  cpulse -l ja        Launch HUD in Japanese\n  cpulse -l zh_TW     Launch HUD in Traditional Chinese\n  cpulse web          Start Web HUD in browser\n  cpulse top          Live top processes list\n  cpulse flush        Purge memory working sets\n  cpulse report       Print system diagnostic card\n  cpulse report --json Export machine-readable telemetry\n"
    )
    parser.add_argument("-v", "--version", action="version", version=f"cpulse {__version__}")
    parser.add_argument(
        "-l", "--lang",
        choices=["zh_CN", "zh_TW", "en", "ja"],
        default=None,
        help="Interface language / 界面语言: zh_CN (简体), zh_TW (繁體), en (English), ja (日本語)"
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # subcommand: hud
    p_hud = subparsers.add_parser("hud", help="Interactive terminal HUD dashboard (Default)")
    p_hud.add_argument("-t", "--theme", choices=["1", "2", "3", "4"], default="1", help="Theme: 1=NightCity, 2=Matrix, 3=Synthwave, 4=Arasaka")
    p_hud.add_argument("-i", "--interval", type=float, default=1.0, help="Refresh interval in seconds (default: 1.0)")
    p_hud.add_argument("-l", "--lang", choices=["zh_CN", "zh_TW", "en", "ja"], default=None, help="Interface language")
    p_hud.set_defaults(func=cmd_hud)

    # subcommand: web
    p_web = subparsers.add_parser("web", help="Launch Web HUD")
    p_web.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    p_web.add_argument("--port", type=int, default=8888, help="Port (default: 8888)")
    p_web.add_argument("--headless", action="store_true", help="Run in headless server mode (no browser popup)")
    p_web.add_argument("--window", action="store_true", help="Launch in standalone desktop webview window")
    p_web.set_defaults(func=cmd_web)

    # subcommand: flush
    p_flush = subparsers.add_parser("flush", help="Execute Neural Flush to purge memory working sets")
    p_flush.add_argument("-l", "--lang", choices=["zh_CN", "zh_TW", "en", "ja"], default=None, help="Language")
    p_flush.set_defaults(func=cmd_flush)

    # subcommand: top
    p_top = subparsers.add_parser("top", help="Top processes monitor")
    p_top.add_argument("-n", "--count", type=int, default=10, help="Number of processes to show (default: 10)")
    p_top.add_argument("-s", "--sort", choices=["cpu", "mem"], default="cpu", help="Sort criteria (default: cpu)")
    p_top.add_argument("-w", "--watch", action="store_true", help="Continuous live watch mode")
    p_top.set_defaults(func=cmd_top)

    # subcommand: kill
    p_kill = subparsers.add_parser("kill", help="Terminate a process by PID")
    p_kill.add_argument("pid", type=int, help="Target process PID")
    p_kill.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    p_kill.set_defaults(func=cmd_kill)

    # subcommand: report
    p_report = subparsers.add_parser("report", help="Generate diagnostic health report")
    p_report.add_argument("-l", "--lang", choices=["zh_CN", "zh_TW", "en", "ja"], default=None, help="Language")
    p_report.add_argument("--json", action="store_true", help="Output in raw JSON format")
    p_report.set_defaults(func=cmd_report)

    # If no args passed, default to interactive HUD
    if len(sys.argv) == 1:
        run_cli_hud(theme="1", interval=1.0)
        return

    args = parser.parse_args()
    if hasattr(args, "lang") and args.lang:
        set_language(args.lang)

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
