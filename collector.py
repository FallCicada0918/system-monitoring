import os
import sys
import time
import psutil
import platform
import subprocess
import threading
import gc
from typing import Dict, Any, List, Optional

CAN_EMPTY_WORKING_SET = False
if sys.platform == 'win32':
    try:
        import ctypes
        from ctypes import wintypes
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.EmptyWorkingSet.argtypes = [wintypes.HANDLE]
        psapi.EmptyWorkingSet.restype = wintypes.BOOL
        CAN_EMPTY_WORKING_SET = True
    except Exception:
        CAN_EMPTY_WORKING_SET = False


class SystemCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._running = True

        self._last_time = time.time()
        self._last_net = psutil.net_io_counters()
        self._last_disk = psutil.disk_io_counters()

        self._last_gpu_check = 0.0
        self._cached_gpu = []

        self._top_processes = []
        self._process_worker_thread = threading.Thread(target=self._process_worker, daemon=True)
        self._process_worker_thread.start()

        psutil.cpu_percent(interval=None, percpu=True)
        psutil.cpu_percent(interval=None)

    def _query_nvidia_smi(self):
        now = time.time()
        if now - self._last_gpu_check < 2.0:
            return self._cached_gpu

        self._last_gpu_check = now
        if hasattr(self, '_nvidia_available') and not self._nvidia_available:
            return []

        try:
            cmd = [
                'nvidia-smi',
                '--query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,power.draw',
                '--format=csv,noheader,nounits'
            ]
            flags = 0
            if sys.platform == 'win32':
                flags = subprocess.CREATE_NO_WINDOW
            out = subprocess.check_output(cmd, encoding='utf-8', errors='ignore', timeout=1.0, creationflags=flags).strip()
            lines = [l.strip() for l in out.split('\n') if l.strip()]
            gpus = []
            for line in lines:
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 8:
                    gpus.append({
                        'name': parts[0],
                        'temperature': float(parts[1]) if parts[1] != '[N/A]' else 0.0,
                        'utilization_gpu': float(parts[2]) if parts[2] != '[N/A]' else 0.0,
                        'utilization_mem': float(parts[3]) if parts[3] != '[N/A]' else 0.0,
                        'memory_total': float(parts[4]) if parts[4] != '[N/A]' else 0.0,
                        'memory_used': float(parts[5]) if parts[5] != '[N/A]' else 0.0,
                        'memory_free': float(parts[6]) if parts[6] != '[N/A]' else 0.0,
                        'power_draw': float(parts[7]) if parts[7] != '[N/A]' else 0.0,
                    })
            self._cached_gpu = gpus
            self._nvidia_available = True
            return gpus
        except Exception:
            self._nvidia_available = False
            self._cached_gpu = []
            return []

    def _process_worker(self):
        while self._running:
            try:
                proc_list = []
                for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info', 'status']):
                    try:
                        info = p.info
                        mem_info = info.get('memory_info')
                        rss_mb = round(mem_info.rss / (1024 * 1024), 1) if mem_info else 0.0
                        proc_list.append({
                            'pid': info['pid'],
                            'name': info['name'] or 'Unknown',
                            'cpu_percent': round(info.get('cpu_percent') or 0.0, 1),
                            'memory_percent': round(info.get('memory_percent') or 0.0, 1),
                            'memory_rss_mb': rss_mb,
                            'status': info.get('status') or 'running'
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue

                top_by_mem = sorted(proc_list, key=lambda x: (x['memory_percent'], x['cpu_percent']), reverse=True)[:25]
                with self._lock:
                    self._top_processes = top_by_mem
            except Exception:
                pass
            time.sleep(2.0)

    def get_stats(self):
        now = time.time()
        dt = max(now - self._last_time, 0.001)

        cpu_total = psutil.cpu_percent(interval=None)
        cpu_cores = psutil.cpu_percent(percpu=True, interval=None)
        cpu_freq = psutil.cpu_freq()
        freq_current = round(cpu_freq.current, 1) if cpu_freq else 0.0
        freq_max = round(cpu_freq.max, 1) if cpu_freq else 0.0

        vmem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        disk_partitions = []
        for p in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(p.mountpoint)
                disk_partitions.append({
                    'device': p.device,
                    'mountpoint': p.mountpoint,
                    'fstype': p.fstype,
                    'total_gb': round(usage.total / (1024 ** 3), 1),
                    'used_gb': round(usage.used / (1024 ** 3), 1),
                    'free_gb': round(usage.free / (1024 ** 3), 1),
                    'percent': usage.percent
                })
            except (PermissionError, OSError):
                continue

        curr_disk = psutil.disk_io_counters()
        if curr_disk and self._last_disk:
            disk_read_bytes_sec = max(0.0, (curr_disk.read_bytes - self._last_disk.read_bytes) / dt)
            disk_write_bytes_sec = max(0.0, (curr_disk.write_bytes - self._last_disk.write_bytes) / dt)
        else:
            disk_read_bytes_sec = 0.0
            disk_write_bytes_sec = 0.0
        self._last_disk = curr_disk

        curr_net = psutil.net_io_counters()
        if curr_net and self._last_net:
            net_rx_sec = max(0.0, (curr_net.bytes_recv - self._last_net.bytes_recv) / dt)
            net_tx_sec = max(0.0, (curr_net.bytes_sent - self._last_net.bytes_sent) / dt)
        else:
            net_rx_sec = 0.0
            net_tx_sec = 0.0
        self._last_net = curr_net
        self._last_time = now

        try:
            conns = psutil.net_connections(kind='inet')
            conns_count = len(conns)
            established_count = sum(1 for c in conns if c.status == 'ESTABLISHED')
        except Exception:
            conns_count = 0
            established_count = 0

        boot_time = psutil.boot_time()
        uptime_sec = int(now - boot_time)

        gpus = self._query_nvidia_smi()

        with self._lock:
            processes = list(self._top_processes)

        return {
            'timestamp': now,
            'system': {
                'hostname': platform.node(),
                'os': f'{platform.system()} {platform.release()}',
                'os_version': platform.version(),
                'arch': platform.machine(),
                'uptime_sec': uptime_sec,
                'boot_time': boot_time,
                'python_version': platform.python_version()
            },
            'cpu': {
                'total_percent': cpu_total,
                'per_core': cpu_cores,
                'cores_physical': psutil.cpu_count(logical=False) or 0,
                'cores_logical': psutil.cpu_count(logical=True) or 0,
                'freq_current_mhz': freq_current,
                'freq_max_mhz': freq_max,
            },
            'memory': {
                'total_gb': round(vmem.total / (1024 ** 3), 2),
                'used_gb': round(vmem.used / (1024 ** 3), 2),
                'available_gb': round(vmem.available / (1024 ** 3), 2),
                'percent': vmem.percent,
                'swap_total_gb': round(swap.total / (1024 ** 3), 2),
                'swap_used_gb': round(swap.used / (1024 ** 3), 2),
                'swap_percent': swap.percent,
            },
            'disks': {
                'partitions': disk_partitions,
                'read_bytes_sec': disk_read_bytes_sec,
                'write_bytes_sec': disk_write_bytes_sec,
                'read_mb_sec': round(disk_read_bytes_sec / (1024 * 1024), 2),
                'write_mb_sec': round(disk_write_bytes_sec / (1024 * 1024), 2)
            },
            'network': {
                'rx_bytes_sec': net_rx_sec,
                'tx_bytes_sec': net_tx_sec,
                'rx_kb_sec': round(net_rx_sec / 1024, 2),
                'tx_kb_sec': round(net_tx_sec / 1024, 2),
                'total_recv_mb': round(curr_net.bytes_recv / (1024 * 1024), 1) if curr_net else 0,
                'total_sent_mb': round(curr_net.bytes_sent / (1024 * 1024), 1) if curr_net else 0,
                'connections_total': conns_count,
                'connections_established': established_count
            },
            'gpus': gpus,
            'processes': processes
        }

    def terminate_process(self, pid: int):
        if pid in (0, 4):
            return {'success': False, 'message': 'SECURITY ALERT: Critical kernel process cannot be terminated.'}
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.terminate()
            return {'success': True, 'message': f'PROCESS [{name}:{pid}] TERMINATION SIGNAL SENT.'}
        except psutil.NoSuchProcess:
            return {'success': False, 'message': f'Process PID {pid} not found.'}
        except psutil.AccessDenied:
            return {'success': False, 'message': f'Access denied: Insufficient privileges to terminate PID {pid}.'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}

    def purge_memory(self):
        vmem_before = psutil.virtual_memory().available
        gc.collect()

        trimmed_procs = 0
        if CAN_EMPTY_WORKING_SET and sys.platform == 'win32':
            try:
                kernel32 = ctypes.windll.kernel32
                psapi = ctypes.windll.psapi
                h = kernel32.GetCurrentProcess()
                psapi.EmptyWorkingSet(h)
                trimmed_procs += 1

                cur_pid = os.getpid()
                for p in psutil.process_iter(['pid']):
                    try:
                        pid = p.info.get('pid')
                        if not pid or pid in (0, 4) or pid == cur_pid:
                            continue
                        h_proc = kernel32.OpenProcess(0x0400 | 0x0100, False, pid)
                        if h_proc:
                            try:
                                if psapi.EmptyWorkingSet(h_proc):
                                    trimmed_procs += 1
                            finally:
                                kernel32.CloseHandle(h_proc)
                    except Exception:
                        continue
            except Exception:
                pass

        time.sleep(0.15)
        vmem_after = psutil.virtual_memory().available
        freed_mb = round((vmem_after - vmem_before) / (1024 * 1024), 1)
        if freed_mb > 0:
            msg = f"NEURAL PURGE COMPLETE // FREED {freed_mb:.1f} MB (TRIMMED {trimmed_procs} PROCS)"
        else:
            msg = f"NEURAL PURGE COMPLETE // {trimmed_procs} PROCESS WORKING SETS PURGED"
        return {
            'success': True,
            'freed_mb': max(0.0, freed_mb),
            'trimmed_procs': trimmed_procs,
            'message': msg
        }

    def stop(self):
        self._running = False
