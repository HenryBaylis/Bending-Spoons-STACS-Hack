"""
Targeted scenario tests for the full detection pipeline (real LLM calls).
Shows every classify call with context + label, full answers, missed detections,
and a quality check on each answer.
Run: ANTHROPIC_API_KEY=... python test_scenarios.py
"""
import asyncio
import time
from collections import deque
import detector
import detector_llm
import answerer
import anthropic
import os

NAME = "Sammy"
TEAM = ""
PROJECT = ""
DEBOUNCE_SECONDS = 10
MENTION_DEBOUNCE = 5
QUESTION_MAX_WAIT = 20.0

_client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


async def check_answer_quality(question_context, answer):
    """Ask Claude if the answer is a reasonable response to the question in context."""
    msg = await _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": (
                f"Meeting context: \"{question_context}\"\n\n"
                f"Suggested response: \"{answer}\"\n\n"
                "Is this a reasonable, relevant response to the question being asked? "
                "Reply with YES or NO and one sentence explaining why."
            )
        }]
    )
    return msg.content[0].text.strip()


async def run_scenario(script, words_per_second=4.5):
    """
    Run a script through the detection pipeline.
    Returns (questions, mentions, classify_log) where classify_log records every
    LLM classify call with its context and result.
    """
    words = []
    for line in script.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            line = line.split(':', 1)[1].strip()
        for word in line.split():
            words.append((word, 1.0 / words_per_second))

    word_buffer = deque(maxlen=100)
    last_triggered = -DEBOUNCE_SECONDS
    last_mention = -MENTION_DEBOUNCE
    pending_question_at = None
    t = 0.0
    questions = []
    mentions = []
    classify_log = []  # every LLM call: (t, context, label)

    for word, delay in words:
        t += delay
        word_buffer.append(word)
        context = " ".join(word_buffer)

        if pending_question_at is None and detector.should_check_llm(context, NAME, TEAM, PROJECT):
            if t - last_triggered >= DEBOUNCE_SECONDS and t - last_mention >= MENTION_DEBOUNCE:
                label = await detector_llm.classify(context, NAME)
                classify_log.append((t, context, label))
                if label == "question":
                    pending_question_at = t
                    last_triggered = t
                elif label == "mention":
                    last_mention = t
                    mentions.append((t, context))

        if pending_question_at is not None:
            question_complete = "?" in word
            timed_out = (t - pending_question_at) >= QUESTION_MAX_WAIT
            if question_complete or timed_out:
                reason = "? found" if question_complete else "timeout"
                pending_question_at = None
                start = time.time()
                result = await answerer.generate_answer(context)
                elapsed = time.time() - start
                quality = await check_answer_quality(context, result["answer"])
                questions.append((t, reason, context, result["answer"], result["follow_up"], elapsed, quality))

    return questions, mentions, classify_log


async def report(desc, script, questions, mentions, classify_log, expect_q):
    q_ok = len(questions) == expect_q
    status = "PASS" if q_ok else "FAIL"

    print(f"\n{'='*60}")
    print(f"[{status}] {desc}")
    print(f"  Detected: {len(questions)} question(s), {len(mentions)} mention(s) — expected {expect_q} question(s)")

    print(f"\n  -- LLM classify calls ({len(classify_log)}) --")
    if classify_log:
        for t, ctx, label in classify_log:
            print(f"  [{t:.1f}s] label={label!r}")
            print(f"    context: \"{ctx[-100:]}\"")
    else:
        print("  (none — heuristic gate never fired)")

    if questions:
        print(f"\n  -- Answers --")
        for t, reason, ctx, answer, follow_up, elapsed, quality in questions:
            print(f"  [{t:.1f}s] fired ({reason}) — answered in {elapsed:.2f}s")
            print(f"  Context: \"{ctx[-120:]}\"")
            print(f"  Answer: {answer}")
            if follow_up:
                print(f"  Follow-up: {follow_up}")
            print(f"  Quality check: {quality}")

    if not q_ok:
        if len(questions) < expect_q:
            print(f"\n  !! MISSED {expect_q - len(questions)} expected question(s)")
            if classify_log:
                labels = [l for _, _, l in classify_log]
                print(f"     LLM labels seen: {labels}")
                if all(l != "question" for l in labels):
                    print(f"     Gate fired but LLM never returned 'question' — check context quality")
            else:
                print(f"     Heuristic gate never fired — name/team/project/pattern not matched")
        else:
            print(f"\n  !! EXTRA {len(questions) - expect_q} unexpected question(s) fired")

    if mentions and not questions:
        print(f"\n  -- Mentions --")
        for t, ctx in mentions:
            print(f"  [{t:.1f}s] mention: \"{ctx[-80:]}\"")

    return q_ok


SCENARIOS = [
    (
        "Direct short question with name",
        """
        Alice: Sammy what do you think about this approach?
        """,
        1
    ),
    (
        "Long question with preamble — fires on ?",
        """
        Alice: ok Sammy here is my question for you, what do you think about
        the architecture approach we took in the last sprint and do you think
        it will scale to the full dataset?
        """,
        1
    ),
    (
        "Mention only — no response expected",
        """
        Alice: I was talking to Sammy yesterday about the deployment.
        Bob: Yeah Sammy has been making great progress on that.
        Alice: Agreed, Sammy's work on the pipeline has been solid.
        """,
        0
    ),
    (
        "Implicit question — no name mentioned",
        """
        Alice: So looking at the results, what's your take on the performance numbers?
        Do you think we should optimise further or ship as is?
        """,
        1
    ),
    (
        "Debounce — second question within 10s should not fire",
        """
        Alice: Sammy what do you think about the timeline?
        Bob: And Sammy how would you approach the testing strategy?
        """,
        1
    ),
    (
        "Question after general discussion",
        """
        Alice: So we have been looking at the new caching layer and it seems promising.
        Bob: Yeah the benchmarks look good. There are some edge cases though.
        Alice: Right we need to think about cache invalidation carefully.
        Bob: Sammy you have dealt with this before, what is the best strategy here?
        """,
        1
    ),
    (
        "Mixed — mention then question",
        """
        Alice: Sammy has been leading the backend work this sprint.
        Bob: Yeah good stuff. Sammy can you walk us through what you built?
        """,
        1
    ),
]


async def main():
    passed = 0
    failed = 0
    for desc, script, expect_q in SCENARIOS:
        print(f"\nRunning: {desc}...")
        questions, mentions, classify_log = await run_scenario(script)
        ok = await report(desc, script, questions, mentions, classify_log, expect_q)
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{passed+failed} passed")


asyncio.run(main())
