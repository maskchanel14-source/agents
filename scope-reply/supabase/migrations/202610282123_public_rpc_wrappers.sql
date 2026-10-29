-- PostgREST exposes the public schema, not the private studio schema.
-- These fixed-purpose wrappers remain executable ONLY by service_role.
CREATE FUNCTION public.scopereply_capture(p_email text,p_segment text,p_consent boolean,p_price integer,p_ip_hash text)
RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path='' AS $$ SELECT studio.capture_commitment(p_email,p_segment,p_consent,p_price,p_ip_hash) $$;
CREATE FUNCTION public.scopereply_snapshot() RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path='' AS $$ SELECT studio.public_snapshot('scopereply-001') $$;
REVOKE ALL ON FUNCTION public.scopereply_capture(text,text,boolean,integer,text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.scopereply_snapshot() FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.scopereply_capture(text,text,boolean,integer,text) TO service_role;
GRANT EXECUTE ON FUNCTION public.scopereply_snapshot() TO service_role;
