import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cyber_pulse.app import app, main, collector, launch_web

if __name__ == "__main__":
    main()
