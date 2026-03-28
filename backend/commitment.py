"""
Promise/commitment detection and audio clip saving.

Detects when someone in the meeting makes a commitment ("I'll", "I will", etc.),
captures the audio from the start of the promise to the end of the sentence,
and saves it as a WAV clip alongside a screenshot.
"""

import os
import re
import wave
from collections import deque
from datetime import datetime

import numpy as np

_PROMISE_PATTERNS = [
    r"\bI'?ll\b",
    r"\bI will\b",
    r"\bwe'?ll\b",
    r"\bwe will\b",
    r"\bI'?m going to\b",
    r"\bI'?m gonna\b",
    r"\bwill (?:send|get|check|follow|update|have|make|do|be|share|look|ping|reach|confirm|review)\b",
    r"\bwill get back\b",
    r"\bwill follow[ -]?up\b",
    r"\bby (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|eod|end of day|tomorrow|next week|tonight|noon)\b",
    r"\blet me (?:check|find|get|send|confirm|look|see|ask)\b",
    r"\bI can (?:do|have|send|get|check|confirm)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _PROMISE_PATTERNS]
_SENTENCE_END = re.compile(r'[.!?]$')


def has_promise(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


def is_sentence_end(word: str) -> bool:
    return bool(_SENTENCE_END.search(word.strip()))


def save_clip(steps: deque, n_steps: int, sample_rate: int, transcript_dir: str) -> str:
    """
    Concatenate the last n_steps from the rolling buffer and write to a WAV file.
    Returns the absolute path to the saved file.
    """
    items = list(steps)
    clip_steps = items[-n_steps:] if n_steps < len(items) else items
    audio = np.concatenate(clip_steps)
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)

    os.makedirs(transcript_dir, exist_ok=True)
    filename = datetime.now().strftime("commitment_%Y-%m-%d_%H-%M-%S.wav")
    path = os.path.join(transcript_dir, filename)

    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(audio_int16.tobytes())

    return path
