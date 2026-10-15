import os
import sys

# Ensure src is in sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(repo_root, "src")
if os.path.exists(src_dir) and src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if __name__ == "__main__":
    from cyber_pulse.cli import main
    main()
