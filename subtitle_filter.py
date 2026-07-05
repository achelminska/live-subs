"""
subtitle_filter.py — drop junk transcriptions before translation.

Live Whisper often emits single words, filler sounds, or classic
hallucinations on silence/music. Translating those wastes DeepL calls
and floods the overlay with nonsense like "Ty" or "Dziękuję".
"""

import re

# Common Whisper hallucinations on non-speech audio.
_HALLUCINATIONS = {
    "thank you",
    "thanks for watching",
    "thanks for listening",
    "subscribe",
    "you",
    "i",
    "a",
    "the",
    "ha",
    "ha ha",
    "huh",
    "oh",
    "uh",
    "um",
    "yeah",
    "yes",
    "no",
    "ok",
    "okay",
    "hmm",
    "hm",
    "wow",
    "bye",
    "hello",
    "hi",
}

# Short exclamations worth keeping despite being one word.
_KEEP_SHORT = {"no!", "yes!", "stop!", "help!", "run!", "go!", "wait!"}


def _normalize(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def is_worth_translating(text: str) -> bool:
    """Return False for fragments that should not reach DeepL or the overlay."""
    raw = text.strip()
    if not raw:
        return False

    if raw.lower().rstrip(".!?") in _HALLUCINATIONS:
        return False

    if raw.lower() in _KEEP_SHORT:
        return True

    # Pure numbers / punctuation.
    if re.fullmatch(r"[\d\s\W]+", raw):
        return False

    normalized = _normalize(raw)
    words = normalized.split()

    # Single letters or two-letter noise ("I", "Oh").
    if len(words) == 1 and len(words[0]) <= 2:
        return False

    # Very short fragments unless they look like real words.
    if len(normalized) < 8 and len(words) < 2:
        return False

    return True
