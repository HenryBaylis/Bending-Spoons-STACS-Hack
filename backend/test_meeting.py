"""
Simulates a realistic meeting transcript through the full pipeline.
Tests the LLM classifier (question / mention / none) and answer quality.
Run: python test_meeting.py
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
DEBOUNCE_SECONDS = 10
MENTION_DEBOUNCE = 5
QUESTION_MAX_WAIT = 3.0

# Simulated meeting — words spoken at 0.15s per word (natural speech rate)
# Mix of general discussion, name mentions, and questions directed at Henry
MEETING_SCRIPT = """
Alice: Alright everyone let's get started. So today we're presenting our paper on Neurosurgeon
which is the collaborative intelligence system between mobile and cloud.
Bob: Yeah for those who haven't read it, the core idea is that instead of doing all the DNN
inference in the cloud you can split it at the layer level between the device and the server.
Alice: Exactly. Henry you've been working through the paper, can you give us the high level overview?
Henry: Sure. So the key insight is that each DNN layer has different compute and data transfer costs
and there's an optimal partition point that minimises latency or energy.
Alice: Great. And what were the main results?
Bob: The latency improvements were pretty significant right.
Alice: Henry what were the actual numbers from the evaluation?
Henry: So Neurosurgeon achieves 3.1 times average latency speedup over cloud only
with some CV tasks getting up to 40 times improvement on 3G networks.
Bob: That's impressive. How does it handle changing network conditions though?
Alice: Right that was one of my questions too. Henry can you explain how Neurosurgeon
adapts when the LTE bandwidth drops?
Henry: So the runtime continuously monitors bandwidth and server load and dynamically
shifts the partition point. When bandwidth drops it moves more computation to the mobile
device to compensate.
Bob: Makes sense. How does it compare to MAUI then?
Alice: Yeah Henry what's your take on the comparison to prior work?
Henry: Neurosurgeon outperforms MAUI by up to 32 times because MAUI uses control centric
offloading at the method level and can't distinguish layers of the same type with different
data sizes. The data centric approach is fundamentally better for DNNs.
Alice: Okay last thing. Henry do you think this approach could work for modern transformer models?
Bob: Oh that's a good question.
Henry: That's an interesting open question. Transformers have a different structure with
attention layers that have quadratic compute complexity so the partitioning tradeoffs
would be quite different from the CNN architectures studied in the paper.
Alice: Great, thanks everyone. Let's wrap up.
""".strip()

def word_timing(script, words_per_second=4.5):
    """Extract just the spoken words with timing, ignoring speaker labels."""
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

    print(f"Running meeting simulation ({len(words)} words)...\n")
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
                    print(f"\n[{t:.1f}s] LLM: question detected, waiting for ?...")
                elif label == "mention":
                    last_mention = t
                    mention_count += 1
                    print(f"\n[{t:.1f}s] LLM: mention ({mention_count}) — \"{' '.join(list(word_buffer)[-20:])[:80]}\"")

        if pending_question_at is not None:
            question_complete = "?" in word
            timed_out = (t - pending_question_at) >= QUESTION_MAX_WAIT
            if question_complete or timed_out:
                reason = "? found" if question_complete else "timeout"
                pending_question_at = None
                question_count += 1
                print(f"[{t:.1f}s] Firing ({reason})")
                print(f"  Context: \"{context[-120:]}\"")
                start = time.time()
                result = await answerer.generate_answer(context)
                elapsed = time.time() - start
                print(f"  Claude ({elapsed:.2f}s): {result['answer']}")
                if result["follow_up"]:
                    print(f"  Follow-up: {result['follow_up']}")
                print()
                print("-" * 60)

    print(f"\nMeeting ended. Questions answered: {question_count}  Mentions: {mention_count}")

asyncio.run(run_meeting())
