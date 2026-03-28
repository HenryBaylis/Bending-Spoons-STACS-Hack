# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user by name, and surfaces a transparent always-on-top overlay with the live transcript, a rolling meeting summary, and an AI-suggested response.

## Stack
- **Python** — audio capture, STT, question detection, summarisation, AI answer generation
- **Electron (JS)** — transparent overlay UI + setup screen, spawns Python as a child process
- **Claude API (Haiku 4.5)** — answer generation and summarisation
- **faster-whisper (tiny, local)** — speech to text
- **parec (Linux) / sounddevice (macOS)** — system audio loopback capture

## How it runs
`npm start` → Electron launches → **setup screen** shown → user enters name, job title, optional context file → clicks Start → Electron writes `profile.json`, spawns `backend/main.py` → Python starts audio pipeline → events written as newline-delimited JSON to stdout → Electron reads stdout, forwards to renderer → overlay displays.

**Ctrl+Shift+M** stops the meeting and returns to the setup screen.

## File overview
- `frontend/main.js` — Electron entry: handles setup IPC, spawns venv Python, reads stdout, bridges to renderer
- `frontend/index.html` — setup screen + transparent overlay UI (vanilla JS, no framework)
- `backend/main.py` — Python entry: wires audio → STT → detector → answerer, emits JSON events
- `backend/audio.py` — cross-platform audio capture (parec on Linux, sounddevice on macOS), overlapping 2.4s chunks with 0.8s step
- `backend/stt.py` — faster-whisper (tiny) transcription with per-word timestamps, vad_filter=True
- `backend/detector.py` — heuristic question/mention detection (name + question patterns + team mention)
- `backend/answerer.py` — Claude Haiku API call with profile + summary + 100-word context + optional meeting doc
- `backend/summarizer.py` — rolling 2-sentence chained summary via Claude Haiku every 100 words
- `backend/vision.py` — optional screen capture via mss for multimodal answers
- `backend/profile.json` — written at runtime from setup screen (name, job_title)
- `backend/config.py` — API keys, audio device, Whisper model, chunk settings
- `backend/transcripts/` — per-session transcript + summary files (gitignored)
- `backend/test_stt.py` — test STT pipeline against audio files
- `backend/test_mic.py` — test live mic input and transcription
- `backend/test_vad.py` — test audio capture + STT pipeline live
- `backend/test_detector.py` — unit tests for question detection patterns
- `backend/test_logic.py` — simulate word-by-word loop, test ? wait and timeout logic
- `backend/test_e2e.py` — end-to-end test with simulated transcripts → Claude API
- `backend/test_meeting.py` — full meeting script simulation through detection + Claude

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- stdout/stdin is the bridge — newline-delimited JSON, no WebSocket needed
- **Overlapping chunks**: 2.4s windows advancing every 0.8s (50% overlap) — words cut at chunk boundaries are re-transcribed with full context in the next chunk
- **Word confirmation**: words only emitted if their timestamp falls within the confirmed overlap region (not at the trailing edge of a chunk)
- **? wait logic**: when a question is detected, waits for `?` before calling Claude (max 3s timeout)
- 100-word rolling buffer sent to Claude for answer context + rolling 2-sentence summary
- Heuristic detector only — no LLM classifier, keeps Claude calls to ~1 per question
- 10s debounce on question detection, 5s debounce on mention ping
- Optional meeting context file (TXT/MD injected into system prompt; PDF via Claude document API)
- Profile written from setup screen at meeting start, not hardcoded
- venv Python used by Electron to avoid system Python package conflicts

## Data flow
```
parec/sounddevice → raw PCM at AUDIO_SAMPLE_RATE
    ↓
audio.py  →  overlapping 2.4s chunks, advancing 0.8s per step
    ↓
stt.py    →  faster-whisper tiny → (word, start, end) tuples
    ↓
main.py   →  per word (timestamp-deduplicated, confirmed only):
              - emit transcript (last 20 chars) to frontend
              - check is_mentioned → emit mention ping (5s debounce)
              - every 100 words:
                  append to transcripts/YYYY-MM-DD_HH-MM-SS.txt
                  Claude Haiku: update 2-sentence summary
                  append to _summary.txt
                  emit summary to frontend
              - detector: name + question pattern?
                  → wait for ? (max 3s)
                  → Claude Haiku: generate answer (profile + doc + summary + last 100 words)
                  → emit question+answer to frontend (10s debounce)
    ↓
frontend  →  transcript → live caption strip
             mention    → yellow border ping on overlay card
             summary    → summary panel
             question   → answer card (slides in, dismissible)
```

## Latency
0.8s chunk step + ~350ms Whisper tiny + 0–3s ? wait + ~1.5s Claude Haiku = **~2.7–5.7s** after question ends

Typical case (~1s after question ends): **~3.7s**

## Setup
```bash
./setup.sh
export ANTHROPIC_API_KEY=your_key_here
npm start
# Fill in name + job title in setup screen, optionally attach a context file
```

## Linux loopback
Audio is captured from system output (not mic) via `parec`. Set `AUDIO_DEVICE` in `config.py`:
```bash
pactl list sources short  # find the line ending in .monitor
```

## macOS
Set `AUDIO_DEVICE = "BlackHole 2ch"` in `config.py` (requires BlackHole virtual audio driver).
