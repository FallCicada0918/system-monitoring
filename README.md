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

### Option A: Windows Double-Click (便捷启动)
Double click run.bat in the root folder to open the interactive mode selector.

### Option B: Command Line (命令行启动)

1. Desktop Window Mode (Recommended):
   python app.py --mode window

2. Browser Fullscreen Mode (Press F11 in browser for immersion):
   python app.py --mode browser

3. Headless LAN Server Mode (Access via phone/tablet on same Wi-Fi):
   python app.py --mode server --port 8888

4. Terminal ANSI Mode (Pure terminal cyberpunk ASCII monitor):
   python app.py --mode cli

---

## 4. File Structure (工程目录)

- app.py: FastAPI server, WebSocket hub, REST endpoints, and pywebview launcher.
- collector.py: Hardware metrics engine (CPU, RAM, GPU, Disks, Network, Processes).
- cli_hud.py: Terminal ANSI cyberpunk dashboard.
- run.bat: Windows batch launcher.
- requirements.txt: Python dependency list.
- static/index.html: Holographic dashboard layout.
- static/css/cyber.css: Cyberpunk styling, neon glow, themes, and CRT scanlines.
- static/js/audio.js: Web Audio API sound generator.
- static/js/matrix.js: Matrix digital rain and 3D grid animation.
- static/js/app.js: Real-time telemetry, holographic gauges, and actions.


---

## 5. API Endpoints (接口概览)

- `GET /api/health` - System health heartbeat status and timestamp
- `GET /api/stats` - Comprehensive hardware telemetry metrics
- `GET /api/summary` - Aggregated resource consumption summary
- `POST /api/purge_memory` - Trigger neural memory flush
- `POST /api/kill/{pid}` - Terminate high-resource target process
- `WS /ws/telemetry` - Real-time streaming WebSocket feed

---
Encoding: UTF-8 (without BOM)
