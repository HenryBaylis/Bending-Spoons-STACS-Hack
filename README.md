# Meeting Monitor

A passive meeting assistant that listens to meeting audio, detects when someone asks you a question (by name or implicitly), and shows a transparent always-on-top overlay with the live transcript, a rolling meeting summary, and an AI-suggested response.

## How it works

- Captures system audio via BlackHole 2ch loopback (or mic) using sounddevice
- Runs faster-whisper locally for transcription with overlapping 2.4s chunks
- Two-stage detection: heuristic gate → Claude Haiku LLM classifier
- Calls Claude Haiku to generate a suggested response personalised to your profile and meeting context
- Keeps a rolling 2-sentence meeting summary for full context
- Displays everything in a transparent always-on-top Electron overlay

**Latency:** ~3–6s from end of question to suggested response appearing

## Stack

- Python — audio capture, STT, detection, summarisation, answer generation
- Electron — transparent overlay UI + setup screen (vanilla JS)
- Claude API (Haiku 4.5) — answers, summarisation, LLM-based question classification
- faster-whisper (base, local, int8) — speech to text
- sounddevice — audio capture (mic + loopback)

## macOS audio setup

To capture meeting audio from speakers (not just your mic), you need BlackHole:

```bash
brew install blackhole-2ch
```

After install, **log out and back in** for the driver to register. Then:

1. Open **Audio MIDI Setup** (search in Spotlight)
2. Click `+` → **Create Multi-Output Device**
3. Add both **MacBook Pro Speakers** and **BlackHole 2ch**
4. Set this Multi-Output Device as your system output in System Settings → Sound

BlackHole 2ch will now receive a copy of all system audio. `backend/config.py` already has `AUDIO_DEVICE = "BlackHole 2ch"` set.

For mic-only use, set `AUDIO_DEVICE` to `"MacBook Pro Microphone"` in `backend/config.py`.

## Setup

**1. Install dependencies**
```bash
./setup.sh
```
Creates the Python venv, installs dependencies, and runs `npm install`.

**2. Set your API key**

Create a `.env` file in the project root (already gitignored):
```
ANTHROPIC_API_KEY=sk-ant-...
```

**3. Run**
```bash
npm start
```

Fill in your name and job title in the setup screen. Optionally attach a context file (PDF, TXT, or MD) for meeting-specific background. Click **Start**.

**Ctrl+Shift+M** stops the meeting and returns to the setup screen.

## Testing

```bash
cd backend
.venv/bin/python test_mic.py     # test live mic input + transcription
.venv/bin/python test_vad.py     # test audio capture + STT pipeline live
.venv/bin/python test_e2e.py     # end-to-end with simulated transcripts → Claude
```

## Project structure

```
frontend/
  main.js       Electron entry: loads .env, spawns Python, bridges IPC
  index.html    Setup screen + transparent overlay UI
backend/
  main.py       Pipeline entry: wires audio → STT → detection → LLM
  audio.py      sounddevice capture, overlapping 2.4s chunks
  stt.py        faster-whisper base transcription
  detector.py   Heuristic gate (name/team/project/question patterns)
  detector_llm.py  Claude Haiku classifier → question/mention/none
  answerer.py   Claude Haiku answer generation
  summarizer.py Rolling 2-sentence meeting summary
  vision.py     Optional screen capture for multimodal answers
  config.py     Audio device, Whisper model, chunk settings
  profile.json  Written at runtime from setup screen
```
