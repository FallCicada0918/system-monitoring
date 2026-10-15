$repoRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$repoRoot\src;$env:PYTHONPATH"
python -m cyber_pulse.cli @args
