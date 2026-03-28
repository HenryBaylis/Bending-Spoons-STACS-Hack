import base64
import io
import mss
from PIL import Image
import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-2.0-flash")

MAX_DIMENSION = 1536
JPEG_QUALITY = 75


def capture() -> str:
    """Capture the primary monitor and return a base64 JPEG string."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    # Resize to fit within MAX_DIMENSION
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


async def generate_answer_with_vision(transcript: str, screenshot_b64: str) -> str:
    """Generate an answer using both transcript and screenshot as context."""
    image_data = base64.b64decode(screenshot_b64)
    response = await _model.generate_content_async([
        {
            "mime_type": "image/jpeg",
            "data": image_data,
        },
        f"Someone asked in a meeting: {transcript}\n\nUsing what you can see on screen as additional context, suggest a concise professional response in 2-3 sentences.",
    ])
    return response.text.strip()
