import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyber_pulse.cli_hud import run_cli_hud, BANNER, THEMES, make_bar

if __name__ == "__main__":
    run_cli_hud()
