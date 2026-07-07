"""Read-only per-status triplet vocabulary from the pinned AFF snapshot.

Loads ``data/kg/aff_triplet_descriptions.v1.json`` (produced by
``scripts/export_aff_triplet_descriptions.py``) and exposes the
deficiency/balance/excess descriptions for each AFF concept. This is the LLM
grounding vocabulary for affect analysis — a pinned artifact, deliberately not a
live DB read in the request path.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ..config import Settings

logger = logging.getLogger("svarupa_affect.triplet_registry")

_STATIC_SNAPSHOT = Settings.load().data_dir / "kg" / "aff_triplet_descriptions.v1.json"
_MET_SNAPSHOT = Settings.load().data_dir / "kg" / "met_triplet_descriptions.v1.json"

STATUSES = ("deficiency", "balance", "excess")


class StaticTripletVocabulary:
    """In-memory per-status descriptions keyed by (dimension_id, slug)."""

    def __init__(self, by_dim_slug: dict[int, dict[str, dict[str, str]]]) -> None:
        self._by_dim_slug = by_dim_slug

    def status_descriptions(self, dimension_id: int, slug: str) -> dict[str, str]:
        return dict(self._by_dim_slug.get(dimension_id, {}).get(slug, {}))


def _load_snapshot(path: Path) -> dict[int, dict[str, dict[str, str]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    by_dim_slug: dict[int, dict[str, dict[str, str]]] = {}
    for row in raw["concepts"]:
        dim_id = int(row["dimension_id"])
        slug = str(row["slug"])
        # keep only statuses that actually have text (coverage gaps -> omitted)
        present = {
            st: str(row["descriptions"][st])
            for st in STATUSES
            if row["descriptions"].get(st)
        }
        by_dim_slug.setdefault(dim_id, {})[slug] = present
    return by_dim_slug


def build_triplet_vocabulary(
    *, path: Path = _STATIC_SNAPSHOT
) -> StaticTripletVocabulary:
    """Composition root: load the pinned triplet snapshot (empty if absent)."""
    try:
        by_dim_slug = _load_snapshot(path)
    except FileNotFoundError:
        logger.warning("Triplet snapshot not found at %s; grounding disabled", path)
        return StaticTripletVocabulary({})
    n = sum(len(s) for s in by_dim_slug.values())
    logger.info(
        "Loaded AFF triplet vocabulary from %s: %d dimension(s), %d concept(s)",
        path.name,
        len(by_dim_slug),
        n,
    )
    return StaticTripletVocabulary(by_dim_slug)


def build_metaphor_triplet_vocabulary(
    *, path: Path = _MET_SNAPSHOT
) -> StaticTripletVocabulary:
    """Composition root: load the pinned MET (Metaphor layer) triplet snapshot.

    Produced by ``scripts/export_met_triplet_descriptions.py`` — the pole
    (deficiency/balance/excess) descriptions for the metaphor layer's primary
    dimensions (D1/D5/D6/D15). Empty vocabulary when absent.
    """
    try:
        by_dim_slug = _load_snapshot(path)
    except FileNotFoundError:
        logger.warning("MET triplet snapshot not found at %s; grounding disabled", path)
        return StaticTripletVocabulary({})
    n = sum(len(s) for s in by_dim_slug.values())
    logger.info(
        "Loaded MET triplet vocabulary from %s: %d dimension(s), %d concept(s)",
        path.name,
        len(by_dim_slug),
        n,
    )
    return StaticTripletVocabulary(by_dim_slug)
