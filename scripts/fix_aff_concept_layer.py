#!/usr/bin/env python3
"""Reconcile ``svarupa_concept_layer`` rows for AFF (Multi-Axis Affect Analysis).

Deletes all existing AFF tags and re-inserts one row per concept in the spec
affinity dimensions {2, 8, 9, 22, 24}. Erroneous tags (e.g. D5 kośa, D6, D15) are
removed. Dimensions with no concepts in ``svarupa_concepts`` are skipped.

Usage:
    python scripts/fix_aff_concept_layer.py
    python scripts/fix_aff_concept_layer.py --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Allow running from repo root without install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

logger = logging.getLogger("fix_aff_concept_layer")

AFF_LAYER_CODE = "AFF"
AFF_DIMENSION_IDS = (2, 8, 9, 22, 24)


def _count_by_dimension(conn, *, layer_code: str) -> dict[int, int]:
    sql = """
        SELECT dimension_id, COUNT(*) AS n
          FROM svarupa_concept_layer
         WHERE layer_code = %s
         GROUP BY dimension_id
         ORDER BY dimension_id
    """
    with conn.cursor() as cur:
        cur.execute(sql, (layer_code,))
        return {int(row["dimension_id"]): int(row["n"]) for row in cur.fetchall()}


def fix_aff_concept_layer(*, dry_run: bool = False) -> tuple[int, int, dict[int, int]]:
    """Return (deleted_rows, inserted_rows, counts_after_by_dimension)."""
    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError("MySQL is not configured (SVARUPA_MYSQL_HOST / SVARUPA_MYSQL_DATABASE)")

    conn = open_mysql(settings)
    try:
        before = _count_by_dimension(conn, layer_code=AFF_LAYER_CODE)
        logger.info("AFF tags before: %s", before or "(none)")

        delete_sql = "DELETE FROM svarupa_concept_layer WHERE layer_code = %s"
        insert_sql = """
            INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code)
            SELECT c.dimension_id, c.concept_id, %s
              FROM svarupa_concepts c
             WHERE c.dimension_id IN %s
             ORDER BY c.dimension_id, c.sort_order, c.slug
        """

        with conn.cursor() as cur:
            if dry_run:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM svarupa_concept_layer WHERE layer_code = %s",
                    (AFF_LAYER_CODE,),
                )
                deleted = int(cur.fetchone()["n"])
                cur.execute(
                    """
                    SELECT COUNT(*) AS n FROM svarupa_concepts
                     WHERE dimension_id IN %s
                    """,
                    (AFF_DIMENSION_IDS,),
                )
                inserted = int(cur.fetchone()["n"])
            else:
                cur.execute(delete_sql, (AFF_LAYER_CODE,))
                deleted = cur.rowcount
                cur.execute(insert_sql, (AFF_LAYER_CODE, AFF_DIMENSION_IDS))
                inserted = cur.rowcount
                conn.commit()

        after = _count_by_dimension(conn, layer_code=AFF_LAYER_CODE) if not dry_run else {}
        if not dry_run:
            logger.info("AFF tags after: %s", after)
        return deleted, inserted, after
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report counts only; do not modify the database",
    )
    args = parser.parse_args(argv)

    deleted, inserted, after = fix_aff_concept_layer(dry_run=args.dry_run)
    mode = "would" if args.dry_run else ""
    print(
        f"{mode} delete {deleted} AFF row(s); {mode} insert {inserted} row(s) "
        f"for dimensions {list(AFF_DIMENSION_IDS)}"
    )
    if after:
        print("Counts by dimension after fix:")
        for dim_id in AFF_DIMENSION_IDS:
            print(f"  D{dim_id}: {after.get(dim_id, 0)} concept(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
