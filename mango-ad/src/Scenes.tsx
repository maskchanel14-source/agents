/**
 * Scenes.tsx — the nine shots of the spot.
 *
 * Each scene takes {p} (0..1 through its own shot) and draws the whole
 * 1080x1920 frame. Copy is in Indonesian, B2B tone: numbers and logistics,
 * not exclamation marks.
 */
import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {C, T, W, H, clamp, easeOut, easeInOut, bell} from './brand';
import {Photo, Grade, LightSweep, Frame} from './Photo';

/**
 * shared: a line that rises and fades in.
 *
 * Deliberately NOT a clipped mask. An earlier version put each line in an
 * `overflow:hidden` box and slid it 108% — Playfair's line box is taller than
 * the container, so consecutive lines overlapped and the last line in every
 * block got cut by the frame edge. This version never clips.
 */
const MaskLine: React.FC<{
  children: React.ReactNode;
  p: number;
  delay?: number;
  dur?: number;
  style?: React.CSSProperties;
}> = ({children, p, delay = 0, dur = 0.55, style}) => {
  const t = easeOut(clamp((p - delay) / dur));
  return (
    <div
      style={{
        transform: `translateY(${(1 - t) * 42}px)`,
        opacity: t,
        willChange: 'transform, opacity',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** small mono label with a leading rule */
const Kicker: React.FC<{children: React.ReactNode; p: number; delay?: number; color?: string}> = ({
  children,
  p,
  delay = 0,
  color = C.amber,
}) => {
  const t = easeOut(clamp((p - delay) / 0.5));
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 0, opacity: t}}>
      <div style={{width: 54 * t, height: 2, background: color, marginRight: 16}} />
      <div
        style={{
          fontFamily: T.ui,
          fontSize: 22,
          fontWeight: 600,
          letterSpacing: 6,
          textTransform: 'uppercase',
          color,
        }}
      >
        {children}
      </div>
    </div>
  );
};

// ============================================================ 1. ORCHARD
export const S1Orchard: React.FC<{p: number}> = ({p}) => {
  return (
    <>
      <Photo src="assets/orchard.png" p={p} move="driftUp" zoom={1.02} />
      <Grade p={p} warm={0.12} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(7,8,10,0.72) 0%, rgba(7,8,10,0) 34%, rgba(7,8,10,0.1) 62%, rgba(7,8,10,0.9) 100%)',
        }}
      />
      <Frame opacity={0.3} />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.14}>Vale do São Francisco · Brasil</Kicker>
      </div>
      <div style={{position: 'absolute', bottom: 300, left: 104, right: 104}}>
        <MaskLine p={p} delay={0.28} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 100, lineHeight: 1.1, fontWeight: 500, color: C.cream}}>
            Dari lembah
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.42} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 100, lineHeight: 1.1, fontWeight: 500, fontStyle: 'italic', color: C.amberHot}}>
            yang sama,
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.58} dur={0.7}>
          <div style={{fontFamily: T.sans, fontSize: 38, fontWeight: 700, letterSpacing: 2, color: C.creamDim, marginTop: 30}}>
            SEPANJANG TAHUN
          </div>
        </MaskLine>
      </div>
    </>
  );
};

