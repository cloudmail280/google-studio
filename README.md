# Google Studio — Auto YouTube Shorts Pipeline

Pipeline otomatis untuk bikin YouTube Shorts dari 0: ide → naskah → stock footage → voiceover → video → upload.

**Stack (semua gratis):**
- [Google Gemini API](https://ai.google.dev/) — ide & naskah (free tier)
- [Edge-TTS](https://github.com/rany2/edge-tts) — voiceover (gratis, suara Microsoft)
- [Pexels API](https://www.pexels.com/api/) — stock footage (gratis)
- [MoviePy](https://zulko.github.io/moviepy/) + FFmpeg — stitching
- [YouTube Data API v3](https://developers.google.com/youtube/v3) — upload (gratis, quota 10.000/hari)

## 🛡️ Safety defaults

- Upload ke **channel kamu sendiri** (OAuth)
- Default privacy: **`unlisted`** — kamu review dulu sebelum publish
- AI content disclosure otomatis di-flag (syarat YouTube untuk AI-generated content)
- Dry-run mode (`--no-upload`) untuk testing

## 📋 Prerequisites

1. **Python 3.10+**
2. **FFmpeg** terinstall di system (`ffmpeg -version` harus jalan)
3. API keys (semua gratis):
   - **Gemini API key** — https://aistudio.google.com/app/apikey
   - **Pexels API key** — https://www.pexels.com/api/new/
   - **YouTube OAuth credentials** — https://console.cloud.google.com/
     - Buat project → enable "YouTube Data API v3" → buat OAuth 2.0 Client (type: Desktop) → download JSON sebagai `client_secret.json`

## 🚀 Setup

```bash
# 1. Clone & masuk folder
git clone <repo-url>
cd google-studio

# 2. Buat virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# 3. Install deps
pip install -r requirements.txt

# 4. Setup env
cp .env.example .env
# Edit .env, isi GEMINI_API_KEY dan PEXELS_API_KEY

# 5. Simpan OAuth credentials YouTube
# Download dari Google Cloud Console, simpan sebagai client_secret.json di root
```

## 🎬 Usage

```bash
# Generate & preview (TANPA upload — recommended pertama kali)
python main.py --topic "fakta unik tentang laut" --no-upload

# Generate + upload (unlisted by default)
python main.py --topic "fakta unik tentang laut"

# Biarkan AI pilih topik sendiri
python main.py

# Upload langsung public (hati-hati!)
python main.py --topic "..." --privacy public
```

Hasil akan ada di `output/<timestamp>/`:
- `script.txt` — naskah
- `voice.mp3` — voiceover
- `final.mp4` — video jadi (1080x1920, 60 detik)

## 📂 Struktur project

```
src/
├── config.py              # Load env vars
├── idea_generator.py      # Gemini → topik
├── script_writer.py       # Gemini → naskah + caption
├── visual_fetcher.py      # Pexels → stock clips
├── voice_synthesizer.py   # Edge-TTS → mp3
├── video_builder.py       # MoviePy → mp4 vertical
└── youtube_uploader.py    # YouTube API upload
prompts/                   # Prompt templates untuk LLM
output/                    # Generated videos (gitignored)
```

## ⚠️ Catatan etis

- Upload hanya ke channel MILIK KAMU SENDIRI
- Jangan bikin konten yang misleading / deepfake orang real / clickbait palsu
- Patuhi [YouTube Community Guidelines](https://www.youtube.com/howyoutubeworks/policies/community-guidelines/) dan [TOS Pexels](https://www.pexels.com/terms-of-service/)
- Kalau monetize, baca kebijakan YouTube soal [AI-generated content](https://support.google.com/youtube/answer/14328491)

## 🧩 Status skeleton

Ini baru skeleton. Setiap modul punya TODO. Jalankan `python main.py --help` buat mulai.
