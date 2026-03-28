"""
Test the question detection + answer firing logic from main.py
without needing real audio or Claude API calls.
Run: python test_logic.py
"""
import time
from collections import deque
import detector

NAME = "Henry"
DEBOUNCE_SECONDS = 10
QUESTION_MAX_WAIT = 3.0

def run_scenario(name, words_with_delays):
    """
    Simulate the main.py word loop.
    words_with_delays: list of (word, seconds_since_last_word)
    Returns list of (event, context, elapsed) when question fires.
    """
    word_buffer = deque(maxlen=20)
    last_triggered = -DEBOUNCE_SECONDS  # allow firing immediately at start
    pending_question_at = None
    fired = []
    t = 0.0

    for word, delay in words_with_delays:
        t += delay
        word_buffer.append(word)
        context = " ".join(word_buffer)

        if pending_question_at is None and detector.is_directed_at_me(context, NAME):
            if t - last_triggered >= DEBOUNCE_SECONDS:
                pending_question_at = t
                print(f"  [{t:.1f}s] question detected, waiting for ?...")

        if pending_question_at is not None:
            question_complete = "?" in word
            timed_out = (t - pending_question_at) >= QUESTION_MAX_WAIT
            if question_complete or timed_out:
                reason = "? found" if question_complete else "timeout"
                last_triggered = t
                pending_question_at = None
                fired.append((reason, context, t))
                print(f"  [{t:.1f}s] FIRED ({reason}): \"{context}\"")

    return fired


SCENARIOS = [
    (
        "Question with ? — should fire on ?",
        [("Henry", 0.8), ("what", 0.8), ("do", 0.8), ("you", 0.8), ("think?", 0.8)],
        1,  # expected fires
    ),
    (
        "Question without ? — should fire on timeout",
        [("Henry", 0.8), ("what", 0.8), ("do", 0.8), ("you", 0.8), ("think", 0.8),
         ("about", 0.8), ("this", 0.8), ("approach", 0.8), ("here", 0.8), ("right", 0.8)],
        1,
    ),
    (
        "Name mentioned but no question — should not fire",
        [("Henry", 0.8), ("is", 0.8), ("working", 0.8), ("on", 0.8), ("auth", 0.8)],
        0,
    ),
    (
        "? fires early before timeout",
        [("Henry", 0.8), ("can", 0.8), ("you", 0.8), ("explain", 0.8),
         ("the", 0.8), ("approach?", 0.8)],
        1,
    ),
    (
        "Debounce — second question within 10s should not fire",
        [("Henry", 0.8), ("what", 0.8), ("do", 0.8), ("you", 0.8), ("think?", 0.8),
         ("and", 1.0), ("Henry", 0.8), ("how", 0.8), ("about", 0.8), ("this?", 0.8)],
        1,  # only first should fire
    ),
]

passed = 0
failed = 0

for desc, words, expected_fires in SCENARIOS:
    print(f"\n--- {desc}")
    fired = run_scenario(NAME, words)
    ok = len(fired) == expected_fires
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"  [{status}] fired {len(fired)} time(s), expected {expected_fires}")

print(f"\n{passed}/{passed+failed} passed")
