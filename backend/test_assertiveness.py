"""
Tests for the assertiveness helper.
Run: python test_assertiveness.py
"""
import asyncio
import time
import assertiveness

SCENARIOS = [
    {
        "name": "Idea dismissed as infeasible",
        "user_context": "I think we should move the auth service to a microservice architecture to improve scalability",
        "dismissal": "That won't work, we've tried that before and it just adds too much complexity",
        "expect_dismissal": True,
    },
    {
        "name": "Proposal shut down with deadline pressure",
        "user_context": "We should take another week to properly evaluate all the options before deciding",
        "dismissal": "No, that's not realistic, let's move on we need to make a call today",
        "expect_dismissal": True,
    },
    {
        "name": "Disagreement on approach",
        "user_context": "I believe the root cause is in the database layer not the API",
        "dismissal": "I disagree, actually that doesn't make sense given what we saw in the logs",
        "expect_dismissal": True,
    },
    {
        "name": "Cost objection to suggestion",
        "user_context": "We could use a dedicated caching layer to solve the latency issues",
        "dismissal": "Too expensive, we're not going to budget for that this quarter",
        "expect_dismissal": True,
    },
    {
        "name": "Neutral agreement — no dismissal",
        "user_context": "I think the deploy went smoothly",
        "dismissal": "Yeah that looks good, metrics are stable and no alerts fired",
        "expect_dismissal": False,
    },
    {
        "name": "Neutral question — no dismissal",
        "user_context": "The test suite takes about 12 minutes to run",
        "dismissal": "Ok thanks, can you share the breakdown of which tests are slowest?",
        "expect_dismissal": False,
    },
]


async def run_scenario(scenario: dict):
    print(f"\n{'='*60}")
    print(f"Scenario: {scenario['name']}")
    print(f"User said:  \"{scenario['user_context']}\"")
    print(f"Response:   \"{scenario['dismissal']}\"")

    detected = assertiveness.is_dismissal(scenario["dismissal"])
    expected = scenario["expect_dismissal"]
    detection_ok = detected == expected
    detection_status = "PASS" if detection_ok else "FAIL"
    print(f"  [{detection_status}] heuristic detected={detected} (expected {expected})")

    if detected:
        start = time.time()
        rebuttal = await assertiveness.generate_rebuttal(
            scenario["user_context"], scenario["dismissal"]
        )
        elapsed = time.time() - start
        print(f"  rebuttal ({elapsed:.2f}s): {rebuttal}")

    return detection_ok


async def main():
    passed = 0
    failed = 0
    for scenario in SCENARIOS:
        ok = await run_scenario(scenario)
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*60}")
    print(f"{passed}/{passed + failed} passed")


asyncio.run(main())
