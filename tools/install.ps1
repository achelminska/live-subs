# Install LiveSubs to a normal Windows location with Desktop + Start Menu shortcuts.
# Usage: .\tools\install.ps1
#        .\tools\install.ps1 -Build

param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$SourceExe = Join-Path $Root "dist\LiveSubs.exe"
$InstallDir = Join-Path $env:LOCALAPPDATA "Programs\LiveSubs"
$DesktopLink = Join-Path ([Environment]::GetFolderPath("Desktop")) "LiveSubs.lnk"
$StartMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\LiveSubs"
$StartMenuLink = Join-Path $StartMenuDir "LiveSubs.lnk"

if ($Build) {
    & "$PSScriptRoot\build.ps1"
}

if (-not (Test-Path $SourceExe)) {
    Write-Error "Missing dist\LiveSubs.exe. Run: .\tools\build.ps1"
}

Write-Host "Installing to: $InstallDir"
Stop-Process -Name LiveSubs -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $StartMenuDir | Out-Null

Copy-Item $SourceExe (Join-Path $InstallDir "LiveSubs.exe") -Force

$EnvExample = Join-Path $Root ".env.example"
if (Test-Path $EnvExample) {
    Copy-Item $EnvExample (Join-Path $InstallDir ".env.example") -Force
}

$TargetEnv = Join-Path $InstallDir ".env"
if (-not (Test-Path $TargetEnv)) {
    if (Test-Path (Join-Path $Root "dist\.env")) {
        Copy-Item (Join-Path $Root "dist\.env") $TargetEnv
        Write-Host "Copied .env"
    } elseif (Test-Path (Join-Path $Root ".env")) {
        Copy-Item (Join-Path $Root ".env") $TargetEnv
        Write-Host "Copied .env"
    } else {
        Write-Host "WARNING: No .env found. Copy .env.example to $TargetEnv and add DEEPL_API_KEY."
    }
} else {
    Write-Host "Kept existing .env in install folder."
}

$ExePath = Join-Path $InstallDir "LiveSubs.exe"

function New-AppShortcut {
    param(
        [string]$LinkPath,
        [string]$TargetPath,
        [string]$WorkingDirectory,
        [string]$Description
    )

    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($LinkPath)
    $shortcut.TargetPath = $TargetPath
    $shortcut.WorkingDirectory = $WorkingDirectory
    $shortcut.IconLocation = "$TargetPath,0"
    $shortcut.Description = $Description
    $shortcut.Save()
}

New-AppShortcut -LinkPath $DesktopLink -TargetPath $ExePath -WorkingDirectory $InstallDir `
    -Description "LiveSubs - live EN to PL subtitles"
New-AppShortcut -LinkPath $StartMenuLink -TargetPath $ExePath -WorkingDirectory $InstallDir `
    -Description "LiveSubs - live EN to PL subtitles"

Write-Host ""
Write-Host "Done."
Write-Host "  Desktop shortcut:  LiveSubs"
Write-Host "  Start menu:        LiveSubs"
Write-Host "  Install folder:    $InstallDir"
Write-Host ""
Write-Host "Launch LiveSubs from your desktop."
