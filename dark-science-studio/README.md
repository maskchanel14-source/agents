# Dark Science Studio

Vertical Shorts engine: Remotion + Piper + SpessaSynth, zero API keys.

**Workspace survives resets only if it is inside this git repo.** `.venv/`, `node_modules/`,
`.models/` and `assets/*.sf2` are ignored and rebuilt by `setup.sh` + `tools/fetch_assets.sh`.

```
setup.sh                 # venv, npm deps, chromium
tools/fetch_assets.sh    # piper voice + GM soundfont
tools/voice_kit.py       # script -> voice.wav + words.json + captions.srt
tools/audio_kit.py       # timeline -> score.mid -> score.wav + SFX + mix.wav
tools/qa_gate.py         # six automated checks + contact sheets
tools/studio/            # Remotion project (src/, scripts/render-midi.mjs)
projects/DS-###/         # per-video data (timeline.json, props, docs)
renders/DS-###/          # final.mp4 + cover_frame.png
build/DS-###/            # intermediates (voice, score, mix, raw render)
```

## Hard-won constraints (do not relearn these)

- **WebGL is unavailable.** All 3D is Canvas2D software projection (`Soft3D`).
- **CSS `gap` is ignored** by the headless Chromium build. Use explicit per-item padding.
- Chromium: `@sparticuz/chromium` binary + unpacked `al2023.tar` libs on `LD_LIBRARY_PATH`;
  launch through a wrapper script, not `--browser-executable` on the raw binary.
- `ffmpeg` rawvideo read to stdout returns **bytes**; never decode as text.
- **SpessaSynth 4.x**: `new SpessaSynthProcessor(sr)` then
  `synth.soundBankManager.addSoundBank(sb, 'main')` — the `soundBank` ctor option is ignored.
  Use typed methods (`noteOn/noteOff/controllerChange/programChange/pitchWheel`);
  `processMessage()`'s option shape is unreliable. `tempoChanges[].tempo` is **BPM**.
- `process(L, R, startIndex, sampleCount)` — 128-sample quantum max.
- Piper: `PiperVoice.load(...).synthesize_wav(text, w, syn_config=SynthesisConfig(...))`.
