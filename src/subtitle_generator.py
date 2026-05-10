"""Generate word-level subtitles from audio using faster-whisper,
then burn them into the video using MoviePy + Pillow (no ImageMagick needed)."""
from pathlib import Path
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip, VideoClip
from .config import config


@dataclass
class WordSegment:
    text: str
    start: float
    end: float


def transcribe(audio_path: Path, language: str = "id") -> list[WordSegment]:
    """Run faster-whisper to get word-level timestamps."""
    from faster_whisper import WhisperModel  # lazy import (model download on first use)

    model = WhisperModel(
        config.whisper_model,
        device="cpu",
        compute_type="int8",
    )
    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
    )
    words: list[WordSegment] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            txt = (w.word or "").strip()
            if txt:
                words.append(WordSegment(text=txt, start=w.start, end=w.end))
    return words


def group_words(words: list[WordSegment], max_chars: int = 22) -> list[WordSegment]:
    """Group words into short phrases (1-3 words) to fit Shorts screen."""
    groups: list[WordSegment] = []
    buf: list[WordSegment] = []
    buf_len = 0
    for w in words:
        add = len(w.text) + (1 if buf else 0)
        if buf and buf_len + add > max_chars:
            groups.append(_merge(buf))
            buf, buf_len = [], 0
        buf.append(w)
        buf_len += add
    if buf:
        groups.append(_merge(buf))
    return groups


def _merge(words: list[WordSegment]) -> WordSegment:
    return WordSegment(
        text=" ".join(w.text for w in words),
        start=words[0].start,
        end=words[-1].end,
    )


def _render_caption(text: str, size: tuple[int, int]) -> np.ndarray:
    """Draw centered text with black outline on transparent bg. Returns RGBA array."""
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font = _load_font(config.subtitle_font_size)
    # Wrap to fit width (rough: re-split if too wide)
    lines = _wrap(text, font, W - 80)
    total_h = sum(_line_h(font) for _ in lines)
    y = (H - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = (W - lw) // 2
        # black outline (stroke)
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=config.subtitle_stroke,
            stroke_fill=(0, 0, 0, 255),
        )
        y += _line_h(font)
    return np.array(img)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        config.subtitle_font_path,
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for p in candidates:
        if p and Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _line_h(font) -> int:
    bbox = font.getbbox("Ag")
    return int((bbox[3] - bbox[1]) * 1.2)


def _wrap(text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        bbox = font.getbbox(trial)
        if bbox[2] - bbox[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def burn_subtitles(base_video: VideoClip, groups: list[WordSegment]) -> CompositeVideoClip:
    """Return a CompositeVideoClip with subtitle text overlays."""
    W, H = base_video.w, base_video.h
    overlay_h = int(H * 0.3)  # subtitle box: bottom 30%
    overlay_y = int(H * 0.6)

    clips = [base_video]
    for g in groups:
        img = _render_caption(g.text.upper(), (W, overlay_h))
        clip = (
            ImageClip(img, transparent=True)
            .set_start(g.start)
            .set_end(min(g.end, base_video.duration))
            .set_position((0, overlay_y))
        )
        clips.append(clip)
    return CompositeVideoClip(clips, size=(W, H))
