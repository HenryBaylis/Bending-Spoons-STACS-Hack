import asyncio
import json
import sys
import time
from collections import deque

import audio
import stt
import detector
import answerer
import summarizer
import config

DEBOUNCE_SECONDS = 10
TRANSCRIPT_WINDOW = 20  # characters to show in the live feed


def emit(event: dict):
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


async def audio_loop(profile: dict):
    buffer = deque(maxlen=5)
    chunk_count = 0
    summary_accumulator = []
    running_summary = ""
    last_triggered = 0

    for chunk in audio.stream():
        text = stt.transcribe(chunk)
        if not text:
            continue

        chunk_count += 1
        buffer.append(text)
        summary_accumulator.append(text)

        # Emit rolling transcript window
        context = " ".join(buffer)
        emit({"type": "transcript", "text": context[-TRANSCRIPT_WINDOW:]})

        # Summarize every N chunks
        if chunk_count % summarizer.SUMMARIZE_EVERY == 0:
            block = " ".join(summary_accumulator)
            summary_accumulator.clear()
            running_summary = await summarizer.summarize(block)
            emit({"type": "summary", "text": running_summary})

        # Question detection
        if detector.is_directed_at_me(context, profile["name"]):
            now = time.time()
            if now - last_triggered < DEBOUNCE_SECONDS:
                continue
            last_triggered = now

            answer = await answerer.generate_answer(context, summary=running_summary)
            emit({"type": "question", "transcript": context, "answer": answer})


async def main():
    with open(config.PROFILE_PATH) as f:
        profile = json.load(f)

    await audio_loop(profile)


if __name__ == "__main__":
    asyncio.run(main())
