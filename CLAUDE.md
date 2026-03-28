# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user, and surfaces a transparent always-on-top overlay with the live transcript, a rolling meeting summary, and an AI-suggested response.

## Stack
- **Python** — VAD, audio capture, STT, question detection, summarisation, AI answer generation
- **Electron (JS)** — transparent overlay UI, spawns Python as a child process
- **Claude API (Haiku 4.5)** — answer generation and summarisation

## How it runs
`npm start` → Electron launches → spawns `backend/main.py` as a child process → Python starts the audio pipeline → events written as newline-delimited JSON to stdout → Electron reads stdout, forwards to renderer → overlay displays.

## File overview
- `frontend/main.js` — Electron entry point: spawns venv Python, reads stdout, bridges to renderer via IPC
- `frontend/index.html` — transparent frameless overlay UI (vanilla JS, no framework)
- `backend/main.py` — Python entry point: wires audio → STT → detector → answerer, emits JSON events
- `backend/audio.py` — sounddevice loopback capture with webrtcvad speech-end detection
- `backend/stt.py` — faster-whisper (tiny model) transcription with per-word timestamps
- `backend/detector.py` — heuristic question/mention detection (name + question patterns)
- `backend/answerer.py` — Claude Haiku API call with user profile + meeting summary as context
- `backend/summarizer.py` — chains meeting transcript into a rolling 2-sentence summary via Claude Haiku
- `backend/vision.py` — optional screen capture via mss for multimodal answers
- `backend/profile.json` — user's name, job title, company, responsibilities (edit before use)
- `backend/config.py` — API keys, audio device, Whisper model size
- `backend/transcripts/` — per-session transcript files (gitignored)
- `backend/test_stt.py` — test VAD + STT pipeline against audio files
- `backend/test_mic.py` — test live mic input and transcription

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- stdout/stdin is the bridge — newline-delimited JSON, no WebSocket needed
- webrtcvad fires Whisper as soon as speech ends (~500ms silence), not on a fixed timer
- Per-word timestamps from faster-whisper — detector runs after every word, not every chunk
- Heuristic detector only — no LLM classifier, keeps Claude calls to ~1 per question
- Rolling 2-sentence chained summary — passes full meeting context to answerer without growing unboundedly
- Raw transcript appended to file every 100 words for persistence
- User profile injected as system prompt so answers are personalised and in-character
- venv Python used by Electron to avoid system Python package conflicts

## Data flow
```
audio.py  →  sounddevice 30ms int16 frames
              webrtcvad detects speech/silence
              yields float32 speech segment on 500ms silence
    ↓
stt.py    →  faster-whisper tiny → (word, start, end) tuples
    ↓
main.py   →  per word:
              - emit transcript (last 20 chars) to frontend
              - every 100 words:
                  append to transcripts/YYYY-MM-DD.txt
                  Claude Haiku: update 2-sentence chained summary
                  emit summary to frontend
              - detector: name + question pattern?
                  → Claude Haiku: generate answer (profile + summary + last 20 words)
                  → emit question+answer to frontend
    ↓
frontend  →  transcript → live caption strip
             summary    → summary panel
             question   → answer card (slides in)
```

## Latency
~500ms VAD + ~350ms Whisper tiny + ~1–2s Claude Haiku = **~2–3s** after speech ends

## Setup
```bash
./setup.sh
# edit backend/profile.json with your details
export ANTHROPIC_API_KEY=your_key_here
npm start
```

## Linux loopback
To capture meeting audio (not mic), set `AUDIO_DEVICE` in `config.py` to your PipeWire monitor source:
```bash
pactl list sources short  # find the line ending in .monitor
```
