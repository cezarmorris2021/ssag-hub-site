-- Neon schema created November 2, 2026
CREATE TABLE IF NOT EXISTS venture_orders (
 id uuid PRIMARY KEY,
 venture text NOT NULL CHECK(venture IN ('bidkit','staydesk')),
 name varchar(120) NOT NULL,
 email varchar(254) NOT NULL,
 phone varchar(40),
 package_id varchar(60) NOT NULL,
 budget_cents integer NOT NULL,
 details jsonb NOT NULL DEFAULT '{}'::jsonb,
 status varchar(30) NOT NULL DEFAULT 'new',
 payment_status varchar(30) NOT NULL DEFAULT 'unpaid',
 payment_provider varchar(30),
 payment_reference varchar(255),
 notes text NOT NULL DEFAULT '',
 is_test boolean NOT NULL DEFAULT false,
 consent boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT NOW(),
 updated_at timestamptz NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS venture_orders_venture_created_idx ON venture_orders(venture,created_at DESC);
CREATE TABLE IF NOT EXISTS venture_requests(fingerprint char(64) NOT NULL,venture varchar(20) NOT NULL,created_at timestamptz NOT NULL DEFAULT NOW());
CREATE INDEX IF NOT EXISTS venture_requests_lookup_idx ON venture_requests(fingerprint,venture,created_at DESC);
CREATE TABLE IF NOT EXISTS venture_audit(id bigint generated always as identity PRIMARY KEY,venture text NOT NULL,order_id uuid,action text NOT NULL,actor text NOT NULL DEFAULT 'system',description jsonb NOT NULL DEFAULT '{}'::jsonb,created_at timestamptz NOT NULL DEFAULT NOW());
