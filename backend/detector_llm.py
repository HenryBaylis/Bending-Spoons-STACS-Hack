"""
LLM-based classifier for meeting transcripts.

Classifies the transcript into one of three outcomes:
  "question" — a question is being directed at the user, requiring a response
  "mention"  — the user is referenced or discussed, but no response is needed
  "none"     — neither

Used as a second-pass filter after detector.should_check_llm() fires.

Usage in main.py:
    result = await detector_llm.classify(context, name)
    if result == "question":   → trigger answer generation
    elif result == "mention":  → trigger mention ping
"""

import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

_PROMPT = (
    "You are analysing a live meeting transcript. "
    "Classify how {name} is involved in the most recent part of the conversation.\n\n"
    "Reply with exactly one word:\n"
    "- \"question\" if {name} is being directly asked something that requires their response\n"
    "- \"mention\" if {name} is referenced or discussed but no response is expected\n"
    "- \"none\" if {name} is not meaningfully involved\n\n"
    "Transcript:\n\"{context}\""
)


async def classify(context: str, name: str) -> str:
    """
    Returns "question", "mention", or "none".
    Should only be called after the loose heuristic gate has fired.
    """
    prompt = _PROMPT.format(name=name, context=context)

    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=5,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = message.content[0].text.strip().lower()
    if answer.startswith("question"):
        return "question"
    if answer.startswith("mention"):
        return "mention"
    return "none"
