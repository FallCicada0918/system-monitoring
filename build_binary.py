import os
import sys
import subprocess

def build():
    print("[+] Initiating CYBER_PULSE Standalone Binary Build...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "cpulse.spec",
        "--noconfirm"
    ]
    print("[*] Running: " + " ".join(cmd))
    res = subprocess.run(cmd, cwd=base_dir)
    if res.returncode == 0:
        exe_name = "cpulse.exe" if sys.platform == "win32" else "cpulse"
        exe_path = os.path.join(base_dir, "dist", exe_name)
        print("\n========================================================")
        print(f"[+] BUILD SUCCESSFUL! Standalone binary created at:")
        print(f"    {exe_path}")
        print("========================================================\n")
    else:
        print(f"[!] Build failed with exit code: {res.returncode}")

if __name__ == "__main__":
    build()
