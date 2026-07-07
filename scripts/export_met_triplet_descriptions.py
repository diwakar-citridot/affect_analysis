#!/usr/bin/env python3
"""Export MET (Metaphor layer) per-status triplet descriptions to
``data/kg/met_triplet_descriptions.v1.json``.

For every concept tagged ``layer_code = 'MET'`` with ``role = 'primary'`` in
``svarupa_concept_layer``, this emits the ``svarupa_concept_descriptions`` text
for **all three statuses** (deficiency / balance / excess). The Metaphor layer
maps a metaphor's source domain onto the felt-quality ontology carried by its
primary dimensions:

    D1  Pañca Mahābhūtas   — Five Great Elements (elemental)
    D5  Pañca Kośa         — Five Sheaths (structural)
    D6  Subtle Energies    — Prāṇa / Chakras / Nāḍīs (energetic)
    D15 Vāta·Pitta·Kapha   — Tridosha (energetic/constitutional)

The ``perspective`` axis in the DB is duplicated (identical text across
perspectives), so it is de-duplicated here to one description per
(concept, status); a missing status is emitted as ``null`` with a ``coverage``
flag so gaps are explicit.

This snapshot is the LLM grounding vocabulary for metaphor analysis — a pinned,
versioned artifact rather than a live DB read in the request path. Regenerate it
after KG changes. Mirrors ``export_aff_triplet_descriptions.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

LAYER_CODE = "MET"
# Focus: only the layer's PRIMARY dimensions carry the metaphor target ontology.
ROLE_FILTER = "primary"

OUT_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "kg" / "met_triplet_descriptions.v1.json"
)

STATUSES = ("deficiency", "balance", "excess")
# When de-duplicating identical-per-perspective rows, prefer this perspective.
PREFERRED_PERSPECTIVE = "overview"


def export_triplet_descriptions(*, out_path: Path = OUT_PATH) -> dict[str, object]:
    settings = Settings.load()
    if not settings.mysql_host or not settings.mysql_database:
        raise RuntimeError("MySQL is not configured")

    sql = """
        SELECT cl.dimension_id, cl.role, c.concept_id, c.slug, c.name,
               s.code AS status, cd.perspective, cd.description
          FROM svarupa_concept_layer cl
          JOIN svarupa_concepts c ON c.concept_id = cl.concept_id
          LEFT JOIN svarupa_concept_descriptions cd ON cd.concept_id = c.concept_id
          LEFT JOIN svarupa_status s ON s.status_id = cd.status_id
         WHERE cl.layer_code = %s AND cl.role = %s
         ORDER BY cl.dimension_id, c.slug
    """
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (LAYER_CODE, ROLE_FILTER))
            rows = cur.fetchall()
    finally:
        conn.close()

    # concept_id -> aggregate; per-status candidate descriptions (dedup by perspective)
    concepts: dict[int, dict[str, object]] = {}
    # (concept_id, status) -> {perspective: text}
    candidates: dict[tuple[int, str], dict[str, str]] = {}

    for row in rows:
        cid = int(row["concept_id"])
        c = concepts.get(cid)
        if c is None:
            c = {
                "concept_id": cid,
                "dimension_id": int(row["dimension_id"]),
                "slug": str(row["slug"]),
                "name": str(row["name"]),
                "role": str(row["role"]),
            }
            concepts[cid] = c

        status = row["status"]
        desc = row["description"]
        if status is None or desc is None or not str(desc).strip():
            continue
        candidates.setdefault((cid, str(status)), {})[
            str(row["perspective"] or "")
        ] = str(desc).strip()

    def pick(cid: int, status: str) -> str | None:
        by_persp = candidates.get((cid, status))
        if not by_persp:
            return None
        if PREFERRED_PERSPECTIVE in by_persp:
            return by_persp[PREFERRED_PERSPECTIVE]
        # perspectives are identical in practice; fall back to the longest defensively
        return max(by_persp.values(), key=len)

    out_concepts = []
    for cid in sorted(concepts):
        c = concepts[cid]
        descriptions = {st: pick(cid, st) for st in STATUSES}
        coverage = {st: descriptions[st] is not None for st in STATUSES}
        out_concepts.append(
            {**c, "descriptions": descriptions, "coverage": coverage}
        )

    affinity = sorted({c["dimension_id"] for c in out_concepts})
    total_statuses = len(out_concepts) * len(STATUSES)
    filled = sum(sum(c["coverage"].values()) for c in out_concepts)  # type: ignore[misc]

    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "layer_code": LAYER_CODE,
        "role_filter": ROLE_FILTER,
        "source_table": f"{settings.mysql_database}.svarupa_concept_descriptions",
        "statuses": list(STATUSES),
        "primary_dimensions": affinity,
        "coverage_summary": {
            "concepts": len(out_concepts),
            "status_slots": total_statuses,
            "filled": filled,
            "missing": total_statuses - filled,
        },
        "concepts": out_concepts,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    payload = export_triplet_descriptions()
    cs = payload["coverage_summary"]  # type: ignore[index]
    print(f"Wrote {cs['concepts']} concept(s) to {OUT_PATH}")  # type: ignore[index]
    print(f"primary_dimensions={payload['primary_dimensions']}")
    print(
        f"status coverage: {cs['filled']}/{cs['status_slots']} filled, "  # type: ignore[index]
        f"{cs['missing']} missing"  # type: ignore[index]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
