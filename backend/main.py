import asyncio
import json
import os
import sys
import threading
import time
from collections import deque
from datetime import datetime

import audio
import stt
import detector
import detector_llm
import answerer
import summarizer
import commitment
import negotiation
import assertiveness
import vision
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


async def audio_loop(profile: dict, raw_buffer: deque, word_buffer: deque, mic_word_buffer: deque):
    word_count = 0
    summary_accumulator = []
    running_summary = ""
    last_triggered = 0
    transcript_path = _transcript_path()

    pending_question_at = None
    QUESTION_MAX_WAIT = 20.0
    last_mention = 0
    MENTION_DEBOUNCE = 5
    last_assertiveness = 0
    ASSERTIVENESS_DEBOUNCE = 10
    pending_promise_at = None
    promise_words = []
    last_commitment = 0
    COMMITMENT_DEBOUNCE = 15
    COMMITMENT_MAX_WAIT = 20.0
    transcript_dir = os.path.join(os.path.dirname(__file__), "transcripts")

    # Run blocking audio+STT in a thread, feed confirmed words via queue
    loop = asyncio.get_event_loop()
    word_queue: asyncio.Queue = asyncio.Queue()

    def _producer():
        last_word_end = 0.0
        chunk_offset = 0.0
        confirm_before = config.AUDIO_CHUNK_SECONDS - config.AUDIO_STEP_SECONDS
        print("[audio] listening...", file=sys.stderr, flush=True)
        for chunk in audio.stream():
            for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
                if start < last_word_end:
                    continue
                if (end - chunk_offset) > confirm_before:
                    continue
                last_word_end = end
                loop.call_soon_threadsafe(word_queue.put_nowait, word)
            chunk_offset += config.AUDIO_STEP_SECONDS

    threading.Thread(target=_producer, daemon=True).start()

    while True:
        word = await word_queue.get()
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
            try:
                running_summary = await summarizer.update_summary(running_summary, block)
            except Exception as e:
                print(f"[summarizer] error: {e}", file=sys.stderr)
            emit({"type": "summary", "text": running_summary})
            with open(transcript_path.replace(".txt", "_summary.txt"), "a") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {running_summary}\n")

        now = time.time()

        if pending_question_at is None and detector.should_check_llm(
            context, profile["name"], profile.get("team", ""), profile.get("current_projects", "")
        ):
            if now - last_triggered >= DEBOUNCE_SECONDS and now - last_mention >= MENTION_DEBOUNCE:
                try:
                    label = await detector_llm.classify(context, profile["name"])
                except Exception as e:
                    print(f"[detector_llm] error: {e}", file=sys.stderr)
                    label = "none"
                if label == "question":
                    pending_question_at = now
                elif label == "mention":
                    last_mention = now
                    emit({"type": "mention", "words": words_20})

        if pending_question_at is not None:
            if "?" in word or (now - pending_question_at) >= QUESTION_MAX_WAIT:
                pending_question_at = None
                last_triggered = now
                try:
                    result = await answerer.generate_answer(context, summary=running_summary)
                    emit({"type": "question", "transcript": context, "answer": result["answer"], "follow_up": result["follow_up"]})
                except Exception as e:
                    print(f"[answerer] error: {e}", file=sys.stderr)

        if pending_promise_at is None:
            if commitment.has_promise(context) and now - last_commitment >= COMMITMENT_DEBOUNCE:
                pending_promise_at = now
                promise_words = list(word_buffer)
        else:
            promise_words.append(word)
            if commitment.is_sentence_end(word) or (now - pending_promise_at) >= COMMITMENT_MAX_WAIT:
                commitment_text = " ".join(promise_words)
                n_steps = int((now - pending_promise_at) / config.AUDIO_STEP_SECONDS) + 3
                clip_path = commitment.save_clip(raw_buffer, n_steps, config.AUDIO_SAMPLE_RATE, transcript_dir)
                screenshot = vision.capture()
                last_commitment = now
                pending_promise_at = None
                promise_words = []
                emit({"type": "commitment", "text": commitment_text, "clip_path": clip_path, "screenshot": screenshot})

        if assertiveness.is_dismissal(context) and now - last_assertiveness >= ASSERTIVENESS_DEBOUNCE:
            if mic_word_buffer:
                last_assertiveness = now
                user_context = " ".join(list(mic_word_buffer)[-30:])
                try:
                    rebuttal = await assertiveness.generate_rebuttal(user_context, context[-200:])
                    emit({"type": "assertiveness", "rebuttal": rebuttal})
                except Exception as e:
                    print(f"[assertiveness] error: {e}", file=sys.stderr)


