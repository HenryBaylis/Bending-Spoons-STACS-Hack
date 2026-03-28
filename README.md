# Meeting Monitor

A passive meeting assistant that listens to audio, detects when someone asks you a question, and shows a transparent overlay with the transcript and an AI-suggested response.

## How it works

- Captures system audio via loopback (or mic)
- Runs webrtcvad to detect when speech ends, then fires Whisper for transcription
- Detects questions directed at you by name using heuristic patterns
- Calls Claude to generate a suggested response personalised to your profile
- Keeps a rolling 2-sentence meeting summary so the LLM has full context
- Displays everything in a transparent always-on-top overlay

**Latency:** ~2–4s from end of question to suggested response appearing

## Stack

- Python — VAD, STT, detection, summarisation, answer generation
- Electron — transparent overlay UI
- Claude API (free tier) — answers + summarisation
- faster-whisper (tiny, local) — speech to text
- webrtcvad — speech end detection

## Setup

**1. Install dependencies**
```bash
./setup.sh
```
This creates the venv, installs Python deps, patches webrtcvad for Python 3.12+, and runs `npm install`.

**2. Set your API key**
```bash
export ANTHROPIC_API_KEY=your_key_here
```

**3. Edit your profile**

Edit `backend/profile.json` with your name, job title, and current projects. The more detail, the better the suggested answers.

**4. Set your audio device (Linux)**

To capture meeting audio from speakers rather than mic:
```bash
pactl list sources short  # find the .monitor device
```
Set `AUDIO_DEVICE` in `backend/config.py` to that device name.

**5. Run**
```bash
npm start
```

## Testing

```bash
cd backend
../.venv/bin/python test_stt.py   # run VAD + STT on sample audio files
../.venv/bin/python test_mic.py   # test mic input live
```

## Project structure

```
frontend/
  main.js       Electron entry point
  index.html    Overlay UI
backend/
  main.py       Pipeline entry point
  audio.py      VAD + audio capture
  stt.py        Whisper transcription
  detector.py   Question detection
  answerer.py   Claude answer generation
  summarizer.py Rolling meeting summary
  vision.py     Optional screen capture
  config.py     Settings
  profile.json  Your profile (edit this)
```
