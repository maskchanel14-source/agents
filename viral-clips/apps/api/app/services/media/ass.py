"""Subtitle engine: transcript -> ASS (libass) with styling, karaoke and keyword
highlighting. Pure functions, fully unit-testable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .presets import PRESETS, get_preset

STOPWORDS = {
    # English
    "the", "and", "for", "that", "this", "with", "you", "your", "are", "was", "were",
    "have", "has", "had", "but", "not", "they", "them", "there", "here", "what", "when",
    "who", "how", "why", "from", "into", "about", "just", "like", "very", "will", "would",
    "could", "should", "can", "get", "got", "our", "out", "all", "any", "his", "her",
    "its", "it's", "i'm", "don't", "didn't", "isn't", "we're", "you're", "so", "if",
    # Indonesian
    "yang", "dan", "di", "ke", "dari", "itu", "ini", "dengan", "untuk", "tidak", "juga",
    "akan", "bisa", "ada", "saya", "kamu", "kita", "kami", "mereka", "dia", "tapi",
    "karena", "sudah", "belum", "saja", "lebih", "paling", "kalau", "jadi", "pada",
    "dalam", "adalah", "atau", "sangat", "banyak", "semua", "gitu", "sih", "ya",
}

_WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ'’\-]+")


def hex_to_ass(color: str) -> str:
    c = color.lstrip("#")
    if len(c) == 6:
        r, g, b = c[0:2], c[2:4], c[4:6]
        return f"&H00{b}{g}{r}".upper()
    return "&H00FFFFFF"


def ass_time(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def extract_keywords(words: list[dict], top_n: int = 12) -> set[str]:
    """Frequency x length heuristic with bilingual stopword filtering."""
    counts: dict[str, int] = {}
    for w in words:
        token = str(w.get("w", "")).strip()
        for m in _WORD_RE.finditer(token):
            word = m.group(0).lower()
            if len(word) < 5 or word in STOPWORDS:
                continue
            counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (kv[1], len(kv[0])), reverse=True)
    return {w for w, _ in ranked[:top_n]}


def _clean_marks(word: str) -> str:
    """ASS braces/newlines would break override tags."""
    return word.replace("{", "(").replace("}", ")").replace("\n", " ").strip()


def _is_keyword(token: str, keywords: set[str]) -> bool:
    for m in _WORD_RE.finditer(token):
        if m.group(0).lower() in keywords:
            return True
    return False


@dataclass
class Cue:
    start: float
    end: float
    words: list[dict]  # [{w, s, e}] relative to clip start


def group_cues(words: list[dict], *, max_words: int, max_gap: float = 0.7,
               max_duration: float = 3.6) -> list[Cue]:
    """Group word timings into on-screen caption chunks."""
    cues: list[Cue] = []
    current: list[dict] = []
    for w in words:
        if not current:
            current = [w]
            continue
        gap = float(w["s"]) - float(current[-1]["e"])
        span = float(w["e"]) - float(current[0]["s"])
        if len(current) >= max_words or gap > max_gap or span > max_duration:
            cues.append(Cue(float(current[0]["s"]), float(current[-1]["e"]), current))
            current = [w]
        else:
            current.append(w)
    if current:
        cues.append(Cue(float(current[0]["s"]), float(current[-1]["e"]), current))
    # enforce non-overlap / minimum readable duration
    for i, c in enumerate(cues):
        nxt = cues[i + 1].start if i + 1 < len(cues) else None
        end = max(c.end, c.start + 0.9)
        if nxt is not None:
            end = min(end, nxt - 0.01)
        c.end = max(c.start + 0.35, end)
    return cues


def sentences_to_words(sentence: str, start: float, end: float) -> list[dict]:
    """Fallback 'alignment': distribute sentence duration across words by length.

    Used only when the ASR provider returns segment timings without word-level
    timestamps. Approximate by design (documented in README).
    """
    tokens = sentence.split()
    if not tokens:
        return []
    weights = [max(2, len(t)) + 1 for t in tokens]
    total = sum(weights)
    dur = max(0.2, end - start)
    out, cursor = [], start
    for tok, weight in zip(tokens, weights, strict=True):
        share = dur * weight / total
        out.append({"w": tok, "s": round(cursor, 3), "e": round(cursor + share, 3)})
        cursor += share
    return out


def build_ass(
    cues: list[Cue],
    *,
    preset: str | None = "bold_viral",
    keywords: set[str] | None = None,
    width: int = 1080,
    height: int = 1920,
    title: str | None = None,
    highlight_color: str | None = None,
) -> str:
    style = get_preset(preset)
    kw = keywords or set()
    primary = hex_to_ass(highlight_color or style["primary"])
    highlight = hex_to_ass(style["highlight"])
    outline_col = hex_to_ass(style["outline_color"])
    back_col = hex_to_ass(style["back_color"]) if style.get("back_color") else "&H80000000"
    border_style = 3 if style.get("boxed") else 1
    bold = -1 if style["bold"] else 0
    font_size = int(round(style["size"] * (width / 1080)))

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        (
            f"Style: Caption,{style['font']},{font_size},{primary},{highlight},{outline_col},"
            f"{back_col},{bold},0,0,0,100,100,{style.get('spacing', 0)},0,{border_style},"
            f"{style['outline']},{style['shadow']},{style['alignment']},80,80,"
            f"{style['margin_v']},1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    if title:
        lines.append(
            f"Dialogue: 1,{ass_time(0)},{ass_time(2.2)},Caption,,0,0,0,,"
            f"{{\\an8\\fs{int(font_size * 0.7)}\\fad(180,180)}}{_clean_marks(title)}"
        )

    fade = style.get("fade_ms", 120)
    for cue in cues:
        if cue.end <= cue.start:
            continue
        words = cue.words
        texts = [_clean_marks(str(w.get("w", ""))) for w in words]
        if style["uppercase"]:
            texts = [t.upper() for t in texts]

        if style["karaoke"] and len(words) > 1:
            # one event per word: the chunk stays on screen, the active word is
            # re-coloured with the accent colour (robust across libass builds)
            for idx, w in enumerate(words):
                start = max(cue.start, float(w["s"]))
                end = min(cue.end, max(float(w["e"]), start + 0.12))
                parts = []
                for j, t in enumerate(texts):
                    if j == idx and not _is_keyword(t, kw):
                        parts.append(f"{{\\c{highlight}}}{t}{{\\c{primary}}}")
                    elif _is_keyword(t, kw) and j != idx:
                        parts.append(f"{{\\c{highlight}}}{t}{{\\c{primary}}}")
                    else:
                        parts.append(t)
                body = " ".join(parts)
                lines.append(
                    f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Caption,,0,0,0,,"
                    f"{{\\fad({fade},{fade})}}{body}"
                )
        else:
            parts = []
            for t in texts:
                if _is_keyword(t, kw):
                    parts.append(f"{{\\c{highlight}}}{t}{{\\c{primary}}}")
                else:
                    parts.append(t)
            lines.append(
                f"Dialogue: 0,{ass_time(cue.start)},{ass_time(cue.end)},Caption,,0,0,0,,"
                f"{{\\fad({fade},{fade})}}{' '.join(parts)}"
            )
    return "\n".join(lines) + "\n"


def words_in_range(words: list[dict], start_s: float, end_s: float) -> list[dict]:
    """Slice transcript words to a clip and rebase timestamps to clip start."""
    out = []
    for w in words or []:
        ws, we = float(w.get("s", 0)), float(w.get("e", 0))
        if we <= start_s or ws >= end_s:
            continue
        out.append(
            {
                "w": w.get("w", ""),
                "s": round(max(0.0, ws - start_s), 3),
                "e": round(min(end_s, we) - start_s, 3),
            }
        )
    return out
