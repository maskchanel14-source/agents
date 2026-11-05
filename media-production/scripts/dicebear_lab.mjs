#!/usr/bin/env node
/**
 * Builds the DiceBear "lab sheets" used to choose the host's parts by eye.
 *
 *   node scripts/dicebear_lab.mjs
 *
 * Writes public/_lab/*.svg — one contact sheet per component, every variant
 * labelled. Open the SVGs directly in a browser to pick parts by eye; pair it
 * with scripts/lab_cells.py to measure ink coverage, symmetry and bbox per
 * variant. Authoring aid only — nothing in public/_lab is shipped.
 *
 * The avatar style is Notionists (Zoish, CC0 1.0) via @dicebear/core (MIT).
 */
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const STUDIO = path.dirname(HERE);
const LAB = path.join(STUDIO, 'public', '_lab');

const require = createRequire(import.meta.url);
const {Avatar, Style} = require('@dicebear/core');
// the styles package does not export the raw JSON, so read it off disk
const def = JSON.parse(fs.readFileSync(path.join(
  STUDIO, 'node_modules', '@dicebear', 'styles', 'dist', 'notionists.min.json'), 'utf8'));



// paper (#ffffff) is recoloured per component; ink (#000000) stays ink.
const PAPER = {
  head: '#E8B58A',      // skin
  hair: '#6B4A30',      // hair
  clothes: '#35517F',   // blazer
  mouth: '#F6EDE2',     // teeth / tongue (paper inside an open mouth)
  nose: '#E8B58A',
  eyes: '#FDF7F0',
  glasses: '#C79A34',
  eyebrows: '#6B4A30',
  beard: '#6B4A30',
  gesture: '#E8B58A',
};
const INK = '#140F0B';
// components drawn as solid ink silhouettes (hair is a filled black shape, not
// an outline) get their ink tinted so they still read on the dark film backdrop
const INK_TINT = {hair: '#6B4A30'};

const style = new Style(def);

const colourOf = (fill) => {
  if (fill && typeof fill === 'object' && fill.type === 'color') {
    return fill.name === 'ink' ? '#000000' : '#ffffff';
  }
  return typeof fill === 'string' ? fill : '#000000';
};

function elementToSvg(el, paper, ink) {
  const a = el.attributes ?? {};
  const attrs = [];
  for (const [k, v] of Object.entries(a)) {
    if (k === 'fill') continue;
    attrs.push(`${k}="${v}"`);
  }
  const c = colourOf(a.fill);
  const fill = c === '#ffffff' ? paper : ink;
  attrs.push(`fill="${fill}"`);
  return `<${el.name} ${attrs.join(' ')}/>`;
}

/** One component variant on its own, in the component's own coordinate box. */
function componentSvg(comp, variant) {
  const c = def.components[comp];
  const v = c.variants[variant];
  const body = (v.elements ?? []).map(
    (e) => elementToSvg(e, PAPER[comp] ?? '#ffffff', INK_TINT[comp] ?? INK)).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${c.width}" height="${c.height}" `
    + `viewBox="0 0 ${c.width} ${c.height}" `
    + `fill="none" shape-rendering="auto">${body}</svg>`;
}

/** A whole avatar, recoloured per component. */
function avatarSvg(opts) {
  const svg = new Avatar(style, {seed: 'teacher', ...opts})
    .toString()
    .replace('<svg ', '<svg width="1744" height="1744" ');
  return svg.replace(/<g id="([a-zA-Z]+)-([a-zA-Z0-9]+)-[0-9a-f]+">([\s\S]*?)<\/g>/g,
    (m, comp, variant, inner) =>
      `<g id="${comp}-${variant}">${inner.replace(/#ffffff/g, PAPER[comp] ?? '#ffffff')
        .replace(/#000000/g, INK_TINT[comp] ?? INK)}</g>`)
    .replace(/(href="#)([a-zA-Z]+)-([a-zA-Z0-9]+)-[0-9a-f]+"/g, '$1$2-$3"');
}

const sheets = [];
let n = 0;
function write(body) {
  const f = `s${String(n++).padStart(3, '0')}.svg`;
  fs.writeFileSync(path.join(LAB, f), body);
  return f;
}

fs.rmSync(LAB, {recursive: true, force: true});
fs.mkdirSync(LAB, {recursive: true});

// --- sheet 0: full avatars, a few hair candidates ---------------------------
{
  const hairs = (process.env.HERO_HAIR ?? 'variant07,variant12,variant23,variant31')
    .split(',');
  const cells = hairs.map((h) => ({
    file: write(avatarSvg({
      hairVariant: [h], eyesVariant: ['variant01'], eyebrowsVariant: ['variant02'],
      noseVariant: ['variant03'], mouthVariant: ['variant11'], clothesVariant: ['variant07'],
      glassesProbability: 100, glassesVariant: ['variant02'],
      gestureProbability: 100, gestureVariant: ['hand'],
    })),
    label: h,
  }));
  sheets.push({name: 'avatars', cols: 2, rows: Math.ceil(cells.length / 2), cells});
}

// --- sheets 1..: one per component ------------------------------------------
const COMP_SHEETS = [
  ['hair', 8], ['mouth', 6], ['clothes', 5], ['eyes', 3],
  ['eyebrows', 5], ['nose', 5], ['glasses', 4], ['beard', 4], ['gesture', 4],
];
for (const [comp, cols] of COMP_SHEETS) {
  const variants = Object.keys(def.components[comp].variants);
  const cells = variants.map((v) => ({file: write(componentSvg(comp, v)), label: v}));
  sheets.push({name: comp, cols, rows: Math.ceil(cells.length / cols), cells});
}

console.log(`${n} svgs, ${sheets.length} sheets:`);
sheets.forEach((s, i) => console.log(`  ${i}  ${s.name.padEnd(10)} ${s.cols}x${s.rows} (${s.cells.length})`));
