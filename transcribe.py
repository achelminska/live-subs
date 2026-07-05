"""
transcribe.py — first building block of the LiveSubs pipeline.

Takes English speech and turns it into text using faster-whisper — either
from a .wav file (Stage 1) or from a live audio buffer (Stage 3.2).
"""

import numpy as np
from faster_whisper import WhisperModel

from app_paths import app_dir

MODEL_SIZE = "small"
MODEL_DIR = app_dir() / "models"


def load_model() -> WhisperModel:
    """Loads the Whisper model into memory (once, at program startup).

    On a Mac without CUDA GPU we use device="cpu". compute_type="int8"
    quantizes the model weights to lower precision, which speeds up
    inference and reduces memory usage at a small cost to quality.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return WhisperModel(
        MODEL_SIZE,
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR),
    )


def transcribe(model: WhisperModel, audio_path: str):
    """Transcribes an audio file and returns a list of segments.

    Each segment is a chunk of speech with its own start/end time and
    text — these will later be the basis for syncing subtitles with audio.
    We force language="en" so the model doesn't waste time guessing the
    language (faster and more reliable than autodetection).
    """
    segments, info = model.transcribe(audio_path, language="en")
    return list(segments), info


def transcribe_audio(model: WhisperModel, audio: np.ndarray):
    """Transcribes a mono float32 buffer from live capture (16 kHz).

    vad_filter drops silent chunks so Whisper doesn't hallucinate text
    over background noise or quiet music beds.
    """
    segments, info = model.transcribe(
        audio,
        language="en",
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 300},
    )
    return list(segments), info


def main():
    audio_path = "test_audio/sample.wav"

    print(f"Loading Whisper model ({MODEL_SIZE})...")
    model = load_model()

    print(f"Transcribing file: {audio_path}\n")
    segments, info = transcribe(model, audio_path)

    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})\n")

    for segment in segments:
        print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")


if __name__ == "__main__":
    main()
