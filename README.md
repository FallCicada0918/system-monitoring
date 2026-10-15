<div align="center">

# 机体生命征象诊断仪 (CYBER_PULSE v2.0)
### Somatic Vital Signs Diagnostic Monitor // 機体生命兆候診断装置 // 機體生命徵象診斷儀

[简体中文](#-简体中文) • [繁體中文](#-繁體中文) • [English](#-english) • [日本語](#-日本語)

<br/>

![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-00f0ff?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-00ff66?style=flat-square)
![Style](https://img.shields.io/badge/Style-Cyberpunk%20HUD-ff0055?style=flat-square)
![i18n](https://img.shields.io/badge/i18n-zh__CN%20%7C%20zh__TW%20%7C%20en%20%7C%20ja-fcee0a?style=flat-square)

</div>

---

## 🇨🇳 简体中文

### 1. 项目简介
**机体生命征象诊断仪（CYBER_PULSE v2.0）** 是一款基于 Python、FastAPI、WebSocket 和 HTML5 Canvas 构建的沉浸式跨平台系统监控与健康诊断终端。它将硬件遥测数据转化为充满科幻感与赛博朋克风格的全息监控界面，全面支持终端 CLI HUD 与现代化 Web HUD 两种交互形态。

### 2. 核心特性
- **终端交互式 HUD**：采用 ANSI/VT 科技边框渲染，提供 CPU 全核均衡器、内存/交换区矩阵、GPU 负载温度、磁盘 I/O 吞吐、网络雷达以及 Top 进程监听。
- **Web 全息仪表盘**：3D 全息旋转刻度盘、16 核心渐变波形、双通道示波雷达、CRT 扫描线及黑客帝国代码雨视觉特效。
- **全平台原生兼容**：同时适配 **Linux**、**macOS** 与 **Windows**。Unix 下利用 `termios/tty` 实现无阻塞单键响应，Windows 下调用 Win32 API 规避 QuickEdit 点击假死。
- **四语国际化 (i18n)**：完整支持 **简体中文 (`zh_CN`)**、**繁體中文 (`zh_TW`)**、**英语 (`en`)**、**日语 (`ja`)**，支持根据系统环境自动识别与运行中热切换。
- **离线音频合成引擎**：100% 纯前端 Web Audio API 动态合成（开机弦音、触控蜂鸣、警报汽笛、激光脉冲），无需加载任何外部音频素材。
- **战术操作与内存净化**：支持动态超频演示、多平台内存工作集净化（Windows `EmptyWorkingSet`、Linux `sync/drop_caches`、macOS `purge`）及系统健康卡片导出。
- **四套主题色彩**：夜之城 2077（青/粉/黄）、黑客帝国（荧光绿/黑）、合成波 1984（紫/橙/粉）、荒坂赤红（赤红/钛白）。

### 3. 快速上手
```bash
# 安装基础依赖
pip install -r requirements.txt

# 1. 启动终端 HUD 仪表盘（默认）
python main.py hud

# 2. 启动特定语言 HUD
python main.py hud -l zh_CN   # 简体中文
python main.py hud -l zh_TW   # 繁體中文
python main.py hud -l en      # 英语
python main.py hud -l ja      # 日语

# 3. 启动 Web 全息仪表盘
python main.py web

# 4. 生成系统生命体征诊断报告
python main.py report -l zh_CN

# 5. 执行内存净化
python main.py flush -l zh_CN

# 6. 进程实时监控
python main.py top
```

### 4. 终端快捷键
| 按键 | 说明 |
| :--- | :--- |
| `[1-4]` | 快速切换主题（夜之城 / 黑客帝国 / 合成波 / 荒坂） |
| `[L]` / `lang` | 循环切换语言（中简 / 中繁 / 英文 / 日文） |
| `[F]` / `flush` | 触发机体内存净化释放占用 |
| `[W]` / `web` | 后台启动并打开 Web HUD 仪表盘 |
| `[R]` / `report`| 生成并展示完整诊断报告 |
| `[H]` / `help` | 展开/折叠命令帮助矩阵 |
| `[Q]` / `ESC` | 安全断开神经链路并退出 |

---

## 🇭🇰/🇹🇼 繁體中文

### 1. 項目簡介
**機體生命徵象診斷儀（CYBER_PULSE v2.0）** 是一款基於 Python、FastAPI、WebSocket 與 HTML5 Canvas 構建的沉浸式跨平臺系統監控與健康診斷終端。將硬體遙測數據轉化為充滿未來科幻風格的全息監控界面，支援終端 CLI HUD 與現代化 Web HUD 雙重體驗。

### 2. 核心特點
- **終端交互式 HUD**：ANSI/VT 科技邊框渲染，提供 CPU 全核均衡器、記憶體/虛擬存儲矩陣、GPU 負載溫度、磁碟 I/O、網絡雷達及 Top 關鍵進程監視。
- **Web 全息儀表盤**：3D 全息旋轉刻度盤、16 核心波形圖、雙通道示波雷達、CRT 掃描線與駭客任務數位雨視覺特效。
- **全平臺原生相容**：同時適配 **Linux**、**macOS** 與 **Windows**。Unix 下自動接入 `termios/tty` cbreak 模式，Windows 下調用 Win32 API 規避 QuickEdit 卡死。
- **四語國際化 (i18n)**：完整支援 **簡體中文 (`zh_CN`)**、**繁體中文 (`zh_TW`)**、**英語 (`en`)**、**日語 (`ja`)**，支援系統語系自動偵測與實時熱切換。
- **純前端音效引擎**：100% 透過 Web Audio API 實時代碼合成，零外部音訊依賴。
- **記憶體淨化與戰術操作**：支援跨平臺記憶體工作集淨化、超頻特效模擬及系統健康報告導出。

### 3. 快速開始
```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動繁體中文終端 HUD
python main.py hud -l zh_TW

# 啟動 Web 儀表盤
python main.py web

# 導出繁體診斷報告
python main.py report -l zh_TW
```

---

## 🇺🇸 English

### 1. Overview
**Somatic Vital Signs Diagnostic Monitor (CYBER_PULSE v2.0)** is an immersive, futuristic cross-platform system telemetry and health diagnostics workstation built with Python, FastAPI, WebSockets, and HTML5 Canvas. It transforms your raw hardware metrics into a Cyberpunk 2077 Netrunner-inspired telemetry dashboard.

### 2. Key Highlights
- **Interactive Terminal HUD**: Rich ANSI/VT layout with real-time multi-core load equalizer, RAM/swap matrix, GPU telemetry, disk I/O rates, network radar, and top surveillance targets.
- **Holographic Web HUD**: 3D rotary gauges, 16-core equalizer bars, oscilloscope waveforms, CRT scanlines, and Matrix digital rain canvas animations.
- **Cross-Platform Native**: Seamless operation across **Linux**, **macOS**, and **Windows**. Uses Unix `termios/tty` cbreak mode for instantaneous non-blocking keypresses and Windows Win32 API to prevent QuickEdit freezing.
- **Multilingual Support (i18n)**: Out of the box support for **Simplified Chinese (`zh_CN`)**, **Traditional Chinese (`zh_TW`)**, **English (`en`)**, and **Japanese (`ja`)** with automatic locale detection and runtime toggling.
- **Synthesized Offline Web Audio**: 100% code-synthesized via Web Audio API with zero external audio assets.
- **Tactical Actions**: Memory purge protocol, simulated overclock boost, and exportable system health diagnostic cards.

### 3. Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Launch interactive terminal HUD (Default)
python main.py hud -l en

# Launch Web HUD in browser
python main.py web

# Export system diagnostic audit report
python main.py report -l en

# Run memory flush
python main.py flush -l en

# Live process monitor
python main.py top
```

### 4. Interactive HUD Hotkeys
- `[1-4]`: Switch cyberpunk themes (NightCity / Matrix / Synthwave / Arasaka)
- `[L]` or `lang`: Cycle interface language (`zh_CN` -> `zh_TW` -> `en` -> `ja`)
- `[F]` or `flush`: Execute neural memory purge
- `[W]` or `web`: Spin up background Web HUD and launch default browser
- `[R]` or `report`: Generate full telemetry diagnostic audit report
- `[H]` or `help`: Toggle command matrix help overlay
- `[Q]` or `ESC`: Disconnect neural link and exit

---

## 🇯🇵 日本語

### 1. 概要
**機体生命兆候診断装置（CYBER_PULSE v2.0）** は、Python、FastAPI、WebSocket、HTML5 Canvas で構築された、サイバーパンク調の次世代生体・システム健康診断プラットフォームです。ハードウェアのリアルタイムテレメトリを、SFライクなサイバーデッキ風ダッシュボードとして可視化します。

### 2. 主な特徴
- **対話型ターミナル HUD**: ANSI/VT によるハイテクな二重枠インターフェース。全CPUコア負荷イコライザー、メモリ/スワップマトリクス、GPU温度、ディスクI/O、ネットワークレーダー、監視プロセスをリアルタイム表示。
- **Web ホログラフィック HUD**: 3D回転式ホロゲージ、16コア負荷グラデーション波形、CRT走査線、マトリックスコードレイン描画。
- **クロスプラットフォーム完全対応**: **Linux**、**macOS**、**Windows** にネイティブ対応。Unix の `termios/tty` による非同期キー入力、Windows の QuickEdit 固まり回避を実装。
- **4言語対応 (i18n)**: **日本語 (`ja`)**、**英語 (`en`)**、**簡体字中国語 (`zh_CN`)**、**繁体字中国語 (`zh_TW`)** に完全対応。環境に応じた自動判定および動作中の即時言語切り替えをサポート。
- **オフライン Web Audio 合成エンジン**: 外部音声ファイル不要。Web Audio API を使って純コードで起動音や警告サイレンをリアルタイム合成。
- **メモリパージ＆戦術機能**: ワンキーでのメモリ解放プロトコル、オーバークロック演出、診断監査レポート出力に対応。

### 3. クイックスタート
```bash
# 依存関係のインストール
pip install -r requirements.txt

# 日本語ターミナル HUD を起動
python main.py hud -l ja

# Web HUD をブラウザで起動
python main.py web

# 診断監査レポートを出力
python main.py report -l ja

# メモリ解放プロトコルを実行
python main.py flush -l ja
```

---

## 📁 项目目录结构 / Project Structure

```text
system-monitoring/
├── docs/                     # 文档与工程记录 / Documentation
│   └── TASK_PROGRESS.md      # 开发进度与任务跟踪
├── scripts/                  # 启动与打包脚本 / Build & Launch scripts
│   ├── build_binary.py       # PyInstaller 单文件打包脚本
│   ├── cpulse.bat            # Windows 批处理快捷方式
│   ├── cpulse.ps1            # PowerShell 快捷脚本
│   ├── cpulse.spec           # PyInstaller 打包配置
│   ├── entrypoint.py         # 二进制打包入口点
│   ├── install.ps1           # Windows PATH 安装脚本
│   ├── run.bat               # Windows 交互菜单启动脚本
│   └── run.sh                # Linux / macOS Shell 启动脚本
├── src/                      # 核心源代码 (Standard src-layout)
│   └── cyber_pulse/          # 核心包
│       ├── __init__.py       # 包元数据与版本号
│       ├── __main__.py       # 允许 python -m cyber_pulse 执行
│       ├── app.py            # FastAPI Web 服务、WebSocket 与 REST 接口
│       ├── cli.py            # 统一命令行入口 (CLI)
│       ├── cli_hud.py        # 终端 ANSI HUD 交互引擎
│       ├── collector.py      # 系统与硬件指标采集引擎 (CPU/内存/GPU/磁盘/网络)
│       ├── i18n.py           # 多语言国际化核心模块 (中简/中繁/英/日)
│       └── static/           # 赛博朋克 Web HUD 静态资源
│           ├── index.html    # HUD 主画布界面
│           ├── css/          # 霓虹荧光、主题与 CRT 扫描线样式
│           └── js/           # Canvas 动画、Web Audio 音效与遥测通信
├── tests/                    # 自动化单元测试 / Unit Tests
│   ├── __init__.py
│   ├── test_api.py           # API 接口测试
│   ├── test_cli.py           # CLI 命令行参数测试
│   ├── test_collector.py     # 硬件采集器测试
│   └── test_i18n.py          # 多语言国际化单元测试
├── main.py                   # 开发与快速执行主入口
├── pyproject.toml            # Python 构建配置
├── requirements.txt          # Python 运行时依赖
├── setup.py                  # 安装配置兼容垫片
└── README.md                 # 四语项目说明文档
```

---

## 🧪 自动化测试 / Running Tests

项目内置完整的自动化测试套件（支持所有平台运行）：

```bash
# 运行全部单元测试
python -m unittest discover tests

# 单独测试多语言模块
python -m unittest tests/test_i18n.py

# 单独测试 CLI 功能
python -m unittest tests/test_cli.py
```

---

## 📦 跨平台打包建议 / Packaging Guide

本项目推荐保持**单分支**架构，在不同系统上通过构建工具打出原生独立可执行文件：

| 平台 | 目标二进制 | 打包命令 |
| :--- | :--- | :--- |
| **Windows** | `cpulse.exe` | `python scripts/build_binary.py` |
| **Linux** | `cpulse` (ELF) | `pyinstaller --onefile main.py -n cpulse` |
| **macOS** | `cpulse` (Mach-O) | `pyinstaller --onefile main.py -n cpulse` |

---

## 📜 许可证 / License
本项目采用 [MIT License](LICENSE) 授权许可。
