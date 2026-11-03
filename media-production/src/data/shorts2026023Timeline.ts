import {captionsFromWords, createCaptionPages, type WordTiming} from 'remotion-captions-kit';

export const FPS = 30;
export const DURATION = 1230;
export const BPM = 120;
export const FRAMES_PER_BEAT = (FPS * 60) / BPM;

export type NarrationBeat = {
  id: string;
  start: number;
  end: number;
  text: string;
};

// These windows are derived from the exact sentence clips that make narration-v2.m4a.
// The clip sequence is cadence-normalized at render time, so captions follow each
// spoken sentence instead of using broad, static scene titles.
export const narrationBeats: NarrationBeat[] = [
  {id: 'hook', start: 0, end: 2.504, text: 'One mushroom may make people see tiny humans.'},
  {id: 'folklore', start: 2.504, end: 4.728, text: 'That sounds like folklore. It is not.'},
  {id: 'reports', start: 4.728, end: 10.024, text: 'Reports from southwest China and the northern Philippines describe miniature figures moving around real objects.'},
  {id: 'dna', start: 10.024, end: 15.877, text: 'In 2026, DNA linked those reported mushrooms to one species: Lanmaoa asiatica.'},
  {id: 'genome', start: 15.877, end: 21.452, text: 'Then researchers checked its genome. No canonical pathways for psilocybin or ibotenic acid appeared.'},
  {id: 'unknown', start: 21.452, end: 26.747, text: 'So the species has a name. The chemistry does not. The active compound is still unknown.'},
  {id: 'limit', start: 26.747, end: 30.088, text: 'That makes this a scientific lead, not a new drug discovery.'},
  {id: 'png', start: 30.088, end: 33.15, text: 'And reports from Papua New Guinea were not genetically verified.'},
  {id: 'safety', start: 33.15, end: 36.212, text: 'Do not test wild mushrooms. They can poison you.'},
  {id: 'payoff', start: 36.212, end: 40.112, text: 'The tiny people are the headline. The unknown molecule is the mystery.'},
];

const toWordTimings = (beat: NarrationBeat): WordTiming[] => {
  const words = beat.text.split(/\s+/).filter(Boolean);
  const lead = 0.035;
  const tail = 0.13;
  const usable = Math.max(0.2, beat.end - beat.start - lead - tail);
  const weight = (word: string) => Math.max(0.46, word.replace(/[^A-Za-z0-9]/g, '').length * 0.19 + (/[.!?:]/.test(word) ? 0.16 : 0));
  const totalWeight = words.reduce((total, word) => total + weight(word), 0);
  let cursor = beat.start + lead;

  return words.map((word) => {
    const length = usable * (weight(word) / totalWeight);
    const timing = {word, start: cursor, end: cursor + length};
    cursor += length;
    return timing;
  });
};

export const captionWords = narrationBeats.flatMap(toWordTimings);
const {captions} = captionsFromWords({words: captionWords});

// One or two short natural lines. Sentence stops and genuine pauses are honoured,
// avoiding the mid-thought page breaks that made the prior captions read like a bot.
export const captionPages = createCaptionPages({
  captions,
  maxDurationMs: 1150,
  maxCharsPerPage: 29,
  minDurationMs: 360,
  minWordsPerPage: 2,
  silenceGapMs: 330,
}).pages;

export const captionEmphasis = [
  {words: ['tiny', 'humans', 'folklore', 'China', 'Philippines', 'DNA', 'Lanmaoa', 'asiatica', 'genome', 'psilocybin', 'ibotenic', 'unknown', 'lead', 'Papua', 'Guinea', 'poison', 'molecule'], color: '#d8ff7e'},
];

export type EditorialShot = {
  from: number;
  duration: number;
  source: 'growth' | 'moss' | 'log';
  sourceStart: number;
  position: string;
  zoom: [number, number];
  drift: [number, number];
  direction: 'left' | 'right';
};

