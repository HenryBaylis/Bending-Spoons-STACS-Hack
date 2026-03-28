import json
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.0-flash")

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
    prompt = f"{context}Someone just asked: {transcript}"
    response = await _model.generate_content_async(
        [{"role": "user", "parts": [prompt]}],
        generation_config={"system_instruction": _SYSTEM_PROMPT},
    )
    return response.text.strip()
