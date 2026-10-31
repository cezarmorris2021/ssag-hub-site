#!/usr/bin/env python3
"""SSAG YouTube channel publisher: explicit owner-approved uploads only.

This script runs on an owner-controlled computer. The first authorization opens
Google OAuth. Credentials remain on that machine, never in public GitHub.
It reads a package JSON exported by the SSAG YouTube Workstation.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
CLIENT_SECRETS_ENV = "SSAG_YOUTUBE_OAUTH_CLIENT_SECRETS"
DEFAULT_TOKEN = Path.home() / ".config" / "ssag-youtube" / "youtube-token.json"

def validate_manifest(m: dict, video_path: str | Path):
    if not isinstance(m, dict):
        raise ValueError("Manifest must be a JSON object.")
    if not m.get("approved"):
        raise ValueError("Owner approval is required before publishing.")
    if not m.get("rights_confirmed"):
        raise ValueError("Rights confirmation is required for video, voice, music and images.")
    if not m.get("channel_verified"):
        raise ValueError("Verify the destination YouTube channel before publishing.")
    title = str(m.get("title", "")).strip()
    description = str(m.get("description", "")).strip()
    if not title or len(title) > 100:
        raise ValueError("Title must have 1 to 100 characters.")
    if not description or len(description) > 5000:
        raise ValueError("Description must have 1 to 5000 characters.")
    video = Path(video_path).expanduser()
    if not video.is_file() or video.suffix.lower() not in {".mp4", ".mov", ".webm", ".mkv"}:
        raise ValueError("A real local video file must exist.")
    if video.stat().st_size < 1024:
        raise ValueError("Video file is empty or too small.")
    tags = m.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
        raise ValueError("Tags must be a string list.")
    category = str(m.get("category_id", "22"))
    if not category.isdigit():
        raise ValueError("Category ID must be numeric.")
    publish_at = m.get("publish_at")
    if publish_at:
        parsed = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("Schedule requires an explicit timezone.")
        if parsed <= datetime.now(timezone.utc):
            raise ValueError("Publish time must be in the future.")
    kids = m.get("made_for_kids")
    if not isinstance(kids, bool):
        raise ValueError("Set made_for_kids to true or false after reviewing the content.")
    synthetic = m.get("contains_synthetic_media")
    if not isinstance(synthetic, bool):
        raise ValueError("Review and explicitly set contains_synthetic_media.")
    return {
        "snippet": {"title": title, "description": description, "categoryId": category, "tags": tags},
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": kids,
            "containsSyntheticMedia": synthetic,
            **({"publishAt": parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")} if publish_at else {}),
        },
    }

def oauth_service(client_secrets: str, token_path: Path):
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Install youtube-publisher/requirements.txt first.") from exc
    if not Path(client_secrets).is_file():
        raise RuntimeError("OAuth client-secrets JSON file not found; create credentials in your own Google Cloud project.")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.parent.chmod(0o700)
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
        token_path.chmod(0o600)
    return build("youtube", "v3", credentials=creds)

def authorize_channel(youtube):
    identity = youtube.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    if len(identity) != 1:
        raise RuntimeError("Expected exactly one authorized channel; disconnect/reauthorize the intended account.")
    return {"id":identity[0]["id"], "title":identity[0]["snippet"]["title"]}

def main(argv=None):
    p = argparse.ArgumentParser(description="SSAG YouTube approved and private-first uploader")
    p.add_argument("manifest", help="Exported SSAG YouTube Workstation JSON manifest")
    p.add_argument("--video", required=True, help="Local rendered video file")
    p.add_argument("--token-file", default=str(DEFAULT_TOKEN), help="Local private OAuth credential cache")
    p.add_argument("--check-only", action="store_true", help="Validate package; no OAuth or API calls")
    p.add_argument("--verify-channel", action="store_true", help="Check YouTube identity without uploading")
    p.add_argument("--upload-approved", action="store_true", help="Explicit permission to upload this package")
    args = p.parse_args(argv)
    m = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    payload = validate_manifest(m, args.video)
    if args.check_only:
        print(json.dumps({"status": "PACKAGE_VALID_ONLY", "upload_performed": False, "metadata": payload}, indent=2))
        return 0
    client = os.environ.get(CLIENT_SECRETS_ENV)
    if not client:
        raise SystemExit("Set SSAG_YOUTUBE_OAUTH_CLIENT_SECRETS to a local OAuth JSON file; never commit it.")
    youtube = oauth_service(client, Path(args.token_file).expanduser())
    channel = authorize_channel(youtube)
    if args.verify_channel:
        print(json.dumps({"status": "CHANNEL_VERIFIED", "channel": channel, "upload_performed": False}))
        return 0
    expected = str(m.get("channel_id", "")).strip()
    if not expected or expected != channel["id"]:
        raise SystemExit("Destination channel mismatch. Authorized channel: " + channel["title"] +
                         " ("+channel["id"]+"). Update manifest only after confirming this is correct.")
    if not args.upload_approved:
        raise SystemExit("Upload NOT performed. Explicitly add --upload-approved after reviewing video and destination.")
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(str(Path(args.video).expanduser()), resumable=True, chunksize=1024*1024*8)
    request = youtube.videos().insert(part="snippet,status", body=payload, media_body=media)
    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            print(f"Uploaded {progress.progress():.0%}", file=sys.stderr)
    video_id = response.get("id")
    if not video_id:
        raise RuntimeError("YouTube upload returned no video ID. Inspect the dashboard before retrying.")
    print(json.dumps({
        "status": "UPLOADED_PRIVATE_OR_SCHEDULED",
        "channel_id": channel["id"], "youtube_id": video_id,
        "youtube_url": "https://www.youtube.com/watch?v=" + video_id,
        "privacy": payload["status"]["privacyStatus"],
        "scheduled_at": payload["status"].get("publishAt"),
        "note": "Verify the video in YouTube Studio; platform processing may continue."
    }, indent=2))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
