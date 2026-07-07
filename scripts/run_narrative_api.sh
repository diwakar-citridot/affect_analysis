#!/usr/bin/env bash
# Start the NAR (Narrative Arc) API using the project venv Python.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=src
export SVARUPA_LOG_LEVEL="${SVARUPA_LOG_LEVEL:-INFO}"
exec "$ROOT/.venv/bin/python" -m uvicorn svarupa_narrative.api.app:app --reload --port "${PORT:-8100}" "$@"
