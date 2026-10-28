// Public write-only endpoint. No public read access, email list, or payment API.
// Authentication is intentionally disabled; exact-origin CORS, strict schema,
// a honeypot, hashed-IP rate limiting and a private-schema RPC guard writes.
const allowed = (Deno.env.get('SCOPEREPLY_ALLOWED_ORIGINS') ?? '').split(',').map((s) => s.trim()).filter(Boolean);
const json = (body: unknown, status: number, headers: Record<string, string>) => new Response(JSON.stringify(body), { status, headers: { ...headers, 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' } });

async function requestHash(value: string, secret: string) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const result = await crypto.subtle.sign('HMAC', key, encoder.encode(value));
  return Array.from(new Uint8Array(result), (v) => v.toString(16).padStart(2, '0')).join('');
}

Deno.serve(async (req: Request) => {
  const origin = req.headers.get('origin') ?? '';
  const headers: Record<string, string> = { Vary: 'Origin' };
  if (allowed.includes(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS';
    headers['Access-Control-Allow-Headers'] = 'Content-Type';
    headers['Access-Control-Max-Age'] = '600';
  }
  if (req.method === 'OPTIONS') {
    if (!allowed.includes(origin)) return json({ error: 'origin_not_allowed' }, 403, headers);
    return new Response(null, { status: 204, headers });
  }
  if (req.method !== 'POST') return json({ error: 'method_not_allowed' }, 405, { ...headers, Allow: 'POST, OPTIONS' });
  if (!allowed.includes(origin)) return json({ error: 'origin_not_allowed' }, 403, headers);
  if (!req.headers.get('content-type')?.toLowerCase().startsWith('application/json')) return json({ error: 'invalid_input' }, 400, headers);
  const url = Deno.env.get('SUPABASE_URL');
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!url || !key) return json({ error: 'service_unavailable' }, 503, headers);
  try {
    const text = await req.text();
    if (text.length > 2048) return json({ error: 'invalid_input' }, 400, headers);
    const body = JSON.parse(text);
    if (!body || typeof body !== 'object' || Array.isArray(body)) return json({ error: 'invalid_input' }, 400, headers);
    if (typeof body.website === 'string' && body.website.length > 0) return json({ saved: true, payment: false }, 200, headers);
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
    if (email.length < 5 || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !['solo', 'studio'].includes(body.segment) || body.consent !== true || body.price !== 1900) return json({ error: 'invalid_input' }, 400, headers);
    // This header is supplied by the hosting proxy. Do not accept a client IP field.
    const ip = req.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
    const bucket = await requestHash(`scopereply:${ip}`, key);
    const result = await fetch(`${url}/rest/v1/rpc/scopereply_capture`, {
      method: 'POST', headers: { apikey: key, Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_email: email, p_segment: body.segment, p_consent: true, p_price: 1900, p_ip_hash: bucket }),
      signal: AbortSignal.timeout(10000),
    });
    if (!result.ok) {
      // Never log request bodies, emails, authorization headers or raw SQL errors.
      const detail = await result.text();
      if (detail.includes('rate_limited')) return json({ error: 'rate_limited' }, 429, { ...headers, 'Retry-After': '3600' });
      if (detail.includes('experiment_closed')) return json({ error: 'experiment_closed' }, 410, headers);
      if (detail.includes('invalid_input')) return json({ error: 'invalid_input' }, 400, headers);
      console.error('scopereply persistence failed', result.status);
      return json({ error: 'service_unavailable' }, 503, headers);
    }
    return json({ saved: true, payment: false }, 201, headers);
  } catch {
    return json({ error: 'service_unavailable' }, 503, headers);
  }
});
