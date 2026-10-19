// Cetak deck HTML ke PDF 13,333 x 7,5 inci (satu slide satu halaman).
// Butuh puppeteer-core dan Chromium yang bisa dijalankan di sandbox ini.
//   NODE_PATH=<node_modules> node tools/print_pdf.js
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
  await page.goto('file://' + path.join(root, 'ssc-pedodonsia.html'), { waitUntil: 'networkidle0' });
  await page.emulateMediaType('print');
  await page.pdf({
    path: path.join(root, 'ssc-pedodonsia.pdf'),
    width: '13.333in',
    height: '7.5in',
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });
  await browser.close();
  console.log('pdf written');
})();
