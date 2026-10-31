# SSAG YouTube Channel Automation & Support

**Owner-facing workstation:** https://cezarmorris2021.github.io/ssag-hub-site/youtube-operations/

## Current state (October 30, 2026)
- Source: online in the owner-controlled SSAG GitHub hub; website deployment success must be verified through GitHub Actions.
- **Functional in the browser, without payments:** plan each channel's video, outline scripts, prepare metadata and descriptions, render a 1280x720 PNG thumbnail, track the weekly video queue, client approvals, licensing checks, manually recorded delivery evidence, and open/resolve support tickets. Export CSV reports, channel manifest and JSON backups; restore JSON locally.
- **Not yet connected:** actual YouTube OAuth account(s), automatic video uploads, Google-reported publishing receipts, analytics, external scheduler, cross-platform posting and shared production DB. The browser is an owner workstation and not an authenticated multi-user SaaS service. Do not sell it as if those pieces already exist.
- Draft records are local to the browser and device (localStorage), not securely synchronized across a team. Do not enter secrets or confidential client data in public-facing web workstations.

### Existing SSAG content projects
Use the planned names *Clever Living Lab*, *Money Mindset Vault*, *Passive Hustle TV*, *Quantum Gadgetry* and *Circuit Salvage* as **unverified channel labels**, not claims of live ownership or subscribers. Each connected channel requires its own authorized Google OAuth session, channel-ID verification, and permission to upload.

### What we offer after verification
**Production service:** channel audit, content calendar, scripts, title/description/tag package, original/rights-cleared visuals and voice, thumbnails, editing and shorts, human review, privacy/content declarations, uploader setup and support. **Publishing service:** OAuth-channel authentication, approved private-first upload, schedule with publishAt when applicable, verified YouTube video ID, and production log. **Client support:** production requests, revisions, problems, deliverable tracker, weekly status reports and securely stored evidence.

No fixed client price, subscription tier, auto-generated video, automatic analytics, or account-connected channel should be claimed without actual verified resources or owner approval.

## Direct publishing (optional, owner-operated desktop)

YouTube channel publishing requires **authorization from the channel owner**. SSAG never stores tokens in GitHub Pages source or public environment files.

1. In your own [Google Cloud Console](https://console.cloud.google.com/), create a project, enable YouTube Data API v3, configure OAuth consent, and create an *installed application/desktop* OAuth client JSON. You (the user) must complete Google's approval/consent; ChatGPT cannot do that for you.
2. On an owner-controlled computer with Python 3.11+, run: `python -m pip install -r youtube-operations/publisher/requirements.txt`.
3. Put the client JSON in a private local folder. Set `SSAG_YOUTUBE_OAUTH_CLIENT_SECRETS` to its full file path; do **not** send the JSON or refresh tokens to other people or commit them.
4. Run `python youtube-operations/publisher/publish.py manifest.json --video /path/to/your-final.mp4 --check-only` for a no-network manifest check.
5. Verify the authorized destination with `--verify-channel` and cross-check that the actual channel ID matches the exported manifest. A typed channel ID alone does not prove authorization.
6. Once the owner has reviewed final video/thumbnail and all rights, use `--upload-approved`. The program uploads **private by default**, optionally schedules publication if the supplied UTC timestamp is future and valid, and returns the actual YouTube video ID and URL. Record those in the weekly board.
7. Check the video and scheduling status in YouTube Studio. Never claim uploaded merely because a locally queued job exists.

**Real limitations:** An unverified Google API project may have restrictions, and YouTube API quotas and eligibility can change. This script is an operator-driven automation (it automates metadata and upload after explicit approval), not background auto-posting or a permanent always-on cloud service. YouTube API scheduled-publication requirements and the channel's actual permissions must be tested. The upload token allows sensitive channel actions and must never be copied into client-facing site code.

Documentation:
- https://developers.google.com/youtube/v3/docs/videos/insert
- https://developers.google.com/youtube/v3/docs/videos
- https://developers.google.com/youtube/v3/guides/authentication

## SSAG definition of done

- [x] Browser production board, thumbnails, metadata manifests, support tickets and backups committed
- [x] Owner-approved OAuth publishing CLI implemented
- [ ] CI safety tests verified green
- [ ] A real Google account connects and identifies the correct destination channel
- [ ] A rights-cleared video is actually uploaded and returns a real video ID
- [ ] Scheduled publishing confirmed on the platform
- [ ] Channel analytics verified; data pipeline and support system protected by authentication
- [ ] Client onboarding, delegated permissions, privacy and billing verified before sales claims
