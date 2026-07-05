# Build LiveSubs.exe (Windows)
# Usage: .\tools\build.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Installing build dependencies..."
& .\venv\Scripts\pip.exe install -r requirements-build.txt -q

Write-Host "Building LiveSubs.exe..."
& .\venv\Scripts\pyinstaller.exe livesubs.spec --noconfirm

Write-Host ""
Write-Host "Done. Output: dist\LiveSubs.exe"
Write-Host "Copy .env next to LiveSubs.exe before running (see .env.example)."
