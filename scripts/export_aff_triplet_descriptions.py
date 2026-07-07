#!/usr/bin/env python3
"""Export AFF per-status triplet descriptions to
``data/kg/aff_triplet_descriptions.v1.json``.

For every concept tagged ``layer_code = 'AFF'`` in ``svarupa_concept_layer``,
this emits the ``svarupa_concept_descriptions`` text for **all three statuses**
(deficiency / balance / excess). The ``perspective`` axis in the DB is fully
duplicated (identical text across perspectives), so it is de-duplicated here to
one description per (concept, status); a missing status is emitted as ``null``
with a ``coverage`` flag so gaps (e.g. many D9 transient states) are explicit.

This snapshot is the LLM grounding vocabulary for affect analysis — a pinned,
versioned artifact rather than a live DB read in the request path. Regenerate it
after KG changes, alongside ``export_aff_concept_layer.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect import LAYER_CODE
from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

OUT_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "kg" / "aff_triplet_descriptions.v1.json"
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
                "roles": set(),
            }
            concepts[cid] = c
        c["roles"].add(str(row["role"]))  # type: ignore[attr-defined]

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
        roles = c.pop("roles")  # type: ignore[assignment]
        role = "primary" if "primary" in roles else "contributing"
        descriptions = {st: pick(cid, st) for st in STATUSES}
        coverage = {st: descriptions[st] is not None for st in STATUSES}
        out_concepts.append(
            {
                **c,
                "role": role,
                "descriptions": descriptions,
                "coverage": coverage,
            }
        )

    affinity = sorted({c["dimension_id"] for c in out_concepts})
    total_statuses = len(out_concepts) * len(STATUSES)
    filled = sum(sum(c["coverage"].values()) for c in out_concepts)  # type: ignore[misc]

    payload: dict[str, object] = {
        "schema_version": "1.0.0",
        "layer_code": LAYER_CODE,
        "source_table": f"{settings.mysql_database}.svarupa_concept_descriptions",
        "statuses": list(STATUSES),
        "affinity_dimensions": affinity,
        "primary_dimensions": sorted(
            {c["dimension_id"] for c in out_concepts if c["role"] == "primary"}
        ),
        "contributing_dimensions": sorted(
            {c["dimension_id"] for c in out_concepts if c["role"] == "contributing"}
        ),
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
    print(f"affinity_dimensions={payload['affinity_dimensions']}")
    print(
        f"status coverage: {cs['filled']}/{cs['status_slots']} filled, "  # type: ignore[index]
        f"{cs['missing']} missing"  # type: ignore[index]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
