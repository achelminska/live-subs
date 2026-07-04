"""
transcribe.py — first building block of the LiveSubs pipeline.

Takes a ready .wav file with English speech and turns it into text using
faster-whisper. At this stage there's no live audio or translation yet —
just verifying that the transcription engine itself works correctly.
"""

from faster_whisper import WhisperModel

MODEL_SIZE = "small"


def load_model() -> WhisperModel:
    """Loads the Whisper model into memory (once, at program startup).

    On a Mac without CUDA GPU we use device="cpu". compute_type="int8"
    quantizes the model weights to lower precision, which speeds up
    inference and reduces memory usage at a small cost to quality.
    """
    return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def transcribe(model: WhisperModel, audio_path: str):
    """Transcribes an audio file and returns a list of segments.

    Each segment is a chunk of speech with its own start/end time and
    text — these will later be the basis for syncing subtitles with audio.
    We force language="en" so the model doesn't waste time guessing the
    language (faster and more reliable than autodetection).
    """
    segments, info = model.transcribe(audio_path, language="en")
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
