// ==========================================================================
// CYBER_PULSE // NEURAL_APP - TELEMETRY & VISUALIZATION ENGINE
// ==========================================================================

let ws = null;
let currentStats = null;
let networkHistory = { rx: new Array(40).fill(0), tx: new Array(40).fill(0) };
let cpuHistory = new Array(40).fill(0);
let targetToKill = null;
let processSortBy = 'mem';
let processFilter = '';
let gaugeRotationAngle = 0;

// Initialize on DOM Loaded
document.addEventListener('DOMContentLoaded', () => {
  initWebSocket();
  initEventListeners();
  initThemeSelector();
  initLanguageSelector();
  animateGaugesLoop();

  // Try playing startup chime on first click
  window.addEventListener('click', () => {
    if (window.cyberAudio && !window.cyberAudio.initialized) {
      window.cyberAudio.playBoot();
    }
  }, { once: true });
});

// ==========================================================================
// WEBSOCKET TELEMETRY
// ==========================================================================
function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('[+] Neural link established with backend.');
    updateConnectionStatus(true);
    showToast('NEURAL LINK ONLINE // DATA SYNCHRONIZED');
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === 'telemetry') {
        currentStats = data.payload;
        renderTelemetry(currentStats);
      } else if (data.type === 'purge_result') {
        handlePurgeResult(data.payload);
      } else if (data.type === 'kill_result') {
        handleKillResult(data.payload);
      }
    } catch (e) {
      console.error('Error parsing telemetry frame:', e);
    }
  };

  ws.onclose = () => {
    updateConnectionStatus(false);
    setTimeout(initWebSocket, 2000);
  };

  ws.onerror = () => {
    updateConnectionStatus(false);
  };
}

function updateConnectionStatus(isOnline) {
  const dot = document.getElementById('status-dot');
  const txt = document.getElementById('status-text');
  if (isOnline) {
    dot.style.backgroundColor = 'var(--neon-green)';
    dot.style.boxShadow = '0 0 10px var(--neon-green)';
    txt.textContent = 'ONLINE';
  } else {
    dot.style.backgroundColor = 'var(--neon-magenta)';
    dot.style.boxShadow = '0 0 10px var(--neon-magenta)';
    txt.textContent = 'LINK SEVERED';
  }
}

