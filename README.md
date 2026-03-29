# Meeting Monitor

A passive meeting assistant that listens to audio, detects when someone asks you a question, and shows a transparent overlay with the transcript and an AI-suggested response.

## How it works

- Captures system audio via loopback (BlackHole 2ch) or mic
- Runs faster-whisper locally for low-latency transcription with per-word timestamps
- Two-stage detection: heuristic gate fires on name/team/project references or question patterns, then Claude Haiku classifies as `question`, `mention`, or `none`
- On a question: waits for `?` (max 3s), then calls Claude to generate a suggested response personalised to your profile
- On a mention: flashes a yellow border ping with the last 20 words of context
- Keeps a rolling 2-sentence meeting summary so the LLM has full context
- Displays everything in a transparent always-on-top Electron overlay

**Latency:** ~3–6s from end of question to suggested response appearing

## Stack

- Python — audio capture, STT, detection, summarisation, answer generation
- Electron (vanilla JS) — transparent always-on-top overlay UI
- Claude API (Haiku 4.5) — answers, summarisation, and LLM-based question classification
- faster-whisper (base, local, int8) — speech to text
- BlackHole 2ch — macOS system audio loopback

## Setup

**1. Install dependencies**
```bash
./setup.sh
```
Creates the Python venv, installs deps, and runs `npm install`.

**2. Set your API key**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-...
```

**3. macOS audio setup**

To capture meeting audio from speakers:
- Install BlackHole: `brew install blackhole-2ch`, then log out and back in
- In **Audio MIDI Setup**, create a Multi-Output Device with MacBook Pro Speakers + BlackHole 2ch
- This lets audio play through speakers while being captured by the app

**4. Run**
```bash
npm start
```
Fill in your name and job title in the setup screen. Optionally attach a context file (PDF, TXT, or MD) for better answers.

**Ctrl+Shift+M** stops the meeting and returns to the setup screen.

## Testing

```bash
cd backend
.venv/bin/python test_stt.py      # test STT pipeline on audio files
.venv/bin/python test_mic.py      # test live mic input
.venv/bin/python test_detector.py # unit tests for heuristic detection
.venv/bin/python test_e2e.py      # end-to-end with simulated transcripts
```

## Project structure

```
main.js           Electron entry: loads .env, spawns Python, bridges stdout to renderer
index.html        Setup screen + transparent overlay UI
backend/
  main.py         Pipeline entry point
  audio.py        macOS audio capture (overlapping 2.4s chunks, 0.8s step)
  stt.py          faster-whisper transcription with per-word timestamps
  detector.py     Heuristic gate for name/team/project/question patterns
  detector_llm.py LLM classifier (question / mention / none)
  answerer.py     Claude answer + optional follow-up generation
  summarizer.py   Rolling 2-sentence chained summary
  vision.py       Optional screen capture (mss)
  config.py       Audio device, Whisper model, chunk settings
frontend/
  (Linux frontend)
```
