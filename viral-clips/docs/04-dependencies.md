# Third-party dependency inventory

Generated from `apps/api/requirements.txt`, `apps/web/package.json` and vendored assets. Licences were
taken from the packages themselves; **re-verify before any public distribution**.

## Runtime — API (`apps/api/requirements.txt`)

| Package | Version | Licence | Purpose |
|---|---|---|---|
| fastapi | 0.115.6 | MIT | HTTP API |
| uvicorn[standard] | 0.34.0 | BSD-3-Clause | ASGI server |
| pydantic / pydantic-settings | 2.10.4 / 2.7.0 | MIT | Validation + typed settings |
| python-multipart | 0.0.20 | Apache-2.0 | Upload parsing |
| PyJWT | 2.10.1 | MIT | JWT signing/verification |
| httpx | 0.28.1 | BSD-3-Clause | Provider + ingest HTTP client |
| SQLAlchemy[asyncio] | 2.0.36 | MIT | ORM (async) |
| aiosqlite | 0.20.0 | MIT | Dev database driver |
| asyncpg (optional) | 0.30.0 | Apache-2.0 | Postgres driver (prod) |
| alembic | 1.14.0 | MIT | Migration tooling (SQL file is canonical) |
| imageio-ffmpeg | 0.5.1 | BSD-2-Clause | Locates/embeds an FFmpeg binary |
| numpy | 2.2.1 | BSD-3-Clause | Energy/feature maths |
| opencv-python-headless | 4.10.0.84 | Apache-2.0 (wrapper), OpenCV licence for the library | Frame decode, Haar detection |
| pillow | 11.1.0 | MIT-CMU | (transitive image support) |
| boto3 | 1.35.92 | Apache-2.0 | S3-compatible client for R2 |
| redis / rq | 5.2.1 / 2.1.0 | MIT / Apache-2.0 | Production queue |
| pytest / pytest-asyncio | 8.3.4 / 0.25.1 | MIT | Tests |

Optional, not installed by default: `faster-whisper` (MIT), `yt-dlp` (Unlicense), `asyncpg`, `ruff`.

## Runtime — web (`apps/web/package.json`)

| Package | Version | Licence |
|---|---|---|
| next | 15.1.3 | MIT |
| react / react-dom | 19.0.0 | MIT |
| typescript | 5.7.2 | Apache-2.0 |
| tailwindcss / postcss / autoprefixer | 3.4.17 / 8.4.49 / 10.4.20 | MIT |
| @playwright/test | 1.49.1 | Apache-2.0 |

## Vendored assets

| Asset | Source | Licence | Notes |
|---|---|---|---|
| `apps/api/vendor/models/haarcascade_frontalface_default.xml` | `opencv/opencv` `data/haarcascades` (4.x) | Apache-2.0 | 930 KB; attributed in `vendor/models/README.md` |
| `apps/api/tests/fixtures/face.jpg` | user-supplied repo image, downscaled for tests | owner's asset | test-only |
| DejaVu fonts (system) | `/usr/share/fonts/truetype/dejavu` | Bitstream Vera / DejaVu (permissive) | used by libass for burned captions |

## Media binaries — read this before distributing

* `imageio-ffmpeg` downloads the **johnvansickle static FFmpeg 7.0.2 build**: `--enable-gpl` with
  `libx264`. Running it server-side is fine, but **shipping this binary to users brings GPLv2 obligations**.
* Safer options if you distribute: build FFmpeg `--disable-gpl` with `libopenh264` (BSD) or use
  hardware encoders (`h264_nvenc`, `h264_videotoolbox`), and keep `libass` (ISC-style) for captions.
* Set `FFMPEG_BIN=/usr/bin/ffmpeg` to use a system build you control.
* This build has **no freetype/drawtext**; all on-screen text goes through libass + ASS files,
  so captions work regardless.

## Licence compatibility summary

All direct dependencies are MIT / BSD / Apache-2.0 / Unlicense — compatible with a closed SaaS product.
The only copyleft exposure is the GPL FFmpeg binary described above, and (optionally) `yt-dlp` being
Unlicense (fine). Projects reviewed but **not** linked in Phase 1 are listed in `01-resource-discovery.md`;
no AGPL/GPL library is imported by application code.

## Dependency hygiene

* Pinned exact versions in `requirements.txt` and `package.json`; no floating ranges.
* `npm install` and `pip install` were the only installers run; no third-party install scripts executed
  (`yt-dlp` and `faster-whisper` are opt-in and imported lazily).
* Review cadence: bump on a branch, run `make test` (69 tests) + `make e2e`, check FFmpeg/licence notes.
