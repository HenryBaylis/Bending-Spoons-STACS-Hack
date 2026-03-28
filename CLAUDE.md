# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user, and surfaces a transparent always-on-top overlay with the live transcript, a rolling meeting summary, and an AI-suggested response.

## Stack
- **Python** — VAD, audio capture, STT, question detection, summarisation, AI answer generation
- **Electron (JS)** — transparent overlay UI, spawns Python as a child process
- **Gemini API** — answer generation and summarisation (free tier)

## How it runs
`npm start` → Electron launches → spawns `backend/main.py` as a child process → Python starts the audio pipeline → events written as newline-delimited JSON to stdout → Electron reads stdout, forwards to renderer → overlay displays.

## File overview
- `frontend/main.js` — Electron entry point: spawns Python, reads stdout, bridges to renderer via IPC
- `frontend/index.html` — transparent frameless overlay UI (vanilla JS, no framework)
- `backend/main.py` — Python entry point: wires audio → STT → detector → answerer, emits JSON events
- `backend/audio.py` — sounddevice loopback capture with webrtcvad speech-end detection
- `backend/stt.py` — faster-whisper (tiny model) transcription with per-word timestamps
- `backend/detector.py` — heuristic question/mention detection (name + question patterns)
- `backend/answerer.py` — Gemini API call with user profile + meeting summary as context
- `backend/summarizer.py` — chains meeting transcript into a rolling 2-sentence summary via Gemini
- `backend/vision.py` — optional screen capture via mss for multimodal Gemini answers
- `backend/profile.json` — user's name, job title, company, responsibilities (edit before use)
- `backend/config.py` — API keys, audio device, Whisper model size
- `backend/transcripts/` — per-session transcript files (gitignored)

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- stdout/stdin is the bridge — newline-delimited JSON, no WebSocket needed
- webrtcvad fires Whisper as soon as speech ends (~500ms silence), not on a fixed timer
- Per-word timestamps from faster-whisper — detector runs after every word, not every chunk
- Heuristic detector only — no LLM classifier, keeps Gemini calls to ~1 per question
- Rolling 2-sentence chained summary — passes full meeting context to answerer without growing unboundedly
- Raw transcript appended to file every 100 words for persistence
- User profile injected as system prompt so answers are personalised and in-character

## Data flow
```
audio.py  →  webrtcvad (30ms frames) → speech segment on silence
    ↓
stt.py    →  faster-whisper tiny → (word, start, end) tuples
    ↓
main.py   →  per word:
              - emit transcript (last 20 chars) to frontend
              - every 100 words: save to transcript file, update 2-sentence summary
              - detector: name + question pattern? → answerer → emit question+answer
```

## Latency
~500ms VAD + ~350ms Whisper tiny + ~1–3s Gemini = **~2–4s** after speech ends

## Setup
```bash
npm install
python -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
# edit backend/profile.json with your details
# set GEMINI_API_KEY env var
npm start
```

## Linux loopback
To capture meeting audio (not mic), set `AUDIO_DEVICE` in `config.py` to your PipeWire monitor source:
```bash
pactl list sources short  # find the line ending in .monitor
```
