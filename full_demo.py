"""
full_demo.py — visual preview combining all three finished modules:
transcribe.py (Whisper) + translate.py (DeepL) + overlay.py (PyQt6).

Not an official step from the project plan — just a demo to see Polish
subtitles appear on the actual overlay window, driven by a real audio
file, before live audio (Stage 3) is wired in.
"""

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from overlay import SubtitleOverlay
from transcribe import load_model, transcribe
from translate import translate

AUDIO_PATH = "test_audio/sample.wav"


def main():
    print("Loading Whisper model...")
    model = load_model()

    print(f"Transcribing and translating: {AUDIO_PATH}\n")
    segments, _ = transcribe(model, AUDIO_PATH)

    subtitles = []
    for segment in segments:
        english_text = segment.text.strip()
        polish_text = translate(english_text)
        subtitles.append(polish_text)
        print(f"EN: {english_text}")
        print(f"PL: {polish_text}\n")

    app = QApplication(sys.argv)
    overlay = SubtitleOverlay()
    overlay.show()

    counter = {"i": 0}

    def show_next_line():
        if counter["i"] >= len(subtitles):
            counter["i"] = 0
        overlay.set_text(subtitles[counter["i"]])
        counter["i"] += 1

    timer = QTimer()
    timer.timeout.connect(show_next_line)
    timer.start(3000)
    show_next_line()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
