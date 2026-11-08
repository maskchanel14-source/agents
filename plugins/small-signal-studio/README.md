# Small Signal Studio (`small-signal-studio`)

End-to-end production plugin for **Small Signal Studio** — a **Dark Science, Frontier Technology, and Deep Physics** YouTube Shorts documentary channel built strictly on peer-reviewed primary sources and real research footage.

## Components

- **Skill**: [`dark-science-shorts`](skills/dark-science-shorts/SKILL.md) — Complete Cinema Engine v5 workflow (`1080×1920 @ 60fps`, 1:1+ native-pixel stage, `-14.0 LUFS` audio master, `9:16` + `16:9` honest-clickbait covers, Google Drive synchronization, and voluntary audience conversion).
  - [`references/cinema-engine-v5-and-audio.md`](skills/dark-science-shorts/references/cinema-engine-v5-and-audio.md)
  - [`references/sandbox-and-drive-ops.md`](skills/dark-science-shorts/references/sandbox-and-drive-ops.md)
  - [`references/voluntary-conversion-playbook.md`](skills/dark-science-shorts/references/voluntary-conversion-playbook.md)
- **Agent**: [`small-signal-director`](agents/small-signal-director.md) — Directs an episode from primary-paper scouting through pixel/LUFS verification and Google Drive archival.
- **Command**: [`/produce-short`](commands/produce-short.md) — Launch a new `SSS-00X` episode with full quality gates.

## Quick Start in Any New Session

```bash
bash scripts/bootstrap_media_env.sh
```

Reference episode implementations live in:
- `projects/SSS-001-Ghost-Walls-Robot-Parkour/`
- `projects/SSS-002-Universal-Manipulation-Interface/`
- `projects/SSS-003-Seeing-World-Through-Your-Eyes/` (Canonical Cinema Engine v5 template)
