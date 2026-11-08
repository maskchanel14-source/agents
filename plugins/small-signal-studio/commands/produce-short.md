---
description: "Produce a complete Ultra-HD 1080p60 Dark Science YouTube Short (SSS-00X) with covers, -14 LUFS master, voluntary conversion triggers, and Google Drive upload"
argument-hint: "[optional topic, paper URL, or theme direction]"
---

# Produce Short (Small Signal Studio)

Execute an end-to-end **Small Signal Studio** episode (`SSS-00X`) matching the exact Cinema Engine v5 quality of `SSS-003`.

## Requirements

<user_request>
$ARGUMENTS
</user_request>

Treat `<user_request>` as topic or direction input from the creator (if empty, scout a fresh peer-reviewed Dark Science & Frontier Technology breakthrough not yet in `Channel Log.txt`).

## Instructions

1. **Bootstrap & Check Log**: Run `bash scripts/bootstrap_media_env.sh`, load `google_drive`, and inspect `Channel Log.txt` (`1tZFUr28z0ulej-fvrZD7DUxCkUFUAarC`) to pick the next `SSS-00X` ID without repeating prior papers.
2. **Scout & Verify `1080p` Footage**: Consult the `dark-science-shorts` skill (`references/sandbox-and-drive-ops.md`). Clone a peer-reviewed GitHub project page with `12–30+` native `1080p` MP4s (`height == 1080`) and verify every physical number from the paper/code.
3. **Script & Master Audio (`-14.0 LUFS`)**: Write a `128–136` word 8-beat English script (`55s–58.5s`, zero verbal begging, `0.60s` total silence before Beat 8, `"Remember..."` seamless loop), synthesize with `voice-00`, and run two-pass EBU R128 normalization (`-14.0 LUFS`, `<= -1.0 dBTP`).
4. **Build & Inspect Covers**: Produce and visually inspect `SSS-00X_Viral_Cover_9x16.jpg` (`1080x1920`, Frame 0) and `SSS-00X_Viral_Thumbnail_16x9.png` (`1920x1080`).
5. **Render Cinema Engine v5 (`1080p60`)**: Validate 34–36 non-repeating `1080p` cuts via `shotlist.py` (`projects/SSS-003-Seeing-World-Through-Your-Eyes/` is the canonical template) and render with the silent Peak-End Voluntary Dossier Toast (`ARCHIVE #00X • LIKE TO SAVE PAPER • + SUBSCRIBE FOR #00(X+1)`).
6. **Forensic QC & Delivery**: Inspect 5+ full-resolution `1080x1920` encoded frames and `ebur128` loudness, upload all 6 deliverables to a new `SSS-00X` subfolder inside Google Drive `1yj4hdWZeKLbmAfMPh-mG10AEFQOvc3yY`, update `Channel Log.txt`, keep `/home/user` `< 128 MB`, commit `projects/SSS-00X-*/`, present the MP4, and summarize in **Indonesian**.
