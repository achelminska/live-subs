"""
overlay.py — subtitle overlay window.

Single subtitle line, full text, replaced on each update.
"""

import sys

from PyQt6.QtCore import QTimer, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QFont, QFontMetrics
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 80
MAX_WINDOW_HEIGHT = 220
BOTTOM_MARGIN = 60
CLEAR_AFTER_MS = 8000
HORIZONTAL_PADDING = 24
VERTICAL_PADDING = 20

DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 26
DEFAULT_BG_OPACITY = 180


class SubtitleOverlay(QWidget):
    """A frameless, always-on-top window for showing subtitles."""

    subtitle_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._font_size = DEFAULT_FONT_SIZE
        self._bg_opacity = DEFAULT_BG_OPACITY
        self._drag_offset = None
        self._anchor_bottom = True

        self._configure_window()
        self._build_label()
        self._position_bottom_center()
        self._configure_clear_timer()

        self.subtitle_changed.connect(self._show_subtitle)

    def _configure_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.resize(WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    def _build_label(self):
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self._apply_label_style()

    def _apply_label_style(self):
        self.label.setFont(QFont(DEFAULT_FONT_FAMILY, self._font_size, QFont.Weight.Bold))
        self.label.setStyleSheet(
            f"""
            QLabel {{
                color: #ffffff;
                background-color: rgba(0, 0, 0, {self._bg_opacity});
                border-radius: 14px;
                padding: {VERTICAL_PADDING}px {HORIZONTAL_PADDING}px;
            }}
            """
        )

    def _active_screen(self):
        screen = QApplication.screenAt(QCursor.pos())
        if screen is None:
            screen = QApplication.primaryScreen()
        return screen

    def _position_bottom_center(self):
        screen_geometry = self._active_screen().availableGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
        y = screen_geometry.y() + screen_geometry.height() - self.height() - BOTTOM_MARGIN
        self.move(x, y)

    def _configure_clear_timer(self):
        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._clear_subtitle)

    def _clear_subtitle(self):
        self.label.setText("")
        self.resize(WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    def _resize_to_text(self, text: str):
        metrics = QFontMetrics(self.label.font())
        content_width = WINDOW_WIDTH - (HORIZONTAL_PADDING * 2)
        bounding = metrics.boundingRect(
            0,
            0,
            content_width,
            MAX_WINDOW_HEIGHT * 4,
            int(Qt.TextFlag.TextWordWrap),
            text,
        )
        new_height = min(
            MAX_WINDOW_HEIGHT,
            max(MIN_WINDOW_HEIGHT, bounding.height() + (VERTICAL_PADDING * 2) + 8),
        )

        screen_geometry = self._active_screen().availableGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - WINDOW_WIDTH) // 2
        y = screen_geometry.y() + screen_geometry.height() - new_height - BOTTOM_MARGIN
        self.resize(WINDOW_WIDTH, new_height)
        self.label.setGeometry(0, 0, WINDOW_WIDTH, new_height)
        self.move(x, y)

    @pyqtSlot(str)
    def _show_subtitle(self, text: str):
        if not text:
            self._clear_subtitle()
            return

        self.label.setText(text)
        self._resize_to_text(text)
        self.setVisible(True)
        self.show()
        self.raise_()
        self._clear_timer.start(CLEAR_AFTER_MS)

    def set_text(self, text: str):
        """Thread-safe entry point for the pipeline."""
        self.subtitle_changed.emit(text)

    def set_font_size(self, size: int):
        self._font_size = size
        self._apply_label_style()
        if self.label.text():
            self._resize_to_text(self.label.text())

    def set_background_opacity(self, opacity: int):
        self._bg_opacity = max(80, min(255, opacity))
        self._apply_label_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._anchor_bottom = False

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None


def run_demo():
    demo_lines = [
        "Hello, how are you doing today?",
        "I am testing the speech recognition system.",
        "To jest test polskich napisów na ekranie.",
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
    demo_timer.start(3000)
    show_next_line()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_demo()