// ============================================================ 2. HERO WHOLE
export const S2Hero: React.FC<{p: number}> = ({p}) => {
  const glow = 0.5 + 0.5 * Math.sin(p * Math.PI * 1.5);
  return (
    <>
      <Photo src="assets/hero_whole.png" p={p} move="push" scaleFrom={1.02} scaleTo={1.1} offsetY={-20} />
      <Grade p={p} warm={0.1} />
      <LightSweep p={p} delay={0.15} duration={0.55} opacity={0.34} />
      {/* rear rim glow that breathes */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(ellipse 62% 44% at 50% 42%, rgba(232,135,30,${0.16 * glow}) 0%, rgba(232,135,30,0) 68%)`,
          mixBlendMode: 'screen',
        }}
      />
      <Frame opacity={0.34} />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.1}>Palmer</Kicker>
      </div>
      <div style={{position: 'absolute', bottom: 300, left: 104, right: 104}}>
        <MaskLine p={p} delay={0.2} dur={0.75}>
          <div style={{fontFamily: T.serif, fontSize: 124, lineHeight: 1.12, color: C.cream, fontWeight: 500}}>
            510–850
            <span style={{fontSize: 58, fontStyle: 'italic', marginLeft: 18, color: C.amberHot}}>gram</span>
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.34} dur={0.6}>
          <div style={{fontFamily: T.ui, fontSize: 28, fontWeight: 500, letterSpacing: 5, color: C.creamDim, marginTop: 16}}>
            PER BUAH · KELAS EKSPOR
          </div>
        </MaskLine>
      </div>
    </>
  );
};

// ============================================================ 3. FLESH
export const S3Flesh: React.FC<{p: number}> = ({p}) => {
  return (
    <>
      <Photo src="assets/flesh_cut.png" p={p} move="pull" scaleFrom={1.14} scaleTo={1.03} offsetY={10} />
      <Grade p={p} warm={0.05} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(7,8,10,0.82) 0%, rgba(7,8,10,0) 30%, rgba(7,8,10,0) 56%, rgba(7,8,10,0.92) 100%)',
        }}
      />
      <Frame opacity={0.3} />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.12}>Tekstur</Kicker>
      </div>
      <div style={{position: 'absolute', bottom: 280, left: 104, right: 104}}>
        <MaskLine p={p} delay={0.22} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 104, lineHeight: 1.14, color: C.cream, fontWeight: 500}}>
            Padat.
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.38} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 104, lineHeight: 1.14, color: C.cream, fontWeight: 500, fontStyle: 'italic'}}>
            Nyaris tanpa
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.52} dur={0.7}>
          <div style={{fontFamily: T.sans, fontSize: 96, lineHeight: 1.1, color: C.amberHot, fontWeight: 800, letterSpacing: -2, marginTop: 4}}>
            SERAT.
          </div>
        </MaskLine>
      </div>
    </>
  );
};

// ============================================================ 4. NUMBERS (3D bars)
export const S4Numbers: React.FC<{p: number}> = ({p}) => {
  const rows = [
    {k: 'PRODUKTIVITAS', v: '30', unit: 't/ha', note: 'rata-rata nasional 20'},
    {k: 'PANGSA EKSPOR', v: '90', unit: '%', note: 'dari Vale do São Francisco'},
    {k: 'KETERSEDIAAN', v: '12', unit: 'bulan', note: 'tanpa jeda musim'},
  ];
  return (
    <>
      <Photo src="assets/orchard.png" p={p} move="push" zoom={1.34} blur={9} offsetY={-40} />
      <div style={{position: 'absolute', inset: 0, background: 'rgba(7,8,10,0.86)'}} />
      <Grade p={p} warm={0.04} strength={0.7} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse 70% 50% at 50% 40%, rgba(232,135,30,0.13) 0%, rgba(0,0,0,0) 70%)',
        }}
      />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.08}>Angka yang bisa diaudit</Kicker>
      </div>
      <div style={{position: 'absolute', top: 430, left: 104, right: 104}}>
        {rows.map((r, i) => {
          const t = easeOut(clamp((p - 0.16 - i * 0.14) / 0.5));
          const barT = easeInOut(clamp((p - 0.26 - i * 0.14) / 0.7));
          return (
            <div key={r.k} style={{marginBottom: 74, opacity: t}}>
              <div style={{display: 'flex', alignItems: 'flex-end', transform: `translateX(${(1 - t) * -50}px)`}}>
                <div
                  style={{
                    fontFamily: T.serif,
                    fontSize: 132,
                    lineHeight: 0.9,
                    color: C.cream,
                    fontWeight: 500,
                    fontVariantNumeric: 'tabular-nums',
                  }}
                >
                  {r.v}
                </div>
                <div
                  style={{
                    fontFamily: T.ui,
                    fontSize: 34,
                    fontWeight: 600,
                    color: C.amberHot,
                    marginLeft: 12,
                    marginBottom: 18,
                    letterSpacing: 1,
                  }}
                >
                  {r.unit}
                </div>
              </div>
              <div
                style={{
                  fontFamily: T.ui,
                  fontSize: 24,
                  fontWeight: 700,
                  letterSpacing: 5,
                  color: C.cream,
                  marginTop: 6,
                }}
              >
                {r.k}
              </div>
              <div style={{fontFamily: T.ui, fontSize: 20, color: C.creamDim, marginTop: 4, letterSpacing: 1}}>
                {r.note}
              </div>
              {/* the bar */}
              <div style={{height: 3, background: 'rgba(246,237,226,0.14)', marginTop: 16, width: '100%'}}>
                <div
                  style={{
                    height: 3,
                    width: `${barT * (r.unit === 't/ha' ? 0.75 : r.unit === '%' ? 0.9 : 1) * 100}%`,
                    background: `linear-gradient(90deg, ${C.amberDeep}, ${C.amberHot})`,
                    boxShadow: `0 0 18px rgba(232,135,30,0.7)`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
      <Frame opacity={0.26} />
    </>
  );
};

// ============================================================ 5. LINE-UP HERO
export const S5Lineup: React.FC<{p: number}> = ({p}) => {
  const cards = [
    {n: 'PALMER', s: '36%', d: 'daging padat, aroma kuat'},
    {n: 'TOMMY ATKINS', s: '30%', d: 'warna merah pekat'},
    {n: 'KEITT', s: '22%', d: 'ukuran besar'},
    {n: 'KENT', s: '12%', d: 'standar pasar Eropa'},
  ];
  return (
    <>
      <Photo src="assets/hero_whole.png" p={p} move="driftL" zoom={1.5} blur={13} offsetY={30} />
      <div style={{position: 'absolute', inset: 0, background: 'rgba(7,8,10,0.9)'}} />
      <Grade p={p} warm={0.05} strength={0.6} />
      <div style={{position: 'absolute', top: 292, left: 104, right: 104}}>
        <Kicker p={p} delay={0.06}>Lini varietas ekspor</Kicker>
        <div
          style={{
            fontFamily: T.serif,
            fontSize: 68,
            lineHeight: 1.16,
            color: C.cream,
            marginTop: 22,
            fontWeight: 500,
            opacity: easeOut(clamp((p - 0.14) / 0.6)),
          }}
        >
          Empat varietas,
          <br />
          <span style={{fontStyle: 'italic', color: C.amberHot}}>satu standar.</span>
        </div>
      </div>
      <div style={{position: 'absolute', top: 560, left: 104, right: 104}}>
        {cards.map((c, i) => {
          const t = easeOut(clamp((p - 0.24 - i * 0.11) / 0.55));
          return (
            <div
              key={c.n}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '20px 0',
                borderTop: '1px solid rgba(246,237,226,0.16)',
                opacity: t,
                transform: `translateY(${(1 - t) * 24}px)`,
              }}
            >
              <div>
                <div style={{fontFamily: T.sans, fontSize: 34, fontWeight: 800, letterSpacing: 3, color: C.cream}}>
                  {c.n}
                </div>
                <div style={{fontFamily: T.ui, fontSize: 20, color: C.creamDim, marginTop: 6, letterSpacing: 1}}>
                  {c.d}
                </div>
              </div>
              <div style={{display: 'flex', alignItems: 'center'}}>
                <div style={{width: 90 * t, height: 2, background: C.amber, marginRight: 14, opacity: 0.8}} />
                <div style={{fontFamily: T.serif, fontSize: 46, color: C.amberHot, fontVariantNumeric: 'tabular-nums'}}>
                  {c.s}
                </div>
              </div>
            </div>
          );
        })}
        <div style={{borderTop: '1px solid rgba(246,237,226,0.16)'}} />
      </div>
      <Frame opacity={0.26} />
    </>
  );
};

// ============================================================ 6. PACKHOUSE
export const S6Pack: React.FC<{p: number}> = ({p}) => {
  const steps = ['PANEN', 'SORTIR', 'GRADING', 'COLD CHAIN', 'PELABUHAN'];
  return (
    <>
      <Photo src="assets/packhouse.png" p={p} move="push" scaleFrom={1.06} scaleTo={1.18} offsetY={-10} />
      <Grade p={p} warm={0.02} strength={0.85} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(180deg, rgba(7,8,10,0.88) 0%, rgba(7,8,10,0.25) 26%, rgba(7,8,10,0.55) 54%, rgba(7,8,10,0.96) 100%)',
        }}
      />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.08} color={C.cool}>Rantai pasok</Kicker>
        <MaskLine p={p} delay={0.2} dur={0.7} style={{marginTop: 24}}>
          <div style={{fontFamily: T.serif, fontSize: 84, lineHeight: 1.06, color: C.cream, fontWeight: 500}}>
            Satu alur,
            <br />
            <span style={{fontStyle: 'italic', color: C.cream}}>nol tebak-tebakan.</span>
          </div>
        </MaskLine>
      </div>
      {/* supply-chain rail: a continuous line with nodes lighting left to right.
          Replaces an earlier vertical list whose lines wrapped the frame edge. */}
      <div style={{position: 'absolute', bottom: 330, left: 104, right: 104}}>
        <div style={{position: 'relative', height: 3, background: 'rgba(246,237,226,0.16)', marginBottom: 26}}>
          <div
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              height: 3,
              width: `${easeInOut(clamp((p - 0.28) / 0.62)) * 100}%`,
              background: `linear-gradient(90deg, ${C.amberDeep}, ${C.amberHot})`,
              boxShadow: `0 0 20px ${C.amber}`,
            }}
          />
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          {steps.map((s, i) => {
            const t = easeOut(clamp((p - 0.3 - i * 0.11) / 0.4));
            return (
              <div key={s} style={{width: 176, opacity: 0.3 + 0.7 * t}}>
                <div
                  style={{
                    width: 11,
                    height: 11,
                    marginBottom: 14,
                    background: t > 0.5 ? C.amberHot : 'rgba(246,237,226,0.35)',
                    boxShadow: t > 0.5 ? `0 0 16px ${C.amber}` : 'none',
                  }}
                />
                <div
                  style={{
                    fontFamily: T.ui,
                    fontSize: i === 3 ? 17 : 20,
                    fontWeight: 700,
                    letterSpacing: i === 3 ? 1.4 : 2.5,
                    color: C.cream,
                    lineHeight: 1.25,
                  }}
                >
                  {s}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <Frame opacity={0.28} />
    </>
  );
};

// ============================================================ 7. SLICE MACRO
export const S7Slice: React.FC<{p: number}> = ({p}) => {
  return (
    <>
      <Photo src="assets/slice_macro.png" p={p} move="tilt" scaleFrom={1.03} scaleTo={1.16} offsetY={-30} />
      <Grade p={p} warm={0.07} />
      <LightSweep p={p} delay={0.3} duration={0.5} opacity={0.26} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(7,8,10,0.8) 0%, rgba(7,8,10,0) 28%, rgba(7,8,10,0) 50%, rgba(7,8,10,0.94) 100%)',
        }}
      />
      <div style={{position: 'absolute', top: 300, left: 104, right: 104}}>
        <Kicker p={p} delay={0.1}>Brix 14–16</Kicker>
      </div>
      <div style={{position: 'absolute', bottom: 296, left: 104, right: 104}}>
        <MaskLine p={p} delay={0.24} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 108, lineHeight: 1.14, color: C.cream, fontWeight: 500}}>
            Manis yang
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.4} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 108, lineHeight: 1.14, color: C.amberHot, fontWeight: 500, fontStyle: 'italic'}}>
            konsisten.
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.58} dur={0.6}>
          <div style={{fontFamily: T.ui, fontSize: 24, fontWeight: 600, letterSpacing: 4, color: C.creamDim, marginTop: 26}}>
            KONTRAK VOLUME · KUALITAS TERUKUR
          </div>
        </MaskLine>
      </div>
      <Frame opacity={0.3} />
    </>
  );
};

// ============================================================ 8. WATER HERO
export const S8Water: React.FC<{p: number}> = ({p}) => {
  return (
    <>
      <Photo src="assets/hero_wet.png" p={p} move="push" scaleFrom={1.0} scaleTo={1.08} />
      <Grade p={p} warm={0.08} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(180deg, rgba(7,8,10,0.7) 0%, rgba(7,8,10,0) 26%, rgba(7,8,10,0) 58%, rgba(7,8,10,0.95) 100%)',
        }}
      />
      <div style={{position: 'absolute', bottom: 300, left: 104, right: 104}}>
        <MaskLine p={p} delay={0.14} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 112, lineHeight: 1.16, color: C.cream, fontWeight: 500}}>
            Siap
          </div>
        </MaskLine>
        <MaskLine p={p} delay={0.28} dur={0.7}>
          <div style={{fontFamily: T.serif, fontSize: 112, lineHeight: 1.16, color: C.cream, fontWeight: 500, fontStyle: 'italic'}}>
            dikirim.
          </div>
        </MaskLine>
      </div>
      <Frame opacity={0.3} />
    </>
  );
};

// ============================================================ 9. END CARD
export const S9End: React.FC<{p: number}> = ({p}) => {
  const rise = easeOut(clamp((p - 0.05) / 0.5));
  const lineT = easeInOut(clamp((p - 0.25) / 0.6));
  return (
    <>
      <Photo src="assets/hero_whole.png" p={p} move="pull" zoom={1.3} blur={16} offsetY={-10} />
      <div style={{position: 'absolute', inset: 0, background: 'rgba(7,8,10,0.93)'}} />
      <Grade p={p} warm={0.03} strength={0.6} />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'radial-gradient(ellipse 64% 40% at 50% 46%, rgba(232,135,30,0.16) 0%, rgba(0,0,0,0) 70%)',
        }}
      />
      <Frame opacity={0.34} />
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: 104,
          right: 104,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <div style={{opacity: rise, transform: `translateY(${(1 - rise) * 30}px)`}}>
          <div style={{fontFamily: T.ui, fontSize: 24, fontWeight: 700, letterSpacing: 9, color: C.amber, marginBottom: 30}}>
            MANGGA BRASIL · PALMER
          </div>
          <div style={{fontFamily: T.serif, fontSize: 104, lineHeight: 1.16, color: C.cream, fontWeight: 500}}>
            Kualitas
          </div>
          <div
            style={{
              fontFamily: T.serif,
              fontSize: 104,
              lineHeight: 1.16,
              color: C.amberHot,
              fontWeight: 500,
              fontStyle: 'italic',
            }}
          >
            yang bisa
          </div>
          <div style={{fontFamily: T.serif, fontSize: 104, lineHeight: 1.16, color: C.cream, fontWeight: 500}}>
            dijanjikan.
          </div>
          <div style={{height: 2, width: `${lineT * 100}%`, background: C.amber, marginTop: 44, opacity: 0.9}} />
          <div
            style={{
              fontFamily: T.ui,
              fontSize: 26,
              fontWeight: 600,
              letterSpacing: 5,
              color: C.creamDim,
              marginTop: 30,
              lineHeight: 1.7,
              opacity: easeOut(clamp((p - 0.5) / 0.5)),
            }}
          >
            GROSIR · HORECA · EKSPOR
            <br />
            MOQ &amp; JADWAL PENGIRIMAN: HUBUNGI TIM KAMI
          </div>
        </div>
      </div>
    </>
  );
};
