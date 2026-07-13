"""Read-only dimension labels from ``svarupa_dimensions`` (MySQL) with a static seed fallback.

API responses expose ``dimension_name`` using ``sanskrit_term`` (not the English ``name``).
"""

from __future__ import annotations

import logging

from ..config import Settings
from .mysql_client import open_mysql

logger = logging.getLogger("svarupa_affect.dimension_registry")

# Seeded from sql/001_svarupa_dimensions_concepts.sql (``sanskrit_term`` column).
_STATIC_DIMENSION_NAMES: dict[int, str] = {
    1: "Pañca Mahābhūtas",
    2: "Triguṇa — Sattva·Rajas·Tamas",
    3: "Mānasika Prakṛti",
    4: "Sapta Bhūmikā / Planes",
    5: "Pañca Kośa",
    6: "Prāṇa Vāyus · Chakras · Nāḍīs",
    7: "Phenomenology of Experience",
    8: "Sthāyībhāvas",
    9: "Vyabhicārībhāvas",
    10: "Karma · Jñāna · Rāja · Bhakti",
    11: "Aṣṭāṅga Yoga",
    12: "Karma · Saṁskāra · Vāsanā · Eṣaṇā",
    13: "Kāla Chakra (individual)",
    14: "Yuga (collective time)",
    15: "Vāta · Pitta · Kapha",
    16: "Svabhāva & Svadharma",
    17: "Adhibhautika · Adhidaivika · Ādhyātmika",
    18: "Jyotiṣ Śāstra",
    19: "Pañca Kleśa",
    20: "Pañca Vṛtti",
    21: "Antarāyas",
    22: "Brahmavihāras",
    23: "Sādhana Chatuṣṭaya",
    24: "Daivī & Āsurī Sampat",
    25: "Upāsanās & Vidyās",
    26: "Haṭha Disciplines",
    27: "Advaita Darśana",
    28: "Pramāṇa & Jñāna",
    29: "Bandha & Mokṣa",
    30: "Sādhanas",
    31: "Reserved (D31)",
}


class StaticDimensionRegistry:
    """In-memory registry from the seeded SQL snapshot."""

    def __init__(self, names: dict[int, str] | None = None) -> None:
        self._names = dict(names or _STATIC_DIMENSION_NAMES)

    def name_for(self, dimension_id: int) -> str:
        return self._names.get(dimension_id, f"dimension_{dimension_id}")

    def id_for_name(self, dimension_name: str) -> int | None:
        """Resolve dimension_id from sanskrit_term label (exact, then prefix match)."""
        needle = dimension_name.strip().lower()
        if not needle:
            return None
        exact: int | None = None
        prefix: int | None = None
        for dim_id, label in self._names.items():
            label_lower = label.lower()
            if label_lower == needle:
                return dim_id
            head = label_lower.split("—")[0].strip()
            if label_lower.startswith(needle) or needle.startswith(head):
                prefix = dim_id
        return prefix


def _load_names_from_mysql(settings: Settings) -> dict[int, str]:
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError("MySQL host/database not configured")

    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT dimension_id,
                       COALESCE(NULLIF(TRIM(sanskrit_term), ''), name) AS dimension_label
                  FROM svarupa_dimensions
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    if not rows:
        raise RuntimeError("svarupa_dimensions returned no rows")

    return {int(row["dimension_id"]): str(row["dimension_label"]) for row in rows}


class MySQLDimensionRegistry(StaticDimensionRegistry):
    """Loads ``dimension_id -> sanskrit_term`` from MySQL at construction time."""

    def __init__(self, settings: Settings) -> None:
        names = _load_names_from_mysql(settings)
        super().__init__(names)
        logger.info(
            "Loaded %d dimension labels (sanskrit_term) from MySQL (%s)",
            len(names),
            settings.mysql_database,
        )


def build_dimension_registry() -> StaticDimensionRegistry:
    """Composition root: MySQL when configured and reachable, else static seed."""
    settings = Settings.load()
    if settings.mysql_host and settings.mysql_database:
        try:
            return MySQLDimensionRegistry(settings)
        except Exception as exc:
            logger.warning(
                "Could not load svarupa_dimensions from MySQL (%s); using static seed",
                exc,
            )
    return StaticDimensionRegistry()
