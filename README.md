# CYBER_PULSE // Cyberpunk Neural System Monitor v2.0
> Cyberpunk 2077 HUD Hardware Telemetry & Process Surveillance Console

![Python](https://img.shields.io/badge/Python-3.10+-00f0ff?style=flat-square)
![Cyberpunk](https://img.shields.io/badge/Style-Cyberpunk%202077-ff0055?style=flat-square)
![Hardware](https://img.shields.io/badge/GPU-NVIDIA%20RTX%20Ready-fcee0a?style=flat-square)
![Audio](https://img.shields.io/badge/Audio-Web%20Audio%20Synth-00ff66?style=flat-square)

---

## 1. Project Overview (项目介绍)

CYBER_PULSE is a futuristic, highly customizable system status monitor built with Python, FastAPI, WebSocket, and an HTML5 Canvas cyberpunk HUD.
It transforms your machine into a Cyberpunk 2077 Netrunner cyberdeck terminal with real-time hardware telemetry, audio synthesizers, holographic gauges, and tactical controls.

---

## 2. Key Cyber Features (核心特色)

### Holographic Visual HUD (全息赛博视觉)
- Holographic Rotary Gauges: CPU, RAM, NVIDIA GPU (RTX 4060 supported), Storage Arrays with dynamic reticles.
- 16-Core Real-time Equalizer: Live per-core load equalizer bars with neon gradients.
- Dual Oscilloscope Radar: Downlink and uplink live telemetry waveforms, 60s CPU load history.
- Matrix Digital Rain & 3D Cyber Floor Grid: Canvas perspective animations.
- CRT Scanlines & Screen Flicker: Toggleable retro display effect.

### Offline Web Audio Synthesizer (离线赛博音效)
- 100% in-browser Web Audio API synthesis with zero external audio assets.
- Boot-up frequency chord, tactile button chirps, over-temperature/CPU alarm sirens, and laser purge beams.

### Tactical Actions (骚包战术操作)
- OVERCLOCK BOOST: Triggers screen vibration, warp sound, and DEFCON 1 hyper-clock alert for 5 seconds.
- NEURAL FLUSH: Frees memory via Windows EmptyWorkingSet and Python GC, sweeps cyan laser beam across the screen.
- DIAGNOSTIC REPORT: Generates and copies a sci-fi formatted system health report to clipboard.
- PROCESS TERMINATOR: Search, sort, and terminate high-resource target processes with confirmation modal.

### Four Switchable Themes (四套赛博主题)
1. Night City 2077 (Cyan / Neon Pink / Cyber Yellow)
2. Matrix Code (Phosphor Green / Terminal Black)
3. Synthwave Outrun (Purple / Sunset Orange / Electric Pink)
4. Arasaka Blood Ops (Crimson Red / Titanium White / Charcoal)

---

## 3. Quick Start (启动指南)

### Option A: Windows Launcher (便捷启动)
Double click `scripts/run.bat` or run:
```bash
python main.py
```

### Option B: Command Line (命令行启动)

1. Terminal Cyberpunk HUD (Default interactive dashboard):
   ```bash
   python main.py hud
   ```

2. Web Browser Fullscreen Mode:
   ```bash
   python main.py web
   ```

3. Standalone Desktop Window Mode:
   ```bash
   python main.py web --window
   ```

4. Headless LAN Server Mode (Access via phone/tablet on same Wi-Fi):
   ```bash
   python main.py web --headless --port 8888
   ```

5. Live Top Processes Monitor:
   ```bash
   python main.py top
   ```

6. System Diagnostic Telemetry:
   ```bash
   python main.py report
   ```

---

## 4. Project Structure (工程目录规范)

```
system-monitoring/
├── docs/                     # Project documentation & engineering logs
│   └── TASK_PROGRESS.md      # Development and feature tracking
├── scripts/                  # Automation, launcher & build scripts
│   ├── build_binary.py       # Standalone PyInstaller compilation script
│   ├── cpulse.bat            # Windows batch shortcut for CLI
│   ├── cpulse.ps1            # PowerShell shortcut for CLI
│   ├── cpulse.spec           # PyInstaller build specification
│   ├── entrypoint.py         # PyInstaller bootstrap entrypoint
│   ├── install.ps1           # Windows PATH installer script
│   └── run.bat               # Interactive menu launcher
├── src/                      # Source code (standard src-layout)
│   └── cyber_pulse/          # Core package
│       ├── __init__.py       # Package marker and version metadata
│       ├── __main__.py       # Allows python -m cyber_pulse execution
│       ├── app.py            # FastAPI server, WebSockets & REST endpoints
│       ├── cli.py            # Unified command-line interface
│       ├── cli_hud.py        # Terminal ANSI cyberpunk HUD dashboard
│       ├── collector.py      # Hardware telemetry engine (CPU/RAM/GPU/Disk/Net)
│       └── static/           # Cyberpunk Web HUD assets
│           ├── index.html    # HUD canvas interface
│           ├── css/          # Neon glow, themes, CRT scanlines
│           └── js/           # Canvas graphics, Web Audio API, telemetry
├── tests/                    # Automated unit tests
│   ├── __init__.py
│   ├── test_api.py           # REST endpoints test suite
│   ├── test_cli.py           # CLI parser test suite
│   └── test_collector.py     # System collector test suite
├── .gitignore                # Git ignore patterns
├── main.py                   # PyCharm / IDE development entry point
├── pyproject.toml            # Modern Python build & package config
├── requirements.txt          # Python dependency list
├── setup.py                  # Setuptools configuration shim
└── README.md                 # Project documentation
```

---
Encoding: UTF-8 (without BOM)
