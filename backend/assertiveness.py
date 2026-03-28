"""
Assertiveness helper.
Detects when someone dismisses or pushes back on the user's contribution
and suggests a calm, assertive one-sentence rebuttal.
"""

import re
import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

_DISMISSAL_PATTERNS = [
    r"\bthat won'?t work\b",
    r"\bwe('?ve)? tried that\b",
    r"\bnot feasible\b",
    r"\btoo expensive\b",
    r"\blet'?s move on\b",
    r"\bnot the right time\b",
    r"\bwe can'?t do that\b",
    r"\bthat'?s not realistic\b",
    r"\btoo complex\b",
    r"\bdoesn'?t make sense\b",
    r"\bI disagree\b",
    r"\bwe'?re not going to\b",
    r"\bthat'?s not how\b",
    r"\bno[,\.]?\s+(that|this|we|it)\b",
    r"\bactually[,\s]+(that|this|we|I|no)\b",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _DISMISSAL_PATTERNS]

_PROMPT = """\
In a meeting your contribution is being dismissed or pushed back on.
Write a single calm, assertive sentence to hold your ground without being aggressive.

Your recent contribution: "{user_context}"
What was said in response: "{dismissal_context}"

Reply with only the one assertive sentence."""


def is_dismissal(text: str) -> bool:
    return any(p.search(text) for p in _COMPILED)


async def generate_rebuttal(user_context: str, dismissal_context: str) -> str:
    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=60,
        messages=[{"role": "user", "content": _PROMPT.format(
            user_context=user_context or "(no recent contribution)",
            dismissal_context=dismissal_context,
        )}],
    )
    return message.content[0].text.strip()
