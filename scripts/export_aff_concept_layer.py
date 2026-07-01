#!/usr/bin/env python3
"""Export ``svarupa_concept_layer`` AFF rows to ``data/kg/aff_concept_layer.v1.json``."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect import LAYER_CODE
from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "kg" / "aff_concept_layer.v1.json"


def export_concept_layer(*, out_path: Path = OUT_PATH) -> dict[str, object]:
    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError("MySQL is not configured")

    sql = """
        SELECT c.concept_id, cl.dimension_id, c.slug, c.name, cl.role,
               COALESCE(NULLIF(TRIM(c.description), ''), c.name) AS gloss
          FROM svarupa_concept_layer cl
          JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
         WHERE cl.layer_code = %s
         ORDER BY cl.dimension_id, cl.role DESC, c.slug
    """
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (LAYER_CODE,))
            rows = cur.fetchall()
    finally:
        conn.close()

    concepts = [
        {
            "concept_id": int(row["concept_id"]),
            "dimension_id": int(row["dimension_id"]),
            "slug": str(row["slug"]),
            "name": str(row["name"]),
            "role": str(row["role"]),
            "gloss": str(row["gloss"] or row["name"]),
        }
        for row in rows
    ]
    affinity = sorted({c["dimension_id"] for c in concepts})
    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "layer_code": LAYER_CODE,
        "source_table": f"{settings.mysql_database}.svarupa_concept_layer",
        "affinity_dimensions": affinity,
        "primary_dimensions": sorted(
            {c["dimension_id"] for c in concepts if c["role"] == "primary"}
        ),
        "contributing_dimensions": sorted(
            {c["dimension_id"] for c in concepts if c["role"] == "contributing"}
        ),
        "concepts": concepts,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = export_concept_layer()
    n = len(payload["concepts"])  # type: ignore[arg-type]
    print(f"Wrote {n} concept(s) to {OUT_PATH}")
    print(f"affinity_dimensions={payload['affinity_dimensions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
