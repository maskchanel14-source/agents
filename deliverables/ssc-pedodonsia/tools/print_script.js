// Cetak naskah-presentasi.html ke PDF A4.
// Butuh puppeteer-core dan Chromium yang bisa dijalankan di sandbox ini.
//   NODE_PATH=<node_modules> node tools/print_script.js
const puppeteer = require('puppeteer-core');
const path = require('path');

const CHROME = process.env.CHROME_PATH || '/tmp/chromium';
const LIB = process.env.CHROME_LIBS || '/tmp/shot/al/lib';
const FONTS = process.env.FONTCONFIG_FILE || '/tmp/shot/fonts.conf';

(async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--font-render-hinting=none'],
    env: { ...process.env, LD_LIBRARY_PATH: LIB, FONTCONFIG_FILE: FONTS },
  });
  const page = await browser.newPage();
  await page.goto('file://' + path.join(root, 'naskah-presentasi.html'), { waitUntil: 'networkidle0' });
  await page.emulateMediaType('print');
  await page.pdf({
    path: path.join(root, 'naskah-presentasi.pdf'),
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="width:100%;font-family:Inter,Arial,sans-serif;font-size:8pt;color:#8b999b;padding:0 18mm;display:flex;justify-content:space-between;"><span>Naskah presentasi SSC · Galeka Ali Prasetya</span><span class="pageNumber"></span></div>',
    margin: { top: '20mm', right: '18mm', bottom: '16mm', left: '18mm' },
  });
  await browser.close();
  console.log('pdf naskah written');
})();
