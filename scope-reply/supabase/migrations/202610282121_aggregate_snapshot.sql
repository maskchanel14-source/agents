-- Aggregate-only status for the scheduled LOG.md mirror. No prospect rows.
CREATE OR REPLACE FUNCTION studio.public_snapshot(p_experiment text) RETURNS jsonb
LANGUAGE sql STABLE SECURITY DEFINER SET search_path='' AS $$
 SELECT jsonb_build_object('product',e.product,'buyer',e.buyer,'channel',e.channel,'status',e.status,
 'commitments',(SELECT count(*) FROM studio.commitments c WHERE c.experiment_id=e.id),
 'paid_customers',e.paid_customers,'collected_cents',e.collected_cents,
 'outreach_started_at',e.outreach_started_at,'hard_stop_at',e.hard_stop_at,
 'decision',e.decision,'skill_used',e.skill_used,'snapshot_at',now())
 FROM studio.experiments e WHERE e.id=p_experiment
$$;
REVOKE ALL ON FUNCTION studio.public_snapshot(text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION studio.public_snapshot(text) TO service_role;
