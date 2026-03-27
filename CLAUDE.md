# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user, and surfaces a transparent always-on-top overlay with the transcript and an AI-suggested response.

## Stack
- **Python** — audio capture, STT, question detection, AI answer generation
- **Electron (JS)** — transparent overlay UI, spawns Python as a child process
- **Gemini API** — answer generation (free tier)

## How it runs
`npm start` → Electron launches → spawns Python (`main.py`) as a child process → Python starts the audio pipeline → events sent over WebSocket (localhost:8765) → Electron forwards to renderer → overlay displays.

## File overview
- `main.js` — Electron entry point: spawns Python, manages overlay window, bridges WebSocket → IPC
- `index.html` — transparent frameless overlay UI (vanilla JS, no framework)
- `main.py` — Python entry point: wires audio → STT → detector → answerer, runs WebSocket server
- `audio.py` — sounddevice loopback capture
- `stt.py` — faster-whisper transcription
- `detector.py` — heuristic question/mention detection (checks name + question patterns)
- `answerer.py` — Gemini API call with user profile injected as system prompt
- `vision.py` — optional screen capture via mss, sends screenshot alongside transcript to vision LLM
- `profile.json` — user's name, job title, company, responsibilities (edit this before use)
- `config.py` — API keys, audio device, model sizes, WebSocket port
- `gobin.md` — original build plan notes
- `HELP.md` — detailed implementation guide

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- WebSocket is the bridge between Python and Electron (localhost:8765)
- Heuristic detector only — no LLM classifier, keeps Gemini calls to ~1 per question
- User profile injected as system prompt so answers are personalised and in-character
- Linux loopback: use PipeWire monitor source (find with `pactl list sources short`, pick the `.monitor` device)

## Current state
- Demo overlay exists in `main.js` and `index.html` — needs rewriting for real app
- Python files are empty stubs — need implementing
- `config.py` and `profile.json` have placeholder content — edit profile before use
- See `HELP.md` for what needs to be done
