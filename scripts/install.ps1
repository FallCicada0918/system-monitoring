$binDir = "$HOME\.cpulse\bin"
if (!(Test-Path $binDir)) {
    New-Item -ItemType Directory -Path $binDir -Force | Out-Null
}

$repoRoot = $PSScriptRoot
if ((Split-Path -Leaf $repoRoot) -in @("dist", "scripts")) {
    $repoRoot = Split-Path -Parent $repoRoot
}

$distOnefile = Join-Path $repoRoot "dist\cpulse.exe"
$distOnedir = Join-Path $repoRoot "dist\cpulse\cpulse.exe"

if (Test-Path $distOnefile) {
    $cmdContent = "@echo off`r`n`"$distOnefile`" %*"
    Set-Content -Path (Join-Path $binDir "cpulse.cmd") -Value $cmdContent -Encoding Ascii
    Write-Host "[+] Registered compiled standalone cpulse.exe to: $binDir" -ForegroundColor Green
} elseif (Test-Path $distOnedir) {
    $cmdContent = "@echo off`r`n`"$distOnedir`" %*"
    Set-Content -Path (Join-Path $binDir "cpulse.cmd") -Value $cmdContent -Encoding Ascii
    Write-Host "[+] Registered compiled onedir cpulse.exe to: $binDir" -ForegroundColor Green
} else {
    $srcDir = Join-Path $repoRoot "src"
    $cmdContent = "@echo off`r`nset `"PYTHONPATH=$srcDir;%PYTHONPATH%`"`r`npython -m cyber_pulse.cli %*"
    Set-Content -Path (Join-Path $binDir "cpulse.cmd") -Value $cmdContent -Encoding Ascii
    Write-Host "[+] Registered python cpulse runner to: $binDir" -ForegroundColor Green
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$binDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$binDir;$userPath", "User")
    Write-Host "[+] Added $binDir to User PATH." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "[+] CPULSE INSTALLED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "Open a new terminal and type 'cpulse' to run from anywhere." -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
