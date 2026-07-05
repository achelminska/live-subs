"""
audio_capture.py — Stage 3.1: capture system audio (speakers), not the microphone.

Fixed-size chunks every CHUNK_SECONDS — simple and predictable for Whisper.
Uses PyAudioWPatch WASAPI loopback on Windows.
"""

import threading
import time
from typing import Callable

import numpy as np
import pyaudiowpatch as pyaudio

WHISPER_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SECONDS = 3.0
LOOPBACK_SUFFIX = " [Loopback]"


def _to_mono(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return audio
    return audio.mean(axis=1)


def _resample(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate:
        return audio.astype(np.float32, copy=False)

    source_length = len(audio)
    target_length = int(source_length * target_rate / source_rate)
    if target_length == 0:
        return np.array([], dtype=np.float32)

    source_indices = np.arange(source_length)
    target_indices = np.linspace(0, source_length - 1, target_length)
    return np.interp(target_indices, source_indices, audio).astype(np.float32)


def list_loopback_devices() -> list[dict]:
    """Return all WASAPI loopback devices (speaker output mirrored as input)."""
    pa = pyaudio.PyAudio()
    try:
        devices = []
        for info in pa.get_loopback_device_info_generator():
            devices.append(
                {
                    "index": info["index"],
                    "name": info["name"],
                    "channels": info["maxInputChannels"],
                    "sample_rate": int(info["defaultSampleRate"]),
                }
            )
        return devices
    finally:
        pa.terminate()


def find_loopback_device(preferred_output_name: str | None = None) -> dict:
    """Pick the loopback device that matches the default (or named) speakers."""
    pa = pyaudio.PyAudio()
    try:
        loopback_devices = list(pa.get_loopback_device_info_generator())
        if not loopback_devices:
            raise RuntimeError(
                "No WASAPI loopback device found. "
                "Make sure something is set as your default playback device."
            )

        if preferred_output_name is None:
            wasapi_info = pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_output = pa.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            return pa.get_wasapi_loopback_analogue_by_dict(default_output)

        preferred_base = preferred_output_name.removesuffix(LOOPBACK_SUFFIX).strip().lower()
        for device in loopback_devices:
            base_name = device["name"].removesuffix(LOOPBACK_SUFFIX).strip().lower()
            if base_name == preferred_base:
                return device

        return loopback_devices[0]
    finally:
        pa.terminate()


class SystemAudioCapture:
    """Captures live speaker output in fixed CHUNK_SECONDS slices."""

    def __init__(
        self,
        on_chunk: Callable[[np.ndarray], None],
        chunk_seconds: float = DEFAULT_CHUNK_SECONDS,
        device_info: dict | None = None,
    ):
        self.on_chunk = on_chunk
        self.chunk_seconds = chunk_seconds

        if device_info is None:
            device_info = find_loopback_device()
        self.device_info = device_info

        self.device_name = device_info["name"]
        self.device_index = device_info["index"]
        self.sample_rate = int(device_info["defaultSampleRate"])
        self.channels = device_info["maxInputChannels"]

        self._frames_per_chunk = int(self.sample_rate * chunk_seconds)
        self._pending = np.empty(0, dtype=np.float32)
        self._pa: pyaudio.PyAudio | None = None
        self._stream: pyaudio.Stream | None = None
        self._lock = threading.Lock()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            print(f"[audio_capture] {status}")

        audio = np.frombuffer(in_data, dtype=np.float32)
        if self.channels > 1:
            audio = audio.reshape(-1, self.channels)

        mono = _to_mono(audio)
        chunk_to_emit = None

        with self._lock:
            self._pending = np.concatenate((self._pending, mono))
            if len(self._pending) >= self._frames_per_chunk:
                chunk_to_emit = self._pending[: self._frames_per_chunk]
                self._pending = self._pending[self._frames_per_chunk :]

        if chunk_to_emit is not None:
            resampled = _resample(chunk_to_emit, self.sample_rate, WHISPER_SAMPLE_RATE)
            self.on_chunk(resampled)

        return (None, pyaudio.paContinue)

    def start(self):
        if self._stream is not None:
            return

        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=self.channels,
            rate=self.sample_rate,
            frames_per_buffer=1024,
            input=True,
            input_device_index=self.device_index,
            stream_callback=self._audio_callback,
        )
        self._stream.start_stream()

    def stop(self):
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        if self._pa is not None:
            self._pa.terminate()
            self._pa = None

        with self._lock:
            self._pending = np.empty(0, dtype=np.float32)


def main():
    print("Available loopback devices:")
    for device in list_loopback_devices():
        print(f"  [{device['index']}] {device['name']}")

    capture = SystemAudioCapture(on_chunk=lambda audio: None)

    def on_chunk(audio: np.ndarray):
        rms = float(np.sqrt(np.mean(audio**2)))
        bar = "#" * min(40, int(rms * 400))
        print(f"RMS {rms:.4f}  {bar}")

    capture.on_chunk = on_chunk

    print(f"\nCapturing from: {capture.device_name}")
    print(f"Chunk every {capture.chunk_seconds:.1f}s @ {WHISPER_SAMPLE_RATE} Hz mono")
    print("Play something on your speakers. Ctrl+C to stop.\n")

    capture.start()
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        capture.stop()


if __name__ == "__main__":
    main()
