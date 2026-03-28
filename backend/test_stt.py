"""
Demo: loads each audio file in audio_files/, chunks it, and runs STT on each chunk.
Run from the backend directory: python test_stt.py
"""
import os
import numpy as np
import av
import json
from collections import deque
import config
import stt
import detector
from stt import transcribe_words

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_files")
CHUNK_SECONDS = 1


def load_audio(path: str) -> np.ndarray:
    """Decode any audio file to a float32 mono array at 16kHz."""
    container = av.open(path)
    resampler = av.AudioResampler(format="fltp", layout="mono", rate=config.AUDIO_SAMPLE_RATE)
    samples = []
    for frame in container.decode(audio=0):
        for resampled in resampler.resample(frame):
            samples.append(resampled.to_ndarray()[0])
    # flush resampler
    for resampled in resampler.resample(None):
        samples.append(resampled.to_ndarray()[0])
    return np.concatenate(samples).astype(np.float32)


def chunk(audio: np.ndarray, chunk_seconds: float, sample_rate: int):
    """Yield fixed-size chunks from an audio array."""
    size = int(chunk_seconds * sample_rate)
    for start in range(0, len(audio), size):
        yield audio[start:start + size]


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), config.PROFILE_PATH)) as f:
    profile = json.load(f)
name = profile["name"]

files = sorted(f for f in os.listdir(AUDIO_DIR) if not f.startswith("."))

if not files:
    print("No audio files found in audio_files/")
else:
    for filename in files:
        path = os.path.join(AUDIO_DIR, filename)
        print(f"\n=== {filename} ===")
        audio = load_audio(path)
        duration = len(audio) / config.AUDIO_SAMPLE_RATE
        print(f"Duration: {duration:.1f}s — splitting into {CHUNK_SECONDS}s chunks")

        word_buffer = deque(maxlen=20)
        for i, chunk_audio in enumerate(chunk(audio, CHUNK_SECONDS, config.AUDIO_SAMPLE_RATE)):
            offset = i * CHUNK_SECONDS
            words = list(transcribe_words(chunk_audio, chunk_offset=offset))
            if not words:
                print(f"  [{offset:.0f}s] (silence)")
                continue
            for word, start, end in words:
                word_buffer.append(word)
                context = " ".join(word_buffer)
                triggered = detector.is_directed_at_me(context, name)
                flag = " *** TRIGGERED ***" if triggered else ""
                print(f"  [{start:.2f}s] {word}{flag}")
