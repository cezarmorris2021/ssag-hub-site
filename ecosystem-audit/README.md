# SSAG ecosystem data integrity watch

## Live contact-stamp repair

A production database trigger named `ssag_verified_contact_stamp` was installed in the Sentinel Zero Neon project on 2026-11-02. It updates `leads.last_contact_at` only after an actual persisted `call_attempts` event with a recognized successful conversation outcome, matching lead and organization, a valid event time, and no simulation/mock/test AI session. It does not mark an unanswered attempt as a contact, invent calls, or retroactively stamp leads without evidence. Existing records: 0 call attempts and 0 contact stamps at installation; 26 overdue follow-ups.

This trigger is deployed in Neon, not by this repository's workflow. Its idempotent SQL definition is preserved at `ecosystem-audit/migrations/20261102_verified_contact_stamp.sql`; the audit workflow does not apply migrations.

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

## November 2 scanner review

A zero-count logic flaw was corrected: empty lead, request and order pipelines now generate findings rather than being silently classified as healthy. A regression test suite covers empty/nonempty counts and missing schema. The scan now checks missing PayPal destinations and contact emails for Turnslate and NextChapter as well as ClientFlow. The live database inspection found all those fields blank. These are configuration gaps, **not** evidence of zero actual external payments.

The source is on draft PR #4 until the five read-only database secrets and workflow tests are verified; do not claim the scheduled scanner is running yet.
