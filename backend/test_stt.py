"""
Demo: loads each audio file in audio_files/, runs it through the VAD pipeline,
and prints per-word output with detector results.
Run from the backend directory: python test_stt.py
"""
import os
import collections
import time
import numpy as np
import av
import json
import webrtcvad
from collections import deque
import config
import stt
import detector

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_files")
FRAME_MS = 30
FRAME_SAMPLES = int(config.AUDIO_SAMPLE_RATE * FRAME_MS / 1000)
SILENCE_FRAMES = int(500 / FRAME_MS)
MIN_SPEECH_FRAMES = int(200 / FRAME_MS)
PADDING_FRAMES = int(150 / FRAME_MS)


def load_audio_int16(path: str) -> np.ndarray:
    """Decode audio file to int16 mono at 16kHz."""
    container = av.open(path)
    resampler = av.AudioResampler(format="fltp", layout="mono", rate=config.AUDIO_SAMPLE_RATE)
    samples = []
    for frame in container.decode(audio=0):
        for resampled in resampler.resample(frame):
            samples.append(resampled.to_ndarray()[0])
    for resampled in resampler.resample(None):
        samples.append(resampled.to_ndarray()[0])
    audio = np.concatenate(samples).astype(np.float32)
    return (audio * 32768).clip(-32768, 32767).astype(np.int16)


def vad_segments(pcm_int16: np.ndarray):
    """Run webrtcvad on int16 audio, yield float32 speech segments."""
    vad = webrtcvad.Vad(2)
    ring_buffer = collections.deque(maxlen=PADDING_FRAMES)
    speech_frames = []
    in_speech = False
    silent_count = 0

    for start in range(0, len(pcm_int16), FRAME_SAMPLES):
        frame = pcm_int16[start:start + FRAME_SAMPLES]
        if len(frame) < FRAME_SAMPLES:
            break
        frame_bytes = frame.tobytes()
        is_speech = vad.is_speech(frame_bytes, config.AUDIO_SAMPLE_RATE)

        if not in_speech:
            ring_buffer.append(frame)
            if is_speech:
                in_speech = True
                silent_count = 0
                speech_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            speech_frames.append(frame)
            if not is_speech:
                silent_count += 1
                if silent_count >= SILENCE_FRAMES:
                    if len(speech_frames) >= MIN_SPEECH_FRAMES:
                        pcm = np.concatenate(speech_frames).astype(np.float32) / 32768.0
                        yield pcm
                    speech_frames.clear()
                    in_speech = False
                    silent_count = 0
            else:
                silent_count = 0

    # yield any remaining speech
    if speech_frames and len(speech_frames) >= MIN_SPEECH_FRAMES:
        pcm = np.concatenate(speech_frames).astype(np.float32) / 32768.0
        yield pcm


with open(config.PROFILE_PATH) as f:
    profile = json.load(f)
name = profile["name"]

files = sorted(f for f in os.listdir(AUDIO_DIR) if not f.startswith("."))

if not files:
    print("No audio files found in audio_files/")
else:
    for filename in files:
        path = os.path.join(AUDIO_DIR, filename)
        print(f"\n=== {filename} ===")
        pcm = load_audio_int16(path)
        segments = list(vad_segments(pcm))
        print(f"VAD detected {len(segments)} speech segment(s)")

        word_buffer = deque(maxlen=20)
        for i, segment in enumerate(segments):
            duration = len(segment) / config.AUDIO_SAMPLE_RATE
            t0 = time.perf_counter()
            words = list(stt.transcribe_words(segment))
            elapsed = time.perf_counter() - t0
            print(f"\n  Segment {i+1} ({duration:.2f}s) — STT took {elapsed*1000:.0f}ms:")
            if not words:
                print("    (nothing transcribed)")
                continue
            for word, start, end in words:
                word_buffer.append(word)
                context = " ".join(word_buffer)
                triggered = detector.is_directed_at_me(context, name)
                flag = " *** TRIGGERED ***" if triggered else ""
                print(f"    [{start:.2f}s] {word}{flag}")
