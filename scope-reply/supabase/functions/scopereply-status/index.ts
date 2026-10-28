// Aggregate-only status. No email addresses, IP hashes, or prospect rows.
Deno.serve(async (request) => {
  const headers = { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' };
  if (request.method !== 'GET') return Response.json({ error: 'method_not_allowed' }, { status: 405, headers: { ...headers, Allow: 'GET' } });
  const url = Deno.env.get('SUPABASE_URL');
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!url || !key) return Response.json({ error: 'status_unavailable' }, { status: 503, headers });
  try {
    const result = await fetch(`${url}/rest/v1/rpc/scopereply_snapshot`, { method: 'POST', headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: '{}', signal: AbortSignal.timeout(10000) });
    if (!result.ok) return Response.json({ error: 'status_unavailable' }, { status: 503, headers });
    return new Response(await result.text(), { headers: { ...headers, 'Content-Type': 'application/json' } });
  } catch { return Response.json({ error: 'status_unavailable' }, { status: 503, headers }); }
});
