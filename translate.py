"""
translate.py — second building block of the LiveSubs pipeline.

Takes English text and returns its Polish translation using the DeepL API.
This is a plain HTTP request, so unlike audio/transcription it works
identically on macOS and Windows — no platform limitations here.
"""

import os

import deepl

from app_paths import load_env, save_env_value

load_env()


def get_api_key() -> str | None:
    key = os.getenv("DEEPL_API_KEY", "").strip()
    if not key or key.startswith("your-"):
        return None
    return key


def is_api_key_configured() -> bool:
    return get_api_key() is not None


def is_valid_api_key(key: str) -> bool:
    cleaned = key.strip()
    return len(cleaned) >= 20 and ":" in cleaned


def set_api_key(key: str) -> None:
    """Persist key to .env and reset the cached DeepL client."""
    global _translator
    cleaned = key.strip()
    save_env_value("DEEPL_API_KEY", cleaned)
    os.environ["DEEPL_API_KEY"] = cleaned
    _translator = None


_translator = None


def get_translator() -> deepl.Translator:
    """Lazily creates a single DeepL client instance for the whole program."""
    global _translator
    if _translator is None:
        api_key = get_api_key()
        if not api_key:
            raise RuntimeError("DEEPL_API_KEY not configured.")
        _translator = deepl.Translator(api_key)
    return _translator


def translate(text: str, target_lang: str = "PL") -> str:
    """Translates text into the target language.

    If the request fails (no internet, quota exceeded, invalid key, etc.),
    we fall back to returning the original English text instead of
    crashing the whole pipeline — a missing translation is much less
    disruptive than a dead program.
    """
    if not is_api_key_configured():
        return text

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
