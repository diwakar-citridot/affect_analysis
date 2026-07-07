#!/usr/bin/env python3
"""Generate the MET (Metaphor layer) coverage eval set with an LLM.

Mirrors the AFF coverage workflow: emit first-person passages, each labelled with
the ``(expected_dimension, expected_concept, expected_state)`` triplet it targets,
in the same API-ready JSONL schema that ``scripts/bulk_analyze.py`` consumes and
``scripts/score_coverage.py`` scores.

The twist for MET: every passage must carry a **live, imagistic metaphor** whose
*source* domain maps onto the metaphor layer's primary ontology, and whose felt
quality unmistakably sits at the target pole:

    D1  Pañca Mahābhūtas  — Five Great Elements   (water → "drowning" / "parched")
    D5  Pañca Kośa        — Five Sheaths           (which layer of self the image is of)
    D6  Subtle Energies   — Prāṇa                  ("drained", "buzzing", "flat battery")
    D15 Vāta·Pitta·Kapha  — Tridosha               ("burning", "scattered", "leaden")

Cells are the covered ``(dimension, concept, state)`` triplets in
``data/kg/met_triplet_descriptions.v1.json`` (a status with no KG description is
skipped — it has no grounding to author against). ``--n`` is spread as evenly as
possible across those cells, so the same script gives you a 50-question smoke set
or the full ~500 by changing one number. The pole description is fed to the model
as grounding; the passage may not name the concept, element, dosha, or Sanskrit.

Output is resumable: existing ids in ``--output`` are kept and only missing cells
are (re)generated, unless ``--force`` is passed.

Examples:
  # 50-question smoke set (~1 per covered cell):
  bash scripts/run_api.sh --help >/dev/null   # (needs AWS creds for Bedrock)
  .venv/bin/python scripts/generate_met_coverage.py --n 50 \
    --output data/eval/met_coverage_questions_50.jsonl

  # full set (~11 per covered cell):
  .venv/bin/python scripts/generate_met_coverage.py --n 500 \
    --output data/eval/met_coverage_questions.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from svarupa_affect.infrastructure.config import Settings
from svarupa_affect.infrastructure.llm.bedrock_provider import BedrockLLMProvider

TRIPLETS_PATH = ROOT / "data" / "kg" / "met_triplet_descriptions.v1.json"
STATES = ("deficiency", "balance", "excess")

# Fallback per-dimension steer for the *source imagery* the model should reach for.
_DIMENSION_HINT = {
    1: "the concrete physical imagery of one great element",
    5: "imagery that locates the experience in one specific layer of the self",
    6: "imagery of vital energy and charge",
    15: "constitutional imagery of one dosha",
}

# Per-concept source-image family, keyed by KG slug. This BINDS each cell to a
# single image domain so the passage's metaphor lands on the intended concept
# (and pole) rather than drifting into a neighbouring element — the metaphor
# analyzer maps the *actual* source image, so a "fire" image in an "earth" cell
# is a mislabel. Each entry spans all three poles; the pole hint narrows it.
_CONCEPT_HINT = {
    # D1 — Five Great Elements: one element only, never substitute another.
    "water": "flowing water ONLY — rivers, tides, floods, rain, the sea, currents; "
             "or its lack — drought, a parched throat, cracked dry ground, a dried-up well",
    "fire": "fire and heat ONLY — flames, embers, a furnace, wildfire, molten or "
            "searing heat; or its lack — cold ash, a guttering candle, a dead hearth",
    "earth": "solid earth ONLY — soil, rock, mountain, roots, mud, clay, stone, "
             "weight and groundedness; or its lack — dust, shifting sand, no ground underfoot",
    "air": "moving air ONLY — wind, gusts, breeze, storm-winds, being scattered to "
           "the winds; or its lack — dead still stagnant air, airlessness, suffocation",
    "ether": "open space ONLY — vast sky, boundless room, the void, echoing empty "
             "halls; or its lack — cramped, walled-in, boxed, no room left to exist",
    # D15 — Tridosha: each dosha's own constitutional signature (do not borrow another).
    "vata": "dry, cold, MOVING wind — restless gusts, scattering, brittleness, "
            "things drying and cracking, ceaseless erratic motion; in deficiency the "
            "wind falls to a dead, static, frozen stillness",
    "pitta": "FIRE and heat — burning, searing, molten intensity, acid, a blade "
             "heated white, glare; in deficiency a fire guttered down to cold grey ash",
    "kapha": "damp, HEAVY earth — mud, wet clay, stone, sludge, fog, ballast, thick "
             "slow weight, sinking; in deficiency that solid ground crumbled to dry dust",
    # D5 — Five Sheaths: imagery of that LAYER of self, NOT raw single elements
    # (avoid plain drowning/burning, which read as D1 water/fire).
    "annamaya_kosha": "the physical body as a vessel — flesh and bone, hunger and "
                      "food, the body as a house, husk or garment (sturdy and "
                      "well-fed, a starved hollow shell, or an idol obsessively polished)",
    "ananda_mimamsa": "the innermost sheath of joy — a warm hearth-glow of "
                      "contentment, a deep still wellspring of sweetness, an "
                      "overflowing cup (quietly full, run dry, or a giddy honeyed "
                      "intoxication that blots out everything else)",
    "anandamaya": "the innermost sheath of joy — a warm hearth-glow of contentment, "
                  "a deep still wellspring of sweetness, an overflowing cup (quietly "
                  "full, run dry, or a giddy honeyed intoxication that blots out all else)",
    "anandamaya_vidya": "the innermost sheath of joy known clearly — a steady inner "
                        "radiance, a wellspring of sweet contentment (luminously full, "
                        "gone dark and dry, or a dazzling flood that overwhelms discernment)",
    "five_koshas": "the layered self as nested vessels — sheaths, veils, garments or "
                   "nesting rooms wrapped over a still centre (aligned and clear, or "
                   "one layer swollen and crowding out the rest)",
    "four_states_and_five_sheaths": "the layered self as nested sheaths with a "
                                    "witnessing centre — veils or panes of glass "
                                    "stacked over a quiet watcher (all clear and "
                                    "aligned, or clouded and crowding the centre out)",
    # D6 — Subtle energy / prāṇa.
    "prana": "vital charge — a battery, a current, an electric hum, a spring's "
             "tension, fuel for a flame (fully charged and humming, steadily "
             "flowing, drained flat to empty, or surging past control into overload)",
}

_POLE_HINT = {
    "deficiency": "the quality is depleted, blocked, flat, drained, dried-up or "
                  "absent — the source image is one of lack (parched, burnt-out, "
                  "hollow, an ember gone cold)",
    "balance": "the quality is present and well-proportioned — the source image is "
               "one of easy flow, steady warmth, groundedness or graceful motion",
    "excess": "the quality is overwhelming, flooding or over-activated — the source "
              "image is one of too-much (drowning, on fire, buried, storm-tossed)",
}

_SYSTEM = (
    "You author evaluation passages for a metaphor-recognition system. Each passage "
    "is a short first-person account of an inner experience, expressed through a "
    "LIVE, vivid metaphor. Your passages become the gold set that tests whether the "
    "system can recover the metaphor's source imagery and the felt pole it evokes.\n\n"
    "Hard rules for every passage:\n"
    "- 1 to 3 sentences, first person ('I ...'), natural and specific to a moment.\n"
    "- Built around at least one live, imagistic metaphor — the experience is said "
    "through the imagery of another domain ('I'm drowning', 'burnt to a cinder', "
    "'stuck fast in the mud'). Avoid dead / conventional metaphors ('grasp an idea', "
    "'run out of time') — those carry no felt image.\n"
    "- Do NOT name the target concept, its Sanskrit term, the element, the dosha, or "
    "the sheath. Do NOT use clinical, diagnostic or self-labelling language. Show the "
    "experience through the image only.\n"
    "- Vary the situation, register and imagery across passages — no two alike.\n"
    "Output JSON only, matching the schema."
)

_SCHEMA = {
    "type": "object",
    "required": ["passages"],
    "properties": {
        "passages": {"type": "array", "items": {"type": "string"}},
    },
}


def load_cells() -> list[dict]:
    """Covered (dimension, concept, state) cells with their pole description."""
    payload = json.loads(TRIPLETS_PATH.read_text(encoding="utf-8"))
    cells: list[dict] = []
    for c in payload["concepts"]:
        for st in STATES:
            if c["coverage"].get(st) and c["descriptions"].get(st):
                cells.append(
                    {
                        "dimension": int(c["dimension_id"]),
                        "concept": str(c["slug"]),
                        "name": str(c["name"]),
                        "state": st,
                        "description": str(c["descriptions"][st]),
                    }
                )
    return cells


def allocate(keys: list, n: int) -> dict:
    """Spread n across keys as evenly as possible (no per-key cap: the LLM can
    author any count). Extra remainder is handed out one-per-key in stable order."""
    alloc = {k: n // len(keys) for k in keys} if keys else {}
    for k in sorted(keys)[: n % len(keys)] if keys else []:
        alloc[k] += 1
    return alloc


def build_prompt(cell: dict, count: int) -> str:
    hint = _CONCEPT_HINT.get(cell["concept"]) or _DIMENSION_HINT.get(
        cell["dimension"], "vivid physical imagery"
    )
    pole = _POLE_HINT[cell["state"]]
    # Trim the grounding so we keep the salient felt-quality cues without a wall.
    grounding = cell["description"].strip()
    if len(grounding) > 1200:
        grounding = grounding[:1200].rsplit("\n", 1)[0] + " …"
    return (
        f"Write {count} distinct evaluation passages.\n\n"
        f"Each passage's metaphor must draw its SOURCE image from: {hint}.\n"
        "Stay strictly inside that one image family — do NOT substitute a "
        "different element or domain (e.g. no fire imagery in an earth passage), "
        "or the passage is mislabelled.\n"
        f"The felt quality (pole) it must evoke is '{cell['state']}': {pole}.\n\n"
        "The imagery below describes what this pole feels like. Use it ONLY to steer "
        "the mood and choose apt images — never quote it, and never name the concept:\n"
        f'"""{grounding}"""\n\n'
        f'Return JSON: {{"passages": ["...", "..."]}} with exactly {count} passages.'
    )


async def generate_cell(
    provider: BedrockLLMProvider,
    cell: dict,
    count: int,
    *,
    model_id: str,
    batch: int,
    timeout_s: float,
    sem: asyncio.Semaphore,
) -> list[str]:
    passages: list[str] = []
    remaining = count
    attempt_budget = 0
    while remaining > 0 and attempt_budget < count + 2 * batch:
        take = min(batch, remaining)
        prompt = build_prompt(cell, take)
        async with sem:
            try:
                data = await provider.complete_json(
                    system=_SYSTEM,
                    prompt=prompt,
                    schema=_SCHEMA,
                    model_id=model_id,
                    temperature=1.0,
                    timeout_s=timeout_s,
                    max_tokens=4096,
                    request_id=f"met-gen-{cell['concept']}-{cell['state']}",
                )
            except Exception as exc:  # noqa: BLE001 - report and keep going
                print(
                    f"  ! {cell['concept']}/{cell['state']}: {type(exc).__name__}: {exc}",
                    file=sys.stderr,
                )
                break
        got = [str(p).strip() for p in (data.get("passages") or []) if str(p).strip()]
        passages.extend(got)
        remaining = count - len(passages)
        attempt_budget += take
        if not got:  # model returned nothing usable; don't spin
            break
    return passages[:count]


async def run(args: argparse.Namespace) -> int:
    cells = load_cells()
    if not cells:
        print("No covered cells found in the triplet snapshot.", file=sys.stderr)
        return 1

    keys = [(c["dimension"], c["concept"], c["state"]) for c in cells]
    cell_by_key = {(c["dimension"], c["concept"], c["state"]): c for c in cells}
    alloc = allocate(keys, args.n)

    # Resume: keep existing rows unless --force; only fill missing per-cell counts.
    existing: list[dict] = []
    have: dict[tuple, int] = defaultdict(int)
    if args.output.exists() and not args.force:
        for line in args.output.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            existing.append(r)
            have[(int(r["expected_dimension"]), r["expected_concept"], r["expected_state"])] += 1

    print(
        f"cells={len(cells)}  target n={args.n}  "
        f"(resuming: {len(existing)} kept)" if existing else
        f"cells={len(cells)}  target n={args.n}"
    )

    settings = Settings.load()
    if not settings.aws_region:
        print("AWS region not configured (set AWS_REGION / SVARUPA_AWS_REGION).", file=sys.stderr)
        return 1
    model_id = args.model_id or settings.bedrock_model_id
    provider = BedrockLLMProvider(region_name=settings.aws_region)
    sem = asyncio.Semaphore(args.concurrency)

    async def do_cell(key: tuple) -> list[dict]:
        cell = cell_by_key[key]
        need = alloc.get(key, 0) - have.get(key, 0)
        if need <= 0:
            return []
        texts = await generate_cell(
            provider, cell, need,
            model_id=model_id, batch=args.batch, timeout_s=args.timeout_s, sem=sem,
        )
        start = have.get(key, 0)
        rows = []
        for i, text in enumerate(texts, start=start + 1):
            rows.append(
                {
                    "id": f"D{cell['dimension']}-{cell['concept']}-{cell['state']}-{i}",
                    "analysis_text": text,
                    "expected_dimension": str(cell["dimension"]),
                    "expected_concept": cell["concept"],
                    "expected_state": cell["state"],
                }
            )
        print(f"  D{cell['dimension']} {cell['concept']}/{cell['state']}: +{len(rows)}")
        return rows

    produced = await asyncio.gather(*(do_cell(k) for k in keys))
    new_rows = [r for batch in produced for r in batch]

    all_rows = existing + new_rows
    rng = random.Random(args.seed)
    rng.shuffle(all_rows)  # de-cluster so a bulk run isn't grouped by cell
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_rows),
        encoding="utf-8",
    )

    by_dim = defaultdict(int)
    for r in all_rows:
        by_dim[r["expected_dimension"]] += 1
    print(
        f"\nWrote {len(all_rows)} rows ({len(new_rows)} new) -> {args.output}\n"
        f"by dimension: {dict(sorted(by_dim.items()))}"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--output", type=Path, default=ROOT / "data/eval/met_coverage_questions.jsonl")
    ap.add_argument("--n", type=int, default=500, help="total passages, spread across covered cells")
    ap.add_argument("--batch", type=int, default=10, help="passages requested per LLM call")
    ap.add_argument("--concurrency", type=int, default=4, help="concurrent LLM calls")
    ap.add_argument("--timeout-s", type=float, default=90.0)
    ap.add_argument("--model-id", default=None, help="override Bedrock model id")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force", action="store_true", help="ignore any existing output and regenerate")
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
