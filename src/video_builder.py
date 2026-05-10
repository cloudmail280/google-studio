"""Stitch stock clips + voiceover into a vertical 1080x1920 video."""
from pathlib import Path
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)
from .config import config


def build_video(clip_paths: list[Path], audio_path: Path, out_path: Path) -> Path:
    if not clip_paths:
        raise ValueError("No clip paths provided")

    audio = AudioFileClip(str(audio_path))
    total = audio.duration

    # Load clips, resize to vertical, loop/truncate to match audio length
    segments = []
    per_clip = total / len(clip_paths)
    for p in clip_paths:
        v = VideoFileClip(str(p)).without_audio()
        v = _resize_to_vertical(v, config.video_width, config.video_height)
        v = v.subclip(0, min(per_clip, v.duration))
        segments.append(v)

    video = concatenate_videoclips(segments, method="compose")
    # If concatenation is shorter than audio (clips were short), loop to match
    if video.duration < total:
        video = video.fx(vfx.loop, duration=total)
    video = video.subclip(0, total).set_audio(audio)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    video.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )
    return out_path


def _resize_to_vertical(clip, w: int, h: int):
    """Center-crop & resize to exactly w x h."""
    target_ratio = w / h
    src_ratio = clip.w / clip.h
    if src_ratio > target_ratio:
        # source terlalu lebar → crop sisi
        new_w = int(clip.h * target_ratio)
        x1 = (clip.w - new_w) // 2
        clip = clip.crop(x1=x1, x2=x1 + new_w)
    else:
        # source terlalu tinggi → crop atas/bawah
        new_h = int(clip.w / target_ratio)
        y1 = (clip.h - new_h) // 2
        clip = clip.crop(y1=y1, y2=y1 + new_h)
    return clip.resize((w, h))
