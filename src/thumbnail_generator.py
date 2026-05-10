"""Generate a vertical thumbnail (1080x1920) from the first video frame + title overlay."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy.editor import VideoFileClip
from .config import config


def generate_thumbnail(video_path: Path, title: str, out_path: Path) -> Path:
    """Grab a frame, darken it, overlay the title. Returns out_path."""
    with VideoFileClip(str(video_path)) as clip:
        # pick frame around 1s (avoids black intro frame)
        t = min(1.0, max(0.0, clip.duration / 2))
        frame = clip.get_frame(t)

    img = Image.fromarray(frame).convert("RGB")
    img = img.resize((config.video_width, config.video_height))

    # dark gradient overlay for readability
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, 0), img.size], fill=(0, 0, 0, 110))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # title text
    draw = ImageDraw.Draw(img)
    font = _load_font(config.thumbnail_font_size)
    lines = _wrap(title.upper(), font, img.width - 120)
    line_h = _line_h(font)
    total_h = line_h * len(lines)
    y = (img.height - total_h) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        x = (img.width - lw) // 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 235, 59),  # yellow
            stroke_width=6,
            stroke_fill=(0, 0, 0),
        )
        y += line_h

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=92)
    return out_path


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
    return int((bbox[3] - bbox[1]) * 1.25)


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
