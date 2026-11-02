# SSAG ecosystem data integrity watch

## Live contact-stamp repair

A production database trigger named `ssag_verified_contact_stamp` was installed in the Sentinel Zero Neon project on 2026-11-02. It updates `leads.last_contact_at` only after an actual persisted `call_attempts` event with a recognized successful conversation outcome, matching lead and organization, a valid event time, and no simulation/mock/test AI session. It does not mark an unanswered attempt as a contact, invent calls, or retroactively stamp leads without evidence. Existing records: 0 call attempts and 0 contact stamps at installation; 26 overdue follow-ups.

This trigger is deployed in Neon, not by this repository's workflow. Preserve it in database migrations when schema is maintained.

## Cross-division automated checks

`ecosystem-audit/audit.py` is read-only. It checks five independent Neon project databases for missing contact timestamps despite confirmed interactions, overdue follow-ups, DNC queue violations, live campaign safety, absent call timestamps, dispatch staffing/phone setup, missing appointment times, payment schema discovery, zero-order/request signals and media proof gaps. Missing credentials and query failures are **P0**, never silently treated as healthy.

`.github/workflows/ecosystem-data-integrity.yml` schedules a run every three hours and permits manual runs. Every run stores a redacted JSON artifact and fails if a P0 gap exists. The workflow never changes lead data or makes calls.

**Activation prerequisite:** An authorized repository administrator must configure the five encrypted GitHub Actions secrets below using read-only database roles; do not commit URLs/passwords to source:
- `SSAG_SENTINEL_DATABASE_URL`
- `SSAG_DISPATCH_DATABASE_URL`
- `SSAG_CLIENTFLOW_DATABASE_URL`
- `SSAG_TURNSLATE_DATABASE_URL`
- `SSAG_NEXTCHAPTER_DATABASE_URL`

No secrets are currently asserted configured. Until all five are present, the workflow correctly reports missing coverage rather than claiming ecosystem-wide verification. A GitHub Actions schedule may be delayed; use existing Business Command Watch and dashboard monitoring independently.

## Evidence policy

`created_at` is lead creation, `next_action_at` is follow-up due, `call_attempts.started_at` is an attempt, and `last_contact_at` is a verified successful contact. These are not interchangeable. Keep simulation/test activity out of real sales metrics. Never expose customer identifiers, credentials, call recordings or contact lists in public GitHub artifacts.

## Follow-up findings from live database audit

- 26 eligible lead follow-ups were overdue as of 2026-11-02; no call attempts existed.
- No historical contact stamps can be truthfully backfilled.
- Payment, telephony, Google OAuth and GPU owner-only authorizations remain distinct operational blockers; the scanner detects gaps but cannot grant permission or purchase services.
