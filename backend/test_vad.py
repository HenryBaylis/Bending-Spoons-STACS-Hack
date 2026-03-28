"""
Test overlapping audio capture + STT pipeline with word confirmation.
Run: python test_vad.py
Play audio through your speakers — only confirmed words are printed.
Ctrl+C to stop.
"""
import audio
import stt
import config

CONFIRM_BEFORE = config.AUDIO_CHUNK_SECONDS - config.AUDIO_STEP_SECONDS

print(f"Device: {config.AUDIO_DEVICE}")
print(f"Chunk: {config.AUDIO_CHUNK_SECONDS}s | Step: {config.AUDIO_STEP_SECONDS}s | Confirm window: {CONFIRM_BEFORE}s")
print("Listening... (Ctrl+C to stop)\n")

chunk_offset = 0.0
last_word_end = 0.0

for chunk in audio.stream():
    for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
        if start < last_word_end:
            continue
        if (end - chunk_offset) > CONFIRM_BEFORE:
            continue  # near chunk boundary, wait for next chunk
        last_word_end = end
        print(f"[{start:.2f}s] {word}")
    chunk_offset += config.AUDIO_STEP_SECONDS
