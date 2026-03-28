"""
Tests detection of questions directed at Henry without his name being mentioned.
The LLM must infer from conversational context that Henry is being addressed.

Also tests mention classification (third-person references).

Run: python test_implicit.py
"""
import asyncio
import time
from collections import deque
import detector
import detector_llm
import answerer

NAME = "Henry"
TEAM = ""
PROJECT = ""
DEBOUNCE_SECONDS = 5   # shorter for test density
MENTION_DEBOUNCE = 3
QUESTION_MAX_WAIT = 3.0

# Each scenario is labelled with the expected classification
# [Q] = should fire as question
# [M] = should fire as mention
# [N] = should fire as nothing
MEETING_SCRIPT = """
Alice: So Henry has been leading the implementation side of the project.
Alice: What frameworks have you been using for that?
Bob: Yeah and how long did the migration take you?
Alice: Okay moving on. The backend rewrite was Henry's work mostly.
Bob: It's really solid, the latency dropped by half.
Alice: Right. And Henry mentioned in the last meeting that there were still some edge cases to handle.
Bob: Has those been fixed yet?
Alice: Over to you, go ahead.
Bob: So what's the current status on that?
Alice: We also want to know your thoughts on the deployment timeline.
Bob: Yeah, do you think we can hit the deadline?
Alice: Henry suggested last week that we might need more time.
Bob: That seems reasonable given the scope.
Alice: Anyway, can you walk us through what's left?
""".strip()

EXPECTED = [
    # (fragment, expected_label)
    ("What frameworks have you been using", "question"),   # implicit, follows name mention
    ("how long did the migration take you", "question"),   # implicit follow-up
    ("Henry's work mostly", "mention"),                    # third-person reference
    ("Henry mentioned in the last meeting", "mention"),    # third-person reference
    ("Has those been fixed yet", "question"),              # implicit, context is Henry's work
    ("Over to you, go ahead", "question"),                 # direct handoff without name
    ("what's the current status on that", "question"),     # implicit follow-up
    ("your thoughts on the deployment timeline", "question"),  # implicit "your"
    ("do you think we can hit the deadline", "question"),  # implicit
    ("Henry suggested last week", "mention"),              # third-person reference
    ("can you walk us through what's left", "question"),   # implicit
]

def word_timing(script, words_per_second=4.5):
    words = []
    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            line = line.split(':', 1)[1].strip()
        for word in line.split():
            words.append((word, 1.0 / words_per_second))
    return words


async def run_meeting():
    words = word_timing(MEETING_SCRIPT)
    word_buffer = deque(maxlen=100)
    last_triggered = -DEBOUNCE_SECONDS
    last_mention = -MENTION_DEBOUNCE
    pending_question_at = None
    t = 0.0
    question_count = 0
    mention_count = 0

    print(f"Running implicit detection test ({len(words)} words)...\n")
    print("=" * 60)

    for word, delay in words:
        t += delay
        word_buffer.append(word)
        context = " ".join(word_buffer)

        if pending_question_at is None and detector.should_check_llm(context, NAME, TEAM, PROJECT):
            if t - last_triggered >= DEBOUNCE_SECONDS and t - last_mention >= MENTION_DEBOUNCE:
                label = await detector_llm.classify(context, NAME)
                if label == "question":
                    last_triggered = t
                    pending_question_at = t
                    print(f"\n[{t:.1f}s] LLM: QUESTION — waiting for ?...")
                elif label == "mention":
                    last_mention = t
                    mention_count += 1
                    print(f"\n[{t:.1f}s] LLM: MENTION ({mention_count}) — \"{' '.join(list(word_buffer)[-15:])}\"")

        if pending_question_at is not None:
            question_complete = "?" in word
            timed_out = (t - pending_question_at) >= QUESTION_MAX_WAIT
            if question_complete or timed_out:
                reason = "? found" if question_complete else "timeout"
                pending_question_at = None
                question_count += 1
                print(f"[{t:.1f}s] Firing ({reason})")
                print(f"  Context: \"...{context[-100:]}\"")
                start = time.time()
                result = await answerer.generate_answer(context)
                elapsed = time.time() - start
                print(f"  Answer ({elapsed:.2f}s): {result['answer']}")
                if result["follow_up"]:
                    print(f"  Follow-up: {result['follow_up']}")
                print("-" * 60)

    print(f"\nTest ended. Questions: {question_count}  Mentions: {mention_count}")
    print(f"(Script has ~6 expected questions and ~3 expected mentions)")

asyncio.run(run_meeting())
