import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.0-flash")


async def update_summary(previous_summary: str, new_transcript: str) -> str:
    """
    Update the running meeting summary with new transcript content.
    Keeps the summary to two sentences maximum.
    """
    if previous_summary:
        prompt = (
            f"Previous meeting summary: {previous_summary}\n\n"
            f"New transcript: {new_transcript}\n\n"
            "Update the summary to include the new information. "
            "Write exactly two concise sentences capturing the key topics and decisions so far."
        )
    else:
        prompt = (
            f"Summarize the following meeting transcript in exactly two concise sentences. "
            f"Capture the key topics and decisions only.\n\n{new_transcript}"
        )
    response = await _model.generate_content_async(prompt)
    return response.text.strip()