// ==========================================================================
// RENDER TELEMETRY DATA
// ==========================================================================
function renderTelemetry(stats) {
  if (!stats) return;

  const sys = stats.system;
  const cpu = stats.cpu;
  const mem = stats.memory;
  const net = stats.network;
  const disks = stats.disks;
  const gpus = stats.gpus;

  // 1. Header & Threat Level
  document.getElementById('sys-host').textContent = sys.hostname;
  document.getElementById('sys-os').textContent = sys.os;
  document.getElementById('sys-uptime').textContent = formatUptime(sys.uptime_sec);

  const threatBadge = document.getElementById('threat-badge');
  const isCritical = cpu.total_percent >= 85 || mem.percent >= 85;
  const isElevated = cpu.total_percent >= 60 || mem.percent >= 70;

  if (isCritical) {
    threatBadge.textContent = 'DEFCON 1: CRITICAL OVERLOAD';
    threatBadge.className = 'threat-badge critical';
    if (window.cyberAudio && Math.random() > 0.7) window.cyberAudio.playAlert();
  } else if (isElevated) {
    threatBadge.textContent = 'DEFCON 3: ELEVATED LOAD';
    threatBadge.className = 'threat-badge elevated';
  } else {
    threatBadge.textContent = 'DEFCON 5: OPTIMAL / NOMINAL';
    threatBadge.className = 'threat-badge';
  }

  // 2. CPU Readouts & Per-Core Grid
  document.getElementById('cpu-val').textContent = cpu.total_percent.toFixed(1) + '%';
  document.getElementById('cpu-sub').textContent = `${cpu.cores_physical}P / ${cpu.cores_logical}T @ ${cpu.freq_current_mhz} MHz`;
  renderCpuCores(cpu.per_core);

  // 3. Memory Readouts & Bars
  document.getElementById('ram-val').textContent = mem.percent.toFixed(1) + '%';
  document.getElementById('ram-sub').textContent = `${mem.used_gb.toFixed(1)} / ${mem.total_gb.toFixed(1)} GB`;
  document.getElementById('ram-bar-fill').style.width = `${mem.percent}%`;
  document.getElementById('ram-used-text').textContent = `${mem.used_gb.toFixed(1)} GB`;
  document.getElementById('ram-free-text').textContent = `${mem.available_gb.toFixed(1)} GB`;
  document.getElementById('swap-bar-fill').style.width = `${mem.swap_percent}%`;
  document.getElementById('swap-val-text').textContent = `${mem.swap_used_gb.toFixed(1)} / ${mem.swap_total_gb.toFixed(1)} GB`;

  // 4. GPU Readouts
  const gpuCard = document.getElementById('gpu-card');
  if (gpus && gpus.length > 0) {
    gpuCard.style.display = 'flex';
    const gpu = gpus[0];
    document.getElementById('gpu-val').textContent = gpu.utilization_gpu.toFixed(0) + '%';
    document.getElementById('gpu-sub').textContent = `${gpu.temperature.toFixed(0)}?C | ${gpu.power_draw.toFixed(1)}W`;
    document.getElementById('gpu-vram-text').textContent = `${gpu.memory_used.toFixed(0)} / ${gpu.memory_total.toFixed(0)} MB`;
    const vramPct = gpu.memory_total > 0 ? (gpu.memory_used / gpu.memory_total) * 100 : 0;
    document.getElementById('gpu-vram-bar').style.width = `${vramPct}%`;
    document.getElementById('gpu-name-tag').textContent = gpu.name;
  } else {
    gpuCard.style.display = 'none';
  }

  // 5. Storage / Disks
  renderDisks(disks);

  // 6. Network Telemetry & History Buffer
  networkHistory.rx.push(net.rx_kb_sec);
  networkHistory.rx.shift();
  networkHistory.tx.push(net.tx_kb_sec);
  networkHistory.tx.shift();

  document.getElementById('net-dl-speed').textContent = `${net.rx_kb_sec.toFixed(1)} KB/s`;
  document.getElementById('net-ul-speed').textContent = `${net.tx_kb_sec.toFixed(1)} KB/s`;
  document.getElementById('net-total-rx').textContent = `${net.total_recv_mb} MB`;
  document.getElementById('net-total-tx').textContent = `${net.total_sent_mb} MB`;
  document.getElementById('net-conns').textContent = `${net.connections_established} established`;

  // CPU History Buffer
  cpuHistory.push(cpu.total_percent);
  cpuHistory.shift();

  // 7. Render Oscilloscope Canvases
  drawNetworkWaveform();
  drawCpuWaveform();

  // 8. Process Matrix Table
  renderProcessTable(stats.processes);
}

// ==========================================================================
// HOLOGRAPHIC CIRCULAR GAUGES RENDERING
// ==========================================================================
function drawHoloGauge(canvasId, percent, primaryColor, glowColor) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width = 180;
  const h = canvas.height = 180;
  const cx = w / 2;
  const cy = h / 2;
  const radius = 68;

  ctx.clearRect(0, 0, w, h);

  // Background track ring
  ctx.beginPath();
  ctx.arc(cx, cy, radius, 0, Math.PI * 2);
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
  ctx.lineWidth = 6;
  ctx.stroke();

  // Outer segmented tick circle
  const tickCount = 48;
  for (let i = 0; i < tickCount; i++) {
    const angle = (i / tickCount) * Math.PI * 2;
    const r1 = radius + 11;
    const r2 = radius + (i % 4 === 0 ? 17 : 14);
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(angle) * r1, cy + Math.sin(angle) * r1);
    ctx.lineTo(cx + Math.cos(angle) * r2, cy + Math.sin(angle) * r2);
    ctx.strokeStyle = (i / tickCount) * 100 <= percent ? primaryColor : 'rgba(255, 255, 255, 0.12)';
    ctx.lineWidth = i % 4 === 0 ? 2 : 1;
    ctx.stroke();
  }

  // Outer rotating targeting reticle brackets
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(gaugeRotationAngle);
  for (let b = 0; b < 3; b++) {
    const startA = (b * (Math.PI * 2 / 3));
    ctx.beginPath();
    ctx.arc(0, 0, radius + 20, startA, startA + 0.35);
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  ctx.restore();

  // Active glowing progress arc
  const startAngle = -Math.PI / 2;
  const endAngle = startAngle + (Math.PI * 2 * (Math.min(100, Math.max(0, percent)) / 100));

  ctx.save();
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = 14;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, startAngle, endAngle);
  ctx.strokeStyle = primaryColor;
  ctx.lineWidth = 7;
  ctx.lineCap = 'butt';
  ctx.stroke();
  ctx.restore();
}

