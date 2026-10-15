@echo off
chcp 65001 >nul
title CYBER_PULSE // NEURAL_HUD v2.0
color 0b
cls

:: Resolve project root and add src to PYTHONPATH
set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "PYTHONPATH=%REPO_ROOT%\src;%PYTHONPATH%"
cd /d "%REPO_ROOT%"

echo ===============================================================================
echo     CYBER_PULSE // Cyberpunk Neural System Monitor CLI v2.0
echo     [ HARDWARE TELEMETRY // NEURAL LINK READY ]
echo ===============================================================================
echo.
echo   [1] Start Terminal Cyber CLI HUD (Codex-Style Interactive Screen)
echo   [2] Start Desktop Window Mode
echo   [3] Start Web Browser Fullscreen Mode
echo   [4] Start Headless LAN Server Mode
echo   [5] Neural Flush (Purge RAM Working Sets)
echo   [6] Show System Diagnostic Report
echo.
set /p choice="Select Mode [Default: 1]: "

if "%choice%"=="" set choice=1
if "%choice%"=="1" (
    python -m cyber_pulse.cli hud
) else if "%choice%"=="2" (
    python -m cyber_pulse.cli web --window
) else if "%choice%"=="3" (
    python -m cyber_pulse.cli web
) else if "%choice%"=="4" (
    python -m cyber_pulse.cli web --headless
) else if "%choice%"=="5" (
    python -m cyber_pulse.cli flush
    pause
) else if "%choice%"=="6" (
    python -m cyber_pulse.cli report
    pause
) else (
    python -m cyber_pulse.cli hud
)
