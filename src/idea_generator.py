"""Generate a Shorts topic using Gemini."""
from pathlib import Path
import google.generativeai as genai
from .config import config


def generate_idea(hint: str | None = None) -> str:
    """Return a single topic string. If `hint` given, refine around it."""
    genai.configure(api_key=config.gemini_api_key)
    prompt = Path("prompts/idea.txt").read_text(encoding="utf-8")
    if hint:
        prompt += f"\n\nHint topik dari user: {hint}"

    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    return resp.text.strip().strip('"').strip()
