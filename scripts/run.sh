#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH}"

cd "$REPO_ROOT"

PYTHON_BIN="python3"
if ! command -v "$PYTHON_BIN" &>/dev/null; then
    PYTHON_BIN="python"
fi

if [ $# -eq 0 ]; then
    echo "==============================================================================="
    echo "    CYBER_PULSE // Cyberpunk Neural System Monitor CLI v2.0"
    echo "==============================================================================="
    echo "  [1] Interactive Terminal HUD (Default)"
    echo "  [2] Web Browser Mode"
    echo "  [3] Desktop Window Mode"
    echo "  [4] Headless Server Mode"
    echo "  [5] Top Processes Monitor"
    echo "  [6] Diagnostic Report"
    echo ""
    read -p "Select Mode [Default: 1]: " choice
    case "$choice" in
        2) "$PYTHON_BIN" -m cyber_pulse.cli web ;;
        3) "$PYTHON_BIN" -m cyber_pulse.cli web --window ;;
        4) "$PYTHON_BIN" -m cyber_pulse.cli web --headless ;;
        5) "$PYTHON_BIN" -m cyber_pulse.cli top ;;
        6) "$PYTHON_BIN" -m cyber_pulse.cli report ;;
        *) "$PYTHON_BIN" -m cyber_pulse.cli hud ;;
    esac
else
    "$PYTHON_BIN" -m cyber_pulse.cli "$@"
fi
