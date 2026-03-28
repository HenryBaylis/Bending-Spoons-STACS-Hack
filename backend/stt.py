import numpy as np
from faster_whisper import WhisperModel
import config

_model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")


def transcribe(audio: np.ndarray) -> str:
    """
    Transcribe a float32 mono audio array (16kHz) to text.
    Returns an empty string if nothing was detected.
    """
    audio = _normalise(audio)
    segments, _ = _model.transcribe(audio, beam_size=5, language="en")
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text


def transcribe_words(audio: np.ndarray, chunk_offset: float = 0.0):
    """
    Transcribe audio and yield (word, start_time, end_time) tuples.
    chunk_offset adds a base timestamp so times are relative to the file start.
    """
    audio = _normalise(audio)
    segments, _ = _model.transcribe(
        audio, beam_size=5, language="en", word_timestamps=True
    )
    for segment in segments:
        for word in segment.words:
            yield word.word.strip(), chunk_offset + word.start, chunk_offset + word.end


def _normalise(audio: np.ndarray) -> np.ndarray:
    audio = audio.astype(np.float32)
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak
    return audio