function animateGaugesLoop() {
  gaugeRotationAngle += 0.015;

  if (currentStats) {
    const cyan = getComputedStyle(document.body).getPropertyValue('--neon-cyan').trim() || '#00f0ff';
    const cyanGlow = getComputedStyle(document.body).getPropertyValue('--neon-cyan-glow').trim() || 'rgba(0, 240, 255, 0.5)';
    const magenta = getComputedStyle(document.body).getPropertyValue('--neon-magenta').trim() || '#ff0055';
    const magentaGlow = getComputedStyle(document.body).getPropertyValue('--neon-magenta-glow').trim() || 'rgba(255, 0, 85, 0.5)';
    const yellow = getComputedStyle(document.body).getPropertyValue('--neon-yellow').trim() || '#fcee0a';
    const yellowGlow = getComputedStyle(document.body).getPropertyValue('--neon-yellow-glow').trim() || 'rgba(252, 238, 10, 0.5)';

    // CPU Gauge color shift based on load
    let cpuColor = cyan;
    let cpuGlow = cyanGlow;
    if (currentStats.cpu.total_percent >= 85) {
      cpuColor = magenta;
      cpuGlow = magentaGlow;
    } else if (currentStats.cpu.total_percent >= 60) {
      cpuColor = yellow;
      cpuGlow = yellowGlow;
    }

    drawHoloGauge('gauge-cpu', currentStats.cpu.total_percent, cpuColor, cpuGlow);
    drawHoloGauge('gauge-ram', currentStats.memory.percent, cyan, cyanGlow);

    if (currentStats.gpus && currentStats.gpus.length > 0) {
      drawHoloGauge('gauge-gpu', currentStats.gpus[0].utilization_gpu, magenta, magentaGlow);
    }

    if (currentStats.disks.partitions.length > 0) {
      drawHoloGauge('gauge-disk', currentStats.disks.partitions[0].percent, yellow, yellowGlow);
    }
  }

  requestAnimationFrame(animateGaugesLoop);
}

// ==========================================================================
// PER CORE EQUALIZER BARS
// ==========================================================================
function renderCpuCores(perCore) {
  const container = document.getElementById('cpu-cores-grid');
  if (!container) return;

  if (container.children.length !== perCore.length) {
    container.innerHTML = '';
    perCore.forEach((val, i) => {
      const col = document.createElement('div');
      col.className = 'core-bar-wrapper';
      col.title = `Core ${i}: ${val}%`;
      const fill = document.createElement('div');
      fill.className = 'core-bar-fill';
      fill.id = `core-fill-${i}`;
      col.appendChild(fill);
      container.appendChild(col);
    });
  }

  perCore.forEach((val, i) => {
    const fill = document.getElementById(`core-fill-${i}`);
    if (fill) {
      fill.style.height = `${Math.max(4, val)}%`;
      if (val >= 85) {
        fill.style.background = 'var(--neon-magenta)';
      } else if (val >= 60) {
        fill.style.background = 'var(--neon-yellow)';
      } else {
        fill.style.background = 'linear-gradient(0deg, var(--neon-cyan), var(--neon-magenta))';
      }
    }
  });
}

