#!/usr/bin/env bash
# Start the AFF API using the project venv Python (so boto3 and other venv deps are visible).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH=src
export SVARUPA_LOG_LEVEL="${SVARUPA_LOG_LEVEL:-INFO}"
exec "$ROOT/.venv/bin/python" -m uvicorn svarupa_affect.api.app:app --reload --port "${PORT:-8000}" "$@"
