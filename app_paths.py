"""Paths that work both from source and from a PyInstaller one-file exe."""

import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_dir() -> Path:
    """User-writable folder: .env, logs, Whisper cache (next to LiveSubs.exe)."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_dir() -> Path:
    """Bundled read-only assets (icon) — sys._MEIPASS when frozen."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def resource_path(name: str) -> Path:
    return resource_dir() / name


def env_file() -> Path:
    return app_dir() / ".env"


def load_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(env_file(), override=True)


def save_env_value(key: str, value: str) -> None:
    """Write or update a single key in .env next to the executable."""
    path = env_file()
    lines: list[str] = []
    found = False

    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{key}="):
                lines.append(f"{key}={value}")
                found = True
            else:
                lines.append(line)

    if not found:
        lines.append(f"{key}={value}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
