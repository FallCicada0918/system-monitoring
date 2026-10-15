@echo off
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%..\src;%PYTHONPATH%"
python -m cyber_pulse.cli %*
