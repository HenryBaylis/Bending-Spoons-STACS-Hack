"""
Test the mic input pipeline end-to-end using audio.stream_mic() + stt.
Prints input_transcript events live as you speak.
Run: python test_mic_input.py
Ctrl+C to stop.
"""
import sys
from collections import deque
import audio
import stt
import config

TRANSCRIPT_WINDOW = 50

word_buffer = deque(maxlen=100)
last_word_end = 0.0
chunk_offset = 0.0
confirm_before = config.AUDIO_CHUNK_SECONDS - config.AUDIO_STEP_SECONDS

print(f"[mic] listening on {config.MIC_DEVICE} — speak now (Ctrl+C to stop)...\n")

try:
    for chunk in audio.stream_mic():
        for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
            if start < last_word_end:
                continue
            relative_end = end - chunk_offset
            if relative_end > confirm_before:
                continue
            last_word_end = end
            word_buffer.append(word)
            context = " ".join(word_buffer)
            text = context[-TRANSCRIPT_WINDOW:]
            print(f"\r[you] {text:<{TRANSCRIPT_WINDOW}}", end="", flush=True)
        chunk_offset += config.AUDIO_STEP_SECONDS
except KeyboardInterrupt:
    print("\n\n[mic] stopped.")
    if word_buffer:
        print(f"Full transcript: {' '.join(word_buffer)}")
