# Build LiveSubs.exe (Windows)
# Usage: .\tools\build.ps1
#        .\tools\build.ps1 -SkipInstall   (for release build)

param(
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Installing build dependencies..."
& .\venv\Scripts\pip.exe install -r requirements-build.txt -q

Write-Host "Building LiveSubs.exe..."
& .\venv\Scripts\pyinstaller.exe livesubs.spec --noconfirm

if (Test-Path ".env") {
    Copy-Item ".env" "dist\.env" -Force
    Write-Host "Copied .env -> dist\.env"
} else {
    Write-Host "WARNING: No .env in project root. Copy .env next to LiveSubs.exe before running."
}

if ($SkipInstall) {
    Write-Host ""
    Write-Host "Build complete: dist\LiveSubs.exe"
} else {
    Write-Host ""
    Write-Host "Build complete. Installing shortcuts..."
    & "$PSScriptRoot\install.ps1"
}
