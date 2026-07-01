"""Configuration + data-path resolution.

On import, the repo ``.env`` is loaded into ``os.environ`` (``.env`` wins over shell for
most keys). **Exception:** ``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, and
``AWS_SESSION_TOKEN`` always prefer values already present in the OS environment; ``.env``
is used only as a fallback when a credential is not exported in the shell.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_DOTENV_LOADED = False

# AWS credentials: snapshot the real OS environment at import time (before .env is applied).
_AWS_CREDENTIAL_KEYS = frozenset(
    {
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
    }
)
_OS_AWS_CREDENTIALS: dict[str, str] = {
    k: os.environ[k] for k in _AWS_CREDENTIAL_KEYS if k in os.environ
}


def _repo_root() -> Path:
    # src/svarupa_affect/infrastructure/config.py -> repo root is 4 parents up
    return Path(__file__).resolve().parents[3]


def _dotenv_path() -> Path:
    """Path to the ``.env`` file (override with ``SVARUPA_DOTENV_PATH``)."""
    explicit = os.environ.get("SVARUPA_DOTENV_PATH")
    if explicit:
        return Path(explicit).expanduser().resolve()
    return _repo_root() / ".env"


def parse_dotenv(path: Path) -> dict[str, str]:
    """Parse ``KEY=VALUE`` lines from a dotenv file. Later duplicate keys win."""
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if not key:
            continue
        val = val.strip()
        # strip surrounding quotes
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        # drop inline comments on unquoted values: FOO=bar # comment
        if val and val[0] not in "\"'" and " #" in val:
            val = val.split(" #", 1)[0].rstrip()
        out[key] = val
    return out


def _apply_aws_credentials(parsed: dict[str, str]) -> None:
    """OS-exported credentials win; ``.env`` fills only missing keys."""
    for key in _AWS_CREDENTIAL_KEYS:
        if key in _OS_AWS_CREDENTIALS:
            os.environ[key] = _OS_AWS_CREDENTIALS[key]
        elif key in parsed:
            os.environ[key] = parsed[key]


def load_dotenv(path: Path | None = None, *, override: bool = True) -> dict[str, str]:
    """Load properties from ``.env`` into ``os.environ``.

    When ``override=True`` (default), values from the file replace shell variables for
    **all keys except** ``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, and
    ``AWS_SESSION_TOKEN`` — those three prefer the OS environment (snapshot at import),
    then fall back to ``.env`` only when not exported in the shell.
    Returns the parsed key/value map (last duplicate key in the file wins).
    """
    global _DOTENV_LOADED
    env_path = path or _dotenv_path()
    parsed = parse_dotenv(env_path)
    for key, val in parsed.items():
        if key in _AWS_CREDENTIAL_KEYS:
            continue
        if override or key not in os.environ:
            os.environ[key] = val
    _apply_aws_credentials(parsed)
    _DOTENV_LOADED = True
    return parsed


def ensure_dotenv_loaded() -> None:
    """Idempotent: load ``.env`` once before reading settings."""
    if not _DOTENV_LOADED:
        load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    """Read a single env var after ``.env`` has been loaded."""
    ensure_dotenv_loaded()
    return os.environ.get(key, default)


def _env_bool(key: str, default: bool = False) -> bool:
    val = _env(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(key: str, default: float) -> float:
    val = _env(key)
    if val is None:
        return default
    try:
        return float(val)
    except ValueError:
        return default


def _env_int(key: str, default: int) -> int:
    val = _env(key)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    bridge_d8: Path
    bridge_d9: Path
    field_synthesis: Path
    patterns: Path
    appraisal_rules: Path
    interactions: Path
    pole_map_d8: Path
    guna_synthesis: Path
    pole_map_d2: Path
    guna_families: Path
    enable_llm_assist: bool
    force_llm_assist: bool
    llm_strict: bool
    bedrock_model_id: str
    aws_region: str | None
    llm_assist_timeout_s: float
    llm_assist_max_tokens: int
    semantic_encoder: str
    bedrock_embed_model_id: str | None
    mysql_host: str | None
    mysql_port: int
    mysql_user: str | None
    mysql_password: str | None
    mysql_database: str | None

    @classmethod
    def load(cls) -> "Settings":
        ensure_dotenv_loaded()
        root = _repo_root()

        data_dir = Path(_env("SVARUPA_AFFECT_DATA_DIR", str(root / "data")))
        aws_region = (
            _env("AWS_REGION")
            or _env("AWS_DEFAULT_REGION")
            or _env("SVARUPA_AWS_REGION")
            or _env("PIPELINE_AWS_REGION")
        )
        bedrock_model_id = (
            _env("BEDROCK_MODEL_ID")
            or _env("SVARUPA_ANALYSIS_BEDROCK_MODEL_ID")
            or _env("SVARUPA_PHENOMENOLOGICAL_BEDROCK_MODEL_ID")
            or "anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        return cls(
            data_dir=data_dir,
            bridge_d8=data_dir / "bridge" / "hyp2sthayi.v2.json",
            bridge_d9=data_dir / "bridge" / "hyp2vyabhi.v2.json",
            field_synthesis=data_dir / "field" / "field_synthesis.v2.json",
            patterns=data_dir / "field" / "patterns.v1.json",
            appraisal_rules=data_dir / "field" / "appraisal_rules.v1.json",
            interactions=data_dir / "field" / "interactions.v1.json",
            pole_map_d8=data_dir / "pole_maps" / "d8_poles.v1.json",
            guna_synthesis=data_dir / "field" / "guna_synthesis.v1.json",
            pole_map_d2=data_dir / "pole_maps" / "d2_poles.v1.json",
            guna_families=data_dir / "bridge" / "guna_families.v1.json",
            enable_llm_assist=_env_bool("SVARUPA_ENABLE_LLM_ASSIST", default=False),
            force_llm_assist=_env_bool("SVARUPA_FORCE_LLM_ASSIST", default=False),
            llm_strict=_env_bool("SVARUPA_LLM_STRICT", default=False),
            bedrock_model_id=bedrock_model_id,
            aws_region=aws_region,
            llm_assist_timeout_s=_env_float("SVARUPA_LLM_ASSIST_TIMEOUT_S", 60.0),
            llm_assist_max_tokens=_env_int("SVARUPA_LLM_ASSIST_MAX_TOKENS", 4096),
            semantic_encoder=_env("SVARUPA_SEMANTIC_ENCODER", "tfidf") or "tfidf",
            bedrock_embed_model_id=_env("SVARUPA_BEDROCK_EMBED_MODEL_ID")
            or _env("BEDROCK_EMBED_MODEL_ID"),
            mysql_host=_env("SVARUPA_MYSQL_HOST"),
            mysql_port=_env_int("SVARUPA_MYSQL_PORT", 3306),
            mysql_user=_env("SVARUPA_MYSQL_USER"),
            mysql_password=_env("SVARUPA_MYSQL_PASSWORD"),
            mysql_database=_env("SVARUPA_MYSQL_DATABASE_MASTER") or _env("SVARUPA_MYSQL_DATABASE"),
        )


# Snapshot OS AWS credentials, then load .env (credentials: OS first, .env fallback).
load_dotenv(_dotenv_path(), override=True)
