import numpy as np
import sounddevice as sd
import config


def stream(callback=None):
    """
    Yields numpy float32 audio chunks captured from the loopback device.
    If callback is provided, calls callback(chunk) instead of yielding.
    """
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
            # Flatten to 1D mono
            audio = chunk[:, 0] if chunk.ndim > 1 else chunk.flatten()
            if callback:
                callback(audio)
            else:
                yield audio
