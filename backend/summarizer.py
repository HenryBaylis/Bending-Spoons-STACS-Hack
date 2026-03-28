import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.0-flash")

SUMMARIZE_EVERY = 10  # chunks between each summarization


async def summarize(text: str) -> str:
    """Condense a block of meeting transcript into one sentence."""
    prompt = (
        "Summarize the following meeting transcript excerpt in exactly one concise sentence. "
        "Capture the key topic or decision only.\n\n" + text
    )
    response = await _model.generate_content_async(prompt)
    return response.text.strip()
