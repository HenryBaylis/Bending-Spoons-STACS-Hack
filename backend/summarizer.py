import anthropic
import config

_client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)


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
            "Summarize the following meeting transcript in exactly two concise sentences. "
            f"Capture the key topics and decisions only.\n\n{new_transcript}"
        )

    message = await _client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=128,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()
