"""Generate script + metadata for a Shorts video."""
import json
import re
from pathlib import Path
from dataclasses import dataclass
import google.generativeai as genai
from .config import config


@dataclass
class Script:
    title: str
    narration: str       # teks yang akan di-TTS
    description: str     # deskripsi YouTube
    tags: list[str]
    visual_keywords: list[str]  # keyword buat Pexels query


def generate_script(topic: str) -> Script:
    genai.configure(api_key=config.gemini_api_key)
    template = Path("prompts/script.txt").read_text(encoding="utf-8")
    prompt = template.replace("{{topic}}", topic).replace(
        "{{duration}}", str(config.video_duration_sec)
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt)
    data = _extract_json(resp.text)
    return Script(**data)


def _extract_json(text: str) -> dict:
    """Strip markdown code fences if any, then parse."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in LLM response:\n{text}")
    return json.loads(match.group(0))
