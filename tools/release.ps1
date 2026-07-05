# Build LiveSubs-Setup.exe for portfolio download.
# Usage: .\tools\release.ps1
#
# Requires Inno Setup 6 (one-time install):
#   winget install JRSoftware.InnoSetup
#   or https://jrsoftware.org/isdl.php

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Find-InnoSetup {
    $paths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    foreach ($path in $paths) {
        if (Test-Path $path) { return $path }
    }
    $cmd = Get-Command iscc -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

Write-Host "Step 1/2: Building LiveSubs.exe..."
& "$PSScriptRoot\build.ps1" -SkipInstall

$iscc = Find-InnoSetup
if (-not $iscc) {
    Write-Host ""
    Write-Host "Inno Setup 6 not found."
    Write-Host "Install it once:"
    Write-Host "  winget install JRSoftware.InnoSetup"
    Write-Host "Then run this script again."
    exit 1
}

Write-Host ""
Write-Host "Step 2/2: Building installer..."
New-Item -ItemType Directory -Force -Path "release" | Out-Null
& $iscc "$PSScriptRoot\installer.iss"

$setup = Join-Path $Root "release\LiveSubs-Setup.exe"
if (Test-Path $setup) {
    $sizeMb = [math]::Round((Get-Item $setup).Length / 1MB, 1)
    Write-Host ""
    Write-Host "Done. Upload this file to your portfolio:"
    Write-Host "  $setup"
    Write-Host "  Size: ${sizeMb} MB"
} else {
    Write-Error "Installer build failed."
}
