import json
import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)

with open(config.PROFILE_PATH) as f:
    _profile = json.load(f)

_SYSTEM_PROMPT = (
    "You are an assistant helping {name}, a {job_title} at {company} on the {team} team.\n"
    "Their responsibilities: {responsibilities}.\n"
    "Current projects: {current_projects}.\n"
    "{extra_context}\n\n"
    "When asked a question in a meeting, suggest a concise, professional response in first "
    "person as if you are them. Keep it to 2-3 sentences unless more detail is needed."
).format(**_profile)


async def generate_answer(transcript: str, summary: str = "") -> str:
    context = f"Meeting context so far: {summary}\n\n" if summary else ""
    prompt = f"{context}Recent transcript (last 100 words):\n{transcript}\n\nGenerate a response to the question directed at me in the transcript above."

    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
