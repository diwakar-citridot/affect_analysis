#!/usr/bin/env python3
"""Migrate dimension/concept data from companion CMS to assistant_v1 schema.

Source: SVARUPA_MYSQL_DATABASE_COMPANION (svarupa_companion_v2)
Target: SVARUPA_MYSQL_DATABASE_MASTER  (svarupa_assistant_v1)

Steps:
  1. svarupa_dimension_merged   -> svarupa_dimensions
  2. svarupa_concept_merged (deduped) -> svarupa_concepts
  3. DDL on svarupa_concepts: drop physical/emotional/mental if present; add perspective
  4. svarupa_concept_merged rows  -> svarupa_concept_descriptions
     (perspective, status -> status_id; description_new when present else description)
  5. DDL on svarupa_concept_descriptions: drop physical/emotional/mental; add perspective;
     widen unique key to (concept_id, status_id, perspective)
  6. Create svarupa_concept_layer and migrate from svarupa_layers

Run from repo root (``pymysql`` required; see ``requirements.txt``)::

    PYTHONPATH=src:. python scripts/migration/migrate_companion_to_assistant.py
    PYTHONPATH=src:. python scripts/migration/migrate_companion_to_assistant.py --dry-run
    PYTHONPATH=src:. python -m scripts.migration --dry-run
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from svarupa_affect.infrastructure.config import _dotenv_path, load_dotenv  # noqa: E402

logger = logging.getLogger(__name__)

# Companion dimension.id -> assistant dimension_id (see sql/003_migrate_companion_to_assistant.sql).
# IDs 1-19: legacy CMS ordering (explicit remap). IDs 20+: resolved by slug match against
# TARGET_DIMENSIONS, then 1:1 spec-id fallback when the companion id is a known D-number.
COMPANION_DIM_TO_TARGET: dict[int, int] = {
    1: 10,  # paths_of_engagement
    2: 6,  # chakras -> subtle_energies
    3: 4,  # seven_layers_of_consciousness
    4: 15,  # tridosha
    5: 13,  # cyclical_evolution_of_consciousness
    6: 2,  # trigunas
    7: 18,  # jyotish_shastra
    8: 5,  # pancha_koshas
    9: 3,  # manasika_prakriti
    10: 6,  # nadis -> subtle_energies
    11: 1,  # pancha_mahabhutas
    12: 7,  # phenomenological_dimensions -> phenomenology
    13: 6,  # prana_vayus -> subtle_energies
    14: 12,  # samskaras -> architecture_of_inner_life
    15: 8,  # sthayibhavas
    16: 16,  # svabhava_svadharma
    17: 9,  # vyabhicaribhavas
    18: 11,  # ashtanga_yoga
    19: 14,  # yuga_cycles
}

# Canonical registry rows for mapped dimensions (sql/001_svarupa_dimensions_concepts.sql).
TARGET_DIMENSIONS: dict[int, tuple[str, str, str, str, str | None]] = {
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
    9: ("vyabhicaribhavas", "Thirty-Three Transient States", "Vyabhicārībhāvas", "Affective", None),
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
    18: ("jyotish_shastra", "Science of Cosmic Light", "Jyotiṣ Śāstra", "Cosmological", None),
    17: (
        "three_lenses",
        "Three Lenses",
        "Adhibhautika · Adhidaivika · Ādhyātmika",
        "Perceptual & Epistemic",
        None,
    ),
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
    25: ("upasanas_vidyas", "Upanishadic Meditations", "Upāsanās & Vidyās", "Soteriological", None),
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
    31: (
        "reserved_d31",
        "Reserved (D31)",
        None,
        "Reserved",
        "Ratified open slot — registry grows by config, not redesign",
    ),
}

BALANCE_STATUSES = frozenset({"neutral", "balanced", "medium"})
FACET_COLUMNS = ("physical", "emotional", "mental")
DESCRIPTION_BATCH_SIZE = 100

# Companion dimension slug -> target dimension_id (merged / renamed slugs not in svarupa_dimension_merged).
DIMENSION_SLUG_ALIASES: dict[str, int] = {
    "phenomenological_dimensions": 7,
    "chakras": 6,
    "nadis": 6,
    "prana_vayus": 6,
    "samskaras": 12,
}

# svarupa_layers.layer -> svarupa_layer.layer_code
LAYER_CODE_MAP: dict[str, str] = {
    "affect_analysis": "AFF",
    "metaphor_analysis": "MET",
    "narrative_arc": "NAR",
    "psycholinguistic": "PSY",
    "phenomenological": "PHE",
}


@dataclass(frozen=True)
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    companion_db: str
    master_db: str


def _slug_to_name(slug: str) -> str:
    return re.sub(r"\s+", " ", slug.replace("_", " ")).strip().title()


def load_db_config() -> DbConfig:
    load_dotenv(_dotenv_path())
    host = os.environ.get("SVARUPA_MYSQL_HOST")
    user = os.environ.get("SVARUPA_MYSQL_USER")
    password = os.environ.get("SVARUPA_MYSQL_PASSWORD")
    companion_db = os.environ.get("SVARUPA_MYSQL_DATABASE_COMPANION")
    master_db = os.environ.get("SVARUPA_MYSQL_DATABASE_MASTER")
    missing = [
        name
        for name, value in (
            ("SVARUPA_MYSQL_HOST", host),
            ("SVARUPA_MYSQL_USER", user),
            ("SVARUPA_MYSQL_PASSWORD", password),
            ("SVARUPA_MYSQL_DATABASE_COMPANION", companion_db),
            ("SVARUPA_MYSQL_DATABASE_MASTER", master_db),
        )
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
    return DbConfig(
        host=host,
        port=int(os.environ.get("SVARUPA_MYSQL_PORT", "3306")),
        user=user,
        password=password,
        companion_db=companion_db,
        master_db=master_db,
    )


def connect(cfg: DbConfig, database: str) -> Connection[DictCursor]:
    return pymysql.connect(
        host=cfg.host,
        port=cfg.port,
        user=cfg.user,
        password=cfg.password,
        database=database,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=30,
        read_timeout=600,
        write_timeout=600,
    )


def commit_phase(conn: Connection[DictCursor], phase: str, *, dry_run: bool) -> None:
    if dry_run:
        conn.rollback()
        logger.debug("Dry run — rolled back after phase: %s", phase)
        return
    conn.commit()
    logger.info("Committed phase: %s", phase)


def warn_blocking_transactions(conn: Connection[DictCursor]) -> None:
    """Surface stale InnoDB transactions that can block DELETE on svarupa_concepts."""
    with conn.cursor() as cur:
        try:
            cur.execute("""
                SELECT trx_mysql_thread_id, trx_started, trx_tables_locked, trx_rows_locked
                FROM information_schema.innodb_trx
                WHERE trx_tables_locked > 0
                """)
            rows = cur.fetchall()
        except pymysql.Error:
            return
    for row in rows:
        logger.warning(
            "Open InnoDB transaction (thread=%s, started=%s, tables_locked=%s, "
            "rows_locked=%s) may block this migration — kill the stale session first.",
            row["trx_mysql_thread_id"],
            row["trx_started"],
            row["trx_tables_locked"],
            row["trx_rows_locked"],
        )


def table_columns(conn: Connection[DictCursor], table: str) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(f"SHOW COLUMNS FROM `{table}`")
        return {str(row["Field"]) for row in cur.fetchall()}


def drop_columns_if_present(
    conn: Connection[DictCursor], table: str, columns: tuple[str, ...], *, dry_run: bool
) -> None:
    existing = table_columns(conn, table)
    for column in columns:
        if column not in existing:
            continue
        sql = f"ALTER TABLE `{table}` DROP COLUMN `{column}`"
        logger.info("DDL: %s", sql)
        if not dry_run:
            with conn.cursor() as cur:
                cur.execute(sql)


def add_column_if_absent(
    conn: Connection[DictCursor],
    table: str,
    column: str,
    definition: str,
    *,
    dry_run: bool,
) -> None:
    if column in table_columns(conn, table):
        return
    sql = f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}"
    logger.info("DDL: %s", sql)
    if not dry_run:
        with conn.cursor() as cur:
            cur.execute(sql)


def index_names(conn: Connection[DictCursor], table: str) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(f"SHOW INDEX FROM `{table}`")
        return {str(row["Key_name"]) for row in cur.fetchall()}


def ensure_concepts_schema(conn: Connection[DictCursor], *, dry_run: bool) -> None:
    drop_columns_if_present(conn, "svarupa_concepts", FACET_COLUMNS, dry_run=dry_run)
    add_column_if_absent(
        conn,
        "svarupa_concepts",
        "perspective",
        "VARCHAR(32) NULL AFTER `description`",
        dry_run=dry_run,
    )


def ensure_concept_descriptions_schema(conn: Connection[DictCursor], *, dry_run: bool) -> None:
    drop_columns_if_present(conn, "svarupa_concept_descriptions", FACET_COLUMNS, dry_run=dry_run)
    add_column_if_absent(
        conn,
        "svarupa_concept_descriptions",
        "perspective",
        "VARCHAR(32) NOT NULL DEFAULT 'non_spiritual' AFTER `status_id`",
        dry_run=dry_run,
    )
    keys = index_names(conn, "svarupa_concept_descriptions")
    # fk_desc_concept may use uq_desc_concept_status as its supporting index; add a
    # dedicated index on concept_id before dropping that unique key (MySQL error 1553).
    if "uq_desc_concept_status" in keys and "ix_desc_concept" not in keys:
        sql = (
            "ALTER TABLE `svarupa_concept_descriptions` "
            "ADD INDEX `ix_desc_concept` (`concept_id`)"
        )
        logger.info("DDL: %s", sql)
        if not dry_run:
            with conn.cursor() as cur:
                cur.execute(sql)
        keys = index_names(conn, "svarupa_concept_descriptions")

    if "uq_desc_concept_status" in keys:
        sql = "ALTER TABLE `svarupa_concept_descriptions` " "DROP INDEX `uq_desc_concept_status`"
        logger.info("DDL: %s", sql)
        if not dry_run:
            with conn.cursor() as cur:
                cur.execute(sql)
        keys = index_names(conn, "svarupa_concept_descriptions")

    if "uq_desc_concept_status_perspective" not in keys:
        sql = (
            "ALTER TABLE `svarupa_concept_descriptions` "
            "ADD UNIQUE KEY `uq_desc_concept_status_perspective` "
            "(`concept_id`, `status_id`, `perspective`)"
        )
        logger.info("DDL: %s", sql)
        if not dry_run:
            with conn.cursor() as cur:
                cur.execute(sql)


def table_exists(conn: Connection[DictCursor], table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES LIKE %s", (table,))
        return cur.fetchone() is not None


def ensure_concept_layer_schema(conn: Connection[DictCursor], *, dry_run: bool) -> None:
    if table_exists(conn, "svarupa_concept_layer"):
        return
    sql = """
        CREATE TABLE svarupa_concept_layer (
            dimension_id TINYINT UNSIGNED NOT NULL,
            concept_id   INT UNSIGNED     NOT NULL,
            layer_code   VARCHAR(8)       NOT NULL,
            created_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (concept_id, layer_code),
            KEY ix_concept_layer_dimension (dimension_id),
            KEY ix_concept_layer_layer (layer_code),
            CONSTRAINT fk_concept_layer_dimension FOREIGN KEY (dimension_id)
                REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
            CONSTRAINT fk_concept_layer_concept FOREIGN KEY (concept_id)
                REFERENCES svarupa_concepts (concept_id) ON DELETE CASCADE,
            CONSTRAINT fk_concept_layer_layer FOREIGN KEY (layer_code)
                REFERENCES svarupa_layer (layer_code) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    logger.info("DDL: CREATE TABLE svarupa_concept_layer")
    if not dry_run:
        with conn.cursor() as cur:
            cur.execute(sql)


def _target_slug_index() -> dict[str, int]:
    index: dict[str, int] = {slug: dim_id for dim_id, (slug, *_) in TARGET_DIMENSIONS.items()}
    index.update(DIMENSION_SLUG_ALIASES)
    return index


def build_companion_dim_map(companion: Connection[DictCursor]) -> dict[int, int]:
    """Map companion ``svarupa_dimension_merged.id`` -> assistant ``dimension_id``."""
    mapping = dict(COMPANION_DIM_TO_TARGET)
    slug_index = _target_slug_index()
    unmapped: list[tuple[int, str]] = []

    with companion.cursor() as cur:
        cur.execute("SELECT id, dimension FROM svarupa_dimension_merged ORDER BY id")
        for row in cur.fetchall():
            companion_id = int(row["id"])
            if companion_id in mapping:
                continue
            slug = str(row["dimension"]).strip()
            target_id = slug_index.get(slug)
            if target_id is None and companion_id in TARGET_DIMENSIONS:
                target_id = companion_id
            if target_id is not None:
                mapping[companion_id] = target_id
                logger.debug(
                    "Resolved companion dimension id=%s slug=%r -> target_id=%s",
                    companion_id,
                    slug,
                    target_id,
                )
            else:
                unmapped.append((companion_id, slug))

    for companion_id, slug in unmapped:
        logger.warning(
            "Skipping unmapped companion dimension id=%s (slug=%r)",
            companion_id,
            slug,
        )
    return mapping


def build_dimension_slug_map(
    companion: Connection[DictCursor],
    master: Connection[DictCursor],
    companion_dim_map: dict[int, int],
) -> dict[str, int]:
    mapping: dict[str, int] = {}
    with companion.cursor() as cur:
        cur.execute("SELECT id, dimension FROM svarupa_dimension_merged")
        for row in cur.fetchall():
            target_id = companion_dim_map.get(int(row["id"]))
            if target_id is not None:
                mapping[str(row["dimension"])] = target_id
    mapping.update(DIMENSION_SLUG_ALIASES)
    with master.cursor() as cur:
        cur.execute("SELECT dimension_id, slug FROM svarupa_dimensions")
        for row in cur.fetchall():
            mapping.setdefault(str(row["slug"]), int(row["dimension_id"]))
    return mapping


def load_concept_id_map(master: Connection[DictCursor]) -> dict[tuple[int, str], int]:
    with master.cursor() as cur:
        cur.execute("SELECT concept_id, dimension_id, slug FROM svarupa_concepts")
        return {
            (int(row["dimension_id"]), str(row["slug"])): int(row["concept_id"])
            for row in cur.fetchall()
        }


def fetch_source_layers(companion: Connection[DictCursor]) -> list[dict[str, Any]]:
    sql = """
        SELECT layer, dimension, attribute, created_at, updated_at
        FROM svarupa_layers
        ORDER BY dimension, attribute, layer
    """
    with companion.cursor() as cur:
        cur.execute(sql)
        return list(cur.fetchall())


def migrate_concept_layers(
    master: Connection[DictCursor],
    source_rows: list[dict[str, Any]],
    dimension_slug_map: dict[str, int],
    concept_id_map: dict[tuple[int, str], int],
    *,
    dry_run: bool,
) -> tuple[int, int]:
    if not dry_run:
        with master.cursor() as cur:
            cur.execute("DELETE FROM svarupa_concept_layer")

    insert_sql = """
        INSERT INTO svarupa_concept_layer
            (dimension_id, concept_id, layer_code, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            dimension_id = VALUES(dimension_id),
            updated_at = VALUES(updated_at)
    """
    inserted = 0
    skipped = 0
    with master.cursor() as cur:
        for row in source_rows:
            layer_code = LAYER_CODE_MAP.get(str(row["layer"]))
            if layer_code is None:
                logger.warning("Unmapped layer %r", row["layer"])
                skipped += 1
                continue

            dimension_slug = str(row["dimension"]).strip()
            target_dim = dimension_slug_map.get(dimension_slug)
            if target_dim is None:
                logger.warning("Unmapped dimension slug %r for layer row", dimension_slug)
                skipped += 1
                continue

            attribute = str(row["attribute"]).strip()
            if not attribute:
                skipped += 1
                continue

            concept_id = concept_id_map.get((target_dim, attribute))
            if concept_id is None:
                logger.debug(
                    "No concept for dimension_id=%s slug=%r (source %s)",
                    target_dim,
                    attribute,
                    dimension_slug,
                )
                skipped += 1
                continue

            params = (
                target_dim,
                concept_id,
                layer_code,
                row.get("created_at"),
                row.get("updated_at"),
            )
            if not dry_run:
                cur.execute(insert_sql, params)
            inserted += 1
    return inserted, skipped


def build_status_map(conn: Connection[DictCursor]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    with conn.cursor() as cur:
        cur.execute("SELECT status_id, code, legacy_aliases FROM svarupa_status")
        for row in cur.fetchall():
            status_id = int(row["status_id"])
            mapping[str(row["code"])] = status_id
            aliases = row.get("legacy_aliases")
            if aliases:
                for alias in str(aliases).split(","):
                    alias = alias.strip()
                    if alias:
                        mapping[alias] = status_id
    # Jyotish-specific companion statuses not covered by legacy_aliases.
    mapping.setdefault("benefic", mapping.get("balance", 2))
    mapping.setdefault("malefic", mapping.get("deficiency", 1))
    return mapping


def migrate_dimensions(
    companion: Connection[DictCursor],
    master: Connection[DictCursor],
    companion_dim_map: dict[int, int],
    *,
    dry_run: bool,
) -> int:
    with companion.cursor() as cur:
        cur.execute("SELECT id, dimension FROM svarupa_dimension_merged ORDER BY id")
        source_rows = cur.fetchall()

    upsert_sql = """
        INSERT INTO svarupa_dimensions
            (dimension_id, slug, name, sanskrit_term, family, is_reserved, notes)
        VALUES (%s, %s, %s, %s, %s, 0, %s)
        ON DUPLICATE KEY UPDATE
            slug = VALUES(slug),
            name = VALUES(name),
            sanskrit_term = VALUES(sanskrit_term),
            family = VALUES(family),
            notes = VALUES(notes)
    """
    count = 0
    with master.cursor() as cur:
        for row in source_rows:
            companion_id = int(row["id"])
            target_id = companion_dim_map.get(companion_id)
            if target_id is None:
                continue
            canonical = TARGET_DIMENSIONS.get(target_id)
            if canonical is None:
                logger.warning(
                    "No canonical metadata for target dimension_id=%s (companion id=%s)",
                    target_id,
                    companion_id,
                )
                continue
            slug, name, sanskrit_term, family, notes = canonical
            params = (target_id, slug, name, sanskrit_term, family, notes)
            logger.debug("Upsert dimension %s <- companion %s (%s)", target_id, companion_id, slug)
            if not dry_run:
                cur.execute(upsert_sql, params)
            count += 1
    return count


def _source_concept_description_text(row: dict[str, Any]) -> str | None:
    text = row.get("description_new") or row.get("description")
    if text is None:
        return None
    text = str(text).strip()
    return text or None


def fetch_source_concepts(companion: Connection[DictCursor]) -> list[dict[str, Any]]:
    columns = table_columns(companion, "svarupa_concept_merged")
    select_cols = ["id", "dimension_id", "concept", "perspective", "status", "description"]
    if "description_new" in columns:
        select_cols.append("description_new")
    sql = f"""
        SELECT {", ".join(select_cols)}
        FROM svarupa_concept_merged
        ORDER BY dimension_id, concept, perspective, status, id
    """
    with companion.cursor() as cur:
        cur.execute(sql)
        return list(cur.fetchall())


def pick_overview_description(rows: list[dict[str, Any]]) -> str | None:
    for row in rows:
        if row.get("perspective") != "non_spiritual":
            continue
        if row.get("status") not in BALANCE_STATUSES:
            continue
        text = _source_concept_description_text(row)
        if text:
            return str(text)
    for row in rows:
        if row.get("perspective") == "non_spiritual":
            text = _source_concept_description_text(row)
            if text:
                return str(text)
    for row in rows:
        text = _source_concept_description_text(row)
        if text:
            return str(text)
    return None


def group_source_concepts(
    rows: list[dict[str, Any]],
    companion_dim_map: dict[int, int],
) -> dict[tuple[int, str], list[dict[str, Any]]]:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for row in rows:
        companion_dim = int(row["dimension_id"])
        target_dim = companion_dim_map.get(companion_dim)
        if target_dim is None:
            continue
        slug = str(row["concept"]).strip()
        if not slug:
            continue
        key = (target_dim, slug)
        grouped.setdefault(key, []).append(row)
    return grouped


def migrate_concepts(
    master: Connection[DictCursor],
    grouped: dict[tuple[int, str], list[dict[str, Any]]],
    *,
    dry_run: bool,
) -> dict[tuple[int, str], int]:
    target_dim_ids = sorted({dim_id for dim_id, _ in grouped})
    concept_id_map: dict[tuple[int, str], int] = {}

    if target_dim_ids:
        placeholders = ",".join(["%s"] * len(target_dim_ids))
        logger.info(
            "Replacing concepts for dimension_ids=%s (%d keys)",
            target_dim_ids,
            len(grouped),
        )
        if not dry_run:
            warn_blocking_transactions(master)
            with master.cursor() as cur:
                if table_exists(master, "svarupa_concept_layer"):
                    logger.info("Deleting existing concept_layer rows for mapped dimensions…")
                    cur.execute(
                        f"""
                        DELETE cl FROM svarupa_concept_layer cl
                        INNER JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
                        WHERE c.dimension_id IN ({placeholders})
                        """,
                        target_dim_ids,
                    )
                    logger.info("Deleted %d concept_layer rows", cur.rowcount)

                logger.info("Deleting existing concept_descriptions for mapped dimensions…")
                cur.execute(
                    f"""
                    DELETE cd FROM svarupa_concept_descriptions cd
                    INNER JOIN svarupa_concepts c ON c.concept_id = cd.concept_id
                    WHERE c.dimension_id IN ({placeholders})
                    """,
                    target_dim_ids,
                )
                logger.info("Deleted %d concept_description rows", cur.rowcount)

                logger.info("Deleting existing concepts for mapped dimensions…")
                cur.execute(
                    f"DELETE FROM svarupa_concepts WHERE dimension_id IN ({placeholders})",
                    target_dim_ids,
                )
                logger.info("Deleted %d concept rows", cur.rowcount)

    insert_sql = """
        INSERT INTO svarupa_concepts
            (dimension_id, slug, name, sanskrit_term, description, sort_order)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    insert_params: list[tuple[Any, ...]] = []
    sort_counters: dict[int, int] = {}

    for (target_dim, slug), variants in sorted(grouped.items()):
        sort_counters[target_dim] = sort_counters.get(target_dim, 0) + 1
        display_name = _slug_to_name(slug)
        overview = pick_overview_description(variants)
        insert_params.append(
            (
                target_dim,
                slug,
                display_name,
                display_name,
                overview,
                sort_counters[target_dim],
            )
        )
        concept_id_map[(target_dim, slug)] = -1

    if not dry_run and insert_params:
        logger.info("Inserting %d concepts…", len(insert_params))
        with master.cursor() as cur:
            cur.executemany(insert_sql, insert_params)
        logger.info("Concept inserts complete")

    return concept_id_map


def resolve_description(row: dict[str, Any]) -> str | None:
    return _source_concept_description_text(row)


def _concept_description_params(
    row: dict[str, Any],
    concept_id_map: dict[tuple[int, str], int],
    status_map: dict[str, int],
    companion_dim_map: dict[int, int],
) -> tuple[tuple[Any, ...] | None, str | None]:
    companion_dim = int(row["dimension_id"])
    target_dim = companion_dim_map.get(companion_dim)
    if target_dim is None:
        return None, "dimension"
    slug = str(row["concept"]).strip()
    concept_id = concept_id_map.get((target_dim, slug))
    if concept_id is None:
        return None, "concept"

    status = row.get("status")
    if status is None:
        return None, "status"
    status_id = status_map.get(str(status))
    if status_id is None:
        logger.warning("Unmapped status %r for concept %s/%s", status, target_dim, slug)
        return None, "status"

    perspective = row.get("perspective")
    if not perspective:
        return None, "perspective"

    description = resolve_description(row)
    if description is None:
        return None, "description"

    return (concept_id, status_id, perspective, description), None


def migrate_concept_descriptions(
    master: Connection[DictCursor],
    source_rows: list[dict[str, Any]],
    concept_id_map: dict[tuple[int, str], int],
    status_map: dict[str, int],
    companion_dim_map: dict[int, int],
    *,
    dry_run: bool,
) -> tuple[int, int]:
    insert_sql = """
        INSERT INTO svarupa_concept_descriptions
            (concept_id, status_id, perspective, description)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            description = VALUES(description)
    """
    pending: list[tuple[Any, ...]] = []
    inserted = 0
    skipped = 0

    def flush_batch() -> None:
        nonlocal inserted
        if dry_run or not pending:
            inserted += len(pending)
            pending.clear()
            return
        with master.cursor() as cur:
            cur.executemany(insert_sql, pending)
        inserted += len(pending)
        pending.clear()

    logger.info("Migrating up to %d concept_description rows…", len(source_rows))
    for row in source_rows:
        params, _skip_reason = _concept_description_params(
            row, concept_id_map, status_map, companion_dim_map
        )
        if params is None:
            skipped += 1
            continue

        pending.append(params)
        if len(pending) >= DESCRIPTION_BATCH_SIZE:
            flush_batch()
            if inserted % (DESCRIPTION_BATCH_SIZE * 5) == 0:
                logger.info("Concept descriptions progress: %d rows", inserted)

    flush_batch()
    logger.info("Concept descriptions migration pass complete")
    return inserted, skipped


def run_migration(*, dry_run: bool) -> None:
    cfg = load_db_config()
    companion = connect(cfg, cfg.companion_db)
    master = connect(cfg, cfg.master_db)

    try:
        logger.info(
            "Migrating %s -> %s (dry_run=%s)",
            cfg.companion_db,
            cfg.master_db,
            dry_run,
        )

        ensure_concepts_schema(master, dry_run=dry_run)
        ensure_concept_descriptions_schema(master, dry_run=dry_run)
        ensure_concept_layer_schema(master, dry_run=dry_run)
        commit_phase(master, "schema", dry_run=dry_run)

        companion_dim_map = build_companion_dim_map(companion)
        dimension_slug_map = build_dimension_slug_map(companion, master, companion_dim_map)

        dim_count = migrate_dimensions(
            companion, master, companion_dim_map, dry_run=dry_run
        )
        logger.info("Dimensions upserted: %d", dim_count)
        commit_phase(master, "dimensions", dry_run=dry_run)

        source_rows = fetch_source_concepts(companion)
        grouped = group_source_concepts(source_rows, companion_dim_map)
        logger.info(
            "Source concept rows=%d; unique target concepts=%d",
            len(source_rows),
            len(grouped),
        )

        concept_id_map = migrate_concepts(master, grouped, dry_run=dry_run)
        commit_phase(master, "concepts", dry_run=dry_run)
        if not dry_run:
            concept_id_map = load_concept_id_map(master)
        elif not concept_id_map or all(v == -1 for v in concept_id_map.values()):
            concept_id_map = load_concept_id_map(master)

        status_map = build_status_map(master)
        inserted, skipped = migrate_concept_descriptions(
            master,
            source_rows,
            concept_id_map,
            status_map,
            companion_dim_map,
            dry_run=dry_run,
        )
        logger.info("Concept descriptions inserted/updated: %d (skipped: %d)", inserted, skipped)
        commit_phase(master, "concept_descriptions", dry_run=dry_run)

        layer_rows = fetch_source_layers(companion)
        layer_inserted, layer_skipped = migrate_concept_layers(
            master,
            layer_rows,
            dimension_slug_map,
            concept_id_map,
            dry_run=dry_run,
        )
        logger.info(
            "Concept layer rows inserted/updated: %d (skipped: %d)",
            layer_inserted,
            layer_skipped,
        )

        if dry_run:
            master.rollback()
            logger.info("Dry run complete — no changes committed.")
        else:
            master.commit()
            logger.info("Migration committed successfully.")
    except Exception:
        master.rollback()
        raise
    finally:
        companion.close()
        master.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions and roll back without persisting changes.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        force=True,
    )
    run_migration(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
