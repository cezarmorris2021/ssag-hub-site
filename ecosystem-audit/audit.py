#!/usr/bin/env python3
"""SSAG evidence-first data gap audit. Read-only; never repairs or fabricates business events."""
import json, os, sys
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
    FINDINGS.append(dict(system=system, code=code, severity=severity, count=count, note=note))
def query(conn, sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchone()[0]
def table_exists(conn, name):
    return query(conn, "select to_regclass('public." + name + "') is not null")
def check_sentinel(conn):
    if not table_exists(conn, "leads"):
        flag("sentinel","LEADS_TABLE_MISSING","P0"); return
    checks = [
      ("MISSING_CONTACT_STAMP_WITH_VERIFIED_OUTCOME","P0", """
       select count(*) from leads l where l.last_contact_at is null and exists
       (select 1 from call_attempts a where a.lead_id=l.id and a.organization_id=l.organization_id
        and lower(coalesce(a.outcome,'')) in ('connected','answered','conversation','appointment_booked','booked')
        and not exists (select 1 from ai_call_sessions s where s.id=a.ai_session_id and s.transport in ('simulation','mock','test')))"""),
      ("STALE_UNCONTACTED_LEADS_7D","P1","select count(*) from leads where last_contact_at is null and do_not_call is not true and created_at < now()-interval '7 days'"),
      ("OVERDUE_NEXT_ACTION","P1","select count(*) from leads where next_action_at < now() and do_not_call is not true and status not in ('closed','won','lost')"),
      ("LEADS_MISSING_NEXT_ACTION","P1","select count(*) from leads where next_action_at is null and do_not_call is not true and status not in ('closed','won','lost')"),
      ("DNC_WITH_CAMPAIGN_QUEUE","P0","select count(*) from ai_campaign_leads c join leads l on l.id=c.lead_id where l.do_not_call is true and c.status in ('queued','retry')"),
      ("LIVE_CAMPAIGN_WITHOUT_CALLER_ID_OR_APPROVAL","P0","select count(*) from ai_campaigns where status in ('active','running') and (nullif(trim(caller_id),'') is null or compliance_status <> 'approved')"),
      ("LIVE_SESSION_MISSING_STARTED_AT","P0","select count(*) from ai_call_sessions where transport not in ('simulation','mock','test') and started_at is null"),
      ("CALL_ATTEMPT_WITHOUT_TIMESTAMP","P0","select count(*) from call_attempts where started_at is null"),
      ("APPOINTMENT_WITHOUT_SCHEDULED_AT","P0","select count(*) from appointments where scheduled_at is null"),
    ]
    for code,severity,sql in checks:
        try:
            count=query(conn,sql)
            if count: flag("sentinel",code,severity,count)
        except psycopg.Error as exc:
            flag("sentinel",code+"_CHECK_FAILED","P0",note=exc.__class__.__name__)
            conn.rollback()
def check_dispatch(conn):
    for code,sql in [
       ("BUSINESS_NUMBER_MISSING","select count(*) from organizations where nullif(trim(business_phone),'') is null"),
       ("NO_ELIGIBLE_EMPLOYEE","select count(*) from organizations o where not exists (select 1 from employees e where e.organization_id=o.id and e.active and e.on_duty and e.phone_verified and e.phone_approved and not e.busy)"),
       ("ROUTED_CALL_WITHOUT_START","select count(*) from calls where status in ('routed','answered','completed') and started_at is null"),
       ("APPOINTMENT_WITHOUT_DATE","select count(*) from appointments where scheduled_at is null")]:
        n=query(conn,sql)
        if n: flag("dispatch",code,"P0",n)
def check_clientflow(conn):
    if table_exists(conn,"leads"):
        n=query(conn,"select count(*) from leads")
        if n==0: flag("clientflow","NO_LEADS_RECORDED","P1",0)
    cols=query(conn,"select count(*) from information_schema.columns where table_schema='public' and column_name ilike '%paypal%'")
    if cols==0: flag("clientflow","PAYPAL_FIELD_NOT_DISCOVERED","P1")
def check_generic(conn, system):
    for table in ("orders","requests","leads"):
        if table_exists(conn,table):
            n=query(conn,"select count(*) from public."+table)
            if n==0: flag(system,"NO_"+table.upper()+"_RECORDED","P1",0)
def check_proofs():
    for name in ("capability-proof.json","youtube-capability-proof.json"):
        path=Path(__file__).resolve().parents[1]/"owner-master-dashboard"/name
        if not path.exists():
            flag("media",name+"_MISSING","P0"); continue
        data=json.loads(path.read_text())
        if data.get("status") not in ("READY","VERIFIED_END_TO_END"):
            flag("media",data.get("capability_id",name)+"_NOT_E2E","P1",note=data.get("status","unknown"))
def main():
    check_proofs()
    for system, env in SOURCES.items():
        dsn=os.environ.get(env)
        if not dsn:
            flag(system,"DATABASE_CONNECTION_NOT_CONFIGURED","P0",note="Set encrypted GitHub Actions secret "+env); continue
        try:
            with psycopg.connect(dsn,connect_timeout=10,options="-c default_transaction_read_only=on") as conn:
                {"sentinel":check_sentinel,"dispatch":check_dispatch,"clientflow":check_clientflow}.get(system,lambda c:check_generic(c,system))(conn)
        except Exception as exc:
            flag(system,"AUDIT_CONNECTION_OR_QUERY_FAILED","P0",note=exc.__class__.__name__)
    report={"checked_at":datetime.now(timezone.utc).isoformat(),"mode":"read_only","sources":list(SOURCES),"findings":FINDINGS,
            "counts":{"P0":sum(f["severity"]=="P0" for f in FINDINGS),"P1":sum(f["severity"]=="P1" for f in FINDINGS)}}
    out=Path(os.environ.get("SSAG_AUDIT_OUTPUT","ssag-gap-audit.json"))
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report["counts"]))
    return 1 if report["counts"]["P0"] else 0
if __name__=="__main__": sys.exit(main())
