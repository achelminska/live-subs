# LiveSubs

Real-time AI subtitle overlay for Windows. LiveSubs listens to your system audio (whatever is playing through your speakers or headphones — a game, a movie, a YouTube video), transcribes the English speech live using AI, translates it to Polish, and displays it as an on-screen subtitle overlay — just like movie subtitles, generated on the fly.

It works with **any application that plays audio through Windows** — not just one specific game. As long as the sound goes through your system's audio output, LiveSubs can subtitle it.

## How it works

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. AUDIO    │───▶│ 2. WHISPER   │───▶│ 3. DEEPL    │───▶│ 4. OVERLAY  │
│  capture    │    │ transcription│    │ translation │    │ on screen   │
│ (WASAPI)    │    │  (EN text)   │    │  (EN → PL)  │    │  (PyQt6)    │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

Audio is captured in small chunks via WASAPI loopback, transcribed locally with `faster-whisper`, translated through the DeepL API, and rendered on a frameless, always-on-top, click-through-friendly overlay window. Capture, transcription and UI each run on their own thread so audio is never dropped while a previous chunk is still being processed.

## Features

- **Live EN → PL subtitles** for any system audio source (games, browser video, streaming apps)
- **Frameless, transparent overlay** — always on top, doesn't show up in the taskbar/Alt+Tab, draggable to any position on screen
- **System tray icon** — show/hide the control panel or subtitles, update your DeepL key, or quit, without hunting for a close button on the overlay
- **Control panel** to:
  - pick which audio device to capture (speakers vs. headphones, auto-detects available loopback devices)
  - adjust subtitle font size and background opacity live
  - show/hide the overlay
  - set or change your DeepL API key at any time
- **Works without a DeepL key too** — skip the setup and LiveSubs still shows English subtitles from Whisper
- **Silence filtering** so the app doesn't try to transcribe/translate quiet or empty audio chunks
- Packaged as a single Windows installer — no Python installation required for end users

## Tech stack

| Stage | Library | Why |
|---|---|---|
| Audio capture | `sounddevice` / `pyaudiowpatch` (WASAPI loopback) | Captures whatever is playing on your speakers/headphones |
| Transcription | `faster-whisper` | ~4x faster than stock Whisper, runs fully offline/locally |
| Translation | `deepl` (API) | Best-in-class EN → PL translation quality, free tier available |
| UI / overlay | `PyQt6` | Transparent, always-on-top, frameless window + native tray icon |
| Packaging | `PyInstaller` + Inno Setup | Single `.exe` and a proper Windows installer |

## Installation (end users)

1. Download the latest installer from the [Releases page](https://github.com/achelminska/live-subs/releases) (`LiveSubs-Setup.exe`).
2. Run it — it installs LiveSubs with Desktop and Start Menu shortcuts, no Python required.
3. On first launch, LiveSubs will ask for a free [DeepL API key](https://www.deepl.com/pro-api) to enable Polish translation. You can skip this and get English-only subtitles, and add a key later from the tray/control panel.
4. Play anything with English audio through your speakers or headphones — subtitles appear at the bottom of your screen.

## Running from source (developers)

Requires Python 3.11+ on Windows (audio capture needs WASAPI, so this only works fully on Windows — see [Limitations](#known-limitations)).

```bash
git clone https://github.com/achelminska/live-subs.git
cd live-subs
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edit .env and add your DEEPL_API_KEY
python main.py
```

To build your own installer, see the scripts in `tools/` (`build.ps1` for the PyInstaller `.exe`, `installer.iss` for the Inno Setup installer, `install.ps1` to install locally with shortcuts).

## Known limitations

- **Windows only.** Audio capture relies on WASAPI loopback, which doesn't exist on macOS/Linux. The AI/translation/UI modules (`transcribe.py`, `translate.py`, `overlay.py`) can be developed and tested cross-platform, but live audio capture and `.exe` builds require a real Windows PC — virtual machines with emulated audio hardware are not reliable for this.
- **Requires internet for translation.** Transcription runs fully offline, but translation goes through the DeepL API. Without internet, LiveSubs falls back to showing the original English text instead of crashing.
- **~1–1.5s latency** between speech and subtitle, inherent to the chunk-based approach (the app has to hear a full chunk before it can transcribe it).
- **DeepL free tier limit**: 500,000 characters/month. Check usage at [deepl.com/pro-account/usage](https://www.deepl.com/pro-account/usage).

## License

MIT — see [LICENSE](LICENSE).
