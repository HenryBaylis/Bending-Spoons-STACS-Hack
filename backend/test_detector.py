"""
Test question detection logic.
Run: python test_detector.py
"""
from detector import is_directed_at_me

NAME = "Henry"

# (text, expected_result, description)
CASES = [
    # --- Should trigger ---
    ("Henry, what do you think about this?",            True,  "direct question with name + what"),
    ("Can you explain that Henry?",                     True,  "can you + name"),
    ("Henry can you walk us through the architecture?", True,  "walk us through"),
    ("What's your take on this Henry?",                 True,  "take on"),
    ("Henry, how does that work?",                      True,  "how + name"),
    ("Do you have any thoughts on that Henry?",         True,  "thoughts on"),
    ("Henry would you be able to do that?",             True,  "would you"),
    ("Could you give us an update Henry?",              True,  "give us"),
    ("Henry, why did you choose that approach?",        True,  "why"),
    ("Henry is that something you could look into?",    True,  "is that + you"),

    # --- Should NOT trigger ---
    ("Henry is working on the auth service",            False, "name mentioned but no question"),
    ("We should ask Henry to do it later",              False, "no question directed at Henry"),
    ("Henry said it works fine",                        False, "statement about Henry"),
    ("Henry explained how it works yesterday",          False, "how but not a question to Henry"),
    ("Let Henry handle it",                             False, "instruction but not a question"),
    ("I spoke to Henry about this",                     False, "past tense mention"),
    ("Henry's approach is correct",                     False, "possessive, no question"),
    ("What did Henry say about it?",                    False, "question about Henry, not to Henry"),
    ("How is Henry getting on?",                        False, "question about Henry, not to Henry"),
    ("No name mentioned at all, what do you think?",   False, "question but no name"),
]

passed = 0
failed = 0

for text, expected, desc in CASES:
    result = is_directed_at_me(text, NAME)
    status = "PASS" if result == expected else "FAIL"
    if result == expected:
        passed += 1
    else:
        failed += 1
    marker = "✓" if result == expected else "✗"
    print(f"[{status}] {marker} {desc}")
    print(f"       \"{text}\"")
    if result != expected:
        print(f"       got={result} expected={expected}")

print(f"\n{passed}/{passed+failed} passed")
