# Implementation Guide

Everything that needs to be built for the app to work, in order.

---

## 1. `audio.py` — Loopback audio capture

Capture system audio (what comes out of the speakers — i.e. the other meeting participants).

**What it needs to do:**
- Open the system loopback device using `sounddevice`
- Continuously read audio in chunks (e.g. 3 seconds at a time)
- Yield raw audio numpy arrays to whoever is calling it

**Key details:**
- Sample rate: 16000 Hz (what Whisper expects)
- Channels: 1 (mono)
- On Linux: device must be the PipeWire/PulseAudio monitor source — find it with `pactl list sources short`, it ends in `.monitor`
- `AUDIO_DEVICE` in `config.py` can be set to the device name, or left as `None` to use default

**Interface to expose:**
```python
def stream(callback):
    # calls callback(numpy_array) for each audio chunk
```

---

## 2. `stt.py` — Speech to text

Convert raw audio chunks into text using faster-whisper (runs locally, no API key).

**What it needs to do:**
- Load the faster-whisper model once on startup (model size set in `config.py`)
- Accept a numpy audio array
- Return the transcribed text string

**Key details:**
- faster-whisper expects float32 audio normalised to [-1.0, 1.0]
- `WhisperModel` from `faster_whisper` package
- Use `beam_size=5` for accuracy, `beam_size=1` for speed
- Model is downloaded automatically on first run (~150MB for `base`)

**Interface to expose:**
```python
def transcribe(audio_array) -> str:
    # returns transcribed text or empty string if silence
```

---

## 3. `detector.py` — Question/mention detection

Decide whether the transcribed text is a question directed at the user.

**What it needs to do:**
- Check if the user's name appears in the transcript
- Check if the text matches question patterns (ends in `?`, starts with can/could/would etc., contains "tell me", "walk me through" etc.)
- Return True/False

**Key details:**
- Name comes from `profile.json`
- Heuristic only — no LLM call here, keeps it fast and free
- Should operate on a rolling buffer of the last N transcript chunks joined together, not just the latest chunk — questions often span multiple STT outputs

**Interface to expose:**
```python
def is_directed_at_me(text: str, name: str) -> bool:
```

---

## 4. `answerer.py` — AI answer generation

Call Gemini with the transcript and user profile to generate a suggested response.

**What it needs to do:**
- Load `profile.json` on startup
- Build a system prompt from the profile (name, job title, company, responsibilities, current projects)
- On each call, send the transcript + system prompt to Gemini
- Return the suggested answer as a string

**Key details:**
- Use `google-generativeai` package
- Model: `gemini-2.0-flash` (fast, free tier)
- System prompt should instruct Gemini to reply in first person as the user, keep it concise (2-3 sentences)
- API key from `config.py`

**System prompt template:**
```
You are an assistant helping {name}, a {job_title} at {company} on the {team} team.
Their responsibilities: {responsibilities}.
Current projects: {current_projects}.
{extra_context}

When asked a question in a meeting, suggest a concise, professional response in first
person as if you are them. Keep it to 2-3 sentences unless more detail is needed.
```

**Interface to expose:**
```python
async def generate_answer(transcript: str) -> str:
```

---

## 5. `vision.py` — Screen capture (optional)

Capture a screenshot when a question is detected and send it alongside the transcript to a vision LLM for extra context (useful when someone refers to a shared document or slide).

**What it needs to do:**
- Grab a screenshot of the primary monitor
- Resize to max 1536px and compress to JPEG (to reduce API payload)
- Return as base64 string
- Optionally: send to Gemini multimodal API instead of text-only

**Key details:**
- Use `mss` for screen capture
- Use `Pillow` for resizing/compression
- Only call this when a question is detected (not continuously)

**Interface to expose:**
```python
def capture() -> str:
    # returns base64 JPEG string

async def generate_answer_with_vision(transcript: str, screenshot_b64: str) -> str:
```

---

## 6. `main.py` — Entry point

Wire everything together and emit events to Electron over stdout.

**What it needs to do:**
- Start the audio stream
- For each audio chunk: transcribe → check detector → if triggered: generate answer → print JSON event to stdout

**Event format printed to stdout (one JSON object per line):**
```json
{"type": "question", "transcript": "Henry, what is the status of the auth migration?", "answer": "We're about 70% through..."}
```

**Key details:**
- Use `asyncio`
- Rolling buffer: keep last 5 transcript chunks, join them before running detector
- Debounce: once a question is detected, don't trigger again for 10 seconds (avoid repeated alerts for the same question)
- `sys.stdout.flush()` after every write so Electron receives it immediately

**Rough structure:**
```python
def emit(event):
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()

async def audio_loop():
    buffer = deque(maxlen=5)
    for chunk in audio.stream():
        text = stt.transcribe(chunk)
        if text:
            buffer.append(text)
            context = " ".join(buffer)
            if detector.is_directed_at_me(context, profile["name"]):
                answer = await answerer.generate_answer(context)
                emit({"type": "question", "transcript": context, "answer": answer})
```

---

## 7. `main.js` — Electron entry point (rewrite demo version)

The demo version needs replacing with the real app.

**What it needs to do:**
- Create the transparent, frameless, always-on-top overlay window
- Spawn `backend/main.py` as a child process on app start
- Read newline-delimited JSON from the child process's stdout
- Forward incoming events to the renderer via `ipcMain`/`ipcRenderer`
- Kill the Python process when the app quits

**Key details:**
- Use `child_process.spawn('python', ['../backend/main.py'])` — log stderr for debugging
- No WebSocket needed — stdout is the bridge
- Window settings: `transparent: true`, `frame: false`, `alwaysOnTop: true`, `skipTaskbar: true`
- Position bottom-right of screen
- `setIgnoreMouseEvents(true, { forward: true })` when idle so it doesn't block clicks, `false` when a card is showing

---

## 8. `index.html` — Overlay UI (rewrite demo version)

The demo version is close but needs to match the real event format and handle the idle/active states properly.

**What it needs to do:**
- Stay invisible (fully transparent) when no question is active
- Slide in a card when a `question` IPC event arrives
- Show transcript and suggested answer
- Dismiss button hides the card and re-enables mouse passthrough

**Key details:**
- No framework needed — vanilla JS is fine
- `ipcRenderer.on('question', ...)` to receive events from main process
- On dismiss: send `ipcRenderer.send('dismiss')` back to main so it can re-enable mouse passthrough

---

## 9. `profile.json` — Fill in real details

Replace the placeholder content with real information before use. The more detail, the better the AI answers.

---

## Python dependencies (`requirements.txt`)

```
sounddevice
numpy
faster-whisper
google-generativeai
mss
Pillow
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Running the app

```bash
npm install          # install Electron (first time only)
pip install -r requirements.txt   # install Python deps (first time only)
npm start            # starts everything
```
