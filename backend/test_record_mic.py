"""
Records 5 seconds from the mic device and saves as mic_test.wav.
Play it back to verify the mic is capturing correctly.
Run: python test_record_mic.py
"""
import subprocess
import numpy as np
import wave
import config

SECONDS = 5
SAMPLE_RATE = config.AUDIO_SAMPLE_RATE
OUTPUT = "mic_test.wav"

print(f"Recording {SECONDS}s from {config.MIC_DEVICE}...")
print("Speak now!")

cmd = [
    "parec",
    f"--device={config.MIC_DEVICE}",
    "--format=s16le",
    f"--rate={SAMPLE_RATE}",
    "--channels=1",
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
n_bytes = SAMPLE_RATE * SECONDS * 2  # 2 bytes per sample (s16le)
raw = proc.stdout.read(n_bytes)
proc.terminate()

with wave.open(OUTPUT, "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    f.writeframes(raw)

print(f"Saved to {OUTPUT} — play with: aplay {OUTPUT}")
