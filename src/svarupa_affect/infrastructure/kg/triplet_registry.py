"""Read-only per-status triplet vocabulary (deficiency / balance / excess).

Primary source when MySQL is configured: ``svarupa_concept_descriptions`` joined
through ``svarupa_concept_layer`` for the requested layer. Offline fallback:
pinned JSON snapshots under ``data/kg/*_triplet_descriptions.v1.json``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ... import LAYER_CODE
from ..config import Settings
from .mysql_client import open_mysql

logger = logging.getLogger("svarupa_affect.triplet_registry")

_STATIC_SNAPSHOT = Settings.load().data_dir / "kg" / "aff_triplet_descriptions.v1.json"
_MET_SNAPSHOT = Settings.load().data_dir / "kg" / "met_triplet_descriptions.v1.json"
_NAR_SNAPSHOT = Settings.load().data_dir / "kg" / "nar_triplet_descriptions.v1.json"
_PSY_SNAPSHOT = Settings.load().data_dir / "kg" / "psy_triplet_descriptions.v1.json"

STATUSES = ("deficiency", "balance", "excess")
PREFERRED_PERSPECTIVE = "overview"


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
        descriptions = row.get("descriptions") or {}
        present = {
            st: str(descriptions[st])
            for st in STATUSES
            if descriptions.get(st)
        }
        by_dim_slug.setdefault(dim_id, {})[slug] = present
    return by_dim_slug


def _pick_text(by_perspective: dict[str, str]) -> str | None:
    if not by_perspective:
        return None
    if PREFERRED_PERSPECTIVE in by_perspective:
        return by_perspective[PREFERRED_PERSPECTIVE]
    return max(by_perspective.values(), key=len)


def _load_from_mysql(
    settings: Settings,
    layer_code: str,
    *,
    role: str | None = "primary",
) -> dict[int, dict[str, dict[str, str]]]:
    """Load deficiency/balance/excess text from ``svarupa_concept_descriptions``."""
    sql = """
        SELECT cl.dimension_id, c.slug, s.code AS status, cd.perspective,
               cd.description, cd.overview
          FROM svarupa_concept_layer cl
          JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
          JOIN svarupa_concept_descriptions cd ON cd.concept_id = c.concept_id
          JOIN svarupa_status s ON s.status_id = cd.status_id
         WHERE cl.layer_code = %s
           AND (%s IS NULL OR cl.role = %s)
         ORDER BY cl.dimension_id, c.slug, s.sort_order
    """
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (layer_code, role, role))
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        raise RuntimeError(
            f"svarupa_concept_descriptions returned no rows for layer_code={layer_code!r}"
        )

    # (dimension_id, slug, status) -> {perspective: text}
    candidates: dict[tuple[int, str, str], dict[str, str]] = {}
    for row in rows:
        status = str(row["status"] or "").strip().lower()
        if status not in STATUSES:
            continue
        text = str(row.get("overview") or "").strip() or str(row.get("description") or "").strip()
        if not text:
            continue
        key = (int(row["dimension_id"]), str(row["slug"]), status)
        candidates.setdefault(key, {})[str(row.get("perspective") or "")] = text

    by_dim_slug: dict[int, dict[str, dict[str, str]]] = {}
    for (dim_id, slug, status), by_persp in candidates.items():
        picked = _pick_text(by_persp)
        if not picked:
            continue
        by_dim_slug.setdefault(dim_id, {}).setdefault(slug, {})[status] = picked

    if not by_dim_slug:
        raise RuntimeError(
            f"no usable pole descriptions for layer_code={layer_code!r} "
            "(check svarupa_concept_descriptions)"
        )
    return by_dim_slug


def _build_layer_vocabulary(
    *,
    layer_code: str,
    snapshot_path: Path,
    role: str | None = "primary",
) -> StaticTripletVocabulary:
    """MySQL ``svarupa_concept_descriptions`` when configured; else pinned snapshot.

    When MySQL loads successfully, any missing poles are filled from the pinned
    snapshot so concepts that exist in KG JSON but not yet in
    ``svarupa_concept_descriptions`` (e.g. newly seeded D17) still ground the prompt.
    """
    settings = Settings.load()
    snapshot: dict[int, dict[str, dict[str, str]]] = {}
    try:
        snapshot = _load_snapshot(snapshot_path)
    except FileNotFoundError:
        snapshot = {}

    if settings.mysql_host and settings.mysql_database:
        try:
            by_dim_slug = _load_from_mysql(settings, layer_code, role=role)
            # Fill gaps from snapshot (deficiency/balance/excess independently).
            for dim_id, by_slug in snapshot.items():
                for slug, poles in by_slug.items():
                    dest = by_dim_slug.setdefault(dim_id, {}).setdefault(slug, {})
                    for status, text in poles.items():
                        dest.setdefault(status, text)
            n = sum(len(s) for s in by_dim_slug.values())
            poles = sum(len(p) for dims in by_dim_slug.values() for p in dims.values())
            logger.info(
                "Loaded %s triplet vocabulary from MySQL (%s): "
                "%d dimension(s), %d concept(s), %d pole text(s)",
                layer_code,
                settings.mysql_database,
                len(by_dim_slug),
                n,
                poles,
            )
            return StaticTripletVocabulary(by_dim_slug)
        except Exception as exc:
            logger.warning(
                "Could not load %s triplet descriptions from MySQL (%s); "
                "using static snapshot",
                layer_code,
                exc,
            )

    if not snapshot:
        logger.warning(
            "%s triplet snapshot not found at %s; grounding disabled",
            layer_code,
            snapshot_path,
        )
        return StaticTripletVocabulary({})
    n = sum(len(s) for s in snapshot.values())
    logger.info(
        "Loaded %s triplet vocabulary from %s: %d dimension(s), %d concept(s)",
        layer_code,
        snapshot_path.name,
        len(snapshot),
        n,
    )
    return StaticTripletVocabulary(snapshot)


def build_triplet_vocabulary(
    *, path: Path = _STATIC_SNAPSHOT
) -> StaticTripletVocabulary:
    """Composition root: AFF triplets (MySQL when configured, else pinned snapshot)."""
    return _build_layer_vocabulary(
        layer_code=LAYER_CODE,
        snapshot_path=path,
        role=None,
    )


def build_metaphor_triplet_vocabulary(
    *, path: Path = _MET_SNAPSHOT
) -> StaticTripletVocabulary:
    """MET triplets from ``svarupa_concept_descriptions`` (primary concepts)."""
    return _build_layer_vocabulary(
        layer_code="MET",
        snapshot_path=path,
        role="primary",
    )


def build_narrative_triplet_vocabulary(
    *, path: Path = _NAR_SNAPSHOT
) -> StaticTripletVocabulary:
    """NAR triplets from ``svarupa_concept_descriptions`` (primary concepts)."""
    return _build_layer_vocabulary(
        layer_code="NAR",
        snapshot_path=path,
        role="primary",
    )


def build_psycholinguistic_triplet_vocabulary(
    *, path: Path = _PSY_SNAPSHOT
) -> StaticTripletVocabulary:
    """PSY triplets from ``svarupa_concept_descriptions`` (primary concepts)."""
    return _build_layer_vocabulary(
        layer_code="PSY",
        snapshot_path=path,
        role="primary",
    )
