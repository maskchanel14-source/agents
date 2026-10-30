"""Viral-moment scoring: deterministic heuristic model + LLM rubric, blended.

Scores are honest estimates, never guarantees. Every score ships with a
per-dimension breakdown and a human-readable explanation.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field

from app.core.config import settings
from app.services.ai import LLMError, LLMResult, estimate_cost_usd

log = logging.getLogger(__name__)

DIMENSIONS = [
    ("hook_strength", 0.18),
    ("curiosity", 0.12),
    ("emotional_impact", 0.14),
    ("story_completeness", 0.14),
    ("shareability", 0.12),
    ("engagement", 0.10),
    ("information_value", 0.08),
    ("context_independence", 0.07),
    ("visual_engagement", 0.05),
]

HOOK_MARKERS = (
    "kenapa", "mengapa", "rahasia", "tidak pernah", "jangan", "ternyata", "sebenarnya",
    "why", "how", "secret", "never", "nobody", "truth", "actually", "imagine",
    "the problem is", "here's", "listen", "percaya", "gila", "salah",
)
EMOTION_WORDS = (
    "gila", "luar biasa", "shock", "shocked", "amazing", "crazy", "hate", "love", "takut",
    "sedih", "marah", "bangga", "kaget", "incredible", "terrible", "brutal", "jujur",
    "honestly", "scary", "painful", "hope", "grateful",
)
STORY_MARKERS = ("pertama", "kemudian", "akhirnya", "waktu itu", "first", "then", "finally", "one day")
CONTEXT_RISK = ("itu", "tersebut", "tadi", "seperti yang saya bilang", "as i said", "that thing", "sebelumnya")


@dataclass
class ScoredCandidate:
    start: float
    end: float
    duration: float
    text: str
    title: str
    hook: str
    score: float
    breakdown: dict[str, float] = field(default_factory=dict)
    explanation: str = ""
    tags: list[str] = field(default_factory=list)
    source: str = "heuristic"
    llm_notes: str | None = None


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def heuristic_dimensions(f: dict) -> dict[str, float]:
    """Map measurable features onto the nine rubric dimensions (0-100)."""
    text = (f.get("text") or "").lower()
    dur = max(1.0, f.get("duration", 1.0))
    wpm = f.get("wpm", 0.0)

    hook_markers = sum(1 for m in HOOK_MARKERS if m in text)
    emotion_markers = sum(1 for m in EMOTION_WORDS if m in text)
    story_markers = sum(1 for m in STORY_MARKERS if m in text)
    context_risk = sum(1 for m in CONTEXT_RISK if m in text)

    # opening 3 seconds carry most of the hook weight
    opening = text[:180]
    opening_hooks = sum(1 for m in HOOK_MARKERS if m in opening)

    if f.get("has_transcript"):
        hook = 38 + opening_hooks * 18 + hook_markers * 5 + (8 if text.rstrip().endswith("?") else 0)
        curiosity = 34 + f.get("questions", 0) * 12 + hook_markers * 6
        emotion = 32 + emotion_markers * 11 + min(18.0, f.get("energy_std", 0.0) * 1.6)
        story = 34 + story_markers * 12 + (14 if 18 <= dur <= 75 else 0)
        share = 30 + emotion_markers * 8 + hook_markers * 5 + (10 if f.get("numbers") else 0)
        info = 30 + min(38.0, wpm * 0.55) + min(12.0, f.get("word_count", 0) / 12)
        engage = 32 + min(30.0, wpm * 0.5) + (8 if f.get("has_cta") else 0)
        context = 72 - context_risk * 12 + (10 if dur >= 20 else -8)
    else:
        # no transcript: lean on acoustics + visuals only
        hook = 34 + min(24.0, max(0.0, f.get("energy_peak", -60) + 40) * 0.6)
        curiosity = 30
        emotion = 30 + min(30.0, f.get("energy_std", 0.0) * 2.0)
        story = 28 + (12 if 15 <= dur <= 60 else 0)
        share = 30
        info = 26
        engage = 34 + min(26.0, f.get("motion_mean", 0.0) * 260)
        context = 45

    visual = 30 + min(40.0, f.get("motion_mean", 0.0) * 320) + f.get("face_coverage", 0.0) * 30
    if f.get("scene_cuts", 0) >= 2:
        visual += 6

    return {
        "hook_strength": round(_clamp(hook), 1),
        "curiosity": round(_clamp(curiosity), 1),
        "emotional_impact": round(_clamp(emotion), 1),
        "story_completeness": round(_clamp(story), 1),
        "shareability": round(_clamp(share), 1),
        "engagement": round(_clamp(engage), 1),
        "information_value": round(_clamp(info), 1),
        "context_independence": round(_clamp(context), 1),
        "visual_engagement": round(_clamp(visual), 1),
    }


def weighted_total(dims: dict[str, float]) -> float:
    total = sum(dims.get(k, 0.0) * w for k, w in DIMENSIONS)
    return round(_clamp(total), 1)


def _explanation(dims: dict[str, float], f: dict) -> str:
    top = sorted(dims.items(), key=lambda kv: kv[1], reverse=True)[:2]
    weak = sorted(dims.items(), key=lambda kv: kv[1])[:1]
    pretty = {k: k.replace("_", " ") for k, _ in DIMENSIONS}
    bits = [f"Strongest: {pretty.get(top[0][0], top[0][0])} ({top[0][1]:.0f}/100)"]
    if len(top) > 1:
        bits.append(f"{pretty.get(top[1][0], top[1][0])} ({top[1][1]:.0f}/100)")
    if weak:
        bits.append(f"weakest: {pretty.get(weak[0][0], weak[0][0])} ({weak[0][1]:.0f}/100)")
    if f.get("has_transcript"):
        bits.append(
            f"{f.get('word_count', 0)} words over {f.get('duration', 0):.0f}s "
            f"({f.get('wpm', 0):.0f} wpm)"
        )
    else:
        bits.append("no transcript available — audio/visual signals only")
    return "; ".join(bits) + "."


def _tags(dims: dict[str, float], f: dict) -> list[str]:
    tags = []
    if dims["hook_strength"] >= 70:
        tags.append("strong_hook")
    if dims["emotional_impact"] >= 70:
        tags.append("emotional")
    if dims["information_value"] >= 70:
        tags.append("educational")
    if dims["shareability"] >= 70:
        tags.append("shareable")
    if f.get("questions", 0) >= 1:
        tags.append("question_driven")
    if f.get("has_cta"):
        tags.append("cta")
    if not f.get("has_transcript"):
        tags.append("audio_visual_only")
    return tags


def _fallback_title(text: str, index: int) -> str:
    if not text:
        return f"Highlight {index + 1}"
    first = re.split(r"(?<=[.!?])\s", text.strip())[0]
    words = first.split()[:9]
    title = " ".join(words).strip(" .,!?:;")
    return (title[:1].upper() + title[1:]) if title else f"Highlight {index + 1}"


SYSTEM_PROMPT = """You are a senior short-form video editor who has cut thousands of
Shorts/TikTok/Reels. You judge real podcast and interview transcripts.

