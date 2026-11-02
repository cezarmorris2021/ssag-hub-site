# SSAG YouTube Production Acceptance Ledger

This is an evidence template, **not a claim of connected accounts or delivered client videos**. Store only non-sensitive receipts here. Keep OAuth tokens, private client information, and unreleased content out of public GitHub.

## Gate-by-gate checklist (per authorized channel)

| Gate | Required evidence | Current verified state |
|---|---|---|
| Weekly content calendar | dated, approved work order | Local workstation only |
| Script and metadata | client-approved revision and date | Drafting code only |
| Thumbnail and finished video | SHA-256 of approved PNG and rendered MP4 | Test render only |
| Rights and consent | private rights/guardian consent record reference | Not verified |
| Client approval | dated approval reference, stored privately | Not verified |
| OAuth channel identity | API-confirmed channel ID, authorized owner | Not connected |
| Private upload | returned video ID, timestamp, API receipt | Not verified |
| Scheduling | verified publishAt and privacy status | Not verified |
| Cross-platform distribution | provider-specific post IDs | Not connected |
| Analytics | dated API channel/video metrics | Not connected |
| Support resolution | customer-confirmed ticket closure | Local-only tracking |

## Receipt format (no credentials)

```json
{
  "channel_label": "",
  "verified_channel_id": null,
  "rights_approval_reference": null,
  "client_approval_reference": null,
  "asset_sha256": null,
  "youtube_video_id": null,
  "upload_verified_at": null,
  "privacy_status": null,
  "publish_at_utc": null,
  "published_verified_at": null,
  "support_resolution_reference": null,
  "status": "BLOCKED"
}
```

## Release rule

Only mark a client channel **READY** after authenticated OAuth channel verification, approved media rights, successful real private upload, recorded YouTube video ID and independently verified status. An HTTP 200 homepage, successful CI, local board entry or test MP4 alone never passes this gate. Do not start unattended posting or claim client revenue from planning records.

## Owner-only prerequisite

Channel owner authorizes Google OAuth and confirms the exact destination channel. SSAG personnel may prepare code and approval packets, but cannot supply the owner's consent. See [publisher procedure](./README.md).
