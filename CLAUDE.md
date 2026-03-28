# Meeting Monitor

## What this is
A passive meeting assistant that listens to meeting audio, detects when someone directs a question at the user by name (or implicitly via conversational context), and surfaces a transparent always-on-top overlay with the live transcript, a rolling meeting summary, and an AI-suggested response.

## Stack
- **Python** — audio capture, STT, question detection, summarisation, AI answer generation
- **Electron (JS)** — transparent overlay UI + setup screen, spawns Python as a child process
- **Claude API (Haiku 4.5)** — answer generation, summarisation, and LLM-based question/mention classification
- **faster-whisper (tiny, local)** — speech to text
- **parec (Linux) / sounddevice (macOS)** — system audio loopback capture

## How it runs
`npm start` → Electron launches → **setup screen** shown → user enters name, job title, optional context file → clicks Start → Electron writes `profile.json`, saves context file to `backend/`, spawns `backend/main.py` with env vars → Python starts audio pipeline → events written as newline-delimited JSON to stdout → Electron reads stdout, forwards to renderer → overlay displays.

**Ctrl+Shift+M** stops the meeting and returns to the setup screen.

## Frontend detail

### Setup screen (`frontend/index.html`)
- User enters name and job title (both required to enable Start)
- Optional context file: PDF, TXT, or MD — drag & drop or click to browse
- File is read in the renderer via `FileReader`:
  - PDF → `readAsArrayBuffer` → stored as `Uint8Array` in `pendingFile.data`
  - TXT/MD → `readAsText` → stored as string in `pendingFile.data`
- On Start, `ipcRenderer.send('start-meeting', { name, jobTitle, contextFile })` is sent to main process

### Main process (`frontend/main.js`)
- Receives `start-meeting` payload via `ipcMain.on`
- Writes `backend/profile.json` with name, job_title, and empty fields for company/team/projects
- If a context file was attached:
  - PDF: writes `Buffer.from(payload.contextFile.data)` to `backend/meeting_context.pdf`
  - TXT/MD: writes string to `backend/meeting_context.txt` / `.md`
  - Sets `MEETING_CONTEXT_PATH` and `MEETING_CONTEXT_TYPE` env vars before spawning Python
- Spawns `backend/main.py` via the venv Python at `backend/.venv/bin/python`
- Reads Python stdout line by line, parses JSON events, forwards to renderer via `webContents.send`
- On stop: kills Python process, deletes context file, resets window size, sends `show-setup`

### Overlay card (`frontend/index.html`)
Sections (always visible unless noted):
- **Live** — last 50 chars of rolling transcript
- **Mentioned** — last 20 words, shown for 5s when name/team mentioned, updates with new words during that window
- **Last summary** — rolling 2-sentence meeting summary
- **Someone's asking you** (hidden until triggered) — question transcript + suggested response + optional follow-up question; dismissible

IPC events from Python → renderer:
- `transcript` — updates live strip; if mention window active, updates mention text too
- `mention` — triggers yellow border ping + shows mention section for 5s
- `summary` — updates summary panel
- `question` — shows question section with transcript, answer, optional follow-up
- `dismiss` — hides question section
- `show-setup` / `show-overlay` — switches between screens