You score candidate clips for short-form performance. You never invent content,
never alter what a speaker meant, and never claim a clip will go viral.
Scores are calibrated: 85+ = exceptional, 65-84 = strong, 45-64 = average,
below 45 = weak. Be discriminating; most clips are average.

Return STRICT JSON only, matching this schema:
{"clips":[{"id":<int>,"scores":{"hook_strength":0-100,"curiosity":0-100,
"emotional_impact":0-100,"story_completeness":0-100,"shareability":0-100,
"engagement":0-100,"information_value":0-100,"context_independence":0-100,
"visual_engagement":0-100},"title":"<max 60 chars>","hook":"<the on-screen
opening line, max 90 chars>","explanation":"<max 220 chars, cite what is
actually said>","tags":["..."],"keeps_meaning":true}]}"""


def _build_prompt(cands: list[tuple[int, dict]], language: str | None) -> str:
    lines = [
        f"Source language: {language or 'unknown (detect from text)'}.",
        "Score each candidate clip on how well it works as a standalone short.",
        "Penalise clips that need missing context, that cut a sentence in half,",
        "or that misrepresent the speaker. Tag clip language-appropriately.",
        "",
    ]
    for idx, f in cands:
        text = (f.get("text") or "")[:1200]
        lines.append(f"--- CANDIDATE {idx} ---")
        lines.append(
            f"start={f['start']:.1f}s end={f['end']:.1f}s duration={f['duration']:.0f}s "
            f"words={f.get('word_count', 0)} wpm={f.get('wpm', 0)} "
            f"scene_cuts={f.get('scene_cuts', 0)} face_coverage={f.get('face_coverage', 0)}"
        )
        lines.append(f"transcript: {text if text else '[no transcript — audio/visual analysis only]'}")
        lines.append("")
    ids = [i for i, _ in cands]
    lines.append(f"Return exactly {len(ids)} clip objects with ids {ids}.")
    return "\n".join(lines)


def _parse_llm_json(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"```\s*$", "", text).strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("no JSON object in completion")
    payload = json.loads(m.group(0))
    clips = payload.get("clips") if isinstance(payload, dict) else payload
    if not isinstance(clips, list):
        raise ValueError("expected a 'clips' array")
    return clips


def _llm_score_batch(
    llm, cands: list[tuple[int, dict]], language: str | None, *, deep: bool, usage_sink
) -> dict[int, dict]:
    model = settings.llm_model_deep if deep else settings.llm_model_fast
    res: LLMResult = llm.complete(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_prompt(cands, language)},
        ],
        model=model,
        temperature=0.25,
        json_mode=True,
    )
    if usage_sink:
        usage_sink(
            {
                "provider": llm.name,
                "model": res.model,
                "task": "score",
                "prompt_tokens": res.prompt_tokens,
                "completion_tokens": res.completion_tokens,
                "cost_usd": estimate_cost_usd(res.model, res.prompt_tokens, res.completion_tokens),
                "latency_ms": res.latency_ms,
                "ok": True,
            }
        )
    out: dict[int, dict] = {}
    for item in _parse_llm_json(res.text):
        try:
            out[int(item["id"])] = item
        except (KeyError, TypeError, ValueError):
            continue
    return out


def score_candidates(
    features: list[dict],
    *,
    language: str | None = None,
    target_clips: int = 5,
    use_deep_model: bool = True,
    allow_overlap: bool = False,
    usage_sink=None,
) -> tuple[list[ScoredCandidate], dict]:
    """Score every candidate, then select the best non-overlapping clips."""
    llm = None
    try:
        from app.services.ai.registry import get_llm

        llm = get_llm()
    except Exception as exc:  # pragma: no cover
        log.warning("LLM unavailable: %s", exc)

    indexed = list(enumerate(features))
    llm_map: dict[int, dict] = {}
    llm_error: str | None = None

    if llm is not None and features:
        batch_size = 4 if use_deep_model else 6
        for chunk_start in range(0, len(indexed), batch_size):
            batch = indexed[chunk_start : chunk_start + batch_size]
            try:
                llm_map.update(
                    _llm_score_batch(llm, batch, language, deep=use_deep_model, usage_sink=usage_sink)
                )
            except (LLMError, ValueError, json.JSONDecodeError) as exc:
                llm_error = str(exc)[:300]
                log.warning("LLM scoring batch failed, using heuristics: %s", exc)

    scored: list[ScoredCandidate] = []
    for idx, f in indexed:
        dims = heuristic_dimensions(f)
        heur_total = weighted_total(dims)
        source = "heuristic"
        title, hook, explanation, tags = "", "", _explanation(dims, f), _tags(dims, f)
        keeps_meaning = True

        item = llm_map.get(idx)
        if item and isinstance(item.get("scores"), dict):
            llm_dims = {}
            for key, _ in DIMENSIONS:
                try:
                    llm_dims[key] = round(_clamp(float(item["scores"].get(key, dims[key]))), 1)
                except (TypeError, ValueError):
                    llm_dims[key] = dims[key]
            blended = {
                k: round(0.65 * llm_dims[k] + 0.35 * dims[k], 1) for k in dims
            }
            dims = blended
            source = "llm+heuristic"
            title = (item.get("title") or "").strip()[:120]
            hook = (item.get("hook") or "").strip()[:160]
            if item.get("explanation"):
                explanation = str(item["explanation"])[:400]
            tags = [str(t)[:24] for t in (item.get("tags") or [])][:6] or tags
            keeps_meaning = bool(item.get("keeps_meaning", True))
            if not keeps_meaning:
                dims["context_independence"] = min(dims["context_independence"], 35.0)

        total = weighted_total(dims)
        if not keeps_meaning:
            total = round(max(0.0, total - 15), 1)

        scored.append(
            ScoredCandidate(
                start=f["start"],
                end=f["end"],
                duration=f["duration"],
                text=f.get("text", ""),
                title=title or _fallback_title(f.get("text", ""), idx),
                hook=hook or _fallback_title(f.get("text", ""), idx)[:90],
                score=total,
                breakdown={k: dims[k] for k, _ in DIMENSIONS},
                explanation=f"{explanation} Heuristic baseline: {heur_total:.0f}/100.",
                tags=tags,
                source=source,
                llm_notes=llm_error,
            )
        )

    selected = _select(scored, target_clips=target_clips, allow_overlap=allow_overlap)
    meta = {
        "candidates_generated": len(features),
        "candidates_scored": len(scored),
        "scoring_source": "llm+heuristic" if llm_map else "heuristic",
        "llm_error": llm_error,
        "llm_model": (settings.llm_model_deep if use_deep_model else settings.llm_model_fast)
        if llm_map
        else None,
        "selected": len(selected),
        "mean_score": round(sum(s.score for s in scored) / len(scored), 1) if scored else 0.0,
    }
    return selected, meta


def _select(scored: list[ScoredCandidate], *, target_clips: int, allow_overlap: bool) -> list[ScoredCandidate]:
    ordered = sorted(scored, key=lambda s: s.score, reverse=True)
    picked: list[ScoredCandidate] = []
    for cand in ordered:
        if len(picked) >= target_clips:
            break
        if not allow_overlap:
            clash = False
            for p in picked:
                inter = max(0.0, min(cand.end, p.end) - max(cand.start, p.start))
                if inter / max(1e-6, min(cand.duration, p.duration)) > 0.25:
                    clash = True
                    break
            if clash:
                continue
        picked.append(cand)
    return sorted(picked, key=lambda s: s.start)
