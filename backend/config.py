import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# --- API keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Audio ---
# Set to None to auto-detect, or set to the name of your loopback device.
# On Linux: run `pactl list sources short` and find the line ending in .monitor
AUDIO_DEVICE = None
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SECONDS = 3  # how many seconds of audio per STT chunk

# --- STT ---
# faster-whisper model size: tiny, base, small, medium, large
# smaller = faster but less accurate
WHISPER_MODEL = "base"

# --- Detector ---
# minimum confidence before alerting (0.0 - 1.0, heuristic only uses 0 or 1)
DETECTION_THRESHOLD = 0.8

# --- Profile ---
PROFILE_PATH = os.path.join(_DIR, "profile.json")

