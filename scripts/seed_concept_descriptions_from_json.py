#!/usr/bin/env python3
"""Seed dimensions, concepts, and descriptions from dimension-attribute JSON.

Reads ``data/dimension_concepts/dimension_attribute_descriptions.v2.json`` and:

  1. Clears dependent rows, then ``svarupa_concepts`` / ``svarupa_dimensions``
  2. Inserts dimensions (JSON ``dimension_id`` / ``dimension_name`` + canonical
     slug / family / sanskrit_term from the 31-dimension registry)
  3. Inserts concepts from each attribute (``attribute_slug``, ``attribute``,
     ``sanskrit``, ``aspect``, ``coordinate`` → JSON column ``coordinate``)
  4. Inserts ``svarupa_concept_descriptions`` — one row per facet:

       - ``concept_id``  — newly inserted concept for ``(dimension_id, attribute_slug)``
       - ``status_id``   — ``svarupa_status`` for JSON status keys
         (``balanced`` / ``excess`` / ``deficient``)
       - ``perspective`` — facet key (``overview``, ``somatic``, …)
       - ``description`` — facet text

Clears (when present): ``svarupa_concept_descriptions``, ``svarupa_concept_layer``,
``svarupa_layer_scorer_concept``, ``svarupa_layer_scorer``,
``svarupa_dimension_dependency``, ``svarupa_concepts``, ``svarupa_dimensions``.

Re-seed layer affinity afterward if needed::

    PYTHONPATH=src python scripts/seed_concept_layer_from_excel.py
    PYTHONPATH=src python scripts/seed_aff_layer_scorers.py

Usage:
    PYTHONPATH=src python scripts/seed_concept_descriptions_from_json.py
    PYTHONPATH=src python scripts/seed_concept_descriptions_from_json.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

logger = logging.getLogger("seed_concept_descriptions_from_json")

DEFAULT_JSON = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "dimension_concepts"
    / "dimension_attribute_descriptions.v2.json"
)

# Canonical registry metadata (sql/001_svarupa_dimensions_concepts.sql).
# JSON supplies dimension_id + display name; slug/family/sanskrit come from here.
# tuple: (slug, english_name, sanskrit_term, family, notes)
CANONICAL_DIMENSIONS: dict[int, tuple[str, str, str | None, str, str | None]] = {
    1: ("pancha_mahabhutas", "Five Great Elements", "Pañca Mahābhūtas", "Constitutional", None),
    2: ("trigunas", "Three Gunas", "Triguṇa — Sattva·Rajas·Tamas", "Constitutional", None),
    3: ("manasika_prakriti", "Sixteen Faces of Mind", "Mānasika Prakṛti", "Constitutional", None),
    4: (
        "seven_layers_of_consciousness",
        "Seven Layers of Consciousness",
        "Sapta Bhūmikā / Planes",
        "Consciousness",
        None,
    ),
    5: ("pancha_koshas", "Five Sheaths", "Pañca Kośa", "Consciousness", None),
    6: (
        "subtle_energies",
        "Subtle Energies",
        "Prāṇa Vāyus · Chakras · Nāḍīs",
        "Consciousness",
        "Merges vāyus, chakras, nāḍīs",
    ),
    7: (
        "phenomenology",
        "Phenomenological Dimensions",
        "Phenomenology of Experience",
        "Phenomenological",
        None,
    ),
    8: ("sthayibhavas", "Nine Enduring Emotions", "Sthāyībhāvas", "Affective", None),
    9: (
        "vyabhicaribhavas",
        "Thirty-Three Transient States",
        "Vyabhicārībhāvas",
        "Affective",
        None,
    ),
    10: (
        "paths_of_engagement",
        "Paths of Engagement",
        "Karma · Jñāna · Rāja · Bhakti",
        "Path & Practice",
        None,
    ),
    11: ("ashtanga_yoga", "Eightfold Refinement", "Aṣṭāṅga Yoga", "Path & Practice", None),
    12: (
        "architecture_of_inner_life",
        "Architecture of Inner Life",
        "Karma · Saṁskāra · Vāsanā · Eṣaṇā",
        "Karmic & Temporal",
        None,
    ),
    13: (
        "cyclical_evolution_of_consciousness",
        "Cyclical Evolution of Consciousness",
        "Kāla Chakra (individual)",
        "Karmic & Temporal",
        None,
    ),
    14: ("yuga_cycles", "Yuga Cycles", "Yuga (collective time)", "Karmic & Temporal", None),
    15: ("tridosha", "Tridosha", "Vāta · Pitta · Kapha", "Constitutional", None),
    16: (
        "svabhava_svadharma",
        "Inner Nature & Its Law",
        "Svabhāva & Svadharma",
        "Karmic & Temporal",
        None,
    ),
    17: (
        "three_lenses",
        "Three Lenses",
        "Adhibhautika · Adhidaivika · Ādhyātmika",
        "Perceptual & Epistemic",
        None,
    ),
    18: ("jyotish_shastra", "Science of Cosmic Light", "Jyotiṣ Śāstra", "Cosmological", None),
    19: ("pancha_klesha", "Five Afflictions", "Pañca Kleśa", "Psychodynamic", None),
    20: (
        "pancha_vritti",
        "Five Modifications of Mind",
        "Pañca Vṛtti",
        "Psychodynamic",
        None,
    ),
    21: ("antarayas", "The Nine Obstacles", "Antarāyas", "Psychodynamic", None),
    22: ("brahmaviharas", "Four Sublime Attitudes", "Brahmavihāras", "Psychodynamic", None),
    23: (
        "sadhana_chatushtaya",
        "Fourfold Qualification",
        "Sādhana Chatuṣṭaya",
        "Ethical & Readiness",
        None,
    ),
    24: (
        "daivi_asuri_sampat",
        "Divine & Demoniacal Endowments",
        "Daivī & Āsurī Sampat",
        "Ethical & Readiness",
        None,
    ),
    25: (
        "upasanas_vidyas",
        "Upanishadic Meditations",
        "Upāsanās & Vidyās",
        "Soteriological",
        None,
    ),
    26: ("hatha_disciplines", "The Embodied Path", "Haṭha Disciplines", "Path & Practice", None),
    27: ("advaita_darshana", "The Non-Dual Vision", "Advaita Darśana", "Soteriological", None),
    28: (
        "ways_of_knowing",
        "The Ways of Knowing",
        "Pramāṇa & Jñāna",
        "Perceptual & Epistemic",
        None,
    ),
    29: (
        "bandha_moksha",
        "Anatomy of Bondage & Liberation",
        "Bandha & Mokṣa",
        "Soteriological",
        None,
    ),
    30: (
        "sadhana_practices",
        "Contemplative & Devotional Practice",
        "Sādhanas",
        "Path & Practice",
        None,
    ),
}

STATUS_KEY_TO_CODE: dict[str, str] = {
    "balanced": "balance",
    "balance": "balance",
    "excess": "excess",
    "excessive": "excess",
    "deficient": "deficiency",
    "deficiency": "deficiency",
}

# Child tables cleared before concepts / dimensions (existence-checked at runtime).
CLEAR_BEFORE_CONCEPTS = (
    "svarupa_concept_descriptions",
    "svarupa_concept_layer",
    "svarupa_layer_scorer_concept",
)
CLEAR_BEFORE_DIMENSIONS = (
    "svarupa_layer_scorer",
    "svarupa_dimension_dependency",
)

_EM_DASH_SPLIT = re.compile(r"\s*[—–-]\s*")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "dimensions" not in payload:
        raise ValueError(f"{path} is missing a top-level 'dimensions' array")
    return payload


def _table_exists(cur: Any, table: str) -> bool:
    cur.execute(
        """
        SELECT 1
          FROM information_schema.TABLES
         WHERE TABLE_SCHEMA = DATABASE()
           AND TABLE_NAME = %s
         LIMIT 1
        """,
        (table,),
    )
    return cur.fetchone() is not None


def _column_exists(cur: Any, table: str, column: str) -> bool:
    cur.execute(
        """
        SELECT 1
          FROM information_schema.COLUMNS
         WHERE TABLE_SCHEMA = DATABASE()
           AND TABLE_NAME = %s
           AND COLUMN_NAME = %s
         LIMIT 1
        """,
        (table, column),
    )
    return cur.fetchone() is not None


def _ensure_concepts_coordinate_column(cur: Any) -> None:
    """Add nullable JSON ``coordinate`` on ``svarupa_concepts`` when missing."""
    if not _table_exists(cur, "svarupa_concepts"):
        raise RuntimeError("svarupa_concepts table is missing")
    if _column_exists(cur, "svarupa_concepts", "coordinate"):
        return
    cur.execute(
        """
        ALTER TABLE `svarupa_concepts`
          ADD COLUMN `coordinate` JSON NULL
            AFTER `description`
        """
    )
    logger.info("added svarupa_concepts.coordinate (JSON)")


def _build_status_lookup(rows: list[dict[str, Any]]) -> dict[str, int]:
    lookup: dict[str, int] = {}
    for row in rows:
        status_id = int(row["status_id"])
        code = str(row["code"]).strip().lower()
        lookup[code] = status_id
        aliases = row.get("legacy_aliases") or ""
        for alias in str(aliases).split(","):
            key = alias.strip().lower()
            if key:
                lookup[key] = status_id
    for json_key, code in STATUS_KEY_TO_CODE.items():
        if json_key not in lookup and code in lookup:
            lookup[json_key] = lookup[code]
    return lookup


def _merge_facets(entries: list[dict[str, Any]]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for entry in entries:
        facets = entry.get("facets")
        if not isinstance(facets, dict):
            continue
        for key, value in facets.items():
            text = str(value or "").strip()
            if not text:
                continue
            perspective = str(key).strip()
            if perspective:
                merged[perspective] = text
    return merged


def _clean_sanskrit(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    # Drop trailing chapter / meta tails: "सत्त्व   ·   Chapter 14"
    text = re.split(r"\s*[·|]\s*", text, maxsplit=1)[0].strip()
    return text or None


def _parse_dimension_display(dimension_name: str) -> tuple[str, str | None]:
    """Split ``Sanskrit — English`` style titles when present."""
    name = dimension_name.strip()
    parts = _EM_DASH_SPLIT.split(name, maxsplit=1)
    if len(parts) == 2 and parts[0] and parts[1]:
        left, right = parts[0].strip(), parts[1].strip()
        # Prefer left as sanskrit when it looks non-ASCII-heavy / titled Sanskrit.
        if any(ord(ch) > 127 for ch in left) or any(
            ch in left for ch in ("ā", "ī", "ū", "ṛ", "ṅ", "ñ", "ṭ", "ḍ", "ṇ", "ś", "ṣ", "ḥ")
        ):
            return right, left
    return name, None


def _build_dimension_rows(payload: dict[str, Any]) -> list[tuple[Any, ...]]:
    rows: list[tuple[Any, ...]] = []
    for dimension in payload.get("dimensions") or []:
        dim_id = int(dimension["dimension_id"])
        json_name = str(dimension.get("dimension_name") or "").strip()
        if not json_name:
            raise ValueError(f"dimension_id={dim_id} missing dimension_name")

        canonical = CANONICAL_DIMENSIONS.get(dim_id)
        parsed_name, parsed_sanskrit = _parse_dimension_display(json_name)
        if canonical:
            slug, english_name, sanskrit_term, family, notes = canonical
            # Prefer JSON title for name; keep registry slug/family/sanskrit.
            name = json_name or english_name or parsed_name
            sanskrit = sanskrit_term or parsed_sanskrit
        else:
            slug = f"dimension_{dim_id}"
            name = json_name
            sanskrit = parsed_sanskrit
            family = "Unspecified"
            notes = "slug/family inferred; not in canonical registry"
            logger.warning("no canonical metadata for dimension_id=%s; using slug=%s", dim_id, slug)

        rows.append((dim_id, slug, name, sanskrit, family, 0, notes))
    return rows


def _coordinate_json(attr: dict[str, Any]) -> str | None:
    """Serialize attribute ``coordinate`` object for MySQL JSON column."""
    coordinate = attr.get("coordinate")
    if coordinate is None:
        return None
    if isinstance(coordinate, str):
        text = coordinate.strip()
        return text or None
    if isinstance(coordinate, dict):
        if not coordinate:
            return None
        return json.dumps(coordinate, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(coordinate, ensure_ascii=False, separators=(",", ":"))


def _build_concept_rows(payload: dict[str, Any]) -> list[tuple[Any, ...]]:
    """Return (dimension_id, slug, name, sanskrit, description, coordinate, sort_order)."""
    rows: list[tuple[Any, ...]] = []
    seen: set[tuple[int, str]] = set()
    for dimension in payload.get("dimensions") or []:
        dim_id = int(dimension["dimension_id"])
        for sort_order, attr in enumerate(dimension.get("attributes") or [], start=1):
            slug = str(attr.get("attribute_slug") or "").strip()
            if not slug:
                logger.warning("D%s attribute missing attribute_slug; skipping", dim_id)
                continue
            key = (dim_id, slug)
            if key in seen:
                logger.warning("duplicate attribute_slug D%s/%s; keeping first", dim_id, slug)
                continue
            seen.add(key)
            name = str(attr.get("attribute") or attr.get("title") or slug).strip()
            sanskrit = _clean_sanskrit(attr.get("sanskrit"))
            description = str(attr.get("aspect") or "").strip() or None
            coordinate = _coordinate_json(attr)
            rows.append((dim_id, slug, name, sanskrit, description, coordinate, sort_order))
    return rows


def _build_description_rows(
    payload: dict[str, Any],
    *,
    concepts: dict[tuple[int, str], int],
    status_ids: dict[str, int],
) -> tuple[list[tuple[int, int, str, str]], dict[str, int]]:
    pending: list[tuple[int, int, str, str]] = []
    stats = {
        "attributes": 0,
        "facet_rows": 0,
        "missing_concept": 0,
        "unknown_status": 0,
        "no_facets": 0,
        "empty_skipped": 0,
    }

    for dimension in payload.get("dimensions") or []:
        for attr in dimension.get("attributes") or []:
            stats["attributes"] += 1
            dim_id = int(attr["dimension_id"])
            slug = str(attr.get("attribute_slug") or "").strip()
            if not slug:
                stats["missing_concept"] += 1
                continue
            concept_id = concepts.get((dim_id, slug))
            if concept_id is None:
                stats["missing_concept"] += 1
                continue

            status_map = attr.get("status") or {}
            if not isinstance(status_map, dict):
                continue

            for status_key, entries in status_map.items():
                code_key = str(status_key).strip().lower()
                status_id = status_ids.get(code_key)
                if status_id is None:
                    mapped = STATUS_KEY_TO_CODE.get(code_key)
                    status_id = status_ids.get(mapped or "")
                if status_id is None:
                    stats["unknown_status"] += 1
                    logger.warning("unknown status key %r for %s", status_key, slug)
                    continue

                if not isinstance(entries, list):
                    entries = [entries]
                facets = _merge_facets(entries)
                if not facets:
                    stats["no_facets"] += 1
                    continue

                for perspective, description in facets.items():
                    if not description:
                        stats["empty_skipped"] += 1
                        continue
                    pending.append((concept_id, status_id, perspective, description))
                    stats["facet_rows"] += 1

    by_key: dict[tuple[int, int, str], str] = {}
    for concept_id, status_id, perspective, description in pending:
        by_key[(concept_id, status_id, perspective)] = description
    rows = [
        (concept_id, status_id, perspective, description)
        for (concept_id, status_id, perspective), description in by_key.items()
    ]
    stats["unique_rows"] = len(rows)
    stats["duplicate_collapsed"] = stats["facet_rows"] - len(rows)
    return rows, stats


def _clear_tables(cur: Any, tables: tuple[str, ...]) -> list[str]:
    cleared: list[str] = []
    for table in tables:
        if not _table_exists(cur, table):
            logger.info("skip clear (missing table): %s", table)
            continue
        cur.execute(f"DELETE FROM `{table}`")
        cleared.append(table)
        logger.info("cleared %s (%s row(s))", table, cur.rowcount)
    return cleared


def seed(*, json_path: Path, dry_run: bool = False) -> dict[str, int]:
    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError(
            "MySQL is not configured (SVARUPA_MYSQL_HOST / SVARUPA_MYSQL_DATABASE)"
        )

    payload = _load_json(json_path)
    dimension_rows = _build_dimension_rows(payload)
    concept_rows = _build_concept_rows(payload)

    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT status_id, code, legacy_aliases FROM svarupa_status")
            status_ids = _build_status_lookup(list(cur.fetchall()))

        # Description rows need concept_ids; in dry-run invent sequential ids.
        if dry_run:
            concepts = {
                (dim_id, slug): idx
                for idx, (dim_id, slug, *_rest) in enumerate(concept_rows, start=1)
            }
            desc_rows, desc_stats = _build_description_rows(
                payload, concepts=concepts, status_ids=status_ids
            )
            stats = {
                "dimensions": len(dimension_rows),
                "concepts": len(concept_rows),
                **desc_stats,
            }
            logger.info(
                "DRY RUN: would clear dependents + dimensions/concepts, then insert "
                "%d dimension(s), %d concept(s), %d description row(s) "
                "(no_facets=%d unknown_status=%d)",
                stats["dimensions"],
                stats["concepts"],
                stats["unique_rows"],
                stats["no_facets"],
                stats["unknown_status"],
            )
            logger.warning(
                "This wipe also clears concept_layer / layer_scorer rows when present; "
                "re-run seed_concept_layer_from_excel.py and seed_aff_layer_scorers.py after."
            )
            return stats

        with conn.cursor() as cur:
            _ensure_concepts_coordinate_column(cur)
            _clear_tables(cur, CLEAR_BEFORE_CONCEPTS)
            if _table_exists(cur, "svarupa_concepts"):
                cur.execute("DELETE FROM `svarupa_concepts`")
                logger.info("cleared svarupa_concepts (%s row(s))", cur.rowcount)
            _clear_tables(cur, CLEAR_BEFORE_DIMENSIONS)
            if _table_exists(cur, "svarupa_dimensions"):
                cur.execute("DELETE FROM `svarupa_dimensions`")
                logger.info("cleared svarupa_dimensions (%s row(s))", cur.rowcount)

            cur.executemany(
                """
                INSERT INTO svarupa_dimensions
                    (dimension_id, slug, name, sanskrit_term, family, is_reserved, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                dimension_rows,
            )
            logger.info("inserted %d dimension(s)", len(dimension_rows))

            cur.executemany(
                """
                INSERT INTO svarupa_concepts
                    (dimension_id, slug, name, sanskrit_term, description, coordinate, sort_order)
                VALUES (%s, %s, %s, %s, %s, CAST(%s AS JSON), %s)
                """,
                concept_rows,
            )
            logger.info("inserted %d concept(s)", len(concept_rows))

            cur.execute("SELECT concept_id, dimension_id, slug FROM svarupa_concepts")
            concepts = {
                (int(r["dimension_id"]), str(r["slug"])): int(r["concept_id"])
                for r in cur.fetchall()
            }

        desc_rows, desc_stats = _build_description_rows(
            payload, concepts=concepts, status_ids=status_ids
        )
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO svarupa_concept_descriptions
                    (concept_id, status_id, perspective, description)
                VALUES (%s, %s, %s, %s)
                """,
                desc_rows,
            )
        conn.commit()

        stats = {
            "dimensions": len(dimension_rows),
            "concepts": len(concept_rows),
            **desc_stats,
        }
        logger.info(
            "inserted %d description row(s); attrs=%d no_facets=%d missing_concept=%d",
            stats["unique_rows"],
            stats["attributes"],
            stats["no_facets"],
            stats["missing_concept"],
        )
        logger.warning(
            "Re-seed layer affinity if needed: "
            "seed_concept_layer_from_excel.py / seed_aff_layer_scorers.py"
        )
        return stats
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help="path to dimension_attribute_descriptions JSON",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="parse + report counts without writing to MySQL",
    )
    args = ap.parse_args()

    if not args.json.is_file():
        logger.error("JSON not found: %s", args.json)
        return 1

    stats = seed(json_path=args.json, dry_run=args.dry_run)
    if stats.get("dimensions", 0) == 0 or stats.get("concepts", 0) == 0:
        logger.error("no dimensions/concepts to insert")
        return 1
    if stats.get("unique_rows", 0) == 0:
        logger.error("no description rows to insert")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
