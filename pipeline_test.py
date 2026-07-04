"""
pipeline_test.py — offline mini-pipeline: audio file -> EN text -> PL text.

Connects transcribe.py and translate.py together for the first time.
There's no live audio and no overlay yet — this is just proof that the
"brain" of the program (Whisper + DeepL) works end-to-end on a single
pre-recorded .wav file, segment by segment.

This script is temporary scaffolding for Stage 1.3 of the project plan.
Once live audio (Stage 3) and the UI (Stage 2) are ready, main.py will
replace it as the real entry point, wiring everything together with
threads instead of a simple sequential loop.
"""

from transcribe import load_model, transcribe
from translate import translate

AUDIO_PATH = "test_audio/sample.wav"


def main():
    print(f"Loading Whisper model...")
    model = load_model()

    print(f"Transcribing file: {AUDIO_PATH}\n")
    segments, info = transcribe(model, AUDIO_PATH)

    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})\n")

    for segment in segments:
        english_text = segment.text.strip()
        polish_text = translate(english_text)

        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s]")
        print(f"  EN: {english_text}")
        print(f"  PL: {polish_text}\n")


if __name__ == "__main__":
    main()
