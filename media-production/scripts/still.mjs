#!/usr/bin/env node
/**
 * Render a single still from SHORTS-2026-024-Binance63B.
 *
 *   node scripts/still.mjs --out stills/shot1.png --prompt "wide shot of town"
 *   node scripts/still.mjs --out stills/shot6.png --shot 6
 *   node scripts/still.mjs --out stills/frame0600.png --frame 600
 *
 * `--prompt` is a convenience: keywords are matched against the shot list in
 * src/story.ts, so you can ask for a frame the way you'd describe it. Use
 * `--frame` when you need an exact frame.
 */
import {execFileSync} from 'node:child_process';
import {existsSync, mkdirSync} from 'node:fs';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const STUDIO = resolve(HERE, '..');
const PROJECT = resolve(STUDIO, '..', 'projects', 'SHORTS-2026-024-Binance-63B');
const COMPOSITION = 'SHORTS-2026-024-Binance63B';

/** frame = middle of each shot (see src/story.ts). */
const SHOT_FRAMES = [100, 327, 580, 807, 985, 1230, 1465, 1607, 1847];

const PROMPT_HINTS = [
  [/\bwide|establish|town|skyline|hook\b/i, 1],
  [/\bclock|tower|20:05|october|date\b/i, 2],
  [/\bblockchain|bridge|ten|hot wallet|vault\b/i, 3],
  [/\bbitcoin|btc|18,?270|coin\b/i, 4],
  [/\bfreeze|frozen|tether|circle|ice\b/i, 5],
  [/\binterview|engineer|window|laptop|devops|ceo\b/i, 6],
  [/\bpush|close|screen|takeover|system\b/i, 7],
  [/\brefund|paid|treasury|refill|payback\b/i, 8],
  [/\bfinal|last|record|largest|fbi|korea|bar\b/i, 9],
];

const argv = process.argv.slice(2);
const get = (name) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : null;
};

const out = get('out');
const prompt = get('prompt');
const shotArg = get('shot');
const frameArg = get('frame');

if (!out) {
  console.error('usage: node scripts/still.mjs --out <file.png> [--prompt "..."] [--shot N] [--frame N]');
  process.exit(1);
}

let frame;
let why;
if (frameArg !== null) {
  frame = Number(frameArg);
  why = `--frame ${frameArg}`;
} else if (shotArg !== null) {
  const n = Number(shotArg);
  if (!Number.isInteger(n) || n < 1 || n > SHOT_FRAMES.length) {
    console.error(`--shot must be 1..${SHOT_FRAMES.length}`);
    process.exit(1);
  }
  frame = SHOT_FRAMES[n - 1];
  why = `shot ${n} (mid-shot frame ${frame})`;
} else if (prompt) {
  const hit = PROMPT_HINTS.find(([re]) => re.test(prompt));
  if (!hit) {
    console.error(`could not map prompt "${prompt}" to a shot. Known frames: ${SHOT_FRAMES.join(', ')}`);
    process.exit(1);
  }
  frame = SHOT_FRAMES[hit[1] - 1];
  why = `prompt "${prompt}" -> shot ${hit[1]} (frame ${frame})`;
} else {
  frame = SHOT_FRAMES[0];
  why = `default shot 1 (frame ${frame})`;
}

const target = resolve(process.cwd(), out);
mkdirSync(dirname(target), {recursive: true});

const env = {
  ...process.env,
  LD_LIBRARY_PATH: ['/tmp/al2023/lib', process.env.LD_LIBRARY_PATH].filter(Boolean).join(':'),
  PATH: [
    resolve(STUDIO, 'node_modules', '@ffmpeg-installer', 'linux-x64'),
    process.env.PATH,
  ].join(':'),
};

// Remotion cannot download Chrome here; remotion-env.sh unpacks the npm-shipped
// binary and exports REMOTION_BROWSER_EXECUTABLE. Reuse it when it is present.
const browser = existsSync('/tmp/chromium') ? ['--browser-executable=/tmp/chromium'] : [];

console.log(`[still] ${why}\n[still] -> ${target}`);
execFileSync(
  'npx',
  ['remotion', 'still', 'src/index.ts', COMPOSITION, target,
    `--frame=${frame}`, ...browser, '--gl=swangle'],
  {cwd: STUDIO, env, stdio: 'inherit'},
);
console.log(`[still] done. project root: ${PROJECT}`);
