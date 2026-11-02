#!/usr/bin/env python3
"""Evidence-first SSAG data-gap audit. Read-only; never edits business records."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

SOURCES = {
    "sentinel": "SSAG_SENTINEL_DATABASE_URL",
    "dispatch": "SSAG_DISPATCH_DATABASE_URL",
    "clientflow": "SSAG_CLIENTFLOW_DATABASE_URL",
    "turnslate": "SSAG_TURNSLATE_DATABASE_URL",
    "nextchapter": "SSAG_NEXTCHAPTER_DATABASE_URL",
}
FINDINGS = []


def flag(system, code, severity, count=None, note=""):
    FINDINGS.append({
        "system": system,
        "code": code,
        "severity": severity,
        "count": count,
        "note": note,
    })


def scalar(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()[0]


def table_exists(conn, table):
    return scalar(conn, "select to_regclass(%s) is not null", (f"public.{table}",))


def columns(conn, table):
    with conn.cursor() as cur:
        cur.execute(
            "select column_name from information_schema.columns "
            "where table_schema='public' and table_name=%s",
            (table,),
        )
        return {row[0] for row in cur.fetchall()}


def count_check(conn, system, code, sql, required, severity="P0", alert_when_zero=False):
    for table, needed in required.items():
        if not table_exists(conn, table):
            flag(system, code + "_SCHEMA_MISSING", "P0", note=f"Missing table: {table}")
            return
        missing = set(needed) - columns(conn, table)
        if missing:
            flag(
                system,
                code + "_SCHEMA_MISSING",
                "P0",
                note=f"Missing columns in {table}: {', '.join(sorted(missing))}",
            )
            return
    try:
        count = scalar(conn, sql)
        if (count == 0) if alert_when_zero else (count > 0):
            flag(system, code, severity, count)
    except psycopg.Error as exc:
        conn.rollback()
        flag(system, code + "_CHECK_FAILED", "P0", note=exc.__class__.__name__)


def check_sentinel(conn):
    count_check(
        conn, "sentinel", "MISSING_CONTACT_STAMP_WITH_VERIFIED_OUTCOME",
        """select count(*) from public.leads l
           where l.last_contact_at is null and exists (
             select 1 from public.call_attempts a
             where a.lead_id=l.id and a.organization_id=l.organization_id
               and lower(a.outcome) in ('connected', 'answered', 'conversation', 'appointment_booked', 'booked')
               and a.started_at is not null
               and not exists (
                 select 1 from public.ai_call_sessions s
                 where s.id=a.ai_session_id
                   and lower(s.transport) in ('simulation', 'mock', 'test')
               )
           )""",
        {"leads": {"id", "organization_id", "last_contact_at"},
         "call_attempts": {"lead_id", "organization_id", "outcome", "ai_session_id", "started_at"},
         "ai_call_sessions": {"id", "transport"}},
    )
    count_check(
        conn, "sentinel", "STALE_UNCONTACTED_LEADS_7D",
        """select count(*) from public.leads
           where last_contact_at is null and do_not_call is not true
             and created_at < now() - interval '7 days'""",
        {"leads": {"last_contact_at", "do_not_call", "created_at"}}, "P1",
    )
    count_check(
        conn, "sentinel", "OVERDUE_NEXT_ACTION",
        """select count(*) from public.leads
           where next_action_at < now() and do_not_call is not true
             and status not in ('closed', 'not_interested')""",
        {"leads": {"next_action_at", "do_not_call", "status"}}, "P1",
    )
    count_check(
        conn, "sentinel", "LEADS_MISSING_NEXT_ACTION",
        """select count(*) from public.leads
           where next_action_at is null and do_not_call is not true
             and status not in ('closed', 'not_interested')""",
        {"leads": {"next_action_at", "do_not_call", "status"}}, "P1",
    )
    count_check(
        conn, "sentinel", "DNC_WITH_CAMPAIGN_QUEUE",
        """select count(*) from public.ai_campaign_leads cl
           join public.ai_campaigns c on c.id=cl.campaign_id
           join public.leads l on l.id=cl.lead_id and l.organization_id=c.organization_id
           where l.do_not_call is true and cl.status in ('queued', 'retry')""",
        {"ai_campaign_leads": {"campaign_id", "lead_id", "status"},
         "ai_campaigns": {"id", "organization_id"},
         "leads": {"id", "organization_id", "do_not_call"}},
    )
    count_check(
        conn, "sentinel", "LIVE_CAMPAIGN_WITHOUT_CALLER_ID_OR_APPROVAL",
        """select count(*) from public.ai_campaigns
           where status in ('active', 'running')
             and (nullif(trim(caller_id), '') is null
                  or compliance_status is distinct from 'approved')""",
        {"ai_campaigns": {"status", "caller_id", "compliance_status"}},
    )
    count_check(
        conn, "sentinel", "LIVE_SESSION_MISSING_STARTED_AT",
        """select count(*) from public.ai_call_sessions
           where lower(transport) not in ('simulation', 'mock', 'test')
             and started_at is null""",
        {"ai_call_sessions": {"transport", "started_at"}},
    )
    count_check(
        conn, "sentinel", "CALL_ATTEMPT_WITHOUT_TIMESTAMP",
        "select count(*) from public.call_attempts where started_at is null",
        {"call_attempts": {"started_at"}},
    )
    count_check(
        conn, "sentinel", "APPOINTMENT_WITHOUT_SCHEDULED_AT",
        "select count(*) from public.appointments where scheduled_at is null",
        {"appointments": {"scheduled_at"}},
    )


def check_dispatch(conn):
    count_check(
        conn, "dispatch", "BUSINESS_NUMBER_MISSING",
        """select count(*) from public.organizations
           where nullif(trim(business_phone), '') is null""",
        {"organizations": {"business_phone"}},
    )
    count_check(
        conn, "dispatch", "NO_ELIGIBLE_EMPLOYEE",
        """select count(*) from public.organizations o
           where not exists (
             select 1 from public.employees e
             where e.organization_id=o.id and e.active and e.on_duty
               and e.phone_verified and e.phone_approved and not e.busy
               and nullif(trim(e.forwarding_phone), '') is not null
           )""",
        {"organizations": {"id"}, "employees": {
            "organization_id", "active", "on_duty", "phone_verified",
            "phone_approved", "busy", "forwarding_phone",
        }},
    )
    count_check(
        conn, "dispatch", "ROUTED_CALL_WITHOUT_START",
        """select count(*) from public.calls
           where status in ('routed', 'answered', 'completed') and started_at is null""",
        {"calls": {"status", "started_at"}},
    )
    count_check(
        conn, "dispatch", "APPOINTMENT_WITHOUT_DATE",
        "select count(*) from public.appointments where scheduled_at is null",
        {"appointments": {"scheduled_at"}},
    )


def check_clientflow(conn):
    if not table_exists(conn, "leads"):
        flag("clientflow", "LEADS_TABLE_MISSING", "P0")
    else:
        count_check(
            conn, "clientflow", "NO_LEADS_RECORDED",
            "select count(*) from public.leads",
            {"leads": {"id"}}, "P1", alert_when_zero=True,
        )
    required_settings = {"paypal_me", "paypal_launch", "paypal_growth", "paypal_scale"}
    if not table_exists(conn, "settings"):
        flag("clientflow", "PAYPAL_SETTINGS_TABLE_MISSING", "P0")
        return
    missing = required_settings - columns(conn, "settings")
    if missing:
        flag(
            "clientflow", "PAYPAL_SETTINGS_SCHEMA_INCOMPLETE", "P0",
            note=f"Missing columns: {', '.join(sorted(missing))}",
        )
        return
    try:
        configured = scalar(
            conn,
            """select count(*) from public.settings
               where nullif(trim(paypal_me), '') is not null
                 and nullif(trim(paypal_launch), '') is not null
                 and nullif(trim(paypal_growth), '') is not null
                 and nullif(trim(paypal_scale), '') is not null""",
        )
        if configured == 0:
            flag("clientflow", "PAYPAL_SETTINGS_INCOMPLETE", "P1")
    except psycopg.Error as exc:
        conn.rollback()
        flag("clientflow", "PAYPAL_SETTINGS_CHECK_FAILED", "P0", note=exc.__class__.__name__)


def check_generic(conn, system):
    table = {"turnslate": "requests", "nextchapter": "orders"}[system]
    if not table_exists(conn, table):
        flag(system, f"{table.upper()}_TABLE_MISSING", "P0")
        return
    count_check(
        conn, system, f"NO_{table.upper()}_RECORDED",
        f"select count(*) from public.{table}",
        {table: {"id"}}, "P1", alert_when_zero=True,
    )

    payment_table = {"turnslate": "settings", "nextchapter": "store_settings"}[system]
    payment_fields = {"turnslate": ("paypal_url", "contact_email"),
                      "nextchapter": ("paypal_refresh", "paypal_complete",
                                      "paypal_career", "contact_email")}[system]
    if not table_exists(conn, payment_table):
        flag(system, "PAYMENT_SETTINGS_TABLE_MISSING", "P0")
    else:
        missing = set(payment_fields) - columns(conn, payment_table)
        if missing:
            flag(system, "PAYMENT_SETTINGS_SCHEMA_INCOMPLETE", "P0",
                 note=", ".join(sorted(missing)))
        else:
            for field in payment_fields:
                count_check(
                    conn, system, "MISSING_" + field.upper(), 
                    f"select count(*) from public.{payment_table} "
                    f"where nullif(trim({field}), '') is not null",
                    {payment_table: {field}}, "P1", alert_when_zero=True,
                )



def check_proofs():
    root = Path(__file__).resolve().parents[1] / "owner-master-dashboard"
    for name in ("capability-proof.json", "youtube-capability-proof.json"):
        path = root / name
        if not path.exists():
            flag("media", name + "_MISSING", "P0")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            flag("media", name + "_INVALID", "P0", note=exc.__class__.__name__)
            continue
        if data.get("status") not in ("READY", "VERIFIED_END_TO_END"):
            flag(
                "media",
                data.get("capability_id", name) + "_NOT_E2E",
                "P1",
                note=data.get("status", "unknown"),
            )


def main():
    check_proofs()
    checkers = {
        "sentinel": check_sentinel,
        "dispatch": check_dispatch,
        "clientflow": check_clientflow,
        "turnslate": lambda conn: check_generic(conn, "turnslate"),
        "nextchapter": lambda conn: check_generic(conn, "nextchapter"),
    }
    for system, env in SOURCES.items():
        dsn = os.environ.get(env)
        if not dsn:
            flag(system, "DATABASE_CONNECTION_NOT_CONFIGURED", "P0",
                 note="Set encrypted GitHub Actions secret " + env)
            continue
        try:
            with psycopg.connect(
                dsn,
                connect_timeout=10,
                options="-c default_transaction_read_only=on",
            ) as conn:
                checkers[system](conn)
        except Exception as exc:
            flag(system, "AUDIT_CONNECTION_OR_QUERY_FAILED", "P0",
                 note=exc.__class__.__name__)
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "mode": "read_only",
        "sources": list(SOURCES),
        "findings": FINDINGS,
        "counts": {
            "P0": sum(item["severity"] == "P0" for item in FINDINGS),
            "P1": sum(item["severity"] == "P1" for item in FINDINGS),
        },
    }
    output = Path(os.environ.get("SSAG_AUDIT_OUTPUT", "ssag-gap-audit.json"))
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"]))
    return 1 if report["counts"]["P0"] else 0


if __name__ == "__main__":
    sys.exit(main())
