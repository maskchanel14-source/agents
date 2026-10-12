
## Strategy iteration round — structural variants (H1)

Ranked on TRAIN; VAL/TEST are confirm-only (no peeking). Same ATR band, same risk layer.

| variant | TRAIN expR | VAL expR | TEST expR | TEST win% | TEST PF | TEST maxDD% | TEST trades |
|---|---|---|---|---|---|---|---|
| V0 baseline (as-is) | -0.347 | -0.311 | -0.378 | 14 | 0.34 | -31.0 | 265 |
| V1 +EMA200 trend filter | -0.305 | -0.261 | -0.416 | 15 | 0.33 | -27.7 | 182 |
| V2 trend + TP 3.0xATR | -0.285 | -0.266 | -0.443 | 13 | 0.29 | -29.5 | 182 |
| V3 trend + TP 3.5xATR | -0.279 | -0.257 | -0.442 | 13 | 0.29 | -29.5 | 182 |
| V4 trend, no BE (pure SL/TP) | -0.013 | -0.068 | -0.202 | 36 | 0.71 | -16.6 | 182 |
| V5 trend, no TP (trail after BE) | -0.218 | -0.180 | -0.205 | 0 | 0.00 | -15.9 | 187 |
| V6 trend + SL 2.0 / TP 3.0 (wide) | -0.177 | -0.163 | -0.369 | 20 | 0.34 | -25.2 | 178 |
| V7 trend + SL 1.2 / TP 2.5 (tight) | -0.358 | -0.310 | -0.480 | 9 | 0.25 | -31.6 | 185 |
| V8 trend + 24h session | -0.270 | -0.261 | -0.302 | 22 | 0.47 | -25.1 | 255 |
| V9 no trend, TP 3.0 | -0.343 | -0.309 | -0.389 | 12 | 0.33 | -31.9 | 272 |

Best on train: **V4 trend, no BE (pure SL/TP)**

D1 + EMA200 trend + TP 3.0 (ATR band [6.54,27.5]): TRAIN +0.036R (54) | VAL -0.134R (20) | TEST -0.047R (21) PF 0.96 net $-11 maxDD -1.9%