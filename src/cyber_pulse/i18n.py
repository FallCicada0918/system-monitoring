import os
import locale
from typing import Dict, Any, Optional

# Supported languages
LANG_ZH_CN = "zh_CN"
LANG_ZH_TW = "zh_TW"
LANG_EN = "en"
LANG_JA = "ja"

SUPPORTED_LANGUAGES = [LANG_ZH_CN, LANG_ZH_TW, LANG_EN, LANG_JA]

LANGUAGE_NAMES = {
    LANG_ZH_CN: "简体中文",
    LANG_ZH_TW: "繁體中文",
    LANG_EN: "English",
    LANG_JA: "日本語"
}

TEXTS: Dict[str, Dict[str, Any]] = {
    "title": {
        LANG_ZH_CN: "机体生命征象诊断仪",
        LANG_ZH_TW: "機體生命徵象診斷儀",
        LANG_EN: "Somatic Vital Signs Diagnostic Monitor",
        LANG_JA: "機体生命兆候診断装置"
    },
    "subtitle": {
        LANG_ZH_CN: "神经系统遥测与生命体征健康诊断终端",
        LANG_ZH_TW: "神經系統遙測與生命體徵健康診斷終端",
        LANG_EN: "Neural Telemetry & Vital Signs Diagnostic Terminal",
        LANG_JA: "神経系テレメトリ＆生体診断端末"
    },
    "initializing": {
        LANG_ZH_CN: "[*] 正在初始化遥测传感器与守护进程链路...",
        LANG_ZH_TW: "[*] 正在初始化遙測傳感器與守護進程鏈路...",
        LANG_EN: "[*] INITIALIZING TELEMETRY SENSORS & DAEMON LINK...",
        LANG_JA: "[*] テレメトリセンサーとデーモンリンクを初期化中..."
    },
    "terminated": {
        LANG_ZH_CN: "[+] 机体生命征象诊断仪已关闭。神经链路已断开。",
        LANG_ZH_TW: "[+] 機體生命徵象診斷儀已關閉。神經鏈路已斷開。",
        LANG_EN: "[+] DIAGNOSTIC MONITOR TERMINATED. NEURAL LINK DISENGAGED.",
        LANG_JA: "[+] 機体生命兆候診断装置を終了しました。神経リンクを切断。"
    },
    "system_protocol": {
        LANG_ZH_CN: "系统状态协议",
        LANG_ZH_TW: "系統狀態協定",
        LANG_EN: "SYSTEM PROTOCOL",
        LANG_JA: "システムプロトコル"
    },
    "neural_cpu": {
        LANG_ZH_CN: "核心处理器遥测 (CPU)",
        LANG_ZH_TW: "核心處理器遙測 (CPU)",
        LANG_EN: "NEURAL CPU CORE",
        LANG_JA: "CPUコア診断"
    },
    "neural_mem": {
        LANG_ZH_CN: "内存与虚拟存储矩阵",
        LANG_ZH_TW: "記憶體與虛擬存儲矩陣",
        LANG_EN: "NEURAL MEMORY MATRIX",
        LANG_JA: "メモリマトリクス"
    },
    "neural_gpu": {
        LANG_ZH_CN: "计算加速单元 (GPU)",
        LANG_ZH_TW: "計算加速單元 (GPU)",
        LANG_EN: "NEURAL ACCELERATOR (GPU)",
        LANG_JA: "アクセラレータ (GPU)"
    },
    "storage_io": {
        LANG_ZH_CN: "存储阵列与磁盘 I/O",
        LANG_ZH_TW: "存儲陣列與磁盤 I/O",
        LANG_EN: "STORAGE ARRAYS & DISK I/O",
        LANG_JA: "ストレージ ＆ ディスク I/O"
    },
    "network_radar": {
        LANG_ZH_CN: "网络通信雷达",
        LANG_ZH_TW: "網絡通信雷達",
        LANG_EN: "NETWORK RADAR",
        LANG_JA: "ネットワークレーダー"
    },
    "top_targets": {
        LANG_ZH_CN: "活跃监控目标 (TOP 进程)",
        LANG_ZH_TW: "活躍監控目標 (TOP 進程)",
        LANG_EN: "TOP SURVEILLANCE TARGETS",
        LANG_JA: "最優先監視プロセス"
    },
    "cmd_help": {
        LANG_ZH_CN: "指令矩阵帮助",
        LANG_ZH_TW: "指令矩陣說明",
        LANG_EN: "COMMAND HELP MATRIX",
        LANG_JA: "コマンドヘルプマトリクス"
    },
    "cmd_input": {
        LANG_ZH_CN: "命令输入",
        LANG_ZH_TW: "命令輸入",
        LANG_EN: "COMMAND INPUT",
        LANG_JA: "コマンド入力"
    },
    "hotkey_bar": {
        LANG_ZH_CN: "快捷键: [1-4]主题  [F]清理内存  [W]网页  [R]诊断报告  [L]语言  [H]帮助  [Q/ESC]退出",
        LANG_ZH_TW: "快捷鍵: [1-4]主題  [F]清理記憶體  [W]網頁  [R]診斷報告  [L]語言  [H]說明  [Q/ESC]退出",
        LANG_EN: "Hotkeys: [1-4]Theme  [F]Flush  [W]Web  [R]Report  [L]Lang  [H]Help  [Q/ESC]Quit",
        LANG_JA: "操作: [1-4]テーマ  [F]メモリ解放  [W]Web  [R]レポート  [L]言語  [H]ヘルプ  [Q/ESC]終了"
    },
    "defcon_1": {
        LANG_ZH_CN: "一级戒备 // 临界高负荷",
        LANG_ZH_TW: "一級戒備 // 臨界高負載",
        LANG_EN: "DEFCON 1 // CRITICAL OVERLOAD",
        LANG_JA: "DEFCON 1 // 危機的高負荷"
    },
    "defcon_2": {
        LANG_ZH_CN: "二级戒备 // 负载升高",
        LANG_ZH_TW: "二級戒備 // 負載升高",
        LANG_EN: "DEFCON 2 // ELEVATED LOAD",
        LANG_JA: "DEFCON 2 // 負荷上昇"
    },
    "defcon_4": {
        LANG_ZH_CN: "常规状态 // 运行优良",
        LANG_ZH_TW: "常規狀態 // 運行優良",
        LANG_EN: "DEFCON 4 // NOMINAL OPTIMAL",
        LANG_JA: "DEFCON 4 // 正常稼働"
    },
    "status_online": {
        LANG_ZH_CN: "机体生命体征遥测同步 // 状态: 在线",
        LANG_ZH_TW: "機體生命體徵遙測同步 // 狀態: 在線",
        LANG_EN: "VITAL SIGNS TELEMETRY SYNCHRONIZED // STATUS: ONLINE",
        LANG_JA: "生体兆候テレメトリ同期完了 // 状態: オンライン"
    },
    "link_established": {
        LANG_ZH_CN: "链路已建立 // 可输入 'w', 'r', 'f', 'l', '1-4', 或 'help'",
        LANG_ZH_TW: "鏈路已建立 // 可輸入 'w', 'r', 'f', 'l', '1-4', 或 'help'",
        LANG_EN: "NEURAL LINK ESTABLISHED // TYPE 'w', 'r', 'f', 'l', '1-4', OR 'help'",
        LANG_JA: "リンク確立 // 'w', 'r', 'f', 'l', '1-4', または 'help' を入力"
    },
    "theme_label": {
        LANG_ZH_CN: "主题",
        LANG_ZH_TW: "主題",
        LANG_EN: "THEME",
        LANG_JA: "テーマ"
    },
    "time_label": {
        LANG_ZH_CN: "时间",
        LANG_ZH_TW: "時間",
        LANG_EN: "TIME",
        LANG_JA: "時間"
    },
    "lang_label": {
        LANG_ZH_CN: "语言",
        LANG_ZH_TW: "語言",
        LANG_EN: "LANG",
        LANG_JA: "言語"
    },
    "report_title": {
        LANG_ZH_CN: "机体生命征象诊断分析报告",
        LANG_ZH_TW: "機體生命徵象診斷分析報告",
        LANG_EN: "SOMATIC VITAL SIGNS DIAGNOSTIC AUDIT REPORT",
        LANG_JA: "機体生命兆候診断監査レポート"
    },
    "report_saved": {
        LANG_ZH_CN: "诊断报告已保存至",
        LANG_ZH_TW: "診斷報告已保存至",
        LANG_EN: "REPORT SAVED TO",
        LANG_JA: "診断レポート保存完了:"
    },
    "report_return_hint": {
        LANG_ZH_CN: "输入 'r', 'back' 或按 ESC 返回仪表盘",
        LANG_ZH_TW: "輸入 'r', 'back' 或按 ESC 返回儀表盤",
        LANG_EN: "TYPE 'r', 'back', OR ESC TO RETURN",
        LANG_JA: "'r'、'back' または ESC で戻る"
    },
    "flush_start": {
        LANG_ZH_CN: "[*] 正在执行机体内存净化协议...",
        LANG_ZH_TW: "[*] 正在執行機體記憶體淨化協定...",
        LANG_EN: "[*] INITIATING NEURAL MEMORY FLUSH PROTOCOL...",
        LANG_JA: "[*] メモリ解放プロトコルを実行中..."
    },
    "flush_done": {
        LANG_ZH_CN: "内存净化完成",
        LANG_ZH_TW: "記憶體淨化完成",
        LANG_EN: "MEMORY PURGE COMPLETE",
        LANG_JA: "メモリ解放完了"
    },
    "ram_reclaimed": {
        LANG_ZH_CN: "已回收内存",
        LANG_ZH_TW: "已回收記憶體",
        LANG_EN: "MEMORY RECLAIMED",
        LANG_JA: "解放されたメモリ"
    },
    "avail_ram": {
        LANG_ZH_CN: "可用内存",
        LANG_ZH_TW: "可用記憶體",
        LANG_EN: "Available RAM",
        LANG_JA: "利用可能なメモリ"
    },
    "help_w": {
        LANG_ZH_CN: "启动网页版 Web HUD 并在默认浏览器中打开",
        LANG_ZH_TW: "啟動網頁版 Web HUD 並在默認瀏覽器中打開",
        LANG_EN: "Start Web HUD server and launch in default browser",
        LANG_JA: "Web HUD サーバーを起動して既定のブラウザで開く"
    },
    "help_r": {
        LANG_ZH_CN: "生成并展示完整的机体生命征象诊断分析报告",
        LANG_ZH_TW: "生成並展示完整的機體生命徵象診斷分析報告",
        LANG_EN: "Generate full somatic vital signs diagnostic audit report",
        LANG_JA: "生体兆候診断監査レポートを生成して表示"
    },
    "help_f": {
        LANG_ZH_CN: "执行机体内存净化释放占用",
        LANG_ZH_TW: "執行機體記憶體淨化釋放佔用",
        LANG_EN: "Purge memory working sets to free RAM",
        LANG_JA: "ワーキングセットをパージしてメモリを解放"
    },
    "help_l": {
        LANG_ZH_CN: "切换界面语言 (zh_CN 简体 / zh_TW 繁体 / en 英文 / ja 日语)",
        LANG_ZH_TW: "切換介面語言 (zh_CN 簡體 / zh_TW 繁體 / en 英文 / ja 日語)",
        LANG_EN: "Switch language (zh_CN / zh_TW / en / ja)",
        LANG_JA: "言語を切り替える (zh_CN / zh_TW / en / ja)"
    },
    "help_theme": {
        LANG_ZH_CN: "切换色彩主题: 1=夜之城 2=黑客帝国 3=合成波 4=荒坂赤红",
        LANG_ZH_TW: "切換色彩主題: 1=夜之城 2=駭客任務 3=合成波 4=荒坂赤紅",
        LANG_EN: "Switch themes: 1=NightCity 2=Matrix 3=Synthwave 4=Arasaka",
        LANG_JA: "テーマ切替: 1=NightCity 2=Matrix 3=Synthwave 4=Arasaka"
    },
    "help_h": {
        LANG_ZH_CN: "切换显示/隐藏本帮助卡片",
        LANG_ZH_TW: "切換顯示/隱藏本說明卡片",
        LANG_EN: "Toggle this command matrix help card",
        LANG_JA: "コマンドヘルプカードの表示/非表示"
    },
    "help_q": {
        LANG_ZH_CN: "安全断开神经链路并退出 (也可按 ESC)",
        LANG_ZH_TW: "安全斷開神經鏈路並退出 (也可按 ESC)",
        LANG_EN: "Exit and disconnect neural link (or press ESC)",
        LANG_JA: "神経リンクを切断して終了 (ESCでも可)"
    },
    "help_kill": {
        LANG_ZH_CN: "根据进程 PID 终止指定进程",
        LANG_ZH_TW: "根據進程 PID 終止指定進程",
        LANG_EN: "Terminate target process by PID",
        LANG_JA: "指定した PID のプロセスを終了"
    }
}

