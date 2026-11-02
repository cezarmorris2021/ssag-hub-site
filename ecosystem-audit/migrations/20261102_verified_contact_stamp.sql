-- Sentinel Zero production schema: verified contact evidence stamping.
-- Installed in Neon on 2026-11-02; keep this idempotent definition in source control.
-- Apply only after schema review. Never backfill contact stamps without real evidence.
CREATE OR REPLACE FUNCTION public.ssag_stamp_verified_lead_contact()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.lead_id IS NOT NULL
       AND lower(coalesce(NEW.outcome, '')) IN
           ('connected', 'answered', 'conversation', 'appointment_booked', 'booked')
       AND NEW.started_at IS NOT NULL
       AND NEW.started_at <= now() + interval '5 minutes'
       AND NOT EXISTS (
           SELECT 1 FROM public.ai_call_sessions s
           WHERE s.id = NEW.ai_session_id
             AND lower(coalesce(s.transport, '')) IN ('simulation', 'mock', 'test')
       )
    THEN
        UPDATE public.leads l
        SET last_contact_at = greatest(coalesce(l.last_contact_at, NEW.started_at), NEW.started_at),
            updated_at = now()
        WHERE l.id = NEW.lead_id
          AND l.organization_id = NEW.organization_id
          AND (l.last_contact_at IS NULL OR l.last_contact_at < NEW.started_at);
    END IF;
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'ssag_verified_contact_stamp'
          AND tgrelid = 'public.call_attempts'::regclass
    ) THEN
        CREATE TRIGGER ssag_verified_contact_stamp
        AFTER INSERT OR UPDATE OF outcome, started_at ON public.call_attempts
        FOR EACH ROW EXECUTE FUNCTION public.ssag_stamp_verified_lead_contact();
    END IF;
END;
$$;
