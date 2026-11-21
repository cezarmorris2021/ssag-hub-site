#!/usr/bin/env python3
"""Fail-closed SSAG YouTube production readiness verifier. Standard library only."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("channel_id", "oauth_verified_at", "rights_approved_at", "upload_authorized_at",
            "video_id", "upload_verified_at", "studio_visibility", "scheduled_publish_at",
            "schedule_verified_at", "analytics_verified_at", "client_storage_verified_at",
            "audit_log_verified_at", "support_verified_at", "payment_verified_at")
def iso(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc)
    except (ValueError, AttributeError, TypeError):
        return False

def check(data):
    errors = []
    for key in REQUIRED:
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"Missing evidence: {key}")
    if not str(data.get("channel_id", "")).startswith("UC"):
        errors.append("channel_id must be a verified YouTube channel ID")
    if not (len(str(data.get("video_id", ""))) == 11):
        errors.append("video_id must have 11 characters; must be backed by real upload receipt")
    if data.get("studio_visibility") not in ("private", "unlisted", "public"):
        errors.append("studio_visibility must be verified")
    for key in REQUIRED:
        if key.endswith("_at") and not iso(data.get(key)):
            errors.append(f"Invalid or future timestamp: {key}")
    if data.get("upload_receipt_url", "").startswith("https://") is False:
        errors.append("Missing HTTPS upload receipt URL")
    if data.get("schedule_receipt_url", "").startswith("https://") is False:
        errors.append("Missing HTTPS scheduling receipt URL")
    if data.get("analytics_receipt_url", "").startswith("https://") is False:
        errors.append("Missing HTTPS analytics receipt URL")
    return errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 verify_youtube_readiness.py <private-evidence.json>")
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text())
        errors = check(data)
    except (OSError, ValueError) as exc:
        print("NOT READY: evidence file unavailable or invalid:", exc)
        return 1
    if errors:
        print("NOT READY (no production launch):")
        for err in errors:
            print("-", err)
        return 1
    print("EVIDENCE FIELDS COMPLETE — manual review of authentic receipts, OAuth scopes, security and live YouTube state STILL REQUIRED. NOT production certified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
