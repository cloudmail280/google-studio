"""Pick a random background music track from a local library.

Place your royalty-free .mp3/.wav files in `assets/music/`.
Recommended free sources (you must still check each track's license):
- YouTube Audio Library (download from Studio, "no attribution" filter)
- Pixabay Music (https://pixabay.com/music/)
- Free Music Archive (CC-licensed tracks)

This module does NOT download music automatically to avoid licensing issues.
"""
import random
from pathlib import Path

SUPPORTED_EXT = {".mp3", ".wav", ".m4a", ".ogg"}


def pick_track(library_dir: Path | str = "assets/music") -> Path | None:
    """Return a random track path, or None if library is empty."""
    lib = Path(library_dir)
    if not lib.exists():
        return None
    tracks = [p for p in lib.iterdir() if p.suffix.lower() in SUPPORTED_EXT]
    if not tracks:
        return None
    return random.choice(tracks)
