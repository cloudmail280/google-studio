"""Orchestrator: idea → script → visuals → voice → video → (optional) upload."""
import argparse
from datetime import datetime
from pathlib import Path

from src.config import config
from src.idea_generator import generate_idea
from src.script_writer import generate_script
from src.visual_fetcher import fetch_clips
from src.voice_synthesizer import synthesize
from src.video_builder import build_video
from src.youtube_uploader import upload


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto YouTube Shorts generator")
    parser.add_argument("--topic", help="Topic hint. If omitted, AI picks one.", default=None)
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Generate only, skip YouTube upload (recommended for first run).",
    )
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
    print(f"[1/6] Topic: {topic}")

    # 2. Script
    print("[2/6] Writing script...")
    script = generate_script(topic)
    (run_dir / "script.txt").write_text(
        f"TITLE: {script.title}\n\n{script.narration}\n\n---\n{script.description}",
        encoding="utf-8",
    )
    print(f"       Title: {script.title}")

    # 3. Visuals
    print(f"[3/6] Fetching {len(script.visual_keywords)} clips from Pexels...")
    clips_dir = run_dir / "clips"
    clips = fetch_clips(script.visual_keywords, clips_dir)
    if not clips:
        raise RuntimeError("No clips downloaded. Check Pexels API key / keywords.")
    print(f"       Got {len(clips)} clip(s)")

    # 4. Voice
    print("[4/6] Synthesizing voiceover (Edge-TTS)...")
    voice_path = synthesize(script.narration, run_dir / "voice.mp3")

    # 5. Video
    print("[5/6] Building final video...")
    final_path = build_video(clips, voice_path, run_dir / "final.mp4")
    print(f"       Saved: {final_path}")

    # 6. Upload
    if args.no_upload:
        print("[6/6] --no-upload → skipping YouTube upload.")
        return

    print("[6/6] Uploading to YouTube...")
    video_id = upload(
        final_path,
        title=script.title,
        description=script.description,
        tags=script.tags,
        privacy=args.privacy,
        made_with_ai=True,
    )
    print(f"[OK] Done. Video ID: {video_id}")


if __name__ == "__main__":
    main()
