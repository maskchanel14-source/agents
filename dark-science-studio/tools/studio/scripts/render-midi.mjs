#!/usr/bin/env node
/**
 * render-midi.mjs — MIDI -> stereo WAV via SpessaSynth Core + a GM soundfont.
 *
 * Usage: node render-midi.mjs <in.mid> <out.wav> <soundfont.sf2>
 *
 * SpessaSynth 4.x API (verified on this box):
 *   SoundBankLoader.fromArrayBuffer(buf) -> SoundFont2
 *   new SpessaSynthProcessor(sampleRate, {soundBank})   // ctor takes ONE arg object
 *   BasicMIDI.fromArrayBuffer(buf)
 *   synth.processMessage(ticks, statusByte, d1, d2)
 *   synth.process(L, R, startIndex, sampleCount)        // sampleCount <= 128
 */
import fs from 'fs';
import path from 'path';
import * as S from 'spessasynth_core';

const [inMidi, outWav, inSf2] = process.argv.slice(2);
if (!inMidi || !outWav || !inSf2) {
  console.error('usage: render-midi.mjs <in.mid> <out.wav> <soundfont.sf2>');
  process.exit(2);
}
const SR = 44100;
const toAB = (b) => b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);

const sf = S.SoundBankLoader.fromArrayBuffer(toAB(fs.readFileSync(inSf2)));
const mid = S.BasicMIDI.fromArrayBuffer(toAB(fs.readFileSync(inMidi)));
const synth = new S.SpessaSynthProcessor(SR);
// 4.x ignores the `soundBank` constructor option — the bank must be registered.
synth.soundBankManager.addSoundBank(sf, 'main');
synth.midiChannels.forEach((_, i) => synth.programChange(i, 0));

// Build a flat, globally time-ordered event list in *absolute seconds*.
const evs = [];
for (const tr of mid.tracks) {
  for (const e of tr.events) {
    const st = e.statusByte;
    // keep only channel voice messages (0x80-0xEF); drop meta (0xFF) and sysex
    if (st === undefined || st < 0x80 || st > 0xef) continue;
    evs.push({t: e.ticks, status: st, d1: e.data?.[0] ?? 0, d2: e.data?.[1] ?? 0});
  }
}
evs.sort((a, b) => a.t - b.t);

// ticks -> seconds via the MIDI tempo map.
// NOTE: spessasynth_core exposes tempoChanges[].tempo in BPM (not microseconds/quarter).
const ppq = mid.timeDivision;
const tempos = (mid.tempoChanges ?? [{ticks: 0, tempo: 120}]).slice().sort((a, b) => a.ticks - b.ticks);
const secPerTick = (bpm) => 60 / (bpm * ppq);
const tick2sec = (tick) => {
  let sec = 0, lastTick = 0, bpm = tempos[0]?.tempo ?? 120;
  for (const tc of tempos) {
    if (tc.ticks > tick) break;
    sec += (tc.ticks - lastTick) * secPerTick(bpm);
    lastTick = tc.ticks; bpm = tc.tempo;
  }
  return sec + (tick - lastTick) * secPerTick(bpm);
};

const lastSec = evs.length ? tick2sec(evs[evs.length - 1].t) : 0;
const totalSec = lastSec + 3.5; // let the tail ring out
const total = Math.ceil(totalSec * SR);
const L = new Float32Array(total), R = new Float32Array(total);

const chunkL = new Float32Array(128), chunkR = new Float32Array(128);
let cursor = 0, ei = 0;
while (cursor < total) {
  const nowSec = cursor / SR;
  while (ei < evs.length && tick2sec(evs[ei].t) <= nowSec) {
    const e = evs[ei++];
    try {
      // Use the typed channel methods: processMessage()'s option shape is unstable in 4.x.
      const c = e.status & 0x0f;
      switch (e.status & 0xf0) {
        case 0x80: synth.noteOff(c, e.d1); break;
        case 0x90: e.d2 === 0 ? synth.noteOff(c, e.d1) : synth.noteOn(c, e.d1, e.d2); break;
        case 0xa0: synth.polyPressure(c, e.d1, e.d2); break;
        case 0xb0: synth.controllerChange(c, e.d1, e.d2); break;
        case 0xc0: synth.programChange(c, e.d1); break;
        case 0xd0: synth.channelPressure(c, e.d1); break;
        case 0xe0: synth.pitchWheel(c, ((e.d2 << 7) | e.d1) - 8192); break;
        default: break;
      }
    } catch { /* ignore unsupported */ }
  }
  const n = Math.min(128, total - cursor);
  chunkL.fill(0); chunkR.fill(0);
  synth.process(chunkL, chunkR, 0, n);
  for (let i = 0; i < n; i++) { L[cursor + i] = chunkL[i]; R[cursor + i] = chunkR[i]; }
  cursor += n;
}

let peak = 1e-9;
for (let i = 0; i < total; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
const norm = 0.89 / peak;
const pcm = Buffer.alloc(total * 4);
for (let i = 0; i < total; i++) {
  pcm.writeInt16LE(Math.max(-32768, Math.min(32767, Math.round(L[i] * norm * 32767))), i * 4);
  pcm.writeInt16LE(Math.max(-32768, Math.min(32767, Math.round(R[i] * norm * 32767))), i * 4 + 2);
}
const hdr = Buffer.alloc(44);
hdr.write('RIFF', 0); hdr.writeUInt32LE(36 + pcm.length, 4); hdr.write('WAVE', 8);
hdr.write('fmt ', 12); hdr.writeUInt32LE(16, 16); hdr.writeUInt16LE(1, 20); hdr.writeUInt16LE(2, 22);
hdr.writeUInt32LE(SR, 24); hdr.writeUInt32LE(SR * 4, 28); hdr.writeUInt16LE(4, 32); hdr.writeUInt16LE(16, 34);
hdr.write('data', 36); hdr.writeUInt32LE(pcm.length, 40);
fs.mkdirSync(path.dirname(outWav), {recursive: true});
fs.writeFileSync(outWav, Buffer.concat([hdr, pcm]));
console.log(`rendered ${totalSec.toFixed(2)}s, ${evs.length} events -> ${outWav} (raw peak ${peak.toFixed(3)})`);
