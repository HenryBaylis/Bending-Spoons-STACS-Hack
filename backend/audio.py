import sys
import subprocess
import numpy as np
import sounddevice as sd
import config


def stream(callback=None):
    """
    Yields numpy float32 audio chunks captured from the loopback device.
    On macOS: uses sounddevice (BlackHole or similar).
    On Linux: uses parec to capture from the PulseAudio monitor source.
    If callback is provided, calls callback(chunk) instead of yielding.
    """
    if sys.platform == "darwin":
        yield from _stream_sounddevice(callback)
    else:
        yield from _stream_parec(callback)


def _stream_sounddevice(callback=None):
    """macOS: Konan's original implementation."""
    chunk_samples = int(config.AUDIO_SAMPLE_RATE * config.AUDIO_CHUNK_SECONDS)

    with sd.InputStream(
        device=config.AUDIO_DEVICE,
        samplerate=config.AUDIO_SAMPLE_RATE,
        channels=config.AUDIO_CHANNELS,
        dtype="float32",
        blocksize=chunk_samples,
    ) as stream_:
        while True:
            chunk, _ = stream_.read(chunk_samples)
            audio = chunk[:, 0] if chunk.ndim > 1 else chunk.flatten()
            if callback:
                callback(audio)
            else:
                yield audio


def _stream_parec(callback=None):
    """Linux: capture system audio output via parec (PulseAudio monitor source)."""
    chunk_samples = int(config.AUDIO_SAMPLE_RATE * config.AUDIO_CHUNK_SECONDS)
    chunk_bytes = chunk_samples * 2  # int16 = 2 bytes per sample

    cmd = [
        "parec",
        f"--device={config.AUDIO_DEVICE}",
        "--format=s16le",
        f"--rate={config.AUDIO_SAMPLE_RATE}",
        "--channels=1",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        while True:
            raw = proc.stdout.read(chunk_bytes)
            if len(raw) < chunk_bytes:
                break
            audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            if callback:
                callback(audio)
            else:
                yield audio
    finally:
        proc.terminate()
