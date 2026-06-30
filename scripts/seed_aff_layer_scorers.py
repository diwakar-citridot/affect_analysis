#!/usr/bin/env python3
"""Create ``svarupa_layer_scorer`` tables and seed AFF scorer rows.

Usage:
    python scripts/seed_aff_layer_scorers.py
    python scripts/seed_aff_layer_scorers.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

logger = logging.getLogger("seed_aff_layer_scorers")

AFF_LAYER = "AFF"

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS svarupa_layer_scorer (
        scorer_id       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
        layer_code      VARCHAR(8)        NOT NULL,
        dimension_id    TINYINT UNSIGNED  NOT NULL,
        scorer_slug     VARCHAR(64)       NOT NULL,
        scorer_kind     ENUM('field_native', 'hypothesis_bridge') NOT NULL,
        data_ref        VARCHAR(191)      NOT NULL,
        pole_map_ref    VARCHAR(191)      NULL,
        modulator_ref   VARCHAR(191)      NULL,
        emits_signals   TINYINT(1)        NOT NULL DEFAULT 1,
        sort_order      TINYINT UNSIGNED  NOT NULL DEFAULT 0,
        created_at      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (scorer_id),
        UNIQUE KEY uq_layer_scorer_dim (layer_code, dimension_id),
        KEY ix_scorer_layer (layer_code),
        CONSTRAINT fk_scorer_dimension FOREIGN KEY (dimension_id)
            REFERENCES svarupa_dimensions (dimension_id) ON DELETE CASCADE,
        CONSTRAINT fk_scorer_layer FOREIGN KEY (layer_code)
            REFERENCES svarupa_layer (layer_code) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS svarupa_layer_scorer_concept (
        scorer_id   SMALLINT UNSIGNED NOT NULL,
        concept_id  INT UNSIGNED      NOT NULL,
        created_at  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (scorer_id, concept_id),
        KEY ix_scorer_concept_concept (concept_id),
        CONSTRAINT fk_scorer_concept_scorer FOREIGN KEY (scorer_id)
            REFERENCES svarupa_layer_scorer (scorer_id) ON DELETE CASCADE,
        CONSTRAINT fk_scorer_concept_concept FOREIGN KEY (concept_id)
            REFERENCES svarupa_concepts (concept_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]

AFF_SCORER_ROWS = [
    (2, "guna_field", "field_native", "field/guna_synthesis.v1.json", "pole_maps/d2_poles.v1.json", None, 1, 1),
    (8, "hyp2sthayi", "hypothesis_bridge", "bridge/hyp2sthayi.v2.json", "pole_maps/d8_poles.v1.json", "bridge/guna_families.v1.json", 1, 2),
    (9, "hyp2vyabhi", "hypothesis_bridge", "bridge/hyp2vyabhi.v2.json", None, "bridge/guna_families.v1.json", 1, 3),
    (22, "brahmavihara_tone", "field_native", "field/guna_synthesis.v1.json", None, None, 0, 4),
    (24, "daivi_asuri_tone", "field_native", "field/guna_synthesis.v1.json", None, None, 0, 5),
]


def seed_layer_scorers(*, dry_run: bool = False) -> None:
    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError("MySQL is not configured (SVARUPA_MYSQL_HOST / SVARUPA_MYSQL_DATABASE)")

    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            if not dry_run:
                for ddl in DDL_STATEMENTS:
                    cur.execute(ddl)

            if dry_run:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM svarupa_layer_scorer WHERE layer_code = %s",
                    (AFF_LAYER,),
                )
                logger.info("DRY-RUN: would replace %s AFF scorer row(s)", cur.fetchone()["n"])
                return

            cur.execute(
                """
                DELETE sc FROM svarupa_layer_scorer_concept sc
                  JOIN svarupa_layer_scorer s ON s.scorer_id = sc.scorer_id
                 WHERE s.layer_code = %s
                """,
                (AFF_LAYER,),
            )
            cur.execute("DELETE FROM svarupa_layer_scorer WHERE layer_code = %s", (AFF_LAYER,))

            cur.execute(
                "SELECT dimension_id FROM svarupa_dimensions WHERE dimension_id IN %s",
                ([row[0] for row in AFF_SCORER_ROWS],),
            )
            valid_dims = {int(r["dimension_id"]) for r in cur.fetchall()}

            insert_scorer = """
                INSERT INTO svarupa_layer_scorer
                    (layer_code, dimension_id, scorer_slug, scorer_kind, data_ref,
                     pole_map_ref, modulator_ref, emits_signals, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for row in AFF_SCORER_ROWS:
                if row[0] not in valid_dims:
                    logger.warning("Skipping D%s scorer — dimension not in svarupa_dimensions", row[0])
                    continue
                cur.execute(insert_scorer, (AFF_LAYER, *row))

            cur.execute(
                """
                INSERT INTO svarupa_layer_scorer_concept (scorer_id, concept_id)
                SELECT s.scorer_id, cl.concept_id
                  FROM svarupa_layer_scorer s
                  JOIN svarupa_concept_layer cl
                    ON cl.layer_code = s.layer_code AND cl.dimension_id = s.dimension_id
                 WHERE s.layer_code = %s
                """,
                (AFF_LAYER,),
            )

            cur.execute(
                """
                SELECT s.dimension_id, s.scorer_slug, s.emits_signals,
                       COUNT(sc.concept_id) AS n_concepts
                  FROM svarupa_layer_scorer s
                  LEFT JOIN svarupa_layer_scorer_concept sc ON sc.scorer_id = s.scorer_id
                 WHERE s.layer_code = %s
                 GROUP BY s.scorer_id
                 ORDER BY s.sort_order
                """,
                (AFF_LAYER,),
            )
            for row in cur.fetchall():
                logger.info(
                    "D%s %s emits=%s concepts=%s",
                    row["dimension_id"],
                    row["scorer_slug"],
                    row["emits_signals"],
                    row["n_concepts"],
                )
        conn.commit()
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    seed_layer_scorers(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
