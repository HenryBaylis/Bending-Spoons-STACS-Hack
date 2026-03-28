import os

_DIR = os.path.dirname(os.path.abspath(__file__))

# --- API keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# --- Audio ---
# Set to None to auto-detect, or set to the name of your loopback device.
# On Linux: run `pactl list sources short` and find the line ending in .monitor
AUDIO_DEVICE = "alsa_output.pci-0000_63_00.6.analog-stereo.monitor"  # Linux: pactl list sources short | grep monitor
# AUDIO_DEVICE = "BlackHole 2ch"  # macOS
MIC_DEVICE = "alsa_input.pci-0000_63_00.6.analog-stereo"  # Linux: pactl list sources short | grep input
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SECONDS = 2.4   # window size — 3 overlapping chunks at any time
AUDIO_STEP_SECONDS  = 0.8   # how far each chunk advances (2s overlap between chunks)

# --- STT ---
# faster-whisper model size: tiny, base, small, medium, large
# smaller = faster but less accurate
WHISPER_MODEL = "base"

# --- Detector ---
# minimum confidence before alerting (0.0 - 1.0, heuristic only uses 0 or 1)
DETECTION_THRESHOLD = 0.8

# --- Profile ---
PROFILE_PATH = os.path.join(_DIR, "profile.json")

