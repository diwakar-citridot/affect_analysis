#!/usr/bin/env python3
"""Score bulk_analyze results against the coverage labels.

Joins ``--results`` (bulk_analyze output) to the expected concept/state/dimension
labels (either carried in the results, or joined by ``id`` from ``--labels``) and
reports recall at three levels plus a per-cell breakdown and a token rollup:

  concept       : expected concept appears anywhere in attribute_scores
  concept+state : expected concept appears WITH the expected state (pole)
  top1          : expected concept is the single highest-relevance score

Denominators are reported both over successful rows and over all rows (errors /
abstentions count as misses in the all-rows view).

  .venv/bin/python scripts/score_coverage.py \
    --results sample50_results.jsonl \
    --labels data/eval/aff_coverage_sample_50.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def build_slug_to_dim(path: Path) -> dict[str, str]:
    """concept slug -> dimension_id. Accepts the concept-layer snapshot (.json with
    ``concepts[].slug/dimension_id``) or a coverage .jsonl (expected_concept/dimension)."""
    m: dict[str, str] = {}
    if not path.exists():
        return m
    if path.suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        for c in payload.get("concepts", []):
            if c.get("slug") and c.get("dimension_id") is not None:
                m[str(c["slug"])] = str(c["dimension_id"])
    else:
        for r in load_jsonl(path):
            c, d = r.get("expected_concept"), r.get("expected_dimension")
            if c and d is not None:
                m[str(c)] = str(d)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--labels", type=Path, default=Path("data/eval/aff_coverage_sample_50.jsonl"),
                    help="source sample with expected_* labels (joined by id)")
    ap.add_argument("--slug-map", type=Path, default=Path("data/kg/aff_concept_layer.v1.json"),
                    help="source for concept-slug -> dimension_id (for triplet dimension match)")
    ap.add_argument("--dump", type=Path, default=None,
                    help="write per-row triplet comparison JSONL (default: <results>.triplets.jsonl)")
    ap.add_argument("--show", type=int, default=8, help="print this many example rows inline")
    ap.add_argument("--errors", action="store_true", help="list the failing ids")
    args = ap.parse_args()

    results = load_jsonl(args.results)
    labels = {str(r["id"]): r for r in load_jsonl(args.labels)} if args.labels.exists() else {}
    slug_dim = build_slug_to_dim(args.slug_map)

    # dimension_id -> dimension_name, harvested from the API's own labels in the
    # results (each attribute_score carries dimension_name = sanskrit_term).
    dim_name: dict[str, str] = {}
    for r in results:
        for s in r.get("attribute_scores") or []:
            did = slug_dim.get(s.get("attribute"))
            if did and s.get("dimension_name"):
                dim_name[str(did)] = s["dimension_name"]

    def dname(d) -> str | None:
        if d is None:
            return None
        return dim_name.get(str(d), str(d))

    def expected(r: dict) -> tuple[str | None, str | None, str | None]:
        lab = labels.get(str(r.get("id")), r)
        return (
            str(lab.get("expected_dimension")) if lab.get("expected_dimension") is not None else None,
            lab.get("expected_concept"),
            lab.get("expected_state"),
        )

    total = len(results)
    errors = [r for r in results if not r.get("ok")]
    abstained = [r for r in results if r.get("ok") and r.get("abstained_dimensions")]
    scored = [r for r in results if r.get("ok")]

    keys = ("triplet", "concept", "state", "top1", "triplet_lenient")
    cells: dict[tuple, dict] = defaultdict(lambda: {"n": 0, **{k: 0 for k in keys}})
    tot = {"n": 0, **{k: 0 for k in keys}}
    ambiguous_n = 0
    tokens = {"input_tokens": 0, "output_tokens": 0,
              "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    have_tokens = False
    triplet_dump: list[dict] = []

    for r in results:
        edim, econcept, estate = expected(r)
        edim_name = dname(edim)
        cell = (edim_name, estate)
        cells[cell]["n"] += 1
        tot["n"] += 1
        for k in tokens:  # roll up whatever tokens are present
            v = r.get(k)
            if v is not None:
                tokens[k] += int(v)
                have_tokens = True
        if not r.get("ok"):
            triplet_dump.append({"id": r.get("id"), "ok": False,
                                 "expected": {"dimension": edim_name, "concept": econcept, "state": estate},
                                 "returned": [], "matched": False, "error": r.get("error")})
            continue
        scores = r.get("attribute_scores") or []
        by_attr = {s["attribute"]: s for s in scores}
        # each returned score is a triplet: (dimension_name, concept, state)
        returned = [
            {"dimension": s.get("dimension_name") or dname(slug_dim.get(s["attribute"])),
             "concept": s["attribute"], "state": s.get("state"), "relevance": s.get("relevance")}
            for s in scores
        ]
        returned_triplets = {(t["dimension"], t["concept"], t["state"]) for t in returned}
        exp_triplet = (edim_name, econcept, estate)
        triplet_hit = exp_triplet in returned_triplets
        lab = labels.get(str(r.get("id")), r)
        alts = lab.get("acceptable_alternatives") or []
        alt_triplets = {
            (a.get("dimension") or edim_name, a["concept"], a["state"])
            for a in alts
            if a.get("concept") and a.get("state")
        }
        lenient_hit = triplet_hit or any(t in returned_triplets for t in alt_triplets)
        is_ambiguous = bool(lab.get("ambiguous"))
        if is_ambiguous:
            ambiguous_n += 1
        concept_hit = econcept in by_attr
        state_hit = concept_hit and by_attr[econcept].get("state") == estate
        top1_attr = max(scores, key=lambda s: s.get("relevance", 0))["attribute"] if scores else None
        top1_hit = top1_attr == econcept
        for key, hit in (
            ("triplet", triplet_hit),
            ("triplet_lenient", lenient_hit),
            ("concept", concept_hit),
            ("state", state_hit),
            ("top1", top1_hit),
        ):
            cells[cell][key] += int(hit)
            tot[key] += int(hit)
        matched_alt = next((t for t in alt_triplets if t in returned_triplets), None)
        triplet_dump.append({
            "id": r.get("id"), "ok": True,
            "expected": {"dimension": edim_name, "concept": econcept, "state": estate},
            "ambiguous": is_ambiguous,
            "acceptable_alternatives": [
                {"dimension": t[0], "concept": t[1], "state": t[2]} for t in sorted(alt_triplets)
            ] if alt_triplets else [],
            "matched": triplet_hit,
            "matched_lenient": lenient_hit,
            "matched_triplet": {"dimension": edim_name, "concept": econcept, "state": estate} if triplet_hit else None,
            "matched_alternative": (
                {"dimension": matched_alt[0], "concept": matched_alt[1], "state": matched_alt[2]}
                if matched_alt else None
            ),
            "returned": sorted(returned, key=lambda t: -(t["relevance"] or 0)),
        })

    n_scored = len(scored)
    def pct(x, d):
        return f"{100*x/d:5.1f}%" if d else "   -  "

    print(f"Results: {total} total | ok={n_scored} | abstained={len(abstained)} | errors={len(errors)}"
          f" | ambiguous={ambiguous_n}\n")
    print("Match             over successful   over all rows")
    for key, name in (
        ("triplet", "TRIPLET (d,c,s)"),
        ("triplet_lenient", "triplet+alts"),
        ("concept", "concept only"),
        ("state", "concept+state"),
        ("top1", "top-1 concept"),
    ):
        print(f"  {name:<15} {tot[key]:>3}/{n_scored} {pct(tot[key], n_scored)}"
              f"     {tot[key]:>3}/{total} {pct(tot[key], total)}")

    print("\nTriplet match per (dimension, state) cell  [matched / n]:")
    # order dimensions by their numeric id, but label with the name
    id_by_name = {v: k for k, v in dim_name.items()}
    present = [d for (d, _) in cells if d]
    dims = sorted(set(present), key=lambda nm: int(id_by_name.get(nm, "999")))
    states = ["deficiency", "balance", "excess"]
    print(f"  {'':<26}" + "".join(f"{s:>14}" for s in states))
    for d in dims:
        row = f"  {str(d)[:24]:<26}"
        for s in states:
            c = cells.get((d, s), {"n": 0, "triplet": 0})
            row += f"{c['triplet']:>6}/{c['n']:<7}" if c["n"] else f"{'-':>14}"
        print(row)

    if args.show:
        print(f"\nExample rows (expected triplet vs returned triplets):")
        for rec in [d for d in triplet_dump if d.get("ok")][: args.show]:
            e = rec["expected"]
            mark = "✓" if rec["matched"] else "✗"
            print(f"  [{mark}] {rec['id']}  expected=({e['dimension']},{e['concept']},{e['state']})")
            for t in rec["returned"][:6]:
                hit = "  <== match" if (t["dimension"], t["concept"], t["state"]) == (e["dimension"], e["concept"], e["state"]) else ""
                print(f"         ({t['dimension']},{t['concept']},{t['state']}) rel={t['relevance']}{hit}")

    dump_path = args.dump or args.results.with_suffix(".triplets.jsonl")
    dump_path.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in triplet_dump), encoding="utf-8")
    print(f"\nPer-row triplet comparison written -> {dump_path}")

    if have_tokens:
        print(f"\nTokens (summed over {total} rows): "
              f"input={tokens['input_tokens']}  output={tokens['output_tokens']}  "
              f"cache_read={tokens['cache_read_input_tokens']}  "
              f"cache_write={tokens['cache_creation_input_tokens']}")
        # Sonnet 3.5 list-ish pricing (USD per 1M tokens): input $3, output $15,
        # cache write $3.75, cache read $0.30 — adjust via env if model differs.
        import os

        pin = float(os.environ.get("SVARUPA_COST_INPUT_PER_M", "3.0"))
        pout = float(os.environ.get("SVARUPA_COST_OUTPUT_PER_M", "15.0"))
        pcw = float(os.environ.get("SVARUPA_COST_CACHE_WRITE_PER_M", "3.75"))
        pcr = float(os.environ.get("SVARUPA_COST_CACHE_READ_PER_M", "0.30"))
        fresh_in = max(0, tokens["input_tokens"] - tokens["cache_read_input_tokens"])
        cost = (
            fresh_in * pin / 1_000_000
            + tokens["output_tokens"] * pout / 1_000_000
            + tokens["cache_creation_input_tokens"] * pcw / 1_000_000
            + tokens["cache_read_input_tokens"] * pcr / 1_000_000
        )
        per_row = cost / total if total else 0.0
        print(f"Est. cost @ Sonnet-ish rates: ${cost:.4f} total  (${per_row:.4f}/row)")
        print("  Levers: prompt cache (prefix stable), omit rationale/span in output, "
              "concurrency≤3, avoid --latency deep unless measuring.")
    else:
        print("\nTokens: not present in results (older run, or API not restarted with usage plumbing).")

    if errors:
        codes = defaultdict(int)
        for r in errors:
            codes[r.get("http_status", "network")] += 1
        print(f"\nErrors by status: {dict(codes)}")
        if args.errors:
            for r in errors:
                print(f"  {r['id']}  http={r.get('http_status')}  {str(r.get('error'))[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
