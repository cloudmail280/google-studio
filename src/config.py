"""Central config. Loads env vars from .env."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    pexels_api_key: str = os.getenv("PEXELS_API_KEY", "")
    tts_voice: str = os.getenv("TTS_VOICE", "id-ID-ArdiNeural")

    video_width: int = int(os.getenv("VIDEO_WIDTH", "1080"))
    video_height: int = int(os.getenv("VIDEO_HEIGHT", "1920"))
    video_duration_sec: int = int(os.getenv("VIDEO_DURATION_SEC", "60"))

    yt_client_secret_file: str = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    yt_token_file: str = os.getenv("YOUTUBE_TOKEN_FILE", "token.json")
    default_privacy: str = os.getenv("DEFAULT_PRIVACY", "unlisted")

    def validate(self) -> None:
        missing = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.pexels_api_key:
            missing.append("PEXELS_API_KEY")
        if missing:
            raise RuntimeError(
                f"Missing required env vars: {', '.join(missing)}. "
                "Copy .env.example to .env and fill in the keys."
            )


config = Config()
