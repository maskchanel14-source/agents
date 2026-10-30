"""OpenAI-compatible chat provider (OpenAI, Groq, Together, Ollama, Gemini-OAI).

One adapter covers every vendor that exposes /chat/completions, so switching
providers is a config change rather than a code change.
"""
from __future__ import annotations

import logging

import httpx

from app.core.config import settings

from .base import LLMError, LLMProvider, LLMResult, Message

log = logging.getLogger(__name__)


class OpenAICompatibleProvider(LLMProvider):
    name = "openai-compatible"

    def __init__(self, base_url: str, api_key: str | None, name: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        if name:
            self.name = name

    def _call(
        self,
        messages: list[Message],
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> LLMResult:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body: dict = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        url = f"{self.base_url}/chat/completions"
        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                resp = client.post(url, headers=headers, json=body)
                if resp.status_code == 400 and json_mode:
                    # some providers reject response_format -> retry plainly
                    body.pop("response_format", None)
                    resp = client.post(url, headers=headers, json=body)
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:400]
            raise LLMError(f"HTTP {exc.response.status_code}: {detail}") from exc
        except httpx.HTTPError as exc:
            raise LLMError(str(exc)) from exc

        choices = data.get("choices") or []
        if not choices:
            raise LLMError("provider returned no choices")
        text = (choices[0].get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        return LLMResult(
            text=text,
            model=data.get("model", model),
            prompt_tokens=int(usage.get("prompt_tokens", 0)),
            completion_tokens=int(usage.get("completion_tokens", 0)),
            raw={"id": data.get("id")},
        )


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _call(
        self,
        messages: list[Message],
        *,
        model: str,
        max_tokens: int,
        temperature: float,
        json_mode: bool,
    ) -> LLMResult:
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        user_msgs = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
            if m["role"] in {"user", "assistant"}
        ]
        body = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system or "Respond with valid JSON only.",
            "messages": user_msgs,
        }
        try:
            with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
                resp = client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json=body,
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPStatusError as exc:
            raise LLMError(f"HTTP {exc.response.status_code}: {exc.response.text[:400]}") from exc
        except httpx.HTTPError as exc:
            raise LLMError(str(exc)) from exc

        text = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        )
        usage = data.get("usage") or {}
        return LLMResult(
            text=text,
            model=data.get("model", model),
            prompt_tokens=int(usage.get("input_tokens", 0)),
            completion_tokens=int(usage.get("output_tokens", 0)),
        )
