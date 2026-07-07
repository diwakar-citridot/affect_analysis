#!/usr/bin/env python3
"""Patch nirveda deficiency/excess pole text for eval discrimination.

Pole descriptions are trimmed to ~700 chars in the LLM prefix, so the
discriminative clauses are placed first (after the ### header).

    PYTHONPATH=src python scripts/patch_nirveda_poles.py
    PYTHONPATH=src python scripts/export_aff_triplet_descriptions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.kg.mysql_client import open_mysql

PERSPECTIVE = "overview"

NIRVEDA_DEFICIENCY = """### The Deficiency

When Nirveda is deficient, the person cannot tolerate disillusionment—in themselves or others. When someone close expresses doubt, grief, or existential heaviness, they feel an urgent need to fix that mood or escape it, as though the heaviness were contagious and unbearable. This is reflex positivity and mood-repair, not bhaya (fear of harm) or trasa (panic). They bypass the other's questioning with cheer or solutions before it can be felt.

The Somatic Base: Surface buoyancy that never reaches depth—the body stays light or busy while hollowness runs underneath.

The Emotional Current: Unacknowledged anxiety beneath cheerfulness; intolerance of another's doubt or one's own emptiness.

The Cognitive Map: Reflexive positivity—'everything happens for a reason,' 'I must fix their mood,' 'thinking too much is the problem'—deflecting genuine questioning.

The Inner Presence: Disillusionment that should catalyze growth is suppressed; stagnation dressed as progress."""

NIRVEDA_EXCESS = """### The Excess

When Nirveda is excessive, disillusionment curdles into cynical contempt—not wistful inquiry. The person watches others striving with a cool, metallic distaste and settled certainty that their hustle is pointless, the wheel leads nowhere. Unlike balanced Nirveda (clean sadness, open questioning about one's own path), excess hardens into nihilistic ideology and superior withdrawal toward others' engagement.

The Somatic Base: The body feels leaden; a cool or metallic sensation may arise at the throat; eyes lose brightness; limbs move through thick air.

The Emotional Current: Contempt for the world's offerings and for others' striving—not bitter grief but cold certainty that nothing is worth the effort.

The Cognitive Map: Nihilistic narratives hardened into ideology: 'People are performing,' 'Success is an illusion,' 'I already know this leads nowhere.'

The Inner Presence: The invitation to deeper wisdom is refused; consciousness stuck in cynical resignation, neither inquiring nor re-engaging."""


def patch(*, dry_run: bool = False) -> None:
    settings = Settings.load()
    conn = open_mysql(settings)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT concept_id FROM svarupa_concepts WHERE slug = 'nirveda' AND dimension_id = 9"
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("nirveda concept not found")
            cid = int(row["concept_id"])
            cur.execute("SELECT status_id, code FROM svarupa_status WHERE code IN ('deficiency', 'excess')")
            status = {r["code"]: int(r["status_id"]) for r in cur.fetchall()}

        updates = {
            "deficiency": NIRVEDA_DEFICIENCY,
            "excess": NIRVEDA_EXCESS,
        }
        sql = """
            UPDATE svarupa_concept_descriptions
               SET description = %s
             WHERE concept_id = %s AND status_id = %s AND perspective = %s
        """
        for code, text in updates.items():
            if dry_run:
                print(f"DRY RUN: would update nirveda/{code} ({len(text)} chars)")
                print(text[:400], "...\n")
                continue
            with conn.cursor() as cur:
                cur.executemany(
                    sql,
                    [(text, cid, status[code], PERSPECTIVE)],
                )
                if cur.rowcount == 0:
                    cur.execute(
                        """
                        INSERT INTO svarupa_concept_descriptions
                            (concept_id, status_id, perspective, description)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (cid, status[code], PERSPECTIVE, text),
                    )
            print(f"Updated nirveda/{code} ({len(text)} chars)")
        if not dry_run:
            conn.commit()
    finally:
        conn.close()


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    patch(dry_run=args.dry_run)
    if not args.dry_run:
        print("Regenerate snapshot: PYTHONPATH=src python scripts/export_aff_triplet_descriptions.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
