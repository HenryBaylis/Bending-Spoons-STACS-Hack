import sys
import subprocess
import collections
import numpy as np
import sounddevice as sd
import config

STEP_SECONDS = config.AUDIO_STEP_SECONDS


def stream_mic(callback=None):
    """
    Yields overlapping numpy float32 audio chunks from the microphone input.
    Same chunk/step settings as stream() but captures from MIC_DEVICE.
    """
    if sys.platform == "darwin":
        yield from _stream_sounddevice(callback, device=config.MIC_DEVICE)
    else:
        yield from _stream_parec(callback, device=config.MIC_DEVICE)


def stream(callback=None):
    """
    Yields overlapping numpy float32 audio chunks.
    Each chunk is AUDIO_CHUNK_SECONDS long, advancing by AUDIO_STEP_SECONDS.
    On macOS: uses sounddevice. On Linux: uses parec.
    """
    if sys.platform == "darwin":
        yield from _stream_sounddevice(callback)
    else:
        yield from _stream_parec(callback)


def stream_steps_mic():
    """Same as stream_steps() but captures from MIC_DEVICE."""
    step_samples = int(config.AUDIO_SAMPLE_RATE * STEP_SECONDS)
    with sd.InputStream(
        device=config.MIC_DEVICE,
        samplerate=config.AUDIO_SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=step_samples,
    ) as s:
        while True:
            chunk, _ = s.read(step_samples)
            yield chunk.flatten()


def stream_steps():
    """
    Yields raw non-overlapping float32 step-sized chunks (AUDIO_STEP_SECONDS each).
    Used for the continuous rolling audio buffer — runs independently of the STT pipeline.
    """
    step_samples = int(config.AUDIO_SAMPLE_RATE * STEP_SECONDS)
    step_bytes = step_samples * 2
    if sys.platform == "darwin":
        with sd.InputStream(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=step_samples,
        ) as s:
            while True:
                chunk, _ = s.read(step_samples)
                yield chunk.flatten()
    else:
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
                raw = proc.stdout.read(step_bytes)
                if len(raw) < step_bytes:
                    return
                yield np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        finally:
            proc.terminate()


def _make_overlap_buffer(step_iter):
    """
    Takes an iterator of step-sized audio arrays and yields full-size
    overlapping chunks by maintaining a rolling buffer.
    """
    chunk_samples = int(config.AUDIO_SAMPLE_RATE * config.AUDIO_CHUNK_SECONDS)
    buf = collections.deque()
    buf_len = 0

    for step in step_iter:
        buf.append(step)
        buf_len += len(step)
        if buf_len >= chunk_samples:
            chunk = np.concatenate(list(buf))[-chunk_samples:]
            yield chunk
            # Drop oldest step to advance the window
            buf_len -= len(buf.popleft())


def _stream_sounddevice(callback=None, device=None):
    step_samples = int(config.AUDIO_SAMPLE_RATE * STEP_SECONDS)
    with sd.InputStream(
        device=device or config.AUDIO_DEVICE,
        samplerate=config.AUDIO_SAMPLE_RATE,
        channels=config.AUDIO_CHANNELS,
        dtype="float32",
        blocksize=step_samples,
    ) as s:
        def _steps():
            while True:
                chunk, _ = s.read(step_samples)
                yield chunk[:, 0] if chunk.ndim > 1 else chunk.flatten()
        for chunk in _make_overlap_buffer(_steps()):
            if callback:
                callback(chunk)
            else:
                yield chunk


def _stream_parec(callback=None, device=None):
    step_samples = int(config.AUDIO_SAMPLE_RATE * STEP_SECONDS)
    step_bytes = step_samples * 2

    cmd = [
        "parec",
        f"--device={device or config.AUDIO_DEVICE}",
        "--format=s16le",
        f"--rate={config.AUDIO_SAMPLE_RATE}",
        "--channels=1",
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    try:
        def _steps():
            while True:
                raw = proc.stdout.read(step_bytes)
                if len(raw) < step_bytes:
                    return
                yield np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        for chunk in _make_overlap_buffer(_steps()):
            if callback:
                callback(chunk)
            else:
                yield chunk
    finally:
        proc.terminate()
