"""
End-to-end test: simulated transcript → detection → Claude answer.
Tests the full pipeline without needing real audio.
Run: python test_e2e.py
"""
import asyncio
import time
from collections import deque
import detector
import answerer

NAME = "Henry"
DEBOUNCE_SECONDS = 10
QUESTION_MAX_WAIT = 3.0

SCENARIOS = [
    {
        "name": "Direct question with ?",
        "words": "so we've been looking at the auth service and Henry what do you think about the OAuth2 migration timeline?".split(),
        "summary": "The team is discussing the Q3 roadmap and infrastructure changes.",
    },
    {
        "name": "Question without ? (timeout path)",
        "words": "Henry can you walk us through the current status of the auth migration".split(),
        "summary": "The team has been reviewing Q3 infrastructure priorities.",
    },
    {
        "name": "No question — should not trigger Claude",
        "words": "Henry is going to handle the deployment next week".split(),
        "summary": "",
    },
]

async def run_scenario(scenario):
    print(f"\n{'='*60}")
    print(f"Scenario: {scenario['name']}")
    print(f"Transcript: \"{' '.join(scenario['words'])}\"")
    print(f"Summary: \"{scenario['summary']}\"")
    print()

    word_buffer = deque(maxlen=100)
    last_triggered = -DEBOUNCE_SECONDS
    pending_question_at = None
    t = 0.0
    fired = False

    for word in scenario["words"]:
        t += 0.8
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
                fired = True
                print(f"  [{t:.1f}s] firing ({reason}), calling Claude...")
                start = time.time()
                answer = await answerer.generate_answer(context, summary=scenario["summary"])
                elapsed = time.time() - start
                print(f"  Claude responded in {elapsed:.2f}s:")
                print(f"\n  > {answer}\n")
                break

    if not fired:
        print("  (no question detected — correct)" if "not trigger" in scenario["name"] else "  WARNING: expected a trigger but got none")

async def main():
    for s in SCENARIOS:
        await run_scenario(s)

asyncio.run(main())
