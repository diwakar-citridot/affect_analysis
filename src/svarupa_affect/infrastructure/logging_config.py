"""Console logging for AFF (uvicorn does not configure the ``svarupa_affect`` log namespace)."""

from __future__ import annotations

import logging
import sys

from .config import _env, ensure_dotenv_loaded

_CONFIGURED = False


def setup_console_logging(level: str | None = None) -> None:
    """Attach a stderr stream handler to the ``svarupa_affect`` logger tree."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    ensure_dotenv_loaded()
    lvl_name = (level or _env("SVARUPA_LOG_LEVEL") or "INFO").upper()
    lvl = getattr(logging, lvl_name, logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

    root = logging.getLogger("svarupa_affect")
    root.setLevel(lvl)
    if not root.handlers:
        root.addHandler(handler)
    root.propagate = False

    _CONFIGURED = True


def log_llm_prompt_to_console(
    *,
    system: str,
    prompt: str,
    schema: dict,
    model_id: str,
    temperature: float,
    max_tokens: int,
    timeout_s: float,
    request_id: str | None = None,
    attempt: int = 1,
) -> None:
    """Write the fully rendered field-assist prompt to stderr (always visible on the console)."""
    import json

    setup_console_logging()
    req = f"request_id={request_id} " if request_id else ""
    message = (
        f"Bedrock field-assist invoke {req}attempt={attempt} model_id={model_id} "
        f"temperature={temperature} max_tokens={max_tokens} timeout_s={timeout_s}\n"
        f"----- SYSTEM PROMPT -----\n{system}\n"
        f"----- USER PROMPT -----\n{prompt}\n"
        f"----- SCHEMA -----\n{json.dumps(schema, indent=2, ensure_ascii=False)}"
    )
    logging.getLogger("svarupa_affect.llm_assist").info(message)