// ==========================================================================
// DISKS RENDERING
// ==========================================================================
function renderDisks(disks) {
  const container = document.getElementById('disks-container');
  if (!container) return;

  let html = '';
  disks.partitions.forEach(p => {
    html += `
      <div class="disk-item">
        <div class="disk-meta">
          <span><b>${p.mountpoint}</b> (${p.fstype})</span>
          <span>${p.used_gb} / ${p.total_gb} GB (${p.percent}%)</span>
        </div>
        <div class="sub-bar-track">
          <div class="sub-bar-progress yellow" style="width: ${p.percent}%"></div>
        </div>
      </div>
    `;
  });

  html += `
    <div class="io-badge-group">
      <span>DISK READ: <b style="color:var(--neon-cyan);">${disks.read_mb_sec.toFixed(2)} MB/s</b></span>
      <span>DISK WRITE: <b style="color:var(--neon-magenta);">${disks.write_mb_sec.toFixed(2)} MB/s</b></span>
    </div>
  `;

  container.innerHTML = html;
}

// ==========================================================================
// REAL-TIME OSCILLOSCOPE WAVEFORMS
// ==========================================================================
function drawNetworkWaveform() {
  const canvas = document.getElementById('net-waveform-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width = canvas.parentElement.clientWidth;
  const h = canvas.height = 150;

  ctx.clearRect(0, 0, w, h);
  drawGridLines(ctx, w, h);

  const maxRate = Math.max(...networkHistory.rx, ...networkHistory.tx, 50);

  // Draw Download Waveform (Cyan)
  drawWaveLine(ctx, networkHistory.rx, maxRate, w, h, 'rgba(0, 240, 255, 1)', 'rgba(0, 240, 255, 0.15)');

  // Draw Upload Waveform (Magenta)
  drawWaveLine(ctx, networkHistory.tx, maxRate, w, h, 'rgba(255, 0, 85, 1)', 'rgba(255, 0, 85, 0.15)');
}

function drawCpuWaveform() {
  const canvas = document.getElementById('cpu-waveform-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width = canvas.parentElement.clientWidth;
  const h = canvas.height = 150;

  ctx.clearRect(0, 0, w, h);
  drawGridLines(ctx, w, h);

  drawWaveLine(ctx, cpuHistory, 100, w, h, 'rgba(0, 255, 102, 1)', 'rgba(0, 255, 102, 0.18)');
}

function drawGridLines(ctx, w, h) {
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  const stepX = w / 10;
  const stepY = h / 4;

  for (let x = 0; x <= w; x += stepX) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y <= h; y += stepY) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
}

function drawWaveLine(ctx, dataArr, maxVal, w, h, strokeColor, fillColor) {
  if (dataArr.length < 2) return;
  const stepX = w / (dataArr.length - 1);

  ctx.save();
  ctx.beginPath();
  dataArr.forEach((val, i) => {
    const x = i * stepX;
    const y = h - (val / maxVal) * (h - 15) - 5;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.strokeStyle = strokeColor;
  ctx.lineWidth = 2;
  ctx.shadowColor = strokeColor;
  ctx.shadowBlur = 8;
  ctx.stroke();

  // Fill gradient under curve
  ctx.lineTo(w, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  ctx.fillStyle = fillColor;
  ctx.fill();
  ctx.restore();
}

// ==========================================================================
// TARGET SURVEILLANCE / PROCESS MATRIX
// ==========================================================================
function renderProcessTable(processes) {
  const tbody = document.getElementById('process-table-body');
  if (!tbody || !processes) return;

  let filtered = processes.filter(p => {
    if (!processFilter) return true;
    return p.name.toLowerCase().includes(processFilter.toLowerCase()) || String(p.pid).includes(processFilter);
  });

  if (processSortBy === 'cpu') {
    filtered.sort((a, b) => b.cpu_percent - a.cpu_percent);
  } else {
    filtered.sort((a, b) => b.memory_percent - a.memory_percent);
  }

  let html = '';
  filtered.forEach(p => {
    html += `
      <tr>
        <td style="color:var(--neon-cyan); font-weight:700;">#${p.pid}</td>
        <td style="color:#fff;">${escapeHtml(p.name)}</td>
        <td style="color:${p.cpu_percent > 20 ? 'var(--neon-magenta)' : 'inherit'}; font-weight:700;">${p.cpu_percent.toFixed(1)}%</td>
        <td style="font-weight:700;">${p.memory_percent.toFixed(1)}%</td>
        <td>${p.memory_rss_mb.toFixed(1)} MB</td>
        <td><span style="color:var(--neon-green)">${p.status}</span></td>
        <td>
          <button class="btn-kill" onclick="confirmKillTarget(${p.pid}, '${escapeHtml(p.name)}')">[ TERMINATE ]</button>
        </td>
      </tr>
    `;
  });

  tbody.innerHTML = html;
}

window.confirmKillTarget = function(pid, name) {
  targetToKill = { pid, name };
  document.getElementById('modal-target-info').textContent = `[PID: ${pid}] - ${name}`;
  document.getElementById('kill-modal').classList.add('open');
  if (window.cyberAudio) window.cyberAudio.playAlert();
};

window.abortKill = function() {
  targetToKill = null;
  document.getElementById('kill-modal').classList.remove('open');
  if (window.cyberAudio) window.cyberAudio.playClick();
};

window.executeKill = function() {
  if (!targetToKill) return;
  const { pid } = targetToKill;
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'kill', pid }));
  } else {
    fetch(`/api/kill/${pid}`, { method: 'POST' })
      .then(res => res.json())
      .then(handleKillResult);
  }
  document.getElementById('kill-modal').classList.remove('open');
};

