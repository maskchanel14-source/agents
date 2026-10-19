// Render assets/art/fig-*.svg menjadi PNG (2x) untuk dipakai di deck.
// Foto di-inline sebagai data URI supaya resolusi path tidak bergantung cwd.
// Butuh @resvg/resvg-js: npm i @resvg/resvg-js (di luar repo) lalu jalankan
//   NODE_PATH=<node_modules> node tools/render_svg.js 2
const { Resvg } = require('@resvg/resvg-js');
const fs = require('fs'), path = require('path');
const dir = path.resolve(__dirname, '..', 'assets', 'art');
const scale = Number(process.argv[2] || 2);
const fonts = path.resolve(__dirname, 'fonts');

const files = fs.readdirSync(dir).filter(f => f.startsWith('fig-') && f.endsWith('.svg'));
for (const f of files) {
  let svg = fs.readFileSync(path.join(dir, f), 'utf8');
  svg = svg.replace(/href="(photo-[^"]+)"/g, (m, name) => {
    const p = path.join(dir, name);
    if (!fs.existsSync(p)) throw new Error('foto hilang: ' + p);
    const mime = name.endsWith('.jpg') ? 'jpeg' : 'png';
    return 'href="data:image/' + mime + ';base64,' + fs.readFileSync(p).toString('base64') + '"';
  });
  const r = new Resvg(svg, {
    fitTo: { mode: 'zoom', value: scale },
    font: {
      fontFiles: fs.readdirSync(fonts).filter(x => x.endsWith('.ttf')).map(x => path.join(fonts, x)),
      loadSystemFonts: false, defaultFontFamily: 'Inter',
    },
  });
  const png = r.render().asPng();
  fs.writeFileSync(path.join(dir, f.replace('.svg', '.png')), png);
  console.log('rendered', f, (png.length / 1024).toFixed(0) + 'KB');
}