def mic_loop(mic_word_buffer: deque):
    """Captures mic audio, transcribes, and emits input_transcript events."""
    last_word_end = 0.0
    chunk_offset = 0.0
    confirm_before = config.AUDIO_CHUNK_SECONDS - config.AUDIO_STEP_SECONDS
    word_buffer = mic_word_buffer

    print("[mic] listening...", file=sys.stderr, flush=True)
    for chunk in audio.stream_mic():
        for word, start, end in stt.transcribe_words(chunk, chunk_offset=chunk_offset):
            if start < last_word_end:
                continue
            relative_end = end - chunk_offset
            if relative_end > confirm_before:
                continue
            last_word_end = end
            word_buffer.append(word)
            context = " ".join(word_buffer)
            emit({"type": "input_transcript", "text": context[-TRANSCRIPT_WINDOW:], "words": " ".join(list(word_buffer)[-20:])})
        chunk_offset += config.AUDIO_STEP_SECONDS


def _raw_buffer_thread(raw_buffer: deque, stop_event: threading.Event, device_stream=None):
    """Continuously fills raw_buffer with step-sized audio chunks, independent of STT."""
    stream_fn = device_stream or audio.stream_steps
    for step in stream_fn():
        if stop_event.is_set():
            break
        raw_buffer.append(step)



async def stdin_loop(word_buffer: deque, mic_word_buffer: deque):
    """Reads commands from Electron via stdin and acts on them."""
    while True:
        line = await asyncio.to_thread(sys.stdin.readline)
        if not line:
            break
        cmd = line.strip()
        if cmd == "analyse-tactics":
            if not word_buffer:
                emit({"type": "tactic", "tactic": "no transcript yet", "counter": "Start the meeting and let some audio accumulate first."})
            else:
                try:
                    context = " ".join(list(word_buffer))
                    result = await negotiation.analyse(context)
                    emit({"type": "tactic", "tactic": result["tactic"], "counter": result["counter"]})
                except Exception as e:
                    print(f"[negotiate] error: {e}", file=sys.stderr)
                    emit({"type": "tactic", "tactic": "error", "counter": "API call failed, please try again."})
        elif cmd == "trigger-assertiveness":
            try:
                user_context = " ".join(list(mic_word_buffer)[-30:])
                dismissal_context = " ".join(list(word_buffer))[-200:]
                rebuttal = await assertiveness.generate_rebuttal(user_context, dismissal_context)
                emit({"type": "assertiveness", "rebuttal": rebuttal})
            except Exception as e:
                print(f"[assertiveness] error: {e}", file=sys.stderr)


async def main():
    with open(config.PROFILE_PATH) as f:
        profile = json.load(f)

    PROMISE_BUFFER_SECONDS = 15
    raw_buffer = deque(maxlen=int(PROMISE_BUFFER_SECONDS / config.AUDIO_STEP_SECONDS) + 1)
    word_buffer = deque(maxlen=100)
    mic_word_buffer = deque(maxlen=100)
    stop_event = threading.Event()
    t = threading.Thread(target=_raw_buffer_thread, args=(raw_buffer, stop_event), daemon=True)
    t.start()

    t_mic = threading.Thread(target=mic_loop, args=(mic_word_buffer,), daemon=True)
    t_mic.start()

    try:
        await asyncio.gather(
            audio_loop(profile, raw_buffer, word_buffer, mic_word_buffer),
            stdin_loop(word_buffer, mic_word_buffer),
        )
    finally:
        stop_event.set()


if __name__ == "__main__":
    asyncio.run(main())
