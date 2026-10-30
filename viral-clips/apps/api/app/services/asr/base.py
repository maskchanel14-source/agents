"""Speech-recognition provider abstraction.

Providers:
  openai|groq  — any Whisper-compatible /audio/transcriptions endpoint
  faster_whisper — local inference (model must be pre-provisioned)
  fixture      — reads an operator-supplied transcript sidecar (demos & tests)
  none         — no ASR; pipeline runs vision/energy-only
"""
from __future__ import annotations

import json
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

CHUNK_SECONDS = 600.0


@dataclass
class ASRResult:
    provider: str
    model: str | None
    language: str | None
    text: str
    segments: list[dict] = field(default_factory=list)  # {start,end,text}
    words: list[dict] = field(default_factory=list)  # {w,s,e}

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "model": self.model,
            "language": self.language,
            "text": self.text,
            "segments": self.segments,
            "words": self.words,
        }


class ASREngine(ABC):
    name: str = "none"
    model: str | None = None

    @abstractmethod
    def transcribe(self, audio_path: Path, *, duration_s: float, language: str | None = None) -> ASRResult: ...


def _pick_language(detected: str | None, fallback: str | None) -> str | None:
    return (detected or fallback or None)


class OpenAICompatASR(ASREngine):
    """Whisper-compatible API. Long audio is chunked to stay under limits."""

    def __init__(self, base_url: str, api_key: str, model: str, name: str = "openai"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.name = name

    def _post(self, path: Path, language: str | None, offset: float) -> dict:
        data = {
            "model": self.model,
            "response_format": "verbose_json",
            "timestamp_granularities[]": ["segment", "word"],
        }
        if language:
            data["language"] = language
        with Path(path).open("rb") as fh:
            files = {"file": (Path(path).name, fh, "audio/wav")}
            with httpx.Client(timeout=900) as client:
                resp = client.post(
                    f"{self.base_url}/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    data=data,
                    files=files,
                )
        if resp.status_code >= 400:
            raise RuntimeError(f"ASR HTTP {resp.status_code}: {resp.text[:300]}")
        payload = resp.json()
        # normalise offsets for chunked input
        for seg in payload.get("segments", []) or []:
            seg["start"] = float(seg.get("start", 0)) + offset
            seg["end"] = float(seg.get("end", 0)) + offset
        for w in payload.get("words", []) or []:
            w["start"] = float(w.get("start", 0)) + offset
            w["end"] = float(w.get("end", 0)) + offset
        return payload

    def transcribe(self, audio_path: Path, *, duration_s: float, language: str | None = None) -> ASRResult:
        chunks: list[tuple[Path, float]] = []
        if duration_s <= CHUNK_SECONDS + 5:
            chunks = [(audio_path, 0.0)]
        else:
            from app.services.media.ffmpeg import run_ffmpeg

            parts = math.ceil(duration_s / CHUNK_SECONDS)
            for i in range(parts):
                out = audio_path.with_name(f"{audio_path.stem}.part{i}.wav")
                run_ffmpeg(
                    [
                        "-y", "-ss", str(i * CHUNK_SECONDS), "-t", str(CHUNK_SECONDS),
                        "-i", str(audio_path), "-c", "copy", str(out),
                    ],
                    timeout=600,
                )
                chunks.append((out, i * CHUNK_SECONDS))

        segments: list[dict] = []
        words: list[dict] = []
        texts: list[str] = []
        detected_lang = language or settings.asr_language
        for path, offset in chunks:
            payload = self._post(path, language, offset)
            detected_lang = payload.get("language") or detected_lang
            for seg in payload.get("segments", []) or []:
                segments.append(
                    {
                        "start": round(float(seg["start"]), 3),
                        "end": round(float(seg["end"]), 3),
                        "text": (seg.get("text") or "").strip(),
                    }
                )
            for w in payload.get("words", []) or []:
                token = (w.get("word") or w.get("text") or "").strip()
                if token:
                    words.append(
                        {"w": token, "s": round(float(w["start"]), 3), "e": round(float(w["end"]), 3)}
                    )
            texts.append((payload.get("text") or "").strip())
            if offset and path != audio_path:
                path.unlink(missing_ok=True)

        return ASRResult(
            provider=self.name,
            model=self.model,
            language=_pick_language(detected_lang, language),
            text=" ".join(t for t in texts if t).strip(),
            segments=segments,
            words=words,
        )


class FasterWhisperASR(ASREngine):
    """Local inference. Word timestamps included; CPU or CUDA."""

    name = "faster_whisper"

    def __init__(self, model_size: str | None = None, device: str = "cpu"):
        self.model = model_size or settings.faster_whisper_model
        self.device = device
        self._model = None

    def _load(self):
        if self._model is None:
            from faster_whisper import WhisperModel  # optional dependency

            self._model = WhisperModel(self.model, device=self.device, compute_type="int8")
        return self._model

    def transcribe(self, audio_path: Path, *, duration_s: float, language: str | None = None) -> ASRResult:
        model = self._load()
        seg_iter, info = model.transcribe(
            str(audio_path),
            language=language or settings.asr_language,
            word_timestamps=True,
            vad_filter=True,
        )
        segments, words = [], []
        for seg in seg_iter:
            segments.append(
                {"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text.strip()}
            )
            for w in seg.words or []:
                words.append(
                    {"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)}
                )
        return ASRResult(
            provider=self.name,
            model=self.model,
            language=getattr(info, "language", language),
            text=" ".join(s["text"] for s in segments).strip(),
            segments=segments,
            words=words,
        )


class FixtureASR(ASREngine):
    """Deterministic transcript from a sidecar file (demo / e2e / regression).

    Looks for `<audio>.fixture.json` or `data/fixtures/transcript.json` with
    {"language","text","segments":[{"start","end","text"}],"words":[...]}.
    Never used silently: provider is recorded as "fixture" on the transcript.
    """

    name = "fixture"
    model = "fixture"

    def transcribe(self, audio_path: Path, *, duration_s: float, language: str | None = None) -> ASRResult:
        candidates = [
            audio_path.with_suffix(".fixture.json"),
            audio_path.parent / "transcript.fixture.json",
            Path(settings.data_dir) / "fixtures" / "transcript.json",
        ]
        for path in candidates:
            if path.is_file():
                payload = json.loads(path.read_text())
                return ASRResult(
                    provider=self.name,
                    model=self.model,
                    language=payload.get("language") or language,
                    text=payload.get("text", ""),
                    segments=payload.get("segments", []),
                    words=payload.get("words", []),
                )
        raise RuntimeError(
            "ASR_PROVIDER=fixture but no fixture transcript found next to the audio "
            f"(looked in: {[str(c) for c in candidates]})"
        )


class NullASR(ASREngine):
    name = "none"

    def transcribe(self, audio_path: Path, *, duration_s: float, language: str | None = None) -> ASRResult:
        return ASRResult(provider="none", model=None, language=language, text="", segments=[], words=[])


def get_asr() -> ASREngine:
    choice = settings.asr_provider
    if choice == "auto":
        choice = "openai" if settings.asr_api_key else "none"
    if choice == "none":
        return NullASR()
    if choice == "fixture":
        return FixtureASR()
    if choice == "faster_whisper":
        return FasterWhisperASR()
    if choice in {"openai", "groq"}:
        if not settings.asr_api_key:
            log.warning("ASR_PROVIDER=%s but ASR_API_KEY is empty; ASR disabled", choice)
            return NullASR()
        base = (
            "https://api.groq.com/openai/v1"
            if choice == "groq" and settings.asr_base_url == "https://api.openai.com/v1"
            else settings.asr_base_url
        )
        model = settings.asr_model
        if choice == "groq" and model == "whisper-1":
            model = "whisper-large-v3-turbo"
        return OpenAICompatASR(base, settings.asr_api_key, model, name=choice)
    return NullASR()
