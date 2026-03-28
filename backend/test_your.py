"""
Tests whether \byour\b in the gate causes false positives.
Each case is labelled with the expected LLM classification.

The gate fires on "your" — the LLM must correctly filter:
  - "your" in general discussion (not directed at Henry) → none
  - "your" in third-person reference to Henry → mention
  - "your" as direct address to Henry → question

Run: python test_your.py
"""
import asyncio
import detector
import detector_llm

NAME = "Henry"
TEAM = ""
PROJECT = ""

# (context, expected, description)
CASES = [
    # ── FALSE POSITIVES — "your" not directed at Henry ──────────────────
    (
        "Alice: I looked at your paper Bob, the methodology is really solid.",
        "none",
        "your = Bob's paper, Henry not mentioned"
    ),
    (
        "Bob: Yeah your point about latency is well taken Alice.",
        "none",
        "your = Alice's point, Henry not mentioned"
    ),
    (
        "Alice: The system stores your data in the cloud by default.",
        "none",
        "your = generic user, Henry not mentioned"
    ),
    (
        "Bob: In your implementation you used a fixed partition point right Alice?",
        "none",
        "your = Alice's implementation, Henry not mentioned"
    ),
    (
        "Alice: From your results Bob it looks like base outperforms tiny by 40 percent.",
        "none",
        "your = Bob's results, Henry not mentioned"
    ),

    # ── MENTIONS — "your" references Henry in third person ───────────────
    (
        "Alice: Henry your work on the latency benchmarks was really impressive.",
        "mention",
        "your = Henry's work, compliment not a question"
    ),
    (
        "Bob: Henry your implementation is already in the repo right?",
        "mention",
        "your = Henry's implementation, statement not a question"  # could go either way
    ),

    # ── TRUE POSITIVES — "your" as direct address to Henry ───────────────
    (
        "Alice: So Henry we've read through the paper, what's your take on the main contribution?",
        "question",
        "your take — direct question to Henry"
    ),
    (
        "Bob: Henry can you walk us through your benchmarking approach?",
        "question",
        "your benchmarking — direct question to Henry"
    ),
    (
        "Alice: What were your findings on the 3G network results Henry?",
        "question",
        "your findings — direct question to Henry"
    ),
    (
        "Bob: Henry we want to know your thoughts on deploying this to edge devices.",
        "question",
        "your thoughts — direct question to Henry"
    ),

    # ── TRICKY — "your" directed at someone but Henry in context ─────────
    (
        "Alice: Henry just explained the approach. Bob what's your reaction to that?",
        "none",
        "your = Bob's reaction, question directed at Bob not Henry"
    ),
    (
        "Bob: Henry mentioned the partition point. Alice what's your take?",
        "none",
        "your = Alice's take, Henry only mentioned in passing"
    ),
]


async def run():
    print(f"Testing \\byour\\b gate with LLM classifier ({len(CASES)} cases)\n")
    print("=" * 70)

    correct = 0
    for context, expected, description in CASES:
        gate = detector.should_check_llm(context, NAME, TEAM, PROJECT)
        if gate:
            label = await detector_llm.classify(context, NAME)
        else:
            label = "gate_blocked"

        ok = label == expected
        if ok:
            correct += 1
        status = "✓" if ok else "✗"
        print(f"{status} [{expected:8s}] got [{label:8s}] — {description}")

    print(f"\n{correct}/{len(CASES)} correct")
    fp = sum(1 for _, exp, _ in CASES if exp == "none")
    fp_correct = sum(
        1 for (ctx, exp, desc), (_, _, _) in
        zip(CASES, CASES)
        if exp == "none"
    )
    print(f"(Gate fires on all {len(CASES)} since all contain 'your' or name)")

asyncio.run(run())
