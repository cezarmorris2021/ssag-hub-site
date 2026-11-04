# YouTube Issue #2 — Evidence and acceptance

The new `verify_youtube_readiness.py` is a **fail-closed evidence-field check**, not a YouTube uploader or certification. Run `python3 youtube-operations/verify_youtube_readiness.py /secure/evidence.json` locally. Never commit OAuth tokens, customer receipts or private channel evidence.

Required evidence fields: channel_id, oauth_verified_at, rights_approved_at, upload_authorized_at, video_id, upload_verified_at, studio_visibility, scheduled_publish_at, schedule_verified_at, analytics_verified_at, client_storage_verified_at, audit_log_verified_at, support_verified_at, payment_verified_at, upload_receipt_url, schedule_receipt_url, analytics_receipt_url.

Owner must authorize Google OAuth for each intended channel and explicitly approve a rights-cleared real upload. Authenticated YouTube upload ID, Studio visibility, scheduling receipt and analytics must be checked independently. Multi-client isolation, secure token storage, audit logs, SLA and payment verification are separate acceptance requirements. A passing local evidence format check alone never marks the service production-ready. Keep Issue #2 OPEN / PARTIAL until verified.
