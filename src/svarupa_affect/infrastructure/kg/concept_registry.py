"""Read-only concept registry from ``svarupa_concept_layer`` + ``svarupa_concepts`` (MySQL).

AFF applicability is defined by rows in ``svarupa_concept_layer`` where
``layer_code = 'AFF'``. Dimension affinity for the layer is the distinct set of
``dimension_id`` values tagged there. Each row also carries ``role``
(``primary`` | ``contributing``) per the Excel / KG mapping.

Offline fallback: ``data/kg/aff_concept_layer.v1.json`` (export of
``svarupa_assistant_v1.svarupa_concept_layer``).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from ... import LAYER_CODE
from ..config import Settings
from .mysql_client import open_mysql

logger = logging.getLogger("svarupa_affect.concept_registry")

# Legacy bridge / steward spellings -> canonical ``svarupa_concepts.slug``.
BRIDGE_SLUG_ALIASES: dict[str, str] = {
    "shoka": "soka",
    "shama": "sama",
    "vishada": "visada",
    "harsha": "harsa",
    "dhriti": "dhrti",
}

_DATA_DIR = Settings.load().data_dir
_STATIC_SNAPSHOT = _DATA_DIR / "kg" / "aff_concept_layer.v1.json"
_LAYER_SNAPSHOTS: dict[str, Path] = {
    "AFF": _STATIC_SNAPSHOT,
    "NAR": _DATA_DIR / "kg" / "nar_concept_layer.v1.json",
    "MET": _DATA_DIR / "kg" / "met_concept_layer.v1.json",
    "PSY": _DATA_DIR / "kg" / "psy_concept_layer.v1.json",
}


def canonical_slug(slug: str) -> str:
    return BRIDGE_SLUG_ALIASES.get(slug, slug)


@dataclass(frozen=True)
class ConceptInfo:
    concept_id: int
    dimension_id: int
    slug: str
    name: str
    gloss: str
    role: str = "contributing"


def _snapshot_path(layer_code: str) -> Path:
    return _LAYER_SNAPSHOTS.get(layer_code, _STATIC_SNAPSHOT)


def _load_static_snapshot(path: Path | None = None, *, layer_code: str = LAYER_CODE) -> tuple[
    frozenset[int],
    frozenset[int],
    frozenset[int],
    dict[int, dict[str, ConceptInfo]],
]:
    snap = path or _snapshot_path(layer_code)
    raw = json.loads(snap.read_text(encoding="utf-8"))
    by_dimension: dict[int, dict[str, ConceptInfo]] = {}
    for row in raw["concepts"]:
        dim_id = int(row["dimension_id"])
        slug = str(row["slug"])
        info = ConceptInfo(
            concept_id=int(row.get("concept_id", 0)),
            dimension_id=dim_id,
            slug=slug,
            name=str(row["name"]),
            gloss=str(row.get("gloss") or row["name"]),
            role=str(row.get("role", "contributing")),
        )
        by_dimension.setdefault(dim_id, {})[slug] = info

    affinity = frozenset(int(x) for x in raw["affinity_dimensions"])
    primary = frozenset(int(x) for x in raw["primary_dimensions"])
    contributing = frozenset(int(x) for x in raw["contributing_dimensions"])
    return affinity, primary, contributing, by_dimension


_STATIC_AFFINITY, _STATIC_PRIMARY, _STATIC_CONTRIBUTING, _STATIC_BY_DIMENSION = (
    _load_static_snapshot(layer_code=LAYER_CODE)
)
_STATIC_LAYER_CACHE: dict[str, tuple[frozenset[int], frozenset[int], frozenset[int], dict]] = {
    LAYER_CODE: (_STATIC_AFFINITY, _STATIC_PRIMARY, _STATIC_CONTRIBUTING, _STATIC_BY_DIMENSION),
}


def _static_layer_data(layer_code: str) -> tuple[
    frozenset[int],
    frozenset[int],
    frozenset[int],
    dict[int, dict[str, ConceptInfo]],
]:
    if layer_code not in _STATIC_LAYER_CACHE:
        _STATIC_LAYER_CACHE[layer_code] = _load_static_snapshot(layer_code=layer_code)
    return _STATIC_LAYER_CACHE[layer_code]


class StaticConceptRegistry:
    """In-memory AFF concept registry (offline fallback)."""

    def __init__(
        self,
        *,
        layer_code: str = LAYER_CODE,
        by_dimension: dict[int, dict[str, ConceptInfo]] | None = None,
        affinity: frozenset[int] | None = None,
        primary_dimensions: frozenset[int] | None = None,
        contributing_dimensions: frozenset[int] | None = None,
    ) -> None:
        self.layer_code = layer_code
        if by_dimension is None and affinity is None:
            aff, prim, contrib, snap = _static_layer_data(layer_code)
            source = snap
            self._affinity = aff
            self._primary_dimensions = primary_dimensions or prim
            self._contributing_dimensions = contributing_dimensions or contrib
        else:
            source = by_dimension or _static_layer_data(layer_code)[3]
            self._affinity = affinity or _static_layer_data(layer_code)[0]
            self._primary_dimensions = primary_dimensions or _static_layer_data(layer_code)[1]
            self._contributing_dimensions = (
                contributing_dimensions or _static_layer_data(layer_code)[2]
            )
        self._by_dimension: dict[int, dict[str, ConceptInfo]] = {
            dim: dict(slugs) for dim, slugs in source.items()
        }

    def affinity(self, layer_code: str | None = None) -> frozenset[int]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return self._affinity

    def primary_dimensions(self, layer_code: str | None = None) -> frozenset[int]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return self._primary_dimensions

    def contributing_dimensions(self, layer_code: str | None = None) -> frozenset[int]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return self._contributing_dimensions

    def concepts(self, dimension_id: int, layer_code: str | None = None) -> tuple[ConceptInfo, ...]:
        if layer_code and layer_code != self.layer_code:
            return ()
        return tuple(sorted(self._by_dimension.get(dimension_id, {}).values(), key=lambda c: c.slug))

    def slugs(self, dimension_id: int, layer_code: str | None = None) -> frozenset[str]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return frozenset(self._by_dimension.get(dimension_id, {}))

    def glosses(
        self,
        dimension_id: int,
        attributes: list[str],
        layer_code: str | None = None,
    ) -> dict[str, str]:
        if layer_code and layer_code != self.layer_code:
            return {}
        table = self._by_dimension.get(dimension_id, {})
        out: dict[str, str] = {}
        for attr in attributes:
            info = table.get(canonical_slug(attr))
            if info:
                out[attr] = info.gloss or info.name
        return out


def _load_from_mysql(
    settings: Settings, layer_code: str
) -> tuple[
    frozenset[int],
    frozenset[int],
    frozenset[int],
    dict[int, dict[str, ConceptInfo]],
]:
    sql = """
        SELECT
            c.concept_id,
            cl.dimension_id,
            c.slug,
            c.name,
            cl.role,
            COALESCE(NULLIF(TRIM(c.description), ''), c.name) AS gloss
        FROM svarupa_concept_layer cl
        JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
        WHERE cl.layer_code = %s
        ORDER BY cl.dimension_id, cl.role DESC, c.sort_order, c.slug
    """
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (layer_code,))
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        raise RuntimeError(f"svarupa_concept_layer returned no rows for layer_code={layer_code!r}")

    by_dimension: dict[int, dict[str, ConceptInfo]] = {}
    affinity: set[int] = set()
    primary: set[int] = set()
    contributing: set[int] = set()
    for row in rows:
        dim_id = int(row["dimension_id"])
        affinity.add(dim_id)
        role = str(row["role"])
        if role == "primary":
            primary.add(dim_id)
        else:
            contributing.add(dim_id)
        slug = str(row["slug"])
        info = ConceptInfo(
            concept_id=int(row["concept_id"]),
            dimension_id=dim_id,
            slug=slug,
            name=str(row["name"]),
            gloss=str(row["gloss"] or row["name"]),
            role=role,
        )
        by_dimension.setdefault(dim_id, {})[slug] = info

    return frozenset(affinity), frozenset(primary), frozenset(contributing), by_dimension


class MySQLConceptRegistry(StaticConceptRegistry):
    """Loads AFF-tagged concepts from MySQL at construction time."""

    def __init__(self, settings: Settings, *, layer_code: str = LAYER_CODE) -> None:
        affinity, primary, contributing, by_dimension = _load_from_mysql(settings, layer_code)
        super().__init__(
            layer_code=layer_code,
            by_dimension=by_dimension,
            affinity=affinity,
            primary_dimensions=primary,
            contributing_dimensions=contributing,
        )
        logger.info(
            "Loaded AFF concept registry from MySQL (%s): %d dimensions, %d concepts "
            "(primary dims=%s, contributing dims=%s)",
            settings.mysql_database,
            len(affinity),
            sum(len(v) for v in by_dimension.values()),
            sorted(primary),
            sorted(contributing),
        )


def build_concept_registry(*, layer_code: str = LAYER_CODE) -> StaticConceptRegistry:
    """Composition root: MySQL when configured and reachable, else static snapshot."""
    settings = Settings.load()
    if settings.mysql_host and settings.mysql_database:
        try:
            return MySQLConceptRegistry(settings, layer_code=layer_code)
        except Exception as exc:
            logger.warning(
                "Could not load svarupa_concept_layer from MySQL (%s); using static snapshot",
                exc,
            )
    affinity, primary, contributing, by_dimension = _static_layer_data(layer_code)
    return StaticConceptRegistry(
        layer_code=layer_code,
        by_dimension=by_dimension,
        affinity=affinity,
        primary_dimensions=primary,
        contributing_dimensions=contributing,
    )
