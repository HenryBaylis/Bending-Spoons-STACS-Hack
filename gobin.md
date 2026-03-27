# Meeting Monitor — Build Plan

Passive meeting assistant that listens continuously and pings you when someone directs a question or action item at you.

---

## What it does

- Runs silently in the background during a meeting
- Captures system audio (what other participants say)
- Transcribes speech in real-time
- Detects when a question or request is directed at you
- Sends a desktop notification with the transcript and an AI-suggested response
- AI responses are personalised using your profile (name, job title, company, responsibilities)
- **Advanced:** screenshots the screen and combines it with the transcript for context (e.g. shared slides or documents)

---

## Stack

- **Python** — audio capture, STT, question detection, notification
- **JavaScript (Node.js / Electron)** — optional desktop overlay UI if you want something fancier than a system notification

Start with pure Python. Add an Electron overlay only if you want a visible UI.

---

## Architecture

```
System audio loopback
        ↓
  STT (streaming)
        ↓
  Rolling transcript buffer
        ↓
  Question/mention detector
        ↓
  [transcript + screenshot + user profile]  ←── screen capture (optional)
        ↓
  Desktop notification + AI answer
```

---

## User profile

The AI needs to know who you are to give relevant, in-character answers. Store this in a `profile.json` (or `config.py`) and inject it into every LLM prompt as a system message.

```json
{
  "name": "Henry",
  "job_title": "Software Engineer",
  "company": "Acme Corp",
  "team": "Platform",
  "responsibilities": "Backend services, API design, on-call rotation",
  "current_projects": "Migrating auth service to OAuth2, Q3 infra cost reduction",
  "extra_context": "I prefer concise answers in meetings. I report to the CTO."
}
```

This gets injected as the system prompt:

```python
SYSTEM_PROMPT = """
You are an assistant helping {name}, a {job_title} at {company} on the {team} team.
Their responsibilities: {responsibilities}.
Current projects: {current_projects}.
{extra_context}

When someone asks them a question in a meeting, suggest a concise, professional response
in first person as if you are them. Keep it to 2-3 sentences unless more detail is needed.
"""
```

The more detail in the profile, the better the answers — especially for questions about
project status, decisions, or anything role-specific.

---

## Components

### 1. Audio capture (Python)

Use **sounddevice** to capture the system loopback (what plays through speakers = other participants).

```python
import sounddevice as sd
# list devices: sd.query_devices()
# pick the monitor/loopback device for your output
```

On Linux you need PulseAudio/PipeWire monitor source (e.g. `alsa_output.*.monitor`).
On Windows use WASAPI loopback. On macOS use BlackHole or Soundflower.

### 2. Speech-to-text (Python)

Options in rough order of ease:
- **Deepgram** streaming API — best latency, free tier available
- **OpenAI Whisper** (local) — `pip install openai-whisper`, no API key, slower
- **Google Cloud STT** streaming — reliable, needs credentials
- **faster-whisper** — local, much faster than original Whisper

For a hackathon: start with Deepgram streaming or faster-whisper.

### 3. Question/mention detector (Python)

Two approaches:

**Heuristic (instant, no API):**
```python
import re

QUESTION_PATTERNS = [
    r'\?$',
    r'^(can|could|would|will|do|does|did|is|are|was|were|have|has)\b',
    r'\b(tell me|walk me|explain|describe|how would you|what would you|why did you)\b',
]

def is_directed_at_me(text: str, name: str) -> bool:
    text_lower = text.strip().lower()
    mentioned = name.lower() in text_lower
    is_question = any(re.search(p, text_lower) for p in QUESTION_PATTERNS)
    return mentioned or is_question
```

**LLM classifier (smarter, ~200ms):**
```python
# Send last 2-3 sentences + user profile to Gemini Flash
# Prompt: "Is the speaker directing a question or request at {name}? Reply only yes or no."
# Use Gemini Flash — it's free tier and very fast
```

Use heuristic first. Add LLM fallback if too many false positives/negatives.

### 4. Notification (Python)

```python
# Cross-platform
from plyer import notification
notification.notify(title="Someone's asking you something", message=transcript)

# Linux only (no dependency)
import subprocess
subprocess.run(["notify-send", "Someone's asking you something", transcript])
```

### 5. AI answer generation (Python)

When triggered, fire off an async request to Gemini/Ollama with the transcript and user
profile, and stream the suggested answer into a terminal window or overlay.

```python
import google.generativeai as genai

def generate_answer(transcript: str, profile: dict) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
    system = SYSTEM_PROMPT.format(**profile)
    response = model.generate_content(
        f"{system}\n\nThey just said: \"{transcript}\"\n\nSuggest a response:"
    )
    return response.text
```

### 6. Computer vision / screen capture (optional, Python)

When triggered, grab a screenshot and send it alongside the transcript to a vision LLM.
Useful when someone is referring to a shared document, slide, or screen.

```python
import mss
import base64
from PIL import Image
import io

def capture_screen() -> str:
    """Capture screen and return as base64 JPEG string."""
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[1])
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        img.thumbnail((1536, 1536))  # cap size before sending
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode()
```

Then pass both to Gemini's multimodal API:

```python
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content([
    f"{system}\n\nThey just said: \"{transcript}\"\n\nThe current screen is attached. Suggest a response:",
    {"mime_type": "image/jpeg", "data": capture_screen()}
])
```

Use a vision-capable local model (e.g. `llava-phi3` via Ollama) if you want no API key.

---

## File structure (starting from scratch)

```
meeting-monitor/
  main.py              # entry point, wires everything together
  audio.py             # sounddevice capture + chunking
  stt.py               # STT wrapper (Deepgram / Whisper)
  detector.py          # question/mention detection (heuristic + optional LLM)
  notifier.py          # desktop notification
  answerer.py          # LLM answer generation using user profile
  vision.py            # optional: screen capture + vision LLM
  profile.json         # your name, job title, company, responsibilities etc
  config.py            # API keys, device names, thresholds
  requirements.txt
```

---

## Quick start order

1. Get audio capture working — print raw audio chunks to terminal
2. Pipe into STT — print transcript chunks to terminal
3. Add question/mention detector — print "DIRECTED AT YOU" when triggered
4. Add notification
5. Add AI answer generation with user profile injected as system prompt
6. Add screen capture — grab screenshot on trigger and send alongside transcript to vision LLM

---

## Key packages

```
sounddevice
numpy
faster-whisper        # or deepgram-sdk
plyer                 # notifications
google-generativeai   # Gemini (free tier)
mss                   # screen capture
Pillow                # image resizing before sending
```

---

## Linux gotcha

System loopback on Linux requires capturing the PulseAudio/PipeWire monitor device, not the default input. Run:

```bash
pactl list sources short
```

Find the one ending in `.monitor` — use that device name in sounddevice.
