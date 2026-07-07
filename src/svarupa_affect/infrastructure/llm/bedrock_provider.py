"""ILLMProvider adapters (§6).

``BedrockLLMProvider`` calls Claude on AWS Bedrock via ``boto3``. When credentials/boto3
are unavailable, the layer falls back to ``NullLLMProvider`` after logging the real cause.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import sys
from pathlib import Path

from ...domain.exceptions import ModelUnavailable, SchemaValidationError
from ...infrastructure.logging_config import log_llm_prompt_to_console

logger = logging.getLogger("svarupa_affect.bedrock_provider")

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)

# Newer Claude models removed the sampling parameters — sending `temperature`
# (or top_p/top_k) returns a ValidationException. Steer via prompting instead.
_NO_SAMPLING_MARKERS = ("fable-5", "mythos-5", "opus-4-7", "opus-4-8", "sonnet-5")


def _supports_sampling(model_id: str) -> bool:
    mid = model_id.lower()
    return not any(marker in mid for marker in _NO_SAMPLING_MARKERS)


def _import_boto3():
    """Lazy import so we surface the real failure (wrong interpreter, missing package, …)."""
    try:
        import boto3  # type: ignore

        return boto3
    except ImportError as exc:
        venv_python = Path(__file__).resolve().parents[4] / ".venv" / "bin" / "python"
        run_api = Path(__file__).resolve().parents[4] / "scripts" / "run_api.sh"
        venv_hint = (
            f"Use the project venv: {run_api}"
            if run_api.is_file()
            else f"PYTHONPATH=src {venv_python} -m uvicorn svarupa_affect.api.app:app"
        )
        raise ModelUnavailable(
            f"boto3 is not available in this Python interpreter ({sys.executable}). "
            f"{venv_hint} — or install here: '{sys.executable} -m pip install boto3'."
        ) from exc


def _parse_llm_json(text: str) -> dict:
    """Parse JSON from the model body, tolerating markdown fences and leading prose."""
    stripped = text.strip()
    fence = _JSON_FENCE_RE.search(stripped)
    if fence:
        stripped = fence.group(1).strip()
    elif stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)

    candidates = [stripped]
    start, end = stripped.find("{"), stripped.rfind("}")
    if start >= 0 and end > start:
        candidates.append(stripped[start : end + 1])

    last_exc: json.JSONDecodeError | None = None
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict):
                return payload
            raise SchemaValidationError("Bedrock returned JSON that is not an object")
        except json.JSONDecodeError as exc:
            last_exc = exc
            continue
    raise SchemaValidationError(
        f"Bedrock returned non-JSON content" + (f" ({last_exc})" if last_exc else "")
    )


class NullLLMProvider:
    """Always-unavailable provider. The default when the assist is disabled / unconfigured."""

    async def complete_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict,
        model_id: str,
        temperature: float,
        timeout_s: float,
        max_tokens: int = 4096,
        request_id: str | None = None,
        attempt: int = 1,
        metrics: dict | None = None,
    ) -> dict:
        raise ModelUnavailable("LLM field-assist is not configured (NullLLMProvider)")


class BedrockLLMProvider:
    """Claude-on-Bedrock provider implementing :class:`ILLMProvider`."""

    def __init__(self, region_name: str | None = None, *, read_timeout_s: float = 65.0) -> None:
        boto3 = _import_boto3()
        if not region_name:
            raise ModelUnavailable(
                "AWS region is not set. Set AWS_REGION or AWS_DEFAULT_REGION "
                "(or SVARUPA_AWS_REGION in .env)."
            )
        from botocore.config import Config  # type: ignore

        cfg = Config(
            connect_timeout=10,
            read_timeout=max(30.0, read_timeout_s),
            retries={"max_attempts": 2},
        )
        self._client = boto3.client("bedrock-runtime", region_name=region_name, config=cfg)

    async def complete_json(
        self,
        *,
        system: str,
        prompt: str,
        schema: dict,
        model_id: str,
        temperature: float,
        timeout_s: float,
        max_tokens: int = 4096,
        request_id: str | None = None,
        attempt: int = 1,
        metrics: dict | None = None,
    ) -> dict:  # pragma: no cover - requires live AWS credentials
        # Cache the static system prefix (contract + closed vocabulary + task rules)
        # so repeat requests within the ~5-minute TTL read it at ~0.1x input price
        # instead of reprocessing ~9k tokens each call. Manual cache_control is
        # required on Bedrock (no automatic caching); the model must support prompt
        # caching (Claude Sonnet 5 does). Below-minimum prefixes silently don't cache.
        body: dict = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max(256, max_tokens),
            "system": [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [{"role": "user", "content": prompt}],
        }
        # Newer Claude models (Sonnet 5, Opus 4.7/4.8, Fable 5) reject `temperature`.
        if _supports_sampling(model_id):
            body["temperature"] = temperature

        log_llm_prompt_to_console(
            system=system,
            prompt=prompt,
            schema=schema,
            model_id=model_id,
            temperature=temperature,
            max_tokens=body["max_tokens"],
            timeout_s=timeout_s,
            request_id=request_id,
            attempt=attempt,
        )

        def _invoke() -> dict:
            resp = self._client.invoke_model(modelId=model_id, body=json.dumps(body))
            payload = json.loads(resp["body"].read())
            usage = payload.get("usage") or {}
            if metrics is not None:
                for key in (
                    "input_tokens",
                    "output_tokens",
                    "cache_read_input_tokens",
                    "cache_creation_input_tokens",
                ):
                    metrics[key] = int(usage.get(key) or 0)
            logger.debug(
                "bedrock usage model_id=%s cache_read=%s cache_write=%s input=%s output=%s",
                model_id,
                usage.get("cache_read_input_tokens"),
                usage.get("cache_creation_input_tokens"),
                usage.get("input_tokens"),
                usage.get("output_tokens"),
            )
            stop_reason = payload.get("stop_reason")
            if stop_reason == "max_tokens":
                raise SchemaValidationError(
                    "Bedrock response was truncated (stop_reason=max_tokens); "
                    "increase SVARUPA_LLM_ASSIST_MAX_TOKENS"
                )
            # Newer models (adaptive thinking on by default) may lead with a
            # thinking block, so pick the first text block rather than content[0].
            blocks = payload.get("content") or []
            text = next(
                (b.get("text") for b in blocks if b.get("type") == "text" and b.get("text")),
                None,
            )
            if text is None:
                raise SchemaValidationError(
                    f"Bedrock response had no text block (stop_reason={stop_reason})"
                )
            return _parse_llm_json(text)

        try:
            return await asyncio.wait_for(asyncio.to_thread(_invoke), timeout=timeout_s)
        except asyncio.TimeoutError as exc:
            raise ModelUnavailable(
                f"Bedrock field-assist timed out after {timeout_s:.0f}s "
                f"(model_id={model_id!r}; increase SVARUPA_LLM_ASSIST_TIMEOUT_S)"
            ) from exc
        except json.JSONDecodeError as exc:
            raise SchemaValidationError("Bedrock returned non-JSON content") from exc
        except Exception as exc:  # noqa: BLE001
            raise ModelUnavailable(f"Bedrock invocation failed: {exc}") from exc