function handleKillResult(res) {
  if (res.success) {
    showToast(res.message);
    if (window.cyberAudio) window.cyberAudio.playPurge();
  } else {
    showToast(`PURGE FAILED: ${res.message}`);
  }
}

// ==========================================================================
// CYBER ACTIONS & CONTROLS
// ==========================================================================
function initEventListeners() {
  // Overclock Boost Button
  const btnOverclock = document.getElementById('btn-overclock');
  if (btnOverclock) {
    btnOverclock.addEventListener('click', () => {
      document.body.classList.add('hyperdrive');
      if (window.cyberAudio) window.cyberAudio.playOverclock();
      showToast('HYPER-CLOCK ACTIVE // PROTOCOL 99 ENGAGED');

      const threatBadge = document.getElementById('threat-badge');
      const originalText = threatBadge.textContent;
      threatBadge.textContent = 'DEFCON 1: HYPER-CLOCK ENGAGED';
      threatBadge.className = 'threat-badge critical';

      setTimeout(() => {
        document.body.classList.remove('hyperdrive');
        threatBadge.textContent = originalText;
        showToast('OVERCLOCK STABILIZED // RETURNING TO NOMINAL');
      }, 5000);
    });
  }

  // Neural Flush Button
  const btnPurge = document.getElementById('btn-purge');
  if (btnPurge) {
    btnPurge.addEventListener('click', () => {
      if (window.cyberAudio) window.cyberAudio.playPurge();
      const beam = document.getElementById('scanbeam');
      beam.classList.add('active');
      setTimeout(() => beam.classList.remove('active'), 1200);

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'purge_memory' }));
      } else {
        fetch('/api/purge_memory', { method: 'POST' })
          .then(res => res.json())
          .then(handlePurgeResult);
      }
    });
  }

  // Diagnostic Report Button
  const btnReport = document.getElementById('btn-report');
  if (btnReport) {
    btnReport.addEventListener('click', () => {
      if (window.cyberAudio) window.cyberAudio.playClick();
      generateDiagnosticReport();
    });
  }

  // Audio Toggle Button
  const btnAudio = document.getElementById('btn-audio-toggle');
  if (btnAudio) {
    btnAudio.addEventListener('click', () => {
      const enabled = window.cyberAudio.toggle();
      btnAudio.textContent = enabled ? 'SFX: ON' : 'SFX: OFF';
      btnAudio.style.borderColor = enabled ? 'var(--neon-cyan)' : 'var(--text-dim)';
      if (enabled) window.cyberAudio.playClick();
    });
  }

  // Scanline Toggle Button
  const btnScan = document.getElementById('btn-scanlines-toggle');
  if (btnScan) {
    btnScan.addEventListener('click', () => {
      document.body.classList.toggle('no-scanlines');
      const active = !document.body.classList.contains('no-scanlines');
      btnScan.textContent = active ? 'CRT: ON' : 'CRT: OFF';
      if (window.cyberAudio) window.cyberAudio.playClick();
    });
  }

  // Matrix Rain Toggle Button
  const btnMatrix = document.getElementById('btn-matrix-toggle');
  if (btnMatrix) {
    btnMatrix.addEventListener('click', () => {
      if (window.toggleMatrixRain) {
        const active = window.toggleMatrixRain();
        btnMatrix.textContent = active ? 'RAIN: ON' : 'RAIN: OFF';
      }
      if (window.cyberAudio) window.cyberAudio.playClick();
    });
  }

  // Fullscreen Button
  const btnFs = document.getElementById('btn-fullscreen');
  if (btnFs) {
    btnFs.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
        btnFs.textContent = '? EXIT FS';
      } else {
        document.exitFullscreen().catch(() => {});
        btnFs.textContent = '? FULLSCREEN';
      }
      if (window.cyberAudio) window.cyberAudio.playClick();
    });
  }

  // Process Filter Input
  const filterInput = document.getElementById('process-search');
  if (filterInput) {
    filterInput.addEventListener('input', (e) => {
      processFilter = e.target.value.trim();
      if (currentStats) renderProcessTable(currentStats.processes);
    });
  }

  // Sort buttons
  const sortCpuBtn = document.getElementById('sort-cpu-btn');
  const sortMemBtn = document.getElementById('sort-mem-btn');
  if (sortCpuBtn && sortMemBtn) {
    sortCpuBtn.addEventListener('click', () => {
      processSortBy = 'cpu';
      sortCpuBtn.classList.add('btn-magenta');
      sortMemBtn.classList.remove('btn-magenta');
      if (window.cyberAudio) window.cyberAudio.playClick();
      if (currentStats) renderProcessTable(currentStats.processes);
    });
    sortMemBtn.addEventListener('click', () => {
      processSortBy = 'mem';
      sortMemBtn.classList.add('btn-magenta');
      sortCpuBtn.classList.remove('btn-magenta');
      if (window.cyberAudio) window.cyberAudio.playClick();
      if (currentStats) renderProcessTable(currentStats.processes);
    });
  }
}

