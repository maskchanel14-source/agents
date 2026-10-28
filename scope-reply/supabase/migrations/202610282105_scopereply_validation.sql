-- Applied to project po-pilot-leads through the Supabase connector.
-- Namespaced private schema; does not modify existing PO-PILOT tables.
CREATE SCHEMA IF NOT EXISTS studio;
REVOKE ALL ON SCHEMA studio FROM PUBLIC, anon, authenticated;
CREATE TABLE studio.experiments (
 id text PRIMARY KEY, product text NOT NULL, buyer text NOT NULL, channel text NOT NULL,
 price_cents integer NOT NULL CHECK (price_cents BETWEEN 900 AND 2900),
 status text NOT NULL CHECK (status IN ('validating','killed','validated')),
 created_at timestamptz NOT NULL DEFAULT now(), hard_stop_at timestamptz NOT NULL,
 outreach_started_at timestamptz, collected_cents integer NOT NULL DEFAULT 0 CHECK (collected_cents >= 0),
 paid_customers integer NOT NULL DEFAULT 0 CHECK (paid_customers >= 0), skill_used text NOT NULL, decision text NOT NULL
);
CREATE TABLE studio.commitments (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), experiment_id text NOT NULL REFERENCES studio.experiments(id),
 email text NOT NULL CHECK (length(email) BETWEEN 5 AND 254 AND email = lower(email)),
 buyer_segment text NOT NULL CHECK (buyer_segment IN ('solo','studio')),
 price_cents integer NOT NULL CHECK (price_cents=1900), consent_version text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(experiment_id,email)
);
CREATE TABLE studio.request_limits (bucket text PRIMARY KEY, attempts integer NOT NULL, window_start timestamptz NOT NULL);
CREATE TABLE studio.checkpoints (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, experiment_id text NOT NULL REFERENCES studio.experiments(id),
 created_at timestamptz NOT NULL DEFAULT now(), product text NOT NULL, buyer text NOT NULL, channel text NOT NULL,
 commitments integer NOT NULL, paid_customers integer NOT NULL, collected_cents integer NOT NULL, skill_used text NOT NULL, decision text NOT NULL
);
ALTER TABLE studio.experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio.commitments ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio.request_limits ENABLE ROW LEVEL SECURITY;
ALTER TABLE studio.checkpoints ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON ALL TABLES IN SCHEMA studio FROM PUBLIC, anon, authenticated;
CREATE FUNCTION studio.capture_commitment(p_email text, p_segment text, p_consent boolean, p_price integer, p_ip_hash text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
 IF p_consent IS DISTINCT FROM true OR p_price IS DISTINCT FROM 1900 OR p_segment NOT IN ('solo','studio') OR p_email IS NULL OR length(p_email)>254 OR p_email !~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$' OR p_ip_hash IS NULL OR length(p_ip_hash)>128 THEN RAISE EXCEPTION 'invalid_input'; END IF;
 IF NOT EXISTS (SELECT 1 FROM studio.experiments WHERE id='scopereply-001' AND status='validating' AND hard_stop_at>now()) THEN RAISE EXCEPTION 'experiment_closed'; END IF;
 INSERT INTO studio.request_limits(bucket,attempts,window_start) VALUES (p_ip_hash,1,now())
 ON CONFLICT (bucket) DO UPDATE SET
 attempts=CASE WHEN studio.request_limits.window_start<now()-interval '1 hour' THEN 1 ELSE studio.request_limits.attempts+1 END,
 window_start=CASE WHEN studio.request_limits.window_start<now()-interval '1 hour' THEN now() ELSE studio.request_limits.window_start END;
 IF (SELECT attempts FROM studio.request_limits WHERE bucket=p_ip_hash)>5 THEN RAISE EXCEPTION 'rate_limited'; END IF;
 INSERT INTO studio.commitments(experiment_id,email,buyer_segment,price_cents,consent_version)
 VALUES ('scopereply-001',lower(trim(p_email)),p_segment,1900,'scopereply-19-v1') ON CONFLICT (experiment_id,email) DO NOTHING;
 RETURN jsonb_build_object('saved',true,'payment',false);
END $$;
CREATE FUNCTION studio.checkpoint() RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
 UPDATE studio.experiments e SET status='killed', decision='Killed: fewer than three qualified commitments before the 48-hour hard stop. If outreach never started, this is a distribution failure, not evidence of customer rejection.'
 WHERE e.status='validating' AND e.hard_stop_at<=now() AND (SELECT count(*) FROM studio.commitments c WHERE c.experiment_id=e.id)<3;
 INSERT INTO studio.checkpoints(experiment_id,product,buyer,channel,commitments,paid_customers,collected_cents,skill_used,decision)
 SELECT e.id,e.product,e.buyer,e.channel,(SELECT count(*) FROM studio.commitments c WHERE c.experiment_id=e.id),e.paid_customers,e.collected_cents,e.skill_used,e.decision FROM studio.experiments e;
 DELETE FROM studio.commitments WHERE created_at<now()-interval '60 days';
 DELETE FROM studio.request_limits WHERE window_start<now()-interval '2 days';
END $$;
REVOKE ALL ON FUNCTION studio.capture_commitment(text,text,boolean,integer,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION studio.checkpoint() FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA studio TO service_role;
GRANT EXECUTE ON FUNCTION studio.capture_commitment(text,text,boolean,integer,text) TO service_role;
GRANT EXECUTE ON FUNCTION studio.checkpoint() TO service_role;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA studio TO service_role;
GRANT USAGE, SELECT ON SEQUENCE studio.checkpoints_id_seq TO service_role;
INSERT INTO studio.experiments(id,product,buyer,channel,price_cents,status,created_at,hard_stop_at,skill_used,decision)
VALUES ('scopereply-001','ScopeReply','Solo web designers and two-person studios with fixed-fee projects','Reddit r/web_design only',1900,'validating','2026-10-28 21:05:00+00','2026-10-30 21:05:00+00','before-you-build; competitive-landscape; api-design-principles','Pre-MVP validation. Outreach not started; checkout unavailable. Zero payments. No customer demand inferred from research.');
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('scopereply-three-hour-log','5 */3 * * *','SELECT studio.checkpoint()');
SELECT studio.checkpoint();
