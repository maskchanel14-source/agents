import { parseInterest, type Choice } from './validation';

const samples = {
  add: { price: '$240', label: 'ADDITIONAL FEE', time: '+2 business days', email: 'Thanks for the FAQ idea. It sits outside our agreed five-page scope. I can add it for $240 and two business days, swap it for the resources section, or keep it for phase two. Let me know which works best.' },
  swap: { price: '$0', label: 'SCOPE SWAP · SAME FEE', time: 'No change', email: 'Happy to include the editable FAQ. To keep the original fee and delivery date, we would replace the resources section with it. Please confirm that swap before I update the project plan.' },
  later: { price: '$0 now', label: 'CURRENT PROJECT · UNCHANGED', time: 'No change', email: 'The FAQ is a useful addition, but it is outside the current scope. Let’s finish the agreed five pages first and estimate the FAQ as a separate phase. This keeps the current budget and delivery date intact.' },
} satisfies Record<Choice, { price: string; label: string; time: string; email: string }>;

for (const button of document.querySelectorAll<HTMLButtonElement>('[data-choice]')) {
  button.addEventListener('click', () => {
    const key = button.dataset.choice as Choice;
    if (!Object.hasOwn(samples, key)) return;
    const sample = samples[key];
    for (const other of document.querySelectorAll<HTMLButtonElement>('[data-choice]')) {
      const selected = other === button;
      other.classList.toggle('selected', selected);
      other.setAttribute('aria-pressed', String(selected));
    }
    document.querySelector('#price-label')!.textContent = sample.label;
    document.querySelector('#example-price')!.textContent = sample.price;
    document.querySelector('#example-time')!.textContent = sample.time;
    document.querySelector('#example-email')!.textContent = sample.email;
  });
}

const form = document.querySelector<HTMLFormElement>('#interest-form')!;
const status = document.querySelector<HTMLParagraphElement>('#form-status')!;
const submit = form.querySelector<HTMLButtonElement>('button[type=submit]')!;
const endpoint = import.meta.env.VITE_LEAD_ENDPOINT as string | undefined;

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submit.disabled) return;
  status.className = '';
  const data = new FormData(form);
  if (data.get('website')) return;
  const parsed = parseInterest({ email: data.get('email'), segment: data.get('segment'), consent: data.get('consent') === 'on' });
  if (!parsed.ok) { status.textContent = parsed.error; status.className = 'error'; return; }
  if (!endpoint) { status.textContent = 'The interest service is not connected. No information was saved. Please try again later.'; status.className = 'error'; return; }
  submit.disabled = true;
  submit.textContent = 'Saving your interest…';
  status.textContent = '';
  try {
    const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...parsed.value, price: 1900, website: '' }), signal: AbortSignal.timeout(15000) });
    const result = await response.json();
    if (!response.ok || result.saved !== true) {
      const errors: Record<string, string> = { rate_limited: 'Too many attempts. Please try again in an hour.', experiment_closed: 'This validation window has closed. No new interest was recorded.', invalid_input: 'Please check your email and the $19 interest checkbox.', service_unavailable: 'We could not save your interest. Nothing was charged. Please try again later.' };
      throw new Error(errors[result.error] ?? errors.service_unavailable);
    }
    status.textContent = 'Your $19 interest is saved. No payment was taken and no order was placed. We will email you only if this offer opens for purchase. Thank you for an honest signal.';
    status.className = 'success';
    submit.textContent = 'Interest saved ✓';
    form.reset();
  } catch (error) {
    status.textContent = error instanceof Error && !['Failed to fetch', 'Load failed', 'TimeoutError', 'NetworkError'].includes(error.name) ? error.message : 'Connection failed. Your interest has not been confirmed. Please try again; no payment was taken.';
    status.className = 'error';
    submit.disabled = false;
    submit.textContent = 'Register my $19 interest →';
  }
});
