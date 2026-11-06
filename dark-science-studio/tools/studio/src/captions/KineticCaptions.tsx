/**
 * KineticCaptions.tsx — word-synced burned-in captions.
 *
 * HARD-WON: flex `gap` is silently ignored by this headless Chromium build,
 * so words render jammed together ("scientistspublisheda"). Every word/lane
 * gets explicit horizontal padding instead.
 *
 * Positioned at ~63% height, inside the safe zones, never under the right-edge
 * action buttons.
 */
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {theme, W} from '../brand/theme';

export type Word = {word: string; start: number; end: number};

const EMPHASIS = new Set([
  'never', 'nothing', 'mirror', 'warning', 'handedness', 'antibodies', 'phages',
  'antibiotics', 'exist', 'eat', 'thirty-eight', 'billion', 'ten', 'thirty',
  'bacterium', 'same', 'shape', 'planet', 'flip', 'build', 'please', 'one', 'not',
]);

const clean = (w: string) => w.replace(/[^\p{L}\p{N}'-]/gu, '').toLowerCase();

export const KineticCaptions: React.FC<{
  words: Word[];
  from: number;
  to: number;
  y?: number;
  fontSize?: number;
}> = ({words, from, to, y = 1210, fontSize = 58}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  if (t < from || t > to) return null;

  // group into cues of at most 4 words, breaking on sentence end
  const cues = React.useMemo(() => {
    const out: Word[][] = [];
    let cur: Word[] = [];
    for (const w of words) {
      cur.push(w);
      // A cue may hold a trailing comma; only a real sentence end forces a break.
      const bare = w.word.replace(/[^\p{L}\p{N}]/gu, '');
      const sentenceEnd = /[.!?…]$/.test(w.word) && bare.length > 1;
      if (cur.length >= 4 || (sentenceEnd && cur.length >= 2)) {
        out.push(cur);
        cur = [];
      }
    }
    if (cur.length) out.push(cur);
    return out;
  }, [words]);

  const cue = cues.find((c) => t >= c[0].start - 0.06 && t <= c[c.length - 1].end + 0.10);
  if (!cue) return null;

  return (
    <div
      style={{
        position: 'absolute',
        top: y,
        left: 56,
        right: 56,
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignItems: 'flex-end',
        fontFamily: theme.type.display,
        fontWeight: 800,
        fontSize,
        lineHeight: 1.16,
        letterSpacing: -0.5,
        textTransform: 'uppercase',
      }}
    >
      {cue.map((w, i) => {
        const active = t >= w.start - 0.04 && t <= w.end + 0.06;
        const spoken = t > w.end;
        const emph = EMPHASIS.has(clean(w.word));
        return (
          <span
            key={`${w.start}-${i}`}
            style={{
              // explicit padding, never `gap`
              padding: '0 11px',
              color: emph || active ? theme.ink : spoken ? 'rgba(255,255,255,0.86)' : 'rgba(255,255,255,0.72)',
              textShadow: '0 4px 10px rgba(0,0,0,1), 0 6px 30px rgba(0,0,0,0.95), 0 0 60px rgba(0,0,0,0.9)',
              transform: active ? 'scale(1.06)' : 'scale(1)',
              transformOrigin: 'center bottom',
              WebkitTextStroke: emph ? `1.5px ${theme.accent}` : '0',
              display: 'inline-block',
            }}
          >
            {w.word}
          </span>
        );
      })}
    </div>
  );
};
