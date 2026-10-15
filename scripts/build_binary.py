import os
import sys
import subprocess

def build():
    print("[+] Initiating CYBER_PULSE Standalone Binary Build...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "scripts" else script_dir
    spec_path = os.path.join(script_dir, "cpulse.spec") if os.path.exists(os.path.join(script_dir, "cpulse.spec")) else os.path.join(repo_root, "scripts", "cpulse.spec")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        spec_path,
        "--noconfirm",
        "--distpath", os.path.join(repo_root, "dist"),
        "--workpath", os.path.join(repo_root, "build"),
    ]
    print("[*] Running: " + " ".join(cmd))
    res = subprocess.run(cmd, cwd=repo_root)
    if res.returncode == 0:
        exe_name = "cpulse.exe" if sys.platform == "win32" else "cpulse"
        exe_path = os.path.join(repo_root, "dist", exe_name)
        print("\n========================================================")
        print(f"[+] BUILD SUCCESSFUL! Standalone binary created at:")
        print(f"    {exe_path}")
        print("========================================================\n")
    else:
        print(f"[!] Build failed with exit code: {res.returncode}")

if __name__ == "__main__":
    build()
