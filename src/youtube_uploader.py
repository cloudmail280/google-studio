"""Upload video to YouTube via Data API v3. Defaults to 'unlisted' for safety."""
from pathlib import Path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .config import config

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",  # needed for thumbnails.set
]


def upload(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str | None = None,
    made_with_ai: bool = True,
    thumbnail_path: Path | None = None,
) -> str:
    """Upload & return the YouTube video ID."""
    youtube = _auth()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": privacy or config.default_privacy,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": made_with_ai,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"  uploaded → https://youtu.be/{video_id} (privacy: {body['status']['privacyStatus']})")

    # Set custom thumbnail (requires verified channel)
    if thumbnail_path and Path(thumbnail_path).exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path), mimetype="image/jpeg"),
            ).execute()
            print("  thumbnail uploaded")
        except Exception as e:
            print(f"  [warn] thumbnail upload failed (channel must be verified): {e}")

    return video_id


def _auth():
    creds = None
    token_path = Path(config.yt_token_file)
    if token_path.exists():
        with token_path.open("rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.yt_client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with token_path.open("wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)