_CURRENT_LANG = LANG_ZH_CN


def detect_system_language() -> str:
    env_lang = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
    if not env_lang:
        try:
            loc = locale.getdefaultlocale()[0]
            if loc:
                env_lang = loc
        except Exception:
            pass

    env_lower = env_lang.lower().replace("-", "_")
    if "zh_tw" in env_lower or "zh_hk" in env_lower or "zh_mo" in env_lower or "hant" in env_lower:
        return LANG_ZH_TW
    if "zh" in env_lower:
        return LANG_ZH_CN
    if "ja" in env_lower:
        return LANG_JA
    if "en" in env_lower:
        return LANG_EN
    return LANG_ZH_CN


def set_language(lang: str) -> bool:
    global _CURRENT_LANG
    normalized = lang.strip().replace("-", "_")
    for supported in SUPPORTED_LANGUAGES:
        if normalized.lower() == supported.lower():
            _CURRENT_LANG = supported
            return True
    return False


def get_language() -> str:
    return _CURRENT_LANG


def next_language() -> str:
    global _CURRENT_LANG
    try:
        idx = SUPPORTED_LANGUAGES.index(_CURRENT_LANG)
        _CURRENT_LANG = SUPPORTED_LANGUAGES[(idx + 1) % len(SUPPORTED_LANGUAGES)]
    except ValueError:
        _CURRENT_LANG = LANG_ZH_CN
    return _CURRENT_LANG


def t(key: str, lang: Optional[str] = None) -> str:
    target_lang = lang or _CURRENT_LANG
    if key in TEXTS:
        translations = TEXTS[key]
        if target_lang in translations:
            return translations[target_lang]
        if LANG_ZH_CN in translations:
            return translations[LANG_ZH_CN]
        if LANG_EN in translations:
            return translations[LANG_EN]
    return key
