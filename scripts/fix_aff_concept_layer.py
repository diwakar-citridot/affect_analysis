#!/usr/bin/env python3
"""Reconcile ``svarupa_concept_layer`` rows for AFF (Multi-Axis Affect Analysis).

**Superseded** for normal workflows by the Excel-driven seeder:

    PYTHONPATH=src python scripts/seed_concept_layer_from_excel.py

That script is the source of truth (``Dimension & Attribute Mapping to Analytical
Layers.xlsx`` → ``svarupa_concept_layer`` with ``role``).

This utility remains for one-shot repair using the static snapshot in
``data/kg/aff_concept_layer.v1.json`` (export via ``scripts/export_aff_concept_layer.py``).

Usage:
    python scripts/fix_aff_concept_layer.py
    python scripts/fix_aff_concept_layer.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect import LAYER_CODE
from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

logger = logging.getLogger("fix_aff_concept_layer")

SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "data" / "kg" / "aff_concept_layer.v1.json"


def _load_snapshot_rows() -> list[tuple[int, int, str]]:
  """Return (dimension_id, concept_id, role) tuples from the offline snapshot."""
  raw = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
  return [
      (int(row["dimension_id"]), int(row["concept_id"]), str(row["role"]))
      for row in raw["concepts"]
  ]


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

    rows = _load_snapshot_rows()

    conn = open_mysql(settings)
    try:
        before = _count_by_dimension(conn, layer_code=LAYER_CODE)
        logger.info("AFF tags before: %s", before or "(none)")

        delete_sql = "DELETE FROM svarupa_concept_layer WHERE layer_code = %s"
        insert_sql = """
            INSERT INTO svarupa_concept_layer (dimension_id, concept_id, layer_code, role)
            VALUES (%s, %s, %s, %s)
        """

        with conn.cursor() as cur:
            if dry_run:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM svarupa_concept_layer WHERE layer_code = %s",
                    (LAYER_CODE,),
                )
                deleted = int(cur.fetchone()["n"])
                inserted = len(rows)
            else:
                cur.execute(delete_sql, (LAYER_CODE,))
                deleted = cur.rowcount
                for dim_id, concept_id, role in rows:
                    cur.execute(insert_sql, (dim_id, concept_id, LAYER_CODE, role))
                inserted = len(rows)
                conn.commit()

        after = _count_by_dimension(conn, layer_code=LAYER_CODE) if not dry_run else {}
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
    affinity_dims = sorted({dim for dim, _, _ in _load_snapshot_rows()})
    mode = "would" if args.dry_run else ""
    print(
        f"{mode} delete {deleted} AFF row(s); {mode} insert {inserted} row(s) "
        f"from snapshot {SNAPSHOT_PATH.name} (dimensions {affinity_dims})"
    )
    if after:
        print("Counts by dimension after fix:")
        for dim_id in affinity_dims:
            print(f"  D{dim_id}: {after.get(dim_id, 0)} concept(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
