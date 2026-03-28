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
import detector_llm
import answerer
import summarizer
import config

DEBOUNCE_SECONDS = 10
TRANSCRIPT_WINDOW = 50  # characters to show in the live feed
WORDS_PER_SUMMARY = 100


def emit(event: dict):
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def _transcript_path() -> str:
    os.makedirs(os.path.join(os.path.dirname(__file__), "transcripts"), exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    return os.path.join(os.path.dirname(__file__), "transcripts", filename)


async def audio_loop(profile: dict):
    word_buffer = deque(maxlen=100)
    word_count = 0
    summary_accumulator = []
    running_summary = ""
    last_triggered = 0
    transcript_path = _transcript_path()

    last_word_end = 0.0
    chunk_offset = 0.0
    confirm_before = config.AUDIO_CHUNK_SECONDS - config.AUDIO_STEP_SECONDS
    pending_question_at = None
    QUESTION_MAX_WAIT = 20.0
    last_mention = 0
    MENTION_DEBOUNCE = 5

    print("[audio] listening...", file=sys.stderr, flush=True)
    for chunk in audio.stream():
        for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
            if start < last_word_end:
                continue
            relative_end = end - chunk_offset
            if relative_end > confirm_before:
                continue
            last_word_end = end
            word_count += 1
            word_buffer.append(word)
            summary_accumulator.append(word)
            context = " ".join(word_buffer)

            words_20 = " ".join(list(word_buffer)[-20:])
            emit({"type": "transcript", "text": context[-TRANSCRIPT_WINDOW:], "words": words_20})

            if word_count % WORDS_PER_SUMMARY == 0:
                block = " ".join(summary_accumulator)
                summary_accumulator.clear()
                with open(transcript_path, "a") as f:
                    f.write(block + "\n")
                running_summary = await summarizer.update_summary(running_summary, block)
                emit({"type": "summary", "text": running_summary})
                with open(transcript_path.replace(".txt", "_summary.txt"), "a") as f:
                    f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {running_summary}\n")

            now = time.time()

            # LLM classification — loose gate first, then classify into question/mention/none
            if pending_question_at is None and detector.should_check_llm(
                context, profile["name"], profile.get("team", ""), profile.get("current_projects", "")
            ):
                if now - last_triggered >= DEBOUNCE_SECONDS and now - last_mention >= MENTION_DEBOUNCE:
                    label = await detector_llm.classify(context, profile["name"])
                    if label == "question":
                        pending_question_at = now
                    elif label == "mention":
                        last_mention = now
                        emit({"type": "mention", "words": words_20})

            # Fire if ? appears or max wait exceeded
            if pending_question_at is not None:
                question_complete = "?" in word
                timed_out = (now - pending_question_at) >= QUESTION_MAX_WAIT
                if question_complete or timed_out:
                    pending_question_at = None
                    last_triggered = now
                    result = await answerer.generate_answer(context, summary=running_summary)
                    emit({"type": "question", "transcript": context, "answer": result["answer"], "follow_up": result["follow_up"]})

        chunk_offset += config.AUDIO_STEP_SECONDS


async def main():
    with open(config.PROFILE_PATH) as f:
        profile = json.load(f)

    await audio_loop(profile)


if __name__ == "__main__":
    asyncio.run(main())
