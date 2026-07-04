"""
overlay.py — subtitle overlay window.

Stage 2.1 (static window): transparency, position, "always on top".
Stage 2.2 (this version): the window can now update its text "from the
outside" while running, using Qt signals/slots.

Signals & slots
----------------
Subtitles will eventually be produced by the audio-processing thread,
while this window runs on the main/UI thread. Directly touching a
QLabel from another thread causes hard-to-diagnose crashes. Qt's
signal/slot mechanism is the safe way to cross that boundary: another
thread emits a signal with the new text, and Qt delivers it to this
window's slot on the correct thread.
"""

import sys

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 120
BOTTOM_MARGIN = 80
CLEAR_AFTER_MS = 4000  # hide subtitle after this long without an update


class SubtitleOverlay(QWidget):
    """A frameless, transparent, always-on-top window for showing subtitles."""

    # Emitting this signal is the thread-safe way to change the subtitle text.
    text_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._configure_window()
        self._build_label()
        self._position_bottom_center()
        self._configure_clear_timer()

        self.text_changed.connect(self._on_text_changed)

    def _configure_window(self):
        # FramelessWindowHint: no title bar / system buttons.
        # WindowStaysOnTopHint: stays above the game, even fullscreen (borderless).
        # Tool: hides the window from the taskbar / dock / Cmd+Tab switcher.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        # WA_TranslucentBackground: only the text is visible, not a window rectangle.
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

    def _build_label(self):
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.label.setStyleSheet(
            """
            color: white;
            background-color: rgba(0, 0, 0, 140);
            border-radius: 12px;
            padding: 10px;
            """
        )

    def _position_bottom_center(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - WINDOW_WIDTH) // 2
        y = screen_geometry.height() - WINDOW_HEIGHT - BOTTOM_MARGIN
        self.move(x, y)

    def _configure_clear_timer(self):
        # Single-shot timer restarted on every update; if no new text
        # arrives for CLEAR_AFTER_MS, the old subtitle disappears instead
        # of being stuck on screen forever.
        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(lambda: self.label.setText(""))

    def _on_text_changed(self, text: str):
        self.label.setText(text)
        self._clear_timer.start(CLEAR_AFTER_MS)

    def set_text(self, text: str):
        """Thread-safe entry point: call this from any thread with new subtitle text."""
        self.text_changed.emit(text)


def run_demo():
    """Manual test for Stage 2.2: simulates new subtitles every 2 seconds
    without closing/restarting the window, to verify dynamic updates work."""
    demo_lines = [
        "Hello, how are you doing today?",
        "I am testing the speech recognition system.",
        "This is a sample sentence for the whisper model to transcribe.",
    ]

    app = QApplication(sys.argv)
    overlay = SubtitleOverlay()
    overlay.show()

    counter = {"i": 0}

    def show_next_line():
        line = demo_lines[counter["i"] % len(demo_lines)]
        overlay.set_text(line)
        counter["i"] += 1

    demo_timer = QTimer()
    demo_timer.timeout.connect(show_next_line)
    demo_timer.start(2000)
    show_next_line()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_demo()
