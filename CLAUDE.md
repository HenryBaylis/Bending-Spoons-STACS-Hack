# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user, and surfaces a transparent always-on-top overlay with the transcript and an AI-suggested response.

## Stack
- **Python** — audio capture, STT, question detection, AI answer generation
- **Electron (JS)** — transparent overlay UI, spawns Python as a child process
- **Gemini API** — answer generation (free tier)

## How it runs
`npm start` → Electron launches → spawns Python (`backend/main.py`) as a child process → Python starts the audio pipeline → events written as JSON lines to stdout → Electron reads stdout, forwards to renderer → overlay displays.

## File overview
- `frontend/main.js` — Electron entry point: spawns Python, manages overlay window, bridges WebSocket → IPC
- `frontend/index.html` — transparent frameless overlay UI (vanilla JS, no framework)
- `backend/main.py` — Python entry point: wires audio → STT → detector → answerer, runs WebSocket server
- `backend/audio.py` — sounddevice loopback capture
- `backend/stt.py` — faster-whisper transcription
- `backend/detector.py` — heuristic question/mention detection (checks name + question patterns)
- `backend/answerer.py` — Gemini API call with user profile injected as system prompt
- `backend/vision.py` — optional screen capture via mss, sends screenshot alongside transcript to vision LLM
- `backend/profile.json` — user's name, job title, company, responsibilities (edit this before use)
- `backend/config.py` — API keys, audio device, model sizes, WebSocket port
- `gobin.md` — original build plan notes
- `HELP.md` — detailed implementation guide

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- stdout/stdin is the bridge between Python and Electron — newline-delimited JSON, no WebSocket needed
- Heuristic detector only — no LLM classifier, keeps Gemini calls to ~1 per question
- User profile injected as system prompt so answers are personalised and in-character
- Linux loopback: use PipeWire monitor source (find with `pactl list sources short`, pick the `.monitor` device)

## Current state
- Demo overlay exists in `main.js` and `index.html` — needs rewriting for real app
- Python files are empty stubs — need implementing
- `config.py` and `profile.json` have placeholder content — edit profile before use
- See `HELP.md` for what needs to be done
