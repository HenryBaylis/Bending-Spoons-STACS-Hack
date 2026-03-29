"""
Negotiation tactic analyser.
Called on-demand (user-triggered) with the last 100 words of transcript.
"""

import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

_PROMPT = """\
You are analysing a live meeting or negotiation transcript for manipulation tactics.

Tactics to detect:
- Anchoring (extreme first offer to skew expectations)
- False urgency / artificial deadline
- Social proof ("everyone else does X", "standard practice")
- Scarcity ("limited availability", "only offer")
- Good cop / bad cop
- Lowball / highball
- BATNA pressure ("we have other options")
- Nibbling (asking for extras after agreement)
- Guilt / emotional pressure
- Take it or leave it

Transcript (last 100 words):
\"{context}\"

Reply in exactly this format, nothing else:
TACTIC: <tactic name, or "none detected">
COUNTER: <one sentence counter-move, or a one sentence observation about the conversation if no tactic>"""


async def analyse(context: str) -> dict:
    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=80,
        messages=[{"role": "user", "content": _PROMPT.format(context=context)}],
    )
    text = message.content[0].text.strip()
    tactic, counter = "none", ""
    for line in text.splitlines():
        if line.startswith("TACTIC:"):
            tactic = line[len("TACTIC:"):].strip()
        elif line.startswith("COUNTER:"):
            counter = line[len("COUNTER:"):].strip()
    return {"tactic": tactic, "counter": counter}
