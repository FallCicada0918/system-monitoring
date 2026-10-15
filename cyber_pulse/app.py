import os
import sys
import time
import json
import socket
import argparse
import threading
import webbrowser
from typing import Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from .collector import SystemCollector
    from . import cli_hud
except ImportError:
    from collector import SystemCollector
    import cli_hud

app = FastAPI(title="CYBER_PULSE // NEURAL_HUD", version="2.0")
collector = SystemCollector()


def get_static_dir() -> str:
    # 1. PyInstaller bundled path
    if hasattr(sys, "_MEIPASS"):
        bundled_pkg = os.path.join(sys._MEIPASS, "cyber_pulse", "static")
        if os.path.exists(bundled_pkg):
            return bundled_pkg
        bundled_root = os.path.join(sys._MEIPASS, "static")
        if os.path.exists(bundled_root):
            return bundled_root

    # 2. Package directory
    pkg_static = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    if os.path.exists(pkg_static):
        return pkg_static

    # 3. Root directory if running from source tree
    parent_static = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
    if os.path.exists(parent_static):
        return parent_static

    # 4. Current working directory
    cwd_static = os.path.join(os.getcwd(), "static")
    if os.path.exists(cwd_static):
        return cwd_static

    return pkg_static


STATIC_DIR = get_static_dir()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(
            f"<h1>CYBER_PULSE Web HUD Error</h1><p>Static file not found at: {index_path}</p>",
            status_code=404
        )
    return FileResponse(index_path)


@app.get("/api/stats")
async def get_stats():
    return collector.get_stats()


@app.get("/api/summary")
async def get_summary_metrics():
    stats = collector.get_stats()
    return {
        "status": "active",
        "cpu_percent": stats.get("cpu", {}).get("total", 0.0),
        "ram_percent": stats.get("ram", {}).get("percent", 0.0),
        "disk_percent": stats.get("disk", {}).get("percent", 0.0),
        "network_sent_mb": stats.get("network", {}).get("sent_mb", 0.0),
        "network_recv_mb": stats.get("network", {}).get("recv_mb", 0.0),
        "timestamp": time.time()
    }


@app.post("/api/kill/{pid}")
async def kill_process(pid: int):
    return collector.terminate_process(pid)


@app.post("/api/purge_memory")
async def purge_memory():
    return collector.purge_memory()


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()

    async def client_listener():
        try:
            while True:
                msg_text = await websocket.receive_text()
                try:
                    msg = json.loads(msg_text)
                    action = msg.get("action")
                    if action == "kill":
                        pid = int(msg.get("pid", 0))
                        res = collector.terminate_process(pid)
                        await websocket.send_json({"type": "kill_result", "payload": res})
                    elif action == "purge_memory":
                        res = collector.purge_memory()
                        await websocket.send_json({"type": "purge_result", "payload": res})
                except Exception as ex:
                    print("[!] Error handling client websocket message:", ex)
        except (WebSocketDisconnect, Exception):
            pass

    import asyncio
    listener_task = asyncio.create_task(client_listener())

    try:
        while True:
            stats = collector.get_stats()
            await websocket.send_json({"type": "telemetry", "payload": stats})
            await asyncio.sleep(0.8)
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    finally:
        listener_task.cancel()


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def wait_for_server(host: str, port: int, timeout: float = 6.0) -> bool:
    target_host = "127.0.0.1" if host == "0.0.0.0" else host
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            with socket.create_connection((target_host, port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


_server_thread = None
_server_started = False
_server_lock = threading.Lock()


def run_server(host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_level="warning")


def start_server_background(host: str = "0.0.0.0", port: int = 8888) -> bool:
    global _server_thread, _server_started
    with _server_lock:
        if _server_started or wait_for_server(host, port, timeout=0.3):
            _server_started = True
            return True
        try:
            config = uvicorn.Config(app, host=host, port=port, log_level="error")
            server = uvicorn.Server(config)
            server.install_signal_handlers = lambda: None
            _server_thread = threading.Thread(target=server.run, daemon=True)
            _server_thread.start()
            if wait_for_server(host, port, timeout=5.0):
                _server_started = True
                return True
        except Exception:
            pass
        return _server_started


def launch_web(mode: str = "browser", host: str = "0.0.0.0", port: int = 8888):
    url = f"http://127.0.0.1:{port}"
    lan_ip = get_local_ip()
    lan_url = f"http://{lan_ip}:{port}"

    print("\033[38;2;0;240;255m[+] CYBER_PULSE // NEURAL_HUD v2.0 ENGAGED\033[0m")
    print(f"\033[38;2;255;0;128m>> LOCAL LINK : {url}\033[0m")
    print(f"\033[38;2;252;238;10m>> NEURAL LAN  : {lan_url}\033[0m")

    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()

    if not wait_for_server(host, port):
        print(f"\033[38;2;255;34;85m[!] Timed out waiting for server to bind port {port}.\033[0m")

    if mode == "browser":
        webbrowser.open(url)
        print("\033[38;2;0;255;102m[+] Browser opened. Press Ctrl+C to terminate.\033[0m")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Disconnected.")

    elif mode == "server":
        print(f"\033[38;2;0;255;102m[+] Server active in background. Open {url} or {lan_url} in any browser.\033[0m")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Server stopped.")

    elif mode == "window":
        try:
            import webview
            print("\033[38;2;0;255;102m[+] Initializing Cyber Desktop HUD Window...\033[0m")
            window = webview.create_window(
                title="CYBER_PULSE // NEURAL_HUD v2.0",
                url=url,
                width=1380,
                height=880,
                min_size=(960, 640),
                background_color="#05070f"
            )
            webview.start()
        except Exception as e:
            print(f"\033[38;2;255;34;85m[!] Desktop window fallback to browser: {e}\033[0m")
            webbrowser.open(url)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[!] Disconnected.")


def main():
    parser = argparse.ArgumentParser(description="CYBER_PULSE // Futuristic Cyberpunk System Monitor")
    parser.add_argument(
        "--mode",
        choices=["window", "browser", "server", "cli"],
        default="window",
        help="Display mode: window (Desktop App), browser (Web HUD), server (Headless LAN), or cli (Terminal HUD)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
    parser.add_argument("--port", type=int, default=8888, help="Port to listen on")
    args = parser.parse_args()

    if args.mode == "cli":
        cli_hud.run_cli_hud()
        return

    launch_web(mode=args.mode, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
