# Source archive manifest — footage rebuild

## Included in `source-archive.zip`
- Editable Remotion composition and timing source; the legacy R3F/Three scene is removed.
- `package.json` and `package-lock.json` for reproducible dependency installation.
- Three local 1080p/HD footage proxies used directly by the composition:
  - `mushroom-growth-timelapse-1080p.mp4`
  - `fungus-moss-log-macro-1080p.mp4`
  - `mushroom-moss-macro-hd.mp4`
- Original procedural audio generator, rendered WAV score/SFX, and Arena-generated narration MP3.
- Render bootstrap script, production plan, research log, publishing kit, QC report and footage credits.

## Footage source, attribution and label
| Local proxy | Original supplied file / source page | Credit | Licence / treatment |
|---|---|---|---|
| `mushroom-growth-timelapse-1080p.mp4` | `138429-769521114.mp4`; https://pixabay.com/videos/mushroom-small-mushroom-138429/ | adege | Pixabay Content License. Real three-day mushroom growth timelapse; downscaled to 1080p render proxy, audio removed. Displayed only as `GENERIC MUSHROOM FOOTAGE`. |
| `fungus-moss-log-macro-1080p.mp4` | `278625.mp4`; https://pixabay.com/videos/mushroom-fungus-moss-nature-log-278625/ | BlenderTimer / Daniel Roberts | Pixabay Content License. Real macro fungus/moss footage; downscaled to 1080p render proxy, audio removed. Displayed only as `GENERIC MUSHROOM FOOTAGE`. |
| `mushroom-moss-macro-hd.mp4` | `27560-364570134.mp4`; https://pixabay.com/videos/mushroom-white-small-group-moss-27560/ | TheMarcKnight | Pixabay Content License. Real macro mushroom footage; audio removed. Displayed only as `GENERIC MUSHROOM FOOTAGE`. |

## Explicit exclusions
- `node_modules/`, build/cache directories, browser extraction cache, render temp directories and QC scratch renders.
- The three original 4K/HD uploads are retained in the user’s Drive folder `footage yt`; the archive carries the 1080p/HD proxies actually used by the project so it stays portable and under the 100 MB Drive upload limit.
- No credentials, API tokens or hidden configuration.

## Legal notes
- The footage follows the Pixabay Content License as supplied by the user. Preserve the displayed `GENERIC MUSHROOM FOOTAGE` truth label and the source/credit table; none of the clips depicts or verifies *L. asiatica*.
- Narration is included for the project owner only; follow the voice platform’s terms when reusing it.
- Cover art remains an AI illustration and retains its on-image disclosure.
