"""Download vertical stock clips from Pexels based on keywords."""
from pathlib import Path
import requests
from .config import config

PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"


def fetch_clips(keywords: list[str], out_dir: Path, per_keyword: int = 1) -> list[Path]:
    """Fetch one vertical clip per keyword. Returns list of downloaded file paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": config.pexels_api_key}
    paths: list[Path] = []

    for i, kw in enumerate(keywords):
        params = {"query": kw, "orientation": "portrait", "per_page": per_keyword}
        r = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        videos = r.json().get("videos", [])
        if not videos:
            continue

        # pick highest-quality mp4 file
        files = sorted(videos[0]["video_files"], key=lambda f: f.get("width", 0), reverse=True)
        mp4 = next((f for f in files if f["file_type"] == "video/mp4"), None)
        if not mp4:
            continue

        dest = out_dir / f"clip_{i:02d}.mp4"
        with requests.get(mp4["link"], stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in resp.iter_content(1024 * 1024):
                    fh.write(chunk)
        paths.append(dest)

    return paths
