#!/usr/bin/env python3
"""Draw a stratified sample from aff_coverage_questions.jsonl, balanced uniformly
across dimensions x status.

Splits the target dimensions (default D2/D8/D9) x states
(deficiency/balance/excess) into cells and allocates ``--n`` as evenly as
possible across the cells (capped by availability, with redistribution when a
cell is short). Sampling within a cell is random but seeded, so runs are
reproducible. Output is the same API-ready JSONL schema as the input, so it
feeds straight into scripts/bulk_analyze.py.

Example:
  .venv/bin/python scripts/sample_coverage.py --n 50 \
    --input data/eval/aff_coverage_questions.jsonl \
    --output data/eval/aff_coverage_sample_50.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def allocate(cells: list[tuple], avail: dict, n: int) -> dict:
    """Spread n across cells as evenly as possible, capped by availability."""
    alloc = {c: 0 for c in cells}
    active = [c for c in cells if avail[c] > 0]
    remaining = min(n, sum(avail.values()))
    while remaining > 0 and active:
        share = remaining // len(active)
        if share == 0:
            # hand out the leftover one-per-cell, in stable cell order
            for c in sorted(active):
                if remaining == 0:
                    break
                if alloc[c] < avail[c]:
                    alloc[c] += 1
                    remaining -= 1
            break
        for c in list(active):
            take = min(share, avail[c] - alloc[c])
            alloc[c] += take
            remaining -= take
            if alloc[c] >= avail[c]:
                active.remove(c)
    return alloc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=Path("data/eval/aff_coverage_questions.jsonl"))
    ap.add_argument("--output", type=Path, default=Path("data/eval/aff_coverage_sample_50.jsonl"))
    ap.add_argument("--n", type=int, default=50, help="total questions to sample")
    ap.add_argument("--dimensions", default="2,8,9", help="comma-separated expected_dimension values")
    ap.add_argument("--states", default="deficiency,balance,excess")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    dims = [d.strip() for d in args.dimensions.split(",")]
    states = [s.strip() for s in args.states.split(",")]

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_cell: dict[tuple, list] = defaultdict(list)
    for r in rows:
        key = (str(r.get("expected_dimension")), str(r.get("expected_state")))
        if key[0] in dims and key[1] in states:
            by_cell[key].append(r)

    cells = [(d, s) for d in dims for s in states if (d, s) in by_cell]
    avail = {c: len(by_cell[c]) for c in cells}
    if not cells:
        print("No rows matched the requested dimensions/states.")
        return 1

    alloc = allocate(cells, avail, args.n)

    rng = random.Random(args.seed)
    sample: list[dict] = []
    for c in cells:
        pool = by_cell[c][:]
        rng.shuffle(pool)
        sample.extend(pool[: alloc[c]])
    rng.shuffle(sample)  # mix cells so a bulk run isn't grouped by dimension

    args.output.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in sample), encoding="utf-8"
    )

    # report the realized distribution
    print(f"Sampled {len(sample)} / requested {args.n}  (seed={args.seed})  -> {args.output}\n")
    hdr = f"{'':<8}" + "".join(f"{s:>12}" for s in states) + f"{'TOTAL':>8}"
    print(hdr)
    for d in dims:
        line = f"D{d:<7}"
        tot = 0
        for s in states:
            k = alloc.get((d, s), 0)
            tot += k
            line += f"{k:>12}"
        print(line + f"{tot:>8}")
    col_tot = "".join(f"{sum(alloc.get((d, s), 0) for d in dims):>12}" for s in states)
    print(f"{'TOTAL':<8}{col_tot}{len(sample):>8}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
