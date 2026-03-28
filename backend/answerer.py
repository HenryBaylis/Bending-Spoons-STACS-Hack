import os
import base64
import json
import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

with open(config.PROFILE_PATH) as f:
    _profile = json.load(f)

_SYSTEM_PROMPT = (
    "You are an assistant helping {name}, a {job_title}.\n"
    "When asked a question in a meeting, suggest a concise, professional response in first "
    "person as if you are them. Keep it to 2-3 sentences. "
    "Always provide an answer — never ask for clarification or say the question is incomplete. "
    "Speech transcripts may lack punctuation; treat them as complete questions.\n\n"
    "After your answer, you may optionally add a follow-up question directed at a specific "
    "meeting participant if it would genuinely advance the discussion (e.g. to fill a clear "
    "gap or explore something important that was not addressed). "
    "Be very conservative — only include a follow-up in roughly 1 in 5 cases. "
    "If you include one, put it on a new line starting exactly with 'Follow-up:'. "
    "Most responses should have no follow-up."
).format(**_profile)

# Load optional meeting context file
_context_document = None  # base64 PDF string
_context_path = os.environ.get("MEETING_CONTEXT_PATH", "")
_context_type = os.environ.get("MEETING_CONTEXT_TYPE", "")

if _context_path and os.path.exists(_context_path):
    if _context_type == "text":
        with open(_context_path, "r", encoding="utf-8") as f:
            _SYSTEM_PROMPT += f"\n\nMeeting context document:\n{f.read().strip()}"
    elif _context_type == "pdf":
        with open(_context_path, "rb") as f:
            _context_document = base64.standard_b64encode(f.read()).decode("utf-8")


async def generate_answer(transcript: str, summary: str = "") -> dict:
    context = f"Meeting context so far: {summary}\n\n" if summary else ""
    prompt = f"{context}A colleague just asked you: \"{transcript}\"\n\nReply in 2-3 sentences."

    if _context_document:
        content = [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": _context_document}},
            {"type": "text", "text": prompt},
        ]
    else:
        content = prompt

    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    raw = message.content[0].text.strip()

    if "\nFollow-up:" in raw:
        answer, follow_up = raw.split("\nFollow-up:", 1)
        return {"answer": answer.strip(), "follow_up": follow_up.strip()}
    return {"answer": raw, "follow_up": None}