## File overview
- `frontend/main.js` — Electron entry: handles setup IPC, spawns venv Python, reads stdout, bridges to renderer
- `frontend/index.html` — setup screen + transparent overlay UI (vanilla JS, no framework)
- `backend/main.py` — Python entry: wires audio → STT → detector → LLM classifier → answerer, emits JSON events
- `backend/audio.py` — cross-platform audio capture (parec on Linux, sounddevice on macOS), overlapping 2.4s chunks with 0.8s step
- `backend/stt.py` — faster-whisper tiny transcription with per-word timestamps, vad_filter=True
- `backend/detector.py` — heuristic gate: `should_check_llm(text, name, team, project)` fires on name/team/project reference OR question pattern; also `is_mentioned()` for simple name check
- `backend/detector_llm.py` — LLM classifier: `classify(context, name)` returns `"question"`, `"mention"`, or `"none"` via Claude Haiku
- `backend/answerer.py` — Claude Haiku API call with profile + summary + 100-word context + optional meeting doc; returns `{answer, follow_up}`
- `backend/summarizer.py` — rolling 2-sentence chained summary via Claude Haiku every 100 words
- `backend/vision.py` — optional screen capture via mss for multimodal answers
- `backend/profile.json` — written at runtime from setup screen (name, job_title)
- `backend/config.py` — API keys, audio device, Whisper model, chunk settings
- `backend/transcripts/` — per-session transcript + summary files (gitignored)
- `backend/test_stt.py` — test STT pipeline against audio files
- `backend/test_mic.py` — test live mic input and transcription
- `backend/test_vad.py` — test audio capture + STT pipeline live
- `backend/test_detector.py` — unit tests for heuristic detection patterns
- `backend/test_logic.py` — simulate word-by-word loop, test ? wait and timeout logic
- `backend/test_e2e.py` — end-to-end test with simulated transcripts → Claude API
- `backend/test_meeting.py` — full meeting script simulation through detection + Claude
- `backend/test_implicit.py` — tests implicit detection (questions directed at user without name mention)

## Key decisions
- All AI/audio logic in Python, Electron is just a display shell
- stdout/stdin is the bridge — newline-delimited JSON, no WebSocket needed
- **Overlapping chunks**: 2.4s windows advancing every 0.8s — words cut at chunk boundaries are re-transcribed with full context in the next chunk
- **Word confirmation**: words only emitted if their timestamp falls within the confirmed overlap region (not at the trailing edge of a chunk)
- **? wait logic**: when a question is detected, waits for `?` before calling Claude (max 3s timeout)
- **Two-stage detection**: heuristic gate (`should_check_llm`) → LLM classifier (`classify`) → routes to question or mention. Heuristic fires on name/team/project OR question pattern; LLM decides which it actually is
- **LLM classifier returns question/mention/none**: question → wait for ? → generate answer; mention → emit mention ping with 20-word context
- 100-word rolling buffer sent to Claude for answer context + rolling 2-sentence summary
- 10s debounce on question detection, 5s debounce on mention ping (shared gate check)
- Optional meeting context file: TXT/MD injected into system prompt; PDF sent as base64 document block via Claude document API
- Follow-up question: answerer optionally appends a follow-up on a new line starting with `Follow-up:`, parsed out and shown separately in the overlay
- Profile written from setup screen at meeting start, not hardcoded
- venv Python used by Electron to avoid system Python package conflicts
- **Whisper tiny** used for speed (~247ms/chunk); punctuation accuracy is acceptable for `?` wait logic

## Data flow
```
parec/sounddevice → raw PCM at AUDIO_SAMPLE_RATE
    ↓
audio.py  →  overlapping 2.4s chunks, advancing 0.8s per step
    ↓
stt.py    →  faster-whisper tiny → (word, start, end) tuples
    ↓
main.py   →  per word (timestamp-deduplicated, confirmed only):
              - emit transcript (last 50 chars) + 20-word context to frontend
              - every 100 words:
                  append to transcripts/YYYY-MM-DD_HH-MM-SS.txt
                  Claude Haiku: update 2-sentence summary
                  append to _summary.txt
                  emit summary to frontend
              - heuristic gate fires (name/team/project OR question pattern)?
                  → Claude Haiku classify(context, name) → "question" / "mention" / "none"
                  → "mention": emit mention ping with last 20 words (5s debounce)
                  → "question": wait for ? (max 3s)
                      → Claude Haiku: generate answer + optional follow-up
                      → emit question+answer+follow_up to frontend (10s debounce)
    ↓
frontend  →  transcript → live caption strip (50 chars)
             mention    → yellow border ping + 20-word context shown for 5s
             summary    → summary panel
             question   → answer card with optional follow-up (slides in, dismissible)
```

## Latency
0.8s chunk step + ~247ms Whisper tiny + 0–3s ? wait + ~300ms LLM classify + ~1.5s Claude Haiku answer = **~3.0–6.0s** after question ends

Typical case (~1s after question ends): **~4.0s**

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
