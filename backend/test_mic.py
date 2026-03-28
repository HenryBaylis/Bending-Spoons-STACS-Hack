"""
Test laptop mic: records 5 seconds and transcribes it.
Run: python test_mic.py
"""
import sounddevice as sd
import numpy as np
import config
import stt

SECONDS = 5

print("Available input devices:")
for i, dev in enumerate(sd.query_devices()):
    if dev['max_input_channels'] > 0:
        print(f"  [{i}] {dev['name']}")

print(f"\nRecording {SECONDS}s from default input device — speak now...")
audio = sd.rec(
    int(SECONDS * config.AUDIO_SAMPLE_RATE),
    samplerate=config.AUDIO_SAMPLE_RATE,
    channels=1,
    dtype="float32",
)
sd.wait()
print("Done. Transcribing...")

chunk = audio.flatten()
words = list(stt.transcribe_words(chunk))
if words:
    for word, start, end in words:
        print(f"  [{start:.2f}s] {word}")
else:
    print("  (nothing detected — try speaking louder or check your mic)")
