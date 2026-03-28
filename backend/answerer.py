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
    "Speech transcripts may lack punctuation; treat them as complete questions."
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


async def generate_answer(transcript: str, summary: str = "") -> str:
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
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )
    return message.content[0].text.strip()
