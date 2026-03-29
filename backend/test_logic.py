"""
Test the question detection + answer firing logic from main.py
without needing real audio or Claude API calls.
Run: python test_logic.py
"""
from collections import deque
import detector

NAME = "Sammy"
DEBOUNCE_SECONDS = 10
QUESTION_MAX_WAIT = 20.0  # matches main.py


def mock_classify(context, name):
    """Simulate LLM: return 'question' if name + question pattern present."""
    if detector.is_directed_at_me(context, name):
        return "question"
    if name.lower() in context.lower():
        return "mention"
    return "none"


def run_scenario(name, words_with_delays):
    """
    Simulate the main.py word loop with mocked LLM.
    words_with_delays: list of (word, seconds_since_last_word)
    Returns list of (reason, context, elapsed) when question fires.
    """
    word_buffer = deque(maxlen=100)
    last_triggered = -DEBOUNCE_SECONDS
    last_mention = -DEBOUNCE_SECONDS
    pending_question_at = None
    fired = []
    t = 0.0

    for word, delay in words_with_delays:
        t += delay
        word_buffer.append(word)
        context = " ".join(word_buffer)

        if pending_question_at is None and detector.should_check_llm(context, name, "", ""):
            if t - last_triggered >= DEBOUNCE_SECONDS and t - last_mention >= 5:
                label = mock_classify(context, name)
                if label == "question":
                    pending_question_at = t
                    print(f"  [{t:.1f}s] LLM -> question detected, waiting for ? (max {QUESTION_MAX_WAIT}s)...")
                elif label == "mention":
                    last_mention = t
                    print(f"  [{t:.1f}s] LLM -> mention ping")

        if pending_question_at is not None:
            question_complete = "?" in word
            timed_out = (t - pending_question_at) >= QUESTION_MAX_WAIT
            if question_complete or timed_out:
                reason = "? found" if question_complete else "timeout"
                last_triggered = t
                pending_question_at = None
                fired.append((reason, context, t))
                print(f"  [{t:.1f}s] FIRED ({reason}): \"{context[-80:]}\"")

    return fired


SCENARIOS = [
    (
        "Short question with ? — fires on ?",
        [("Sammy", 0.8), ("what", 0.8), ("do", 0.8), ("you", 0.8), ("think?", 0.8)],
        1, "? found",
    ),
    (
        "Long question (10s) with ? at end — fires on ?, not timeout",
        [
            ("ok", 0.8), ("Sammy", 0.8), ("here", 0.8), ("is", 0.8), ("my", 0.8),
            ("question", 0.8), ("for", 0.8), ("you", 0.8), ("what", 0.8), ("do", 0.8),
            ("you", 0.8), ("think", 0.8), ("about", 0.8), ("the", 0.8), ("approach", 0.8),
            ("we", 0.8), ("took", 0.8), ("in", 0.8), ("the", 0.8), ("last", 0.8),
            ("sprint", 0.8), ("should", 0.8), ("we", 0.8), ("continue", 0.8),
            ("or", 0.8), ("pivot?", 0.8),
        ],
        1, "? found",
    ),
    (
        "Long question without ? — fires on 20s timeout",
        [
            ("ok", 0.8), ("Sammy", 0.8), ("here", 0.8), ("is", 0.8), ("my", 0.8),
            ("question", 0.8), ("for", 0.8), ("you", 0.8), ("what", 0.8), ("do", 0.8),
            ("you", 0.8), ("think", 0.8), ("about", 0.8), ("the", 0.8), ("approach", 0.8),
            ("we", 0.8), ("took", 0.8), ("in", 0.8), ("the", 0.8), ("last", 0.8),
            ("sprint", 0.8), ("should", 0.8), ("we", 0.8), ("continue", 0.8),
            ("or", 0.8), ("pivot", 0.8), ("entirely", 0.8),
            # pad to exceed 20s timeout from detection point
            *[("...", 0.8)] * 20,
        ],
        1, "timeout",
    ),
    (
        "Name mentioned but no question — should not fire",
        [("Sammy", 0.8), ("is", 0.8), ("working", 0.8), ("on", 0.8), ("auth", 0.8)],
        0, None,
    ),
    (
        "Debounce — second question within 10s should not fire",
        [("Sammy", 0.8), ("what", 0.8), ("do", 0.8), ("you", 0.8), ("think?", 0.8),
         ("and", 1.0), ("Sammy", 0.8), ("how", 0.8), ("about", 0.8), ("this?", 0.8)],
        1, "? found",
    ),
]

passed = 0
failed = 0

for desc, words, expected_fires, expected_reason in SCENARIOS:
    print(f"\n--- {desc}")
    fired = run_scenario(NAME, words)
    count_ok = len(fired) == expected_fires
    reason_ok = expected_reason is None or (fired and fired[0][0] == expected_reason)
    ok = count_ok and reason_ok
    status = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    reason_str = f", reason={fired[0][0]!r}" if fired else ""
    print(f"  [{status}] fired {len(fired)}x (expected {expected_fires}){reason_str}")

print(f"\n{passed}/{passed+failed} passed")
