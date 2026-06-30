"""ILLMProvider adapters (§6).

``BedrockLLMProvider`` calls Claude on AWS Bedrock via ``boto3``. When credentials/boto3
are unavailable, the layer falls back to ``NullLLMProvider`` after logging the real cause.
"""

from __future__ import annotations

import asyncio
import json
import re
import sys

from ...domain.exceptions import ModelUnavailable, SchemaValidationError
from ...infrastructure.logging_config import log_llm_prompt_to_console

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _import_boto3():
    """Lazy import so we surface the real failure (wrong interpreter, missing package, …)."""
    try:
        import boto3  # type: ignore

        return boto3
    except ImportError as exc:
        raise ModelUnavailable(
            f"boto3 is not available in this Python interpreter "
            f"({sys.executable}). Install it here: "
            f"'{sys.executable} -m pip install boto3', then start the API with "
            f"'{sys.executable} -m uvicorn svarupa_affect.api.app:app' "
            f"(not the Homebrew/system uvicorn if it points at a different Python)."
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
    ) -> dict:  # pragma: no cover - requires live AWS credentials
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max(256, max_tokens),
            "temperature": temperature,
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }

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
            stop_reason = payload.get("stop_reason")
            text = payload["content"][0]["text"]
            if stop_reason == "max_tokens":
                raise SchemaValidationError(
                    "Bedrock response was truncated (stop_reason=max_tokens); "
                    "increase SVARUPA_LLM_ASSIST_MAX_TOKENS"
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
