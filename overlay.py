"""
overlay.py — subtitle overlay window (Stage 2.1: static window).

Goal of this step: get comfortable with the window itself — transparency,
position, "always on top" — before adding dynamic text updates. The
displayed text is hardcoded for now.
"""

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 120
BOTTOM_MARGIN = 80


class SubtitleOverlay(QWidget):
    """A frameless, transparent, always-on-top window for showing subtitles."""

    def __init__(self):
        super().__init__()
        self._configure_window()
        self._build_label()
        self._position_bottom_center()

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
        self.label = QLabel("Hello, how are you doing today?", self)
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


def main():
    app = QApplication(sys.argv)
    overlay = SubtitleOverlay()
    overlay.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
