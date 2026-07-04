"""
translate.py — second building block of the LiveSubs pipeline.

Takes English text and returns its Polish translation using the DeepL API.
This is a plain HTTP request, so unlike audio/transcription it works
identically on macOS and Windows — no platform limitations here.
"""

import os

import deepl
from dotenv import load_dotenv

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

_translator = None


def get_translator() -> deepl.Translator:
    """Lazily creates a single DeepL client instance for the whole program."""
    global _translator
    if _translator is None:
        if not DEEPL_API_KEY:
            raise RuntimeError(
                "DEEPL_API_KEY not found. Copy .env.example to .env and add your key."
            )
        _translator = deepl.Translator(DEEPL_API_KEY)
    return _translator


def translate(text: str, target_lang: str = "PL") -> str:
    """Translates text into the target language.

    If the request fails (no internet, quota exceeded, invalid key, etc.),
    we fall back to returning the original English text instead of
    crashing the whole pipeline — a missing translation is much less
    disruptive than a dead program.
    """
    try:
        translator = get_translator()
        result = translator.translate_text(text, target_lang=target_lang)
        return result.text
    except Exception as error:
        print(f"[translate] Falling back to original text due to error: {error}")
        return text


def main():
    sample_sentences = [
        "Hello, how are you doing today?",
        "I am testing the speech recognition system.",
        "This is a sample sentence for the whisper model to transcribe.",
    ]

    for sentence in sample_sentences:
        translated = translate(sentence)
        print(f"EN: {sentence}")
        print(f"PL: {translated}\n")


if __name__ == "__main__":
    main()
