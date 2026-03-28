import collections
import numpy as np
import sounddevice as sd
import webrtcvad
import config

# webrtcvad works on 10/20/30ms frames of 16-bit PCM
FRAME_MS = 30
FRAME_SAMPLES = int(config.AUDIO_SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples

# How many consecutive silent frames before we consider speech ended
SILENCE_FRAMES = int(500 / FRAME_MS)  # ~500ms of silence

# Minimum speech duration to bother sending to Whisper
MIN_SPEECH_FRAMES = int(200 / FRAME_MS)  # ~200ms minimum

# Padding: keep N frames before/after speech for better transcription
PADDING_FRAMES = int(150 / FRAME_MS)


def stream():
    """
    Yields numpy float32 audio arrays of variable length.
    Each yielded array is a complete speech segment — Whisper fires
    immediately after the speaker stops, not after a fixed timer.
    """
    vad = webrtcvad.Vad(2)  # aggressiveness 0-3, 2 is a good balance
    ring_buffer = collections.deque(maxlen=PADDING_FRAMES)
    speech_frames = []
    in_speech = False
    silent_count = 0

    with sd.RawInputStream(
        device=config.AUDIO_DEVICE,
        samplerate=config.AUDIO_SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=FRAME_SAMPLES,
    ) as stream_:
        while True:
            frame_bytes, _ = stream_.read(FRAME_SAMPLES)

            is_speech = vad.is_speech(bytes(frame_bytes), config.AUDIO_SAMPLE_RATE)

            if not in_speech:
                ring_buffer.append(frame_bytes)
                if is_speech:
                    in_speech = True
                    silent_count = 0
                    # include the pre-speech padding
                    speech_frames.extend(ring_buffer)
                    ring_buffer.clear()
            else:
                speech_frames.append(frame_bytes)
                if not is_speech:
                    silent_count += 1
                    if silent_count >= SILENCE_FRAMES:
                        # Speech ended — yield if long enough
                        if len(speech_frames) >= MIN_SPEECH_FRAMES:
                            pcm = b"".join(bytes(f) for f in speech_frames)
                            audio = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
                            yield audio
                        speech_frames.clear()
                        in_speech = False
                        silent_count = 0
                else:
                    silent_count = 0
