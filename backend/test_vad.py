"""
Test audio capture + STT pipeline.
Run: python test_vad.py
Play audio through your speakers — transcription will appear in real time.
Ctrl+C to stop.
"""
import audio
import stt
import config

print(f"Device: {config.AUDIO_DEVICE}")
print(f"Chunk: {config.AUDIO_CHUNK_SECONDS}s | Model: {config.WHISPER_MODEL}")
print("Listening... (Ctrl+C to stop)\n")

chunk_offset = 0.0
for chunk in audio.stream():
    for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
        print(f"[{start:.2f}s] {word}")
    chunk_offset += config.AUDIO_CHUNK_SECONDS