function handlePurgeResult(res) {
  showToast(res.message);
}

function generateDiagnosticReport() {
  if (!currentStats) return;
  const sys = currentStats.system;
  const cpu = currentStats.cpu;
  const mem = currentStats.memory;
  const net = currentStats.network;

  const report = `
=====================================================
// CYBER_PULSE DIAGNOSTIC REPORT // NODE-77
// TIMESTAMP: ${new Date().toISOString()}
=====================================================
HOST IDENT:     ${sys.hostname}
OPERATING SYS:  ${sys.os} (${sys.arch})
ACTIVE UPTIME:  ${formatUptime(sys.uptime_sec)}

[CORE CPU TELEMETRY]
Total Load:     ${cpu.total_percent.toFixed(1)}%
Cores Physical: ${cpu.cores_physical} | Logical: ${cpu.cores_logical}
Frequency:      ${cpu.freq_current_mhz} MHz / Max: ${cpu.freq_max_mhz} MHz

[NEURAL MEMORY MATRIX]
RAM Total:      ${mem.total_gb.toFixed(2)} GB
RAM In-Use:     ${mem.used_gb.toFixed(2)} GB (${mem.percent.toFixed(1)}%)
RAM Free:       ${mem.available_gb.toFixed(2)} GB
Swap Usage:     ${mem.swap_used_gb.toFixed(2)} / ${mem.swap_total_gb.toFixed(2)} GB (${mem.swap_percent.toFixed(1)}%)

[NETWORK TELEMETRY]
Downlink Speed: ${net.rx_kb_sec.toFixed(2)} KB/s (Total RX: ${net.total_recv_mb} MB)
Uplink Speed:   ${net.tx_kb_sec.toFixed(2)} KB/s (Total TX: ${net.total_sent_mb} MB)
Connections:    ${net.connections_established} established

STATUS:         OPTIMAL // DEFCON 5
=====================================================
`;

  navigator.clipboard.writeText(report.trim()).then(() => {
    showToast('DIAGNOSTIC REPORT COPIED TO CLIPBOARD');
  }).catch(() => {
    showToast('REPORT GENERATED (CLIPBOARD ACCESS DENIED)');
  });
}


