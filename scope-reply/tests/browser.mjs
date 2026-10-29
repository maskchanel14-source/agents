import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { createServer } from 'vite';
import { chromium as playwright } from 'playwright-core';
import chromium from '@sparticuz/chromium';
import AxeBuilder from '@axe-core/playwright';

process.env.VITE_LEAD_ENDPOINT = '/api/test-interest';
const server = await createServer({ server: { host: '0.0.0.0', port: 5179, strictPort: true }, clearScreen: false });
await server.listen();
let browser;
try {
  const executablePath = await chromium.executablePath();
  // The bundled Chromium supports Lambda; also extract its NSS/NSPR bundle on Debian.
  const { createRequire } = await import('node:module');
  const { dirname, join } = await import('node:path');
  const { pathToFileURL } = await import('node:url');
  const packageDir = dirname(createRequire(import.meta.url).resolve('@sparticuz/chromium'));
  const { inflate } = await import(pathToFileURL(join(packageDir, 'lambdafs.js')).href);
  const { setupLambdaEnvironment } = await import(pathToFileURL(join(packageDir, 'helper.js')).href);
  const lib = await inflate(join(packageDir, '../bin/al2023.tar.br'));
  setupLambdaEnvironment(`${lib}/lib`);
  browser = await playwright.launch({ executablePath, args: chromium.args, headless: true, env: { ...process.env } });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  let requests = 0;
  let mode = 'success';
  await page.route('**/api/test-interest', async (route) => {
    requests++;
    const body = route.request().postDataJSON();
    assert.equal(body.price, 1900);
    assert.equal(body.consent, true);
    assert.equal(body.segment, 'solo');
    assert.equal(body.email, 'browser-test@example.com');
    await route.fulfill({ status: mode === 'success' ? 201 : 503, contentType: 'application/json', body: JSON.stringify(mode === 'success' ? { saved: true, payment: false } : { error: 'service_unavailable' }) });
  });
  await page.goto('http://127.0.0.1:5179', { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  assert.match(await page.title(), /ScopeReply/);
  assert.match(await page.locator('body').innerText(), /NOT YET FOR SALE/);
  await page.getByRole('button', { name: 'Swap scope' }).click();
  assert.equal(await page.locator('#example-price').innerText(), '$0');
  await page.getByRole('button', { name: 'Phase two' }).click();
  assert.equal(await page.locator('#example-price').innerText(), '$0 now');
  await page.getByRole('button', { name: 'Add it' }).click();
  await page.locator('#email').fill('browser-test@example.com');
  await page.locator('[name=consent]').check();
  await page.evaluate(() => { const form = document.querySelector('form'); form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); });
  await page.getByText('Your $19 interest is saved.', { exact: false }).waitFor();
  assert.equal(requests, 1, 'double submit must not duplicate the request');
  assert.match(await page.locator('#form-status').innerText(), /No payment was taken/);
  await page.reload({ waitUntil: 'networkidle' });
  mode = 'failure';
  await page.locator('#email').fill('browser-test@example.com');
  await page.locator('[name=consent]').check();
  await page.getByRole('button', { name: 'Register my $19 interest' }).click();
  await page.getByText('We could not save your interest.', { exact: false }).waitFor();
  assert.equal(await page.locator('button[type=submit]').isEnabled(), true);
  await page.getByText('Can I buy it now?').click();
  assert.equal(await page.locator('details').first().getAttribute('open'), '');
  await mkdir('test-results', { recursive: true });
  for (const width of [320, 375, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.reload({ waitUntil: 'networkidle' });
    const dimensions = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
    assert.ok(dimensions.scroll <= dimensions.client, `horizontal overflow at ${width}: ${JSON.stringify(dimensions)}`);
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
    assert.deepEqual(results.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })), [], `accessibility violations at ${width}`);
    if (width === 1440 || width === 375) {
      await page.evaluate(() => { if (document.activeElement instanceof HTMLElement) document.activeElement.blur(); window.scrollTo(0, 0); });
      await page.screenshot({ path: `test-results/${width}.png`, fullPage: true });
    }
  }
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(() => document.activeElement !== document.body));
  assert.deepEqual(errors, []);
  console.log('PASS: desktop/mobile overflow, axe WCAG A/AA, sample choices, consent payload, duplicate-submit guard, success/failure states, FAQ and keyboard. All submissions mocked; no live prospects created.');
} finally {
  await browser?.close();
  await server.close();
}
