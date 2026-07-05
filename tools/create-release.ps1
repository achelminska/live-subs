# Create GitHub Release with LiveSubs-Setup.exe
# Usage: .\tools\create-release.ps1
# Requires: gh auth login (one-time)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Setup = Join-Path $Root "release\LiveSubs-Setup.exe"
if (-not (Test-Path $Setup)) {
    Write-Error "Missing release\LiveSubs-Setup.exe. Run: .\tools\release.ps1"
}

gh auth status | Out-Null

gh release create v1.0.0 $Setup `
    --repo achelminska/live-subs `
    --title "LiveSubs v1.0.0" `
    --notes @"
LiveSubs - live EN to PL subtitles from system audio.

**Download:** LiveSubs-Setup.exe (~120 MB)

**Requirements:** Windows 10/11, internet (first run downloads Whisper model ~150 MB), free DeepL API key.

**Install:** Run setup, enter DeepL key (or configure later in app), launch from Start menu.
"@

Write-Host ""
Write-Host "Release URL: https://github.com/achelminska/live-subs/releases/tag/v1.0.0"
