"""Validate the active Python interpreter has optional backends AFF expects at runtime."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from .config import Settings

logger = logging.getLogger("svarupa_affect.runtime")

_REPO_ROOT = Path(__file__).resolve().parents[3]
_VENV_PYTHON = _REPO_ROOT / ".venv" / "bin" / "python"


def _needs_bedrock(settings: Settings) -> bool:
    return bool(
        settings.enable_llm_assist
        or settings.enable_llm_primary
        or settings.affect_mode == "llm_primary"
        or settings.semantic_encoder == "bedrock"
    )


def _needs_mysql(settings: Settings) -> bool:
    return bool(settings.mysql_host and settings.mysql_database)


def _in_project_venv() -> bool:
    try:
        return Path(sys.prefix).resolve() == (_REPO_ROOT / ".venv").resolve()
    except OSError:
        return False


def _venv_start_hint() -> str:
    run_api = _REPO_ROOT / "scripts" / "run_api.sh"
    if run_api.is_file():
        return f"Start the API with: {run_api}"
    return (
        f"Start the API with: PYTHONPATH=src {_VENV_PYTHON} -m uvicorn "
        "svarupa_affect.api.app:app --reload --port 8000"
    )


def validate_runtime(*, strict: bool = False) -> list[str]:
    """Return human-readable problems; log them. When ``strict``, re-raise the first as RuntimeError."""
    settings = Settings.load()
    problems: list[str] = []

    if _needs_bedrock(settings):
        try:
            import boto3  # noqa: F401
        except ImportError:
            problems.append(
                "boto3 is not installed for "
                f"{sys.executable}. Bedrock LLM assist/primary is enabled "
                f"(SVARUPA_AFFECT_MODE={settings.affect_mode!r})."
            )

    if _needs_mysql(settings):
        try:
            import pymysql  # noqa: F401
        except ImportError:
            problems.append(
                "PyMySQL is not installed for "
                f"{sys.executable}, but SVARUPA_MYSQL_HOST is set; "
                "dimension/concept registries will fall back to static seeds."
            )

    if problems and not _in_project_venv():
        problems.append(
            "This process is not using the project virtualenv "
            f"({_VENV_PYTHON}). {_venv_start_hint()}"
        )
    elif problems and _in_project_venv():
        problems.append(
            f"Install missing packages in the venv: {_VENV_PYTHON} -m pip install -r requirements.txt"
        )

    for msg in problems:
        logger.error(msg)

    if problems and strict:
        raise RuntimeError(problems[0])
    return problems
