export type Choice = 'add' | 'swap' | 'later';
export type Interest = { email: string; segment: 'solo' | 'studio'; consent: true };
export function exampleFor(choice: Choice): { price: string; time: string } {
  return { add: { price: '$240', time: '+2 business days' }, swap: { price: '$0', time: 'No change' }, later: { price: '$0 now', time: 'No change' } }[choice];
}
export function parseInterest(raw: unknown): { ok: true; value: Interest } | { ok: false; error: string } {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return { ok: false, error: 'Please complete the form.' };
  const data = raw as Record<string, unknown>;
  const email = typeof data.email === 'string' ? data.email.trim().toLowerCase() : '';
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { ok: false, error: 'Enter a valid email address.' };
  if (data.segment !== 'solo' && data.segment !== 'studio') return { ok: false, error: 'Choose the buyer type that fits you.' };
  if (data.consent !== true) return { ok: false, error: 'Please confirm that you would pay $19 for this offer.' };
  return { ok: true, value: { email, segment: data.segment, consent: true } };
}
