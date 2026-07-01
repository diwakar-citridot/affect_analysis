"""Entry point: ``python -m scripts.migration`` (from repo root with PYTHONPATH=src)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.migration.migrate_companion_to_assistant import main  # noqa: E402

if __name__ == "__main__":
    main()
