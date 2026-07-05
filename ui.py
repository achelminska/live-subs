"""
ui.py — LiveSubs control panel (Stage 4 UI).

Small settings window + system tray icon. The subtitle overlay stays
frameless and minimal; this panel is where you start/stop, tweak look,
and quit without hunting for a close button on the overlay itself.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSlider,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).resolve().parent
ICON_PATH = PROJECT_ROOT / "icon.ico"

PANEL_STYLE = """
QWidget#ControlPanel {
    background-color: #14141f;
    color: #e8e8ef;
}
QLabel#Title {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
}
QLabel#Subtitle {
    font-size: 12px;
    color: #8888a0;
}
QLabel#Status {
    font-size: 13px;
    color: #7ee787;
    padding: 8px 0;
}
QLabel#Device {
    font-size: 12px;
    color: #a0a0b8;
}
QLabel#SettingLabel {
    font-size: 12px;
    color: #b0b0c8;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #2a2a3d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 14px;
    margin: -5px 0;
    background: #5b8def;
    border-radius: 7px;
}
QPushButton {
    background-color: #2a2a3d;
    color: #e8e8ef;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #35354d;
}
QPushButton#Primary {
    background-color: #3d6fd9;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#Primary:hover {
    background-color: #4d7fe8;
}
QPushButton#Danger:hover {
    background-color: #5c2a2a;
}
"""


class ControlPanel(QWidget):
    """Main settings / status window for LiveSubs."""

    quit_requested = pyqtSignal()
    overlay_visibility_changed = pyqtSignal(bool)
    font_size_changed = pyqtSignal(int)
    background_opacity_changed = pyqtSignal(int)

    def __init__(self, device_name: str):
        super().__init__()
        self.setObjectName("ControlPanel")
        self.setWindowTitle("LiveSubs")
        self.setFixedWidth(380)
        self.setStyleSheet(PANEL_STYLE)

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self._overlay_visible = True
        self._build_ui(device_name)

    def _build_ui(self, device_name: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("LiveSubs")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("Napisy na żywo EN → PL")
        subtitle.setObjectName("Subtitle")
        layout.addWidget(subtitle)

        self.status_label = QLabel("● Uruchamianie...")
        self.status_label.setObjectName("Status")
        layout.addWidget(self.status_label)

        device_label = QLabel(f"Źródło: {device_name}")
        device_label.setObjectName("Device")
        device_label.setWordWrap(True)
        layout.addWidget(device_label)

        layout.addSpacing(8)

        font_label = QLabel("Rozmiar czcionki")
        font_label.setObjectName("SettingLabel")
        layout.addWidget(font_label)

        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(18, 40)
        self.font_slider.setValue(26)
        self.font_slider.valueChanged.connect(self.font_size_changed.emit)
        layout.addWidget(self.font_slider)

        opacity_label = QLabel("Przezroczystość tła")
        opacity_label.setObjectName("SettingLabel")
        layout.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(60, 220)
        self.opacity_slider.setValue(140)
        self.opacity_slider.valueChanged.connect(self.background_opacity_changed.emit)
        layout.addWidget(self.opacity_slider)

        layout.addSpacing(8)

        button_row = QHBoxLayout()

        self.toggle_button = QPushButton("Ukryj napisy")
        self.toggle_button.clicked.connect(self._toggle_overlay)
        button_row.addWidget(self.toggle_button)

        quit_button = QPushButton("Zakończ")
        quit_button.setObjectName("Danger")
        quit_button.clicked.connect(self.quit_requested.emit)
        button_row.addWidget(quit_button)

        layout.addLayout(button_row)

        hint = QLabel("Przeciągnij overlay myszką, żeby zmienić pozycję.")
        hint.setObjectName("Subtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _toggle_overlay(self):
        self._overlay_visible = not self._overlay_visible
        self.toggle_button.setText("Pokaż napisy" if not self._overlay_visible else "Ukryj napisy")
        self.overlay_visibility_changed.emit(self._overlay_visible)

    def closeEvent(self, event: QCloseEvent):
        """Closing the panel quits the whole app (overlay + tray + worker)."""
        self.quit_requested.emit()
        event.accept()

    def set_status(self, text: str, *, active: bool = True):
        color = "#7ee787" if active else "#8888a0"
        dot = "●" if active else "○"
        self.status_label.setText(f'{dot} {text}')
        self.status_label.setStyleSheet(f"font-size: 13px; color: {color}; padding: 8px 0;")


class LiveSubsTray(QSystemTrayIcon):
    """System tray icon — the overlay hides from the taskbar, so tray is the backup way in."""

    show_panel_requested = pyqtSignal()
    toggle_overlay_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self):
        icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon()
        super().__init__(icon)
        self.setToolTip("LiveSubs")

        menu = QMenu()
        self.setContextMenu(menu)

        show_action = QAction("Pokaż panel", self)
        show_action.triggered.connect(self.show_panel_requested.emit)
        menu.addAction(show_action)

        toggle_action = QAction("Pokaż / ukryj napisy", self)
        toggle_action.triggered.connect(self.toggle_overlay_requested.emit)
        menu.addAction(toggle_action)

        menu.addSeparator()

        quit_action = QAction("Zakończ", self)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_panel_requested.emit()
