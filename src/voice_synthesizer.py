"""Text-to-speech via Edge-TTS (free, Microsoft voices)."""
import asyncio
from pathlib import Path
import edge_tts
from .config import config


def synthesize(text: str, out_path: Path, voice: str | None = None) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_run(text, out_path, voice or config.tts_voice))
    return out_path


async def _run(text: str, out_path: Path, voice: str) -> None:
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(out_path))
