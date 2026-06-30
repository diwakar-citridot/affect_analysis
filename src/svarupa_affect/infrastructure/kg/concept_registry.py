"""Read-only concept registry from ``svarupa_concept_layer`` + ``svarupa_concepts`` (MySQL).

AFF applicability is defined by rows in ``svarupa_concept_layer`` where
``layer_code = 'AFF'``. Dimension affinity for the layer is the distinct set of
``dimension_id`` values tagged there.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

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
    "amarsha": "amarsa",
}

# Offline fallback when MySQL is unavailable (tests / local dev without DB).
_STATIC_AFFINITY: frozenset[int] = frozenset({2, 8, 9, 22, 24})
_STATIC_CONCEPTS: dict[int, dict[str, str]] = {
    2: {
        "sattva": "clarity / equanimity / ease in the field",
        "rajas": "restless activation / driven orienting energy",
        "tamas": "heaviness / inertia / obscured vitality",
    },
    8: {
        "rati": "abiding love / attraction / delight",
        "hasa": "mirth / amusement / laughter",
        "soka": "sorrow / grief held over time",
        "krodha": "anger / wrath",
        "utsaha": "energy / enthusiasm / heroic resolve",
        "bhaya": "fear / dread",
        "jugupsa": "disgust / aversion",
        "vismaya": "wonder / astonishment",
        "sama": "serenity / equanimity / quietude",
    },
    9: {
        "cinta": "anxious rumination / worry",
        "trasa": "sudden fright / alarm",
        "visada": "dejection / despondency",
        "dainya": "wretchedness / feeling lowly",
        "amarsa": "indignation / resentful impatience",
        "avega": "agitation / sudden disturbance",
        "harsa": "joy / gladness",
        "autsukya": "eager longing / anticipation",
        "dhrti": "contentment / steadfastness",
        "nirveda": "world-weariness / disillusion",
        "glani": "weakness / depletion",
    },
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


class StaticConceptRegistry:
    """In-memory AFF concept registry (offline fallback)."""

    def __init__(
        self,
        *,
        layer_code: str = LAYER_CODE,
        by_dimension: dict[int, dict[str, str]] | None = None,
        affinity: frozenset[int] | None = None,
    ) -> None:
        self.layer_code = layer_code
        self._by_dimension: dict[int, dict[str, str]] = {
            dim: dict(slugs) for dim, slugs in (by_dimension or _STATIC_CONCEPTS).items()
        }
        self._affinity = affinity or _STATIC_AFFINITY

    def affinity(self, layer_code: str | None = None) -> frozenset[int]:
        if layer_code and layer_code != self.layer_code:
            return frozenset()
        return self._affinity

    def concepts(self, dimension_id: int, layer_code: str | None = None) -> tuple[ConceptInfo, ...]:
        if layer_code and layer_code != self.layer_code:
            return ()
        table = self._by_dimension.get(dimension_id, {})
        return tuple(
            ConceptInfo(
                concept_id=0,
                dimension_id=dimension_id,
                slug=slug,
                name=slug.replace("_", " ").title(),
                gloss=gloss,
            )
            for slug, gloss in sorted(table.items())
        )

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
            gloss = table.get(canonical_slug(attr), "")
            if gloss:
                out[attr] = gloss
        return out


def _load_from_mysql(
    settings: Settings, layer_code: str
) -> tuple[frozenset[int], dict[int, dict[str, ConceptInfo]]]:
    sql = """
        SELECT
            c.concept_id,
            cl.dimension_id,
            c.slug,
            c.name,
            COALESCE(NULLIF(TRIM(c.description), ''), c.name) AS gloss
        FROM svarupa_concept_layer cl
        JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
        WHERE cl.layer_code = %s
        ORDER BY cl.dimension_id, c.sort_order, c.slug
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
    for row in rows:
        dim_id = int(row["dimension_id"])
        affinity.add(dim_id)
        slug = str(row["slug"])
        info = ConceptInfo(
            concept_id=int(row["concept_id"]),
            dimension_id=dim_id,
            slug=slug,
            name=str(row["name"]),
            gloss=str(row["gloss"] or row["name"]),
        )
        by_dimension.setdefault(dim_id, {})[slug] = info

    return frozenset(affinity), by_dimension


class MySQLConceptRegistry(StaticConceptRegistry):
    """Loads AFF-tagged concepts from MySQL at construction time."""

    def __init__(self, settings: Settings, *, layer_code: str = LAYER_CODE) -> None:
        affinity, by_dimension = _load_from_mysql(settings, layer_code)
        gloss_tables = {
            dim: {slug: info.gloss for slug, info in concepts.items()}
            for dim, concepts in by_dimension.items()
        }
        super().__init__(layer_code=layer_code, by_dimension=gloss_tables, affinity=affinity)
        self._concepts = by_dimension
        logger.info(
            "Loaded AFF concept registry from MySQL (%s): %d dimensions, %d concepts",
            settings.mysql_database,
            len(affinity),
            sum(len(v) for v in by_dimension.values()),
        )

    def concepts(self, dimension_id: int, layer_code: str | None = None) -> tuple[ConceptInfo, ...]:
        if layer_code and layer_code != self.layer_code:
            return ()
        return tuple(sorted(self._concepts.get(dimension_id, {}).values(), key=lambda c: c.slug))


def build_concept_registry(*, layer_code: str = LAYER_CODE) -> StaticConceptRegistry:
    """Composition root: MySQL when configured and reachable, else static fallback."""
    settings = Settings.load()
    if settings.mysql_host and settings.mysql_database:
        try:
            return MySQLConceptRegistry(settings, layer_code=layer_code)
        except Exception as exc:
            logger.warning(
                "Could not load svarupa_concept_layer from MySQL (%s); using static seed",
                exc,
            )
    return StaticConceptRegistry(layer_code=layer_code)
