import { describe, expect, it } from 'vitest';
import { exampleFor, parseInterest } from '../src/validation';

describe('explicit price commitment', () => {
  it('normalizes valid consent', () => { expect(parseInterest({ email: ' Buyer@Example.COM ', segment: 'solo', consent: true })).toEqual({ ok: true, value: { email: 'buyer@example.com', segment: 'solo', consent: true } }); });
  it.each([null, [], {}, { email: 'no', segment: 'solo', consent: true }, { email: 'a@b.co', segment: 'agency', consent: true }, { email: 'a@b.co', segment: 'solo', consent: false }, { email: 'a@b.co', segment: 'solo', consent: 'true' }, { email: 42, segment: 'solo', consent: true }])('rejects invalid input %j', (input) => { expect(parseInterest(input).ok).toBe(false); });
  it('rejects overlong emails', () => { expect(parseInterest({ email: `${'a'.repeat(250)}@b.co`, segment: 'studio', consent: true }).ok).toBe(false); });
});
describe('fictional sample', () => {
  it('keeps scope swaps and phase two distinct from added fees', () => { expect(exampleFor('add').price).toBe('$240'); expect(exampleFor('swap').price).toBe('$0'); expect(exampleFor('later').price).toBe('$0 now'); });
});