const I18N_WEB = {
  'zh-CN': {
    title: '机体生命征象<span>诊断仪</span>',
    nodeBadge: 'NODE-77 // 诊断仪 v2.0',
    sfx: '音效: ',
    crt: 'CRT: ',
    rain: '数字雨: ',
    full: '⛶ 全屏显示',
    toastLang: '语言已切换 // 简体中文'
  },
  'zh-TW': {
    title: '機體生命徵象<span>診斷儀</span>',
    nodeBadge: 'NODE-77 // 診斷儀 v2.0',
    sfx: '音效: ',
    crt: 'CRT: ',
    rain: '數位雨: ',
    full: '⛶ 全螢幕顯示',
    toastLang: '語言已切換 // 繁體中文'
  },
  'en': {
    title: 'SOMATIC VITAL SIGNS <span>MONITOR</span>',
    nodeBadge: 'NODE-77 // HUD v2.0',
    sfx: 'SFX: ',
    crt: 'CRT: ',
    rain: 'RAIN: ',
    full: '⛶ FULLSCREEN',
    toastLang: 'LANGUAGE SWITCHED // ENGLISH'
  },
  'ja': {
    title: '機体生命兆候<span>診断装置</span>',
    nodeBadge: 'NODE-77 // 診断機 v2.0',
    sfx: '効果音: ',
    crt: 'CRT: ',
    rain: 'デジタル雨: ',
    full: '⛶ フルスクリーン',
    toastLang: '言語を切り替えました // 日本語'
  }
};

function initLanguageSelector() {
  const langSelect = document.getElementById('lang-select');
  if (!langSelect) return;

  langSelect.addEventListener('change', (e) => {
    const lang = e.target.value;
    applyLanguage(lang);
    if (window.cyberAudio) window.cyberAudio.playClick();
  });
}

function applyLanguage(lang) {
  const dict = I18N_WEB[lang] || I18N_WEB['zh-CN'];
  const logo = document.getElementById('logo-text');
  if (logo) logo.innerHTML = dict.title;

  const nodeBadge = document.querySelector('.node-badge');
  if (nodeBadge) nodeBadge.textContent = dict.nodeBadge;

  const btnFull = document.getElementById('btn-fullscreen');
  if (btnFull) btnFull.textContent = dict.full;

  showToast(dict.toastLang);
}

function initThemeSelector() {
  const themeSelect = document.getElementById('theme-select');
  if (!themeSelect) return;

  themeSelect.addEventListener('change', (e) => {
    const val = e.target.value;
    document.body.className = '';
    if (val !== 'cyberpunk') {
      document.body.classList.add(`theme-${val}`);
    }
    if (window.cyberAudio) window.cyberAudio.playClick();
    showToast(`THEME APPLIED // ${val.toUpperCase()}`);
  });
}

// ==========================================================================
// UTILITIES
// ==========================================================================
function formatUptime(secs) {
  const d = Math.floor(secs / 86400);
  const h = Math.floor((secs % 86400) / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  if (d > 0) return `${d}d ${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  return `${pad(h)}:${pad(m)}:${pad(s)}`;
}

function pad(n) {
  return n < 10 ? '0' + n : n;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

let toastTimer = null;
function showToast(msg) {
  const toast = document.getElementById('cyber-toast');
  if (!toast) return;
  toast.textContent = `[+] ${msg}`;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, 3200);
}