// Every cut falls on a 120-BPM half-bar or bar. The physical footage changes every
// 1.4–2 seconds; data/typography strikes provide additional beats within the shots.
export const editorialShots: EditorialShot[] = [
  {from: 0, duration: 42, source: 'moss', sourceStart: 24, position: '57% 48%', zoom: [1.24, 1.40], drift: [-56, -18], direction: 'right'},
  {from: 42, duration: 36, source: 'growth', sourceStart: 118, position: '53% 67%', zoom: [1.18, 1.36], drift: [44, -18], direction: 'left'},
  {from: 78, duration: 42, source: 'log', sourceStart: 16, position: '44% 51%', zoom: [1.18, 1.33], drift: [-42, 20], direction: 'right'},
  {from: 120, duration: 42, source: 'growth', sourceStart: 118, position: '53% 67%', zoom: [1.19, 1.36], drift: [56, -12], direction: 'left'},
  {from: 162, duration: 54, source: 'moss', sourceStart: 108, position: '46% 51%', zoom: [1.21, 1.39], drift: [-42, 22], direction: 'right'},
  {from: 216, duration: 54, source: 'log', sourceStart: 98, position: '55% 50%', zoom: [1.16, 1.34], drift: [48, -20], direction: 'left'},
  {from: 270, duration: 60, source: 'moss', sourceStart: 176, position: '54% 50%', zoom: [1.22, 1.42], drift: [36, 16], direction: 'left'},
  {from: 330, duration: 60, source: 'growth', sourceStart: 250, position: '46% 66%', zoom: [1.18, 1.36], drift: [-52, -22], direction: 'right'},
  {from: 390, duration: 60, source: 'log', sourceStart: 204, position: '48% 52%', zoom: [1.22, 1.40], drift: [-50, 14], direction: 'right'},
  {from: 450, duration: 60, source: 'growth', sourceStart: 326, position: '55% 67%', zoom: [1.17, 1.38], drift: [58, -18], direction: 'left'},
  {from: 510, duration: 60, source: 'moss', sourceStart: 260, position: '45% 52%', zoom: [1.20, 1.42], drift: [-42, 16], direction: 'right'},
  {from: 570, duration: 60, source: 'log', sourceStart: 294, position: '55% 50%', zoom: [1.17, 1.37], drift: [50, -22], direction: 'left'},
  {from: 630, duration: 60, source: 'growth', sourceStart: 408, position: '49% 65%', zoom: [1.18, 1.39], drift: [-42, -16], direction: 'right'},
  {from: 690, duration: 60, source: 'moss', sourceStart: 332, position: '56% 49%', zoom: [1.21, 1.40], drift: [46, 18], direction: 'left'},
  {from: 750, duration: 60, source: 'log', sourceStart: 368, position: '44% 53%', zoom: [1.20, 1.40], drift: [-48, 12], direction: 'right'},
  {from: 810, duration: 60, source: 'growth', sourceStart: 500, position: '54% 66%', zoom: [1.20, 1.42], drift: [46, -16], direction: 'left'},
  {from: 870, duration: 60, source: 'moss', sourceStart: 36, position: '47% 52%', zoom: [1.19, 1.39], drift: [-42, 14], direction: 'right'},
  {from: 930, duration: 60, source: 'log', sourceStart: 38, position: '56% 50%', zoom: [1.18, 1.37], drift: [44, -18], direction: 'left'},
  {from: 990, duration: 60, source: 'moss', sourceStart: 130, position: '45% 50%', zoom: [1.22, 1.42], drift: [-46, 16], direction: 'right'},
  {from: 1050, duration: 60, source: 'growth', sourceStart: 614, position: '52% 67%', zoom: [1.18, 1.40], drift: [42, -16], direction: 'left'},
  {from: 1110, duration: 60, source: 'log', sourceStart: 138, position: '48% 51%', zoom: [1.21, 1.41], drift: [-40, 16], direction: 'right'},
  {from: 1170, duration: 60, source: 'growth', sourceStart: 720, position: '48% 66%', zoom: [1.19, 1.43], drift: [36, -18], direction: 'left'},
];

export const hitFrames = [0, 42, 78, 120, 162, 216, 270, 330, 390, 450, 510, 570, 630, 690, 750, 810, 870, 930, 990, 1050, 1110, 1170];
