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
    word_buffer = deque(maxlen=20)
    word_count = 0
    summary_accumulator = []
    running_summary = ""
    last_triggered = 0
    chunk_offset = 0.0

    for chunk in audio.stream():
        words = list(stt.transcribe_words(chunk, chunk_offset=chunk_offset))
        chunk_offset += config.AUDIO_CHUNK_SECONDS

        for word, _start, _end in words:
            word_count += 1
            word_buffer.append(word)
            summary_accumulator.append(word)
            context = " ".join(word_buffer)

            # Emit rolling transcript window after each word
            emit({"type": "transcript", "text": context[-TRANSCRIPT_WINDOW:]})

            # Summarize every N words
            if word_count % (summarizer.SUMMARIZE_EVERY * 10) == 0:
                block = " ".join(summary_accumulator)
                summary_accumulator.clear()
                running_summary = await summarizer.summarize(block)
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
