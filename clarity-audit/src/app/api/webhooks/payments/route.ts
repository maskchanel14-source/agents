import { NextRequest, NextResponse } from "next/server";
import { createHmac, timingSafeEqual } from "node:crypto";
import { persistToSupabase } from "@/lib/store";

// Payment webhook — FAILS CLOSED until the human connects a provider.
// To activate (human, ~15 min):
//   1. Create products in Lemon Squeezy (recommended) or Stripe.
//   2. Set PAYMENT_WEBHOOK_SECRET + PAYMENT_PROVIDER=lemonsqueezy|stripe env vars.
//   3. Point the provider webhook at /api/webhooks/payments.
//   4. Set checkout URLs in src/lib/site.ts offers and flip paymentsConnected.
// Security: HMAC signature verification (Lemon Squeezy: X-Signature sha256;
// Stripe uses its own scheme — swap verify() per provider docs), constant-time
// compare, idempotency via payments.provider_event_id UNIQUE in Postgres.
// Fulfillment on verified paid events: order recorded; report generation is
// triggered from the buyer's scan via /api/report + delivery email (provider).

function verify(raw: string, signature: string | null, secret: string): boolean {
  if (!signature) return false;
  const expected = createHmac("sha256", secret).update(raw).digest("hex");
  const a = Buffer.from(expected);
  const b = Buffer.from(signature.replace(/^sha256=/, ""));
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function POST(req: NextRequest) {
  const secret = process.env.PAYMENT_WEBHOOK_SECRET;
  if (!secret) {
    // Not configured: refuse loudly rather than accept unverifiable events.
    return NextResponse.json({ error: "not_configured", message: "Payments are not connected yet." }, { status: 503 });
  }
  const raw = await req.text();
  const sig = req.headers.get("x-signature") || req.headers.get("stripe-signature");
  if (!verify(raw, sig, secret)) {
    return NextResponse.json({ error: "bad_signature" }, { status: 401 });
  }
  let event: Record<string, unknown>;
  try { event = JSON.parse(raw); } catch { return NextResponse.json({ error: "bad_json" }, { status: 400 }); }

  const eventId = String((event as { id?: string }).id ?? (event as { meta?: { event_id?: string } }).meta?.event_id ?? "");
  const eventType = String((event as { type?: string }).type ?? (event as { meta?: { event_name?: string } }).meta?.event_name ?? "unknown");
  if (!eventId) return NextResponse.json({ error: "missing_event_id" }, { status: 400 });

  // Idempotent record (DB unique constraint dedupes retries).
  await persistToSupabase("payments", { provider_event_id: eventId, event_type: eventType, raw: event });

  const isPaid = /order_created|payment_succeeded|checkout\.session\.completed|order\.paid/i.test(eventType);
  if (isPaid) {
    // TODO on provider activation: extract buyer email/plan/scan_id from the
    // provider payload (custom checkout data), create the orders row, generate
    // the paid report from the scan, and send the delivery email via the
    // configured email provider. Kept explicit rather than guessed per-provider.
    await persistToSupabase("audit_logs", { actor: "webhook", action: "paid_event_received", entity: "payments", entity_id: eventId, meta: { eventType } });
  }
  return NextResponse.json({ received: true });
}
