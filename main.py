#!/usr/bin/env python3
"""CYBER_PULSE // Futuristic Cyberpunk System Telemetry CLI

Main entry point for development, PyCharm / IDE execution, and CLI commands.
"""
import os
import sys
from pathlib import Path

# Add 'src' directory to Python search path so cyber_pulse can be imported directly
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from cyber_pulse.cli import main

if __name__ == "__main__":
    # Support backward-compatible --mode argument
    if "--mode" in sys.argv:
        try:
            from cyber_pulse.app import main as app_main
            app_main()
        except ImportError:
            main()
    else:
        main()
