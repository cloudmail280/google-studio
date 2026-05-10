"""Orchestrator: idea → script → visuals → voice → subtitles → video → thumbnail → upload."""
import argparse
from datetime import datetime
from pathlib import Path

from src.config import config
from src.idea_generator import generate_idea
from src.script_writer import generate_script
from src.visual_fetcher import fetch_clips
from src.voice_synthesizer import synthesize
from src.music_fetcher import pick_track
from src.video_builder import build_video
from src.thumbnail_generator import generate_thumbnail
from src.youtube_uploader import upload


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto YouTube Shorts generator")
    parser.add_argument("--topic", default=None, help="Topic hint. If omitted, AI picks one.")
    parser.add_argument("--no-upload", action="store_true", help="Generate only, skip YouTube upload.")
    parser.add_argument("--no-subtitles", action="store_true", help="Skip subtitle burn-in.")
    parser.add_argument("--no-music", action="store_true", help="Skip background music.")
    parser.add_argument(
        "--privacy",
        choices=["private", "unlisted", "public"],
        default=None,
        help=f"YouTube privacy status (default from env: {config.default_privacy})",
    )
    args = parser.parse_args()

    config.validate()

    run_dir = Path("output") / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[*] Output dir: {run_dir}")

    # 1. Topic
    topic = args.topic or generate_idea()
    print(f"[1/7] Topic: {topic}")

    # 2. Script
    print("[2/7] Writing script...")
    script = generate_script(topic)
    (run_dir / "script.txt").write_text(
        f"TITLE: {script.title}\n\n{script.narration}\n\n---\n{script.description}",
        encoding="utf-8",
    )
    print(f"       Title: {script.title}")

    # 3. Visuals
    print(f"[3/7] Fetching {len(script.visual_keywords)} clips from Pexels...")
    clips_dir = run_dir / "clips"
    clips = fetch_clips(script.visual_keywords, clips_dir)
    if not clips:
        raise RuntimeError("No clips downloaded. Check Pexels API key / keywords.")
    print(f"       Got {len(clips)} clip(s)")

    # 4. Voice
    print("[4/7] Synthesizing voiceover (Edge-TTS)...")
    voice_path = synthesize(script.narration, run_dir / "voice.mp3")

    # 5. Subtitles (optional)
    subtitle_groups = None
    if not args.no_subtitles:
        print("[5/7] Transcribing voice for subtitles (faster-whisper)...")
        from src.subtitle_generator import transcribe, group_words
        words = transcribe(voice_path, language="id")
        subtitle_groups = group_words(words)
        print(f"       {len(subtitle_groups)} caption group(s)")
    else:
        print("[5/7] Skipping subtitles.")

    # 6. Video (stitch + music + subtitles)
    music_path = None if args.no_music else pick_track(config.music_dir)
    if music_path:
        print(f"[6/7] Building video with music: {music_path.name}")
    else:
        print("[6/7] Building video (no music)...")
    final_path = build_video(
        clips, voice_path, run_dir / "final.mp4",
        music_path=music_path,
        subtitle_groups=subtitle_groups,
    )
    print(f"       Saved: {final_path}")

    # 6b. Thumbnail
    thumb_path = generate_thumbnail(final_path, script.title, run_dir / "thumb.jpg")
    print(f"       Thumbnail: {thumb_path}")

    # 7. Upload
    if args.no_upload:
        print("[7/7] --no-upload → skipping YouTube upload.")
        return

    print("[7/7] Uploading to YouTube...")
    video_id = upload(
        final_path,
        title=script.title,
        description=script.description,
        tags=script.tags,
        privacy=args.privacy,
        made_with_ai=True,
        thumbnail_path=thumb_path,
    )
    print(f"[OK] Done. Video ID: {video_id}")


if __name__ == "__main__":
    main()
