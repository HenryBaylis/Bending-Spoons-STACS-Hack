import asyncio
import json
import os
import sys
import time
from collections import deque
from datetime import datetime

import audio
import stt
import detector
import answerer
import summarizer
import config

DEBOUNCE_SECONDS = 10
TRANSCRIPT_WINDOW = 20  # characters to show in the live feed
WORDS_PER_SUMMARY = 100


def emit(event: dict):
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def _transcript_path() -> str:
    os.makedirs(os.path.join(os.path.dirname(__file__), "transcripts"), exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    return os.path.join(os.path.dirname(__file__), "transcripts", filename)


async def audio_loop(profile: dict):
    word_buffer = deque(maxlen=20)
    word_count = 0
    summary_accumulator = []
    running_summary = ""
    last_triggered = 0
    transcript_path = _transcript_path()

    for chunk in audio.stream():
        words = list(stt.transcribe_words(chunk))

        for word, _start, _end in words:
            word_count += 1
            word_buffer.append(word)
            summary_accumulator.append(word)
            context = " ".join(word_buffer)

            # Emit rolling transcript window after each word
            emit({"type": "transcript", "text": context[-TRANSCRIPT_WINDOW:]})

            # Every 100 words: append to transcript file then summarize
            if word_count % WORDS_PER_SUMMARY == 0:
                block = " ".join(summary_accumulator)
                summary_accumulator.clear()
                with open(transcript_path, "a") as f:
                    f.write(block + "\n")
                running_summary = await summarizer.update_summary(running_summary, block)
                emit({"type": "summary", "text": running_summary})

            # Question detection after each word
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
