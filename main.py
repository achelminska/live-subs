"""
main.py — live subtitle pipeline (Stage 3.3 + UI).

System audio (speakers) -> Whisper -> DeepL -> overlay window.

Run:
    .\\venv\\Scripts\\python.exe main.py

Requires .env with DEEPL_API_KEY for Polish translation (see .env.example).
First Whisper run downloads the model (~150 MB).
"""

import queue
import sys
import threading

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon

from audio_capture import (
    SystemAudioCapture,
    find_loopback_device,
    list_loopback_devices_full,
)
from logging_setup import setup_logging
from overlay import SubtitleOverlay
from subtitle_filter import is_worth_translating
from transcribe import load_model, transcribe_audio
from translate import is_api_key_configured, set_api_key, translate
from ui import ApiKeyDialog, ControlPanel, ICON_PATH, LiveSubsTray

CHUNK_QUEUE_SIZE = 2
MIN_RMS = 0.003

logger = setup_logging()


class PipelineBridge(QObject):
    """Thread-safe updates from the worker thread to the UI."""

    status_changed = pyqtSignal(str, bool)
    subtitle_changed = pyqtSignal(str)


class PipelineWorker:
    def __init__(
        self,
        capture: SystemAudioCapture,
        bridge: PipelineBridge,
    ):
        self.capture = capture
        self.bridge = bridge
        self.stop_event = threading.Event()
        self.chunk_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=CHUNK_QUEUE_SIZE)
        self._thread: threading.Thread | None = None
        self._capture_active = False

        capture.on_chunk = self._on_chunk

    def _on_chunk(self, audio: np.ndarray):
        try:
            self.chunk_queue.put_nowait(audio)
        except queue.Full:
            try:
                self.chunk_queue.get_nowait()
            except queue.Empty:
                pass
            self.chunk_queue.put_nowait(audio)

    def start(self):
        self._thread = threading.Thread(target=self._run, name="pipeline-worker", daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        if self.capture is not None:
            self.capture.stop()

    def swap_capture(self, capture: SystemAudioCapture):
        """Hot-swap loopback device without reloading Whisper."""
        if self.capture is not None:
            self.capture.stop()

        self.capture = capture
        capture.on_chunk = self._on_chunk

        if self._capture_active and not self.stop_event.is_set():
            capture.start()

    def _run(self):
        self.bridge.status_changed.emit("Ładowanie modelu Whisper...", False)
        logger.info("Loading Whisper model (first run may download ~150 MB)...")

        try:
            model = load_model()
        except Exception as error:
            message = f"Błąd modelu: {error}"
            logger.exception("Whisper model load failed")
            self.bridge.status_changed.emit(message, False)
            self.bridge.subtitle_changed.emit("Nie udało się załadować Whisper — zobacz livesubs.log")
            return

        logger.info("Whisper model ready, starting audio capture on %s", self.capture.device_name)

        try:
            self.capture.start()
        except Exception as error:
            message = f"Błąd audio: {error}"
            logger.exception("Audio capture start failed")
            self.bridge.status_changed.emit(message, False)
            self.bridge.subtitle_changed.emit("Nie udało się uruchomić loopback — zobacz livesubs.log")
            return

        self._capture_active = True
        self.bridge.status_changed.emit("Nasłuchuję — puść angielski dźwięk", True)

        while not self.stop_event.is_set():
            try:
                audio = self.chunk_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            rms = float(np.sqrt(np.mean(audio**2)))
            if rms < MIN_RMS:
                continue

            self.bridge.status_changed.emit("Transkrypcja...", True)
            logger.debug("Transcribing chunk, RMS=%.4f", rms)

            try:
                segments, _ = transcribe_audio(model, audio)
            except Exception as error:
                logger.error("Transcription error: %s", error)
                self.bridge.status_changed.emit("Nasłuchuję — puść angielski dźwięk", True)
                continue

            english = " ".join(segment.text.strip() for segment in segments).strip()
            if not english or not is_worth_translating(english):
                logger.debug("Skipped fragment: %r", english)
                self.bridge.status_changed.emit("Nasłuchuję — puść angielski dźwięk", True)
                continue

            logger.info("EN: %s", english)
            polish = translate(english)
            logger.info("PL: %s", polish)

            self.bridge.subtitle_changed.emit(polish)
            self.bridge.status_changed.emit("Nasłuchuję — puść angielski dźwięk", True)


def ensure_api_key(parent) -> bool:
    """Show API key dialog if missing. Returns True when setup is OK to continue."""
    if is_api_key_configured():
        return True

    dialog = ApiKeyDialog(parent)
    result = dialog.exec()

    if result == ApiKeyDialog.DialogCode.Accepted:
        set_api_key(dialog.api_key())
        logger.info("DeepL API key saved from first-run dialog")
        return True

    logger.info("Continuing without DeepL API key (English subtitles only)")
    if parent is not None and hasattr(parent, "set_status"):
        parent.set_status("Bez klucza DeepL — napisy po angielsku", active=False)
    return True


def configure_api_key(parent) -> bool:
    """Open settings dialog to add or change the DeepL API key."""
    from translate import get_api_key

    dialog = ApiKeyDialog(parent, initial_key=get_api_key() or "")
    if dialog.exec() != ApiKeyDialog.DialogCode.Accepted:
        return False

    set_api_key(dialog.api_key())
    logger.info("DeepL API key updated from settings")
    if parent is not None and hasattr(parent, "set_status"):
        parent.set_status("Klucz DeepL zapisany — polskie napisy włączone", active=True)
    return True


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LiveSubs")
    logger.info("LiveSubs starting (frozen=%s)", getattr(sys, "frozen", False))

    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    loopback_devices = list_loopback_devices_full()
    if not loopback_devices:
        print("No WASAPI loopback devices found.")
        sys.exit(1)

    default_device = find_loopback_device()
    capture = SystemAudioCapture(on_chunk=lambda audio: None, device_info=default_device)

    overlay = SubtitleOverlay()
    overlay.show()

    panel = ControlPanel(loopback_devices=loopback_devices, default_device=default_device)

    if not ensure_api_key(panel):
        sys.exit(0)

    panel.show()

    bridge = PipelineBridge()
    worker = PipelineWorker(capture=capture, bridge=bridge)

    bridge.status_changed.connect(panel.set_status)
    bridge.subtitle_changed.connect(overlay.set_text)
    panel.font_size_changed.connect(overlay.set_font_size)
    panel.background_opacity_changed.connect(overlay.set_background_opacity)

    def on_audio_device_changed(device_info: dict):
        bridge.status_changed.emit("Zmiana źródła audio...", False)
        new_capture = SystemAudioCapture(on_chunk=worker._on_chunk, device_info=device_info)
        worker.swap_capture(new_capture)
        bridge.status_changed.emit("Nasłuchuję — puść angielski dźwięk", True)

    panel.audio_device_changed.connect(on_audio_device_changed)
    panel.api_key_change_requested.connect(lambda: configure_api_key(panel))

    overlay.show()
    overlay.raise_()

    def set_overlay_visible(visible: bool):
        overlay.setVisible(visible)

    panel.overlay_visibility_changed.connect(set_overlay_visible)

    tray = None
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = LiveSubsTray()
        tray.show_panel_requested.connect(panel.show)
        tray.toggle_overlay_requested.connect(panel.toggle_button.click)
        tray.api_key_change_requested.connect(lambda: configure_api_key(panel))
        tray.quit_requested.connect(app.quit)
        tray.show()

    panel.quit_requested.connect(app.quit)

    def shutdown():
        worker.stop()
        if tray is not None:
            tray.hide()
        overlay.close()

    app.aboutToQuit.connect(shutdown)

    worker.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
