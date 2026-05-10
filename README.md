# Google Studio — Auto YouTube Shorts Pipeline

Pipeline otomatis untuk bikin YouTube Shorts dari 0: ide → naskah → stock footage → voiceover → **subtitle** → **music** → video → **thumbnail** → upload.

**Stack (semua gratis):**
- [Google Gemini API](https://ai.google.dev/) — ide & naskah (free tier)
- [Edge-TTS](https://github.com/rany2/edge-tts) — voiceover (gratis, suara Microsoft)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — subtitle word-level (lokal, gratis)
- [Pexels API](https://www.pexels.com/api/) — stock footage (gratis)
- [MoviePy](https://zulko.github.io/moviepy/) + FFmpeg + Pillow — stitching, subtitle burn-in, thumbnail
- [YouTube Data API v3](https://developers.google.com/youtube/v3) — upload (gratis, quota 10.000/hari)

## 🛡️ Safety defaults

- Upload ke **channel kamu sendiri** (OAuth)
- Default privacy: **`unlisted`** — review dulu sebelum publish
- AI content disclosure otomatis di-flag (syarat YouTube)
- Dry-run mode (`--no-upload`) untuk testing

## 📋 Prerequisites

1. **Python 3.10+**
2. **FFmpeg** (`ffmpeg -version` harus jalan)
3. API keys (semua gratis):
   - **Gemini** — https://aistudio.google.com/app/apikey
   - **Pexels** — https://www.pexels.com/api/new/
   - **YouTube OAuth** — https://console.cloud.google.com/ → enable "YouTube Data API v3" → OAuth 2.0 Client (Desktop) → download `client_secret.json`

## 🚀 Setup

```bash
git clone https://github.com/cloudmail280/google-studio.git
cd google-studio
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # edit: isi GEMINI_API_KEY & PEXELS_API_KEY
# simpan client_secret.json di root folder
```

### (Opsional tapi sangat direkomendasi) Tambah background music

Baca `assets/music/README.md`. Intinya: download beberapa track royalty-free dari YouTube Audio Library atau Pixabay Music, simpan di `assets/music/`.

## 🎬 Usage

```bash
# Dry-run: generate tanpa upload (cek hasilnya dulu)
python main.py --topic "fakta unik tentang laut" --no-upload

# Full pipeline: generate + upload (unlisted)
python main.py --topic "fakta unik tentang laut"

# AI pilih topik sendiri
python main.py

# Matikan fitur individual
python main.py --no-subtitles          # skip subtitle burn-in
python main.py --no-music              # skip background music
python main.py --no-upload             # skip upload

# Publish langsung public (hati-hati!)
python main.py --privacy public
```

Hasil di `output/<timestamp>/`:
- `script.txt` — naskah
- `clips/` — stock footage Pexels
- `voice.mp3` — voiceover
- `final.mp4` — video jadi (1080x1920)
- `thumb.jpg` — thumbnail

## ⏰ Auto-scheduling via GitHub Actions

File workflow ada di `.github/workflows/auto-post.yml`. Default: **setiap hari 09:00 WIB**.

### Setup sekali di GitHub:

1. **Generate `token.json` lokal dulu** dengan menjalankan `python main.py --topic "test" --no-upload` (sekali saja, OAuth flow akan buka browser dan menyimpan `token.json`). Lalu encode:
   ```bash
   base64 -w0 token.json   # Linux. macOS: base64 -i token.json
   ```

2. Buka repo di GitHub → **Settings → Secrets and variables → Actions → New repository secret**. Tambah 4 secret:

   | Nama | Value |
   |---|---|
   | `GEMINI_API_KEY` | API key Gemini kamu |
   | `PEXELS_API_KEY` | API key Pexels kamu |
   | `YT_CLIENT_SECRET_JSON` | Isi file `client_secret.json` (paste semua JSON-nya) |
   | `YT_TOKEN_PICKLE_B64` | Output base64 dari step 1 |

3. Workflow akan otomatis jalan setiap hari. Bisa juga trigger manual via **Actions → Auto-post YouTube Short → Run workflow**.

> **Catatan**: `token.json` bisa expire. Kalau scheduled run gagal dengan auth error, generate ulang lokal dan update secret `YT_TOKEN_PICKLE_B64`.

## 📂 Struktur project

```
src/
├── config.py                # Load env vars
├── idea_generator.py        # Gemini → topik
├── script_writer.py         # Gemini → naskah + caption
├── visual_fetcher.py        # Pexels → stock clips
├── voice_synthesizer.py     # Edge-TTS → mp3
├── subtitle_generator.py    # faster-whisper + Pillow → caption overlay
├── music_fetcher.py         # Random pick dari library lokal
├── video_builder.py         # MoviePy → mp4 vertical + mix music + burn subs
├── thumbnail_generator.py   # Pillow → thumb.jpg
└── youtube_uploader.py      # YouTube API upload + thumbnail
prompts/                     # Prompt templates
assets/music/                # (user-provided) royalty-free music library
.github/workflows/           # Auto-post scheduler
output/                      # Generated videos (gitignored)
```

## ⚠️ Catatan etis

- Upload hanya ke channel MILIK KAMU SENDIRI
- Jangan bikin konten misleading / deepfake / clickbait palsu
- Patuhi [YouTube Community Guidelines](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/), [TOS Pexels](https://www.pexels.com/terms-of-service/), dan lisensi setiap track musik
- Monetize? Baca kebijakan YouTube soal [AI-generated content](https://support.google.com/youtube/answer/14328491)
- Custom thumbnail butuh channel ter-verifikasi (nomor telepon). Kalau belum, pipeline tetap jalan — thumbnail tidak ter-set, tidak ada error fatal

## 🧩 Troubleshooting

| Masalah | Solusi |
|---|---|
| `ImageMagick` error dari MoviePy | Tidak pakai ImageMagick — subtitle pakai Pillow langsung. Update ke versi terbaru repo |
| Subtitle terlalu lambat | Pakai model Whisper lebih kecil: `WHISPER_MODEL=tiny` di `.env` |
| Tidak ada suara musik | Cek `assets/music/` ada file .mp3, dan `MUSIC_VOLUME` > 0 di `.env` |
| Thumbnail upload failed | Channel YouTube belum ter-verifikasi. Verifikasi di [youtube.com/verify](https://www.youtube.com/verify) |
| Font subtitle jelek | Set `SUBTITLE_FONT_PATH` ke path .ttf Bold favorit kamu |
